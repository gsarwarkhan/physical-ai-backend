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
from qdrant_client import QdrantClient
from dotenv import load_dotenv

load_dotenv()

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
        # Support CHAT_MODEL from .env as fallback
        "OPENROUTER_CHAT_MODEL": os.getenv("OPENROUTER_MODEL", os.getenv("CHAT_MODEL", "openai/gpt-4o-mini")),
        "QDRANT_COLLECTION_NAME": os.getenv("QDRANT_COLLECTION_NAME", "humanoid_textbook"),
    }
    
    missing_vars = [key for key, value in required_vars.items() if value is None]
    if missing_vars:
        message = f"Missing required environment variables: {', '.join(missing_vars)}"
        logger.error(message)
        # Check .env file exists? 
        # For now, just log error, but in prod we might want to crash.
        # We'll allow it to proceed to let lifespan fail gracefully if needed.
    
    logger.info("Environment variables check completed.")
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
    
    try:
        # Initialize Qdrant client
        # Note: We rely on default FastEmbed handling (automatic model download/load)
        app.state.qdrant_client = QdrantClient(
            url=config["QDRANT_URL"],
            api_key=config["QDRANT_API_KEY"],
        )
        # Initialize OpenAI client for OpenRouter
        # Auto-detect if using direct OpenAI key (starts with sk-proj)
        openai_api_key = config["OPENROUTER_API_KEY"]
        openai_base_url = config["OPENROUTER_BASE_URL"]
        
        if openai_api_key and openai_api_key.startswith("sk-proj"):
            logger.warning("Detected OpenAI Project Key. Switching base_url to 'https://api.openai.com/v1'.")
            openai_base_url = "https://api.openai.com/v1"
            # Also fix model ID if it has openai/ prefix which is OpenRouter specific
            if config["OPENROUTER_CHAT_MODEL"].strip().startswith("openai/"):
                config["OPENROUTER_CHAT_MODEL"] = config["OPENROUTER_CHAT_MODEL"].replace("openai/", "").strip()
            
            logger.info(f"Model ID updated to: '{config['OPENROUTER_CHAT_MODEL']}' for direct OpenAI usage.")

        app.state.openai_client = OpenAI(
            api_key=openai_api_key,
            base_url=openai_base_url,
        )
        logger.info("Qdrant and OpenAI clients initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize clients: {e}")
        # We don't raise here to allow the app to start and return 500s on endpoints 
        # rather than crashing the whole container immediately, but for dev it's better to see.
    
    yield
    
    # Cleanup clients on shutdown
    logger.info("Closing clients...")
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

from typing import List, Dict, Optional
# ... existing imports ...

# --- API Models ---
class ChatRequest(BaseModel):
    # Frontend sends 'message', not 'prompt'
    message: str = Field(..., min_length=1, description="The user's question for the chatbot.")
    session_id: Optional[str] = Field(None, description="Optional session ID.")

class ChatResponse(BaseModel):
    response: str = Field(..., description="The chatbot's answer.")
    session_id: Optional[str] = Field(None, description="Session ID returned to client.")

class APIResponse(BaseModel):
    status: str
    message: str = None
    data: ChatResponse = None

# --- API Endpoints ---
@app.get("/", summary="Health Check")
def health_check():
    """Provides a simple health check endpoint."""
    return {"status": "ok", "message": "Physical AI & Humanoid Robotics Chatbot is healthy"}

@app.post("/chat", response_model=APIResponse, summary="Process a Chat Request")
async def chat(req: Request, chat_request: ChatRequest):
    """
    Handles the main chat logic, including RAG retrieval and AI generation.
    """
    openai_client: OpenAI = req.app.state.openai_client
    qdrant_client: QdrantClient = req.app.state.qdrant_client
    
    if not openai_client or not qdrant_client:
         raise HTTPException(status_code=503, detail="Services not initialized")

    prompt = chat_request.message
    session_id = chat_request.session_id or "new_session" # Simple handling for now
    
    # 1. Search Qdrant for Relevant Context (using FastEmbed via client.query)
    try:
        # qdrant_client.query automatically embeds the query string
        search_results = qdrant_client.query(
            collection_name=config["QDRANT_COLLECTION_NAME"],
            query_text=prompt,
            limit=3
        )
    except Exception as e:
        logger.error(f"Qdrant query failed. Error: {e}")
        # Fallback to empty context instead of failing entire request? 
        # User requested defensive error handling.
        search_results = []
        # We log and proceed with no context.

    # 2. Assemble Context from Search Results
    context_chunks: List[str] = []
    if search_results:
        for result in search_results:
            # Qdrant 1.10+ query returns QueryResponse objects
            # The text is typically in `document` (if using add) or `metadata['text']` or payload.
            # verify_qdrant_payload.py will help confirm this.
            # Usually with `client.add`, the text is stored in the document.
            # `result.document` attribute exists on QueryResponse.
            if hasattr(result, 'document') and result.document:
                 context_chunks.append(result.document)
            elif result.metadata and 'text' in result.metadata:
                 context_chunks.append(result.metadata['text'])
            elif hasattr(result, 'payload') and result.payload and 'text' in result.payload:
                 context_chunks.append(result.payload['text'])
    
    if not context_chunks:
        logger.info(f"No relevant context found for query: '{prompt}'")
        context_str = "No specific context found in the textbook."
    else:
        context_str = "\n\n---\n\n".join(context_chunks)

    # 3. Construct the Final Prompt for the Chat Model
    system_prompt = """
    You are a specialized professor for the 'Physical AI & Humanoid Robotics' textbook.
    Your role is to provide clear, accurate, and helpful answers to student questions.
    
    Guidelines:
    1. For technical questions, base your answers *primary* on the provided context.
    2. If the user greets you or asks about your identity, verify polite conversation.
    3. If the context does not contain the answer to a technical question, admit it but try to be helpful if possible, or state that the specific detailed information is not in the current context.
    4. Do not use prior knowledge for specific data or facts not in the context, but you can use general knowledge to explain concepts found in the context.
    5. Be concise and directly address the question.
    """.strip()
    
    user_prompt = f"""
Context from the textbook:
---
{context_str}
---

Student's Question:
{prompt}
    """.strip()

    # 4. Generate the Final Answer
    final_response = "I'm sorry, possibly due to a network error, I couldn't generate a response."
    try:
        # Determine if we are using OpenAI direct API based on base_url (hacky check)
        is_openai_direct = "api.openai.com" in str(openai_client.base_url)
        
        request_kwargs = {
            "model": config["OPENROUTER_CHAT_MODEL"],
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
        }
        
        if not is_openai_direct:
             request_kwargs["extra_headers"] = {
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "Physical AI & Humanoid Robotics Textbook",
            }
        
        chat_completion = openai_client.chat.completions.create(**request_kwargs)
        
        if chat_completion.choices:
            final_response = chat_completion.choices[0].message.content
        else:
            logger.warning("LLM returned no choices.")
    
    except Exception as e:
        logger.error(f"Chat completion failed. Error: {e}")
        # Return a polite error message to the user instead of 500
        final_response = "I encountered an error while trying to generate a response. Please try again later."

    return APIResponse(
        status="success",
        data={
            "response": final_response,
            "session_id": session_id
        }
    )

if __name__ == "__main__":
    import uvicorn
    # This allows running the app directly for development
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
