"""This is the main backend server for the RAG chatbot.
It uses FastAPI to expose a /chat endpoint that leverages a Qdrant vector database
and OpenRouter for AI-powered chat completions."""
import os
import logging
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from openai import OpenAI
from qdrant_client import QdrantClient, models

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("rag-chatbot-api")

# --- Environment Variable Loading and Validation ---
def load_env_vars():
    """Loads and validates required environment variables."""
    
    required_vars = {
        "QDRANT_URL": os.getenv("QDRANT_URL"),
        "QDRANT_API_KEY": os.getenv("QDRANT_API_KEY"),
        "OPENROUTER_API_KEY": os.getenv("OPENROUTER_API_KEY"),
        "OPENROUTER_BASE_URL": os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        "OPENROUTER_EMBEDDING_MODEL": os.getenv("OPENROUTER_EMBEDDING_MODEL", "openai/text-embedding-3-small"),
        "OPENROUTER_CHAT_MODEL": os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
        "QDRANT_COLLECTION_NAME": os.getenv("QDRANT_COLLECTION_NAME", "humanoid_textbook"),
    }
    
    missing_vars = [key for key, value in required_vars.items() if value is None]
    if missing_vars:
        message = f"Missing required environment variables: {', '.join(missing_vars)}"
        logger.error(message)
        raise ValueError(message)
        
    logger.info("All required environment variables are loaded.")
    return required_vars

config = load_env_vars()

# --- FastAPI Lifecycle (Resource Management) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the lifecycle of resources needed by the application.
    Initializes Qdrant and OpenAI clients on startup and closes them on shutdown.
    """
    logger.info("Initializing clients...")
    # Initialize Qdrant client
    app.state.qdrant_client = QdrantClient(
        url=config["QDRANT_URL"],
        api_key=config["QDRANT_API_KEY"],
    )
    # Initialize OpenAI client for OpenRouter
    app.state.openai_client = OpenAI(
        api_key=config["OPENROUTER_API_KEY"],
        base_url=config["OPENROUTER_BASE_URL"],
    )
    logger.info("Qdrant and OpenAI clients initialized successfully.")
    
    yield
    
    # Cleanup clients on shutdown
    logger.info("Closing clients...")
    # No explicit close method for qdrant_client or openai client in recent versions
    app.state.qdrant_client = None
    app.state.openai_client = None
    logger.info("Clients closed.")

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Physical AI Humanoid Textbook - RAG Chatbot API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Models ---
class ChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="The user's question for the chatbot.")

class ChatResponse(BaseModel):
    response: str = Field(..., description="The chatbot's answer.")

# --- API Endpoints ---
@app.get("/", summary="Health Check")
def health_check():
    """Provides a simple health check endpoint."""
    return {"status": "ok", "message": "Physical AI & Humanoid Robotics Chatbot is healthy"}

@app.post("/chat", response_model=ChatResponse, summary="Process a Chat Request")
async def chat(req: Request, chat_request: ChatRequest):
    """
    Handles the main chat logic, including RAG retrieval and AI generation.
    """
    openai_client: OpenAI = req.app.state.openai_client
    qdrant_client: QdrantClient = req.app.state.qdrant_client
    
    # 1. Generate Embedding for the User's Query
    try:
        embed_response = openai_client.embeddings.create(
            model=config["OPENROUTER_EMBEDDING_MODEL"],
            input=[chat_request.prompt]
        )
        query_vector = embed_response.data[0].embedding
    except Exception as e:
        logger.error(f"Embedding failed for query: '{chat_request.prompt}'. Error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create text embedding: {e}")

    # 2. Search Qdrant for Relevant Context
    try:
        search_results = qdrant_client.search(
            collection_name=config["QDRANT_COLLECTION_NAME"],
            query_vector=query_vector,
            limit=3,  # Retrieve top 3 most relevant chunks
            with_payload=True,
        )
    except Exception as e:
        logger.error(f"Qdrant search failed. Error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search for context: {e}")

    # 3. Assemble Context from Search Results
    context_chunks: List[str] = []
    if search_results:
        for point in search_results:
            # Defensively extract text from payload
            if point.payload and isinstance(point.payload.get("text"), str):
                context_chunks.append(point.payload["text"])
    
    if not context_chunks:
        logger.warning(f"No relevant context found in database for query: '{chat_request.prompt}'")
        # Fallback: answer without context
        context_str = "No specific context found in the textbook."
    else:
        context_str = "\n\n---\n\n".join(context_chunks)

    # 4. Construct the Final Prompt for the Chat Model
    system_prompt = """
    You are a specialized professor for the 'Physical AI & Humanoid Robotics' textbook.
    Your role is to provide clear, accurate, and helpful answers to student questions.
    You must base your answers *only* on the context provided below from the textbook.
    If the context does not contain the answer, state that the information is not available in the provided materials.
    Do not use any prior knowledge. Be concise and directly address the question.
    """.strip()
    
    user_prompt = f"""
Context from the textbook:
---
{context_str}
---

Student's Question:
{chat_request.prompt}
    """.strip()

    # 5. Generate the Final Answer using OpenRouter
    try:
        chat_completion = openai_client.chat.completions.create(
            model=config["OPENROUTER_CHAT_MODEL"],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            # Add headers required by some OpenRouter models
            extra_headers={
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "Physical AI & Humanoid Robotics Textbook",
            }
        )
        final_response = chat_completion.choices[0].message.content
        if not final_response:
             logger.warning("LLM returned an empty response.")
             final_response = "I'm sorry, but I was unable to generate a response."

    except Exception as e:
        logger.error(f"Chat completion failed. Error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate chat response: {e}")

    return ChatResponse(response=final_response)

if __name__ == "__main__":
    import uvicorn
    # This allows running the app directly for development
    # Use `uvicorn src.main:app --reload` for production-like Gunicorn/Uvicorn workers
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
