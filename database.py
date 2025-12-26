import os
from typing import List, Optional
from sqlmodel import Field, SQLModel, create_engine, Relationship
from datetime import datetime
from uuid import UUID, uuid4 

class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sender: str 
    text: str
    timestamp: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    session_id: Optional[UUID] = Field(default=None, foreign_key="chatsession.id")

    session: Optional["ChatSession"] = Relationship(back_populates="messages")

class ChatSession(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True) 
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    
    messages: List["Message"] = Relationship(back_populates="session") # Corrected back_populates

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# Check for DATABASE_URL environment variable
database_url = os.environ.get("DATABASE_URL")

connect_args = {}
if database_url and database_url.startswith("postgres"):
    # Fix for SQLAlchemy requiring 'postgresql://' instead of 'postgres://' (common in some providers)
    url = database_url.replace("postgres://", "postgresql://")
else:
    url = sqlite_url
    connect_args = {"check_same_thread": False}

engine = create_engine(url, echo=False, connect_args=connect_args) 

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

if __name__ == "__main__":
    create_db_and_tables()