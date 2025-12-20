from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from qdrant_client import QdrantClient
import google.generativeai as genai
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Configuration ---
# Ensure these environment variables are set
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# --- FastAPI App Initialization ---
app = FastAPI(
    title="RAG Chatbot API",
    description="A RAG-based chatbot using Google Gemini and Qdrant.",
    version="1.0.0",
)

# --- CORS Middleware ---
# Set allow_origins=['*'] to eliminate 'Failed to fetch' errors during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

# --- Service Clients Initialization ---
qdrant_client_instance: QdrantClient = None
generation_model_instance: genai.GenerativeModel = None
embedding_model_instance: genai.GenerativeModel = None

@app.on_event("startup")
async def startup_event():
    global qdrant_client_instance, generation_model_instance, embedding_model_instance
    try:
        # Initialize Qdrant client
        if not QDRANT_URL or not QDRANT_API_KEY:
            raise ValueError("QDRANT_URL and QDRANT_API_KEY environment variables must be set.")
        qdrant_client_instance = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        logger.info("Qdrant client initialized successfully.")

        # Configure Google Generative AI
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY environment variable must be set.")
        genai.configure(api_key=GOOGLE_API_KEY)
        logger.info("Google Generative AI configured.")
        
        # Initialize the Gemini model for answer generation
        generation_model_instance = genai.GenerativeModel('gemini-1.5-flash')
        logger.info("Gemini 1.5 Flash model initialized.")
        
        # Initialize the model for embedding
        embedding_model_instance = genai.GenerativeModel('text-embedding-004')
        logger.info("Text Embedding 004 model initialized.")

    except Exception as e:
        logger.error(f"Failed to initialize service clients on startup: {e}", exc_info=True)
        # Re-raise the exception to prevent the application from starting
        raise

# --- Pydantic Models ---
class AskRequest(BaseModel):
    question: str
    user_context: str = ""

class AskResponse(BaseModel):
    answer: str

# --- Health Check Endpoint ---
@app.get("/", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint to test if the server is alive.
    """
    return {"status": "alive", "message": "RAG Chatbot API is running!"}

# --- API Endpoints ---
@app.post("/ask", response_model=AskResponse)
async def ask_rag_chatbot(request: AskRequest):
    """
    Handles a user's question by performing Retrieval-Augmented Generation.
    1.  Generates an embedding for the user's question.
    2.  Searches Qdrant for the most relevant context.
    3.  Uses the retrieved context and the original question to generate an answer.
    """
    if not request.question:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Question cannot be empty.")

    try:
        # 1. Generate embedding for the user's question
        # Ensure embedding_model_instance is initialized
        if embedding_model_instance is None:
            raise RuntimeError("Embedding model not initialized.")
            
        question_embedding = genai.embed_content(
            model=f'models/{embedding_model_instance.model_name}',
            content=request.question,
            task_type="retrieval_query"
        )['embedding']
        logger.info("Question embedding generated.")

    except Exception as e:
        logger.error(f"Gemini API (embedding) failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate embedding: {e}"
        )

    try:
        # 2. Search Qdrant for relevant documents
        # Ensure qdrant_client_instance is initialized
        if qdrant_client_instance is None:
            raise RuntimeError("Qdrant client not initialized.")
            
        search_results = qdrant_client_instance.search(
            collection_name="humanoid_textbook",
            query_vector=question_embedding,
            limit=3,
        )
        logger.info(f"Qdrant search returned {len(search_results)} results.")
        
        # 3. Assemble the context from search results
        context = "\n\n".join([
            f"--- Context Snippet from: {res.payload.get('source', 'Unknown')} ---\n"
            f"{res.payload.get('text', '')}"
            for res in search_results
        ])
        logger.debug(f"Assembled context: {context}")

    except Exception as e:
        logger.error(f"Qdrant failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve context from Qdrant: {e}"
        )

    try:
        # 4. Generate an answer using the Gemini model
        # Ensure generation_model_instance is initialized
        if generation_model_instance is None:
            raise RuntimeError("Generation model not initialized.")

        prompt = f"""
        You are an expert AI tutor for a course on Physical AI and Humanoid Robotics.
A student has asked a question. Use the following context from the course textbook to provide a clear,
professional, and helpful answer. Ensure your answer is directly relevant to the question and the provided context.

**Student Background (if provided):**
{request.user_context if request.user_context else "N/A"}

**Context from the textbook:**
{context if context else "No relevant context found in the textbook."} 

**Student's Question:**
{request.question}

**Answer:**
"""
        
        response = generation_model_instance.generate_content(prompt)
        logger.info("Answer generated by Gemini.")
        
        return {"answer": response.text}

    except Exception as e:
        logger.error(f"Gemini API (generation) failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate answer: {e}"
        )

# --- Uvicorn Runner ---
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server with Uvicorn...")
    uvicorn.run(app, host="0.0.0.0", port=8000)