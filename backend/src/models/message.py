from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING
import uuid
from datetime import datetime
from enum import Enum


if TYPE_CHECKING:
    from .conversation import Conversation


class MessageRole(str, Enum):
    user = "user"
    assistant = "assistant"
    system = "system"


class Message(SQLModel, table=True):
    """
    Individual exchanges between user and AI, stored with timestamps and roles
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: uuid.UUID = Field(foreign_key="conversations.id")
    role: MessageRole = Field(default=MessageRole.user)
    content: str = Field(min_length=1)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    sequence_number: int = Field(default=0)

    # Relationship to conversation
    conversation: Conversation = Relationship(back_populates="messages")