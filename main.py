from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from uuid import UUID
from sqlmodel import Session
import os
import logging

from router import ai_wrapper
from database import ChatSession, create_db_and_tables, engine
from crud import (
    get_chat_session_by_id, 
    create_new_chat_session, 
    get_messages_for_session, 
    add_message_to_session
)

# --------------------------
# Logging Configuration
# --------------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --------------------------
# FastAPI App & CORS
# --------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://hackathon-1-q4.vercel.app"  # your frontend URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------
# Request / Response Models
# --------------------------
class ChatRequest(BaseModel):
    session_id: Optional[UUID] = None
    message: str

class APIResponse(BaseModel):
    status: str = "success"
    message: Optional[str] = None
    data: Optional[Dict] = None

class APIErrorResponse(BaseModel):
    status: str = "error"
    message: str = Field(..., description="Detailed error message")
    code: Optional[int] = Field(None, description="Optional error code")

# --------------------------
# DB Session Dependency
# --------------------------
def get_session():
    with Session(engine) as session:
        yield session

# --------------------------
# Startup Event
# --------------------------
@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    logger.info("Database tables created successfully.")

# --------------------------
# Health Check
# --------------------------
@app.get("/")
def health_check():
    return {"status": "ok", "message": "Physical AI & Humanoid Robotics Chatbot is healthy"}

# --------------------------
# Chat Endpoint
# --------------------------
@app.post("/chat", response_model=APIResponse, responses={
    400: {"model": APIErrorResponse, "description": "Invalid Request"},
    500: {"model": APIErrorResponse, "description": "Internal Server Error"},
    502: {"model": APIErrorResponse, "description": "AI Service Error"}
})
async def chat(request: ChatRequest, db_session: Session = Depends(get_session)):
    try:
        # --------------------------
        # Handle Chat Session
        # --------------------------
        chat_session: Optional[ChatSession] = None

        if request.session_id:
            chat_session = get_chat_session_by_id(db_session, request.session_id)

        if not chat_session:
            chat_session = create_new_chat_session(db_session)
            logger.info(f"Created new chat session: {chat_session.id}")

        # --------------------------
        # Retrieve conversation
        # --------------------------
        db_messages = get_messages_for_session(db_session, chat_session.id)
        conversation_history = [{"sender": msg.sender, "text": msg.text} for msg in db_messages]

        # Add user message
        conversation_history.append({"sender": "user", "text": request.message})
        add_message_to_session(db_session, chat_session.id, "user", request.message)

        # --------------------------
        # Get AI response
        # --------------------------
        ai_response_text = ai_wrapper.get_ai_response(conversation_history)
        add_message_to_session(db_session, chat_session.id, "ai", ai_response_text)

        return APIResponse(
            status="success",
            data={"response": ai_response_text, "session_id": chat_session.id}
        )

    except ValueError as e:
        logger.error(f"AI Service Error for session {request.session_id}: {e}")
        return JSONResponse(
            status_code=502,
            content=APIErrorResponse(status="error", message=str(e), code=502).dict()
        )
    except HTTPException as e:
        logger.warning(f"HTTP Exception: {e.detail}")
        raise e
    except Exception as e:
        logger.exception(f"Unexpected internal server error for session {request.session_id}")
        return JSONResponse(
            status_code=500,
            content=APIErrorResponse(
                status="error",
                message="An unexpected internal server error occurred.",
                code=500
            ).dict()
        )

# --------------------------
# Run server
# --------------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
