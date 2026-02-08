"""
Conversation model for storing chat session data.
Represents a user's chat session with the AI, containing message history and context.
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum

class MessageRole(str, Enum):
    """
    Role of a message in a conversation.
    """
    user = "user"
    assistant = "assistant"
    system = "system"

class Conversation(SQLModel, table=True):
    """
    Represents a user's chat session with the AI, containing message history and context.
    """
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", ondelete="CASCADE")
    title: Optional[str] = Field(default=None, max_length=200)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to messages
    messages: List["Message"] = Relationship(back_populates="conversation", cascade_delete=True)

class Message(SQLModel, table=True):
    """
    Individual exchanges between user and AI, stored with timestamps and roles.
    """
    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", ondelete="CASCADE")
    role: MessageRole = Field(default=MessageRole.user)
    content: str = Field(max_length=5000)  # Increased for longer AI responses
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    sequence_number: int = Field(default=0)  # For ordering messages in conversation

    # Relationship to conversation
    conversation: Conversation = Relationship(back_populates="messages")