"""
Conversation service for managing chat sessions.
Handles creation, retrieval, and updates of conversation data.
"""
from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from ..models.conversation import Conversation as ConversationModel, Message as MessageModel

class ConversationService:
    """
    Service class for managing conversation data with database operations.
    """

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create_conversation(self, user_id: UUID, title: Optional[str] = None) -> ConversationModel:
        """
        Create a new conversation for a user.

        Args:
            user_id: The ID of the user creating the conversation
            title: Optional title for the conversation

        Returns:
            Created conversation object
        """
        conversation = ConversationModel(
            user_id=user_id,
            title=title
        )

        self.db_session.add(conversation)
        self.db_session.commit()
        self.db_session.refresh(conversation)

        logger.info(f"Created new conversation: {conversation.id} for user: {user_id}")
        return conversation

    def get_conversation_by_id(self, conversation_id: UUID) -> Optional[ConversationModel]:
        """
        Get a conversation by its ID.

        Args:
            conversation_id: The ID of the conversation

        Returns:
            Conversation object if found, None otherwise
        """
        statement = select(ConversationModel).where(ConversationModel.id == conversation_id)
        conversation = self.db_session.exec(statement).first()
        return conversation

    def get_conversation_by_id_and_user(self, conversation_id: UUID, user_id: UUID) -> Optional[ConversationModel]:
        """
        Get a conversation by its ID and verify it belongs to the user.

        Args:
            conversation_id: The ID of the conversation
            user_id: The ID of the user

        Returns:
            Conversation object if found and belongs to user, None otherwise
        """
        statement = select(ConversationModel).where(
            ConversationModel.id == conversation_id,
            ConversationModel.user_id == user_id
        )
        conversation = self.db_session.exec(statement).first()
        return conversation

    def get_conversations_by_user_id(self, user_id: UUID, limit: int = 20, offset: int = 0) -> List[ConversationModel]:
        """
        Get all conversations for a specific user with pagination.

        Args:
            user_id: The ID of the user
            limit: Number of conversations to return
            offset: Number of conversations to skip

        Returns:
            List of conversation objects
        """
        statement = select(ConversationModel).where(
            ConversationModel.user_id == user_id
        ).offset(offset).limit(limit)
        conversations = self.db_session.exec(statement).all()
        return conversations

    def update_conversation(self, conversation_id: UUID, update_data: dict) -> Optional[ConversationModel]:
        """
        Update a conversation with new data.

        Args:
            conversation_id: The ID of the conversation to update
            update_data: Dictionary with fields to update

        Returns:
            Updated conversation object if successful, None otherwise
        """
        conversation = self.get_conversation_by_id(conversation_id)
        if not conversation:
            return None

        # Update allowed fields
        allowed_fields = {"title", "updated_at"}
        for field, value in update_data.items():
            if field in allowed_fields:
                setattr(conversation, field, value)

        conversation.updated_at = datetime.utcnow()

        self.db_session.add(conversation)
        self.db_session.commit()
        self.db_session.refresh(conversation)

        logger.info(f"Updated conversation: {conversation_id}")
        return conversation

    def delete_conversation(self, conversation_id: UUID) -> bool:
        """
        Delete a conversation by its ID.

        Args:
            conversation_id: The ID of the conversation to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        conversation = self.get_conversation_by_id(conversation_id)
        if not conversation:
            return False

        self.db_session.delete(conversation)
        self.db_session.commit()

        logger.info(f"Deleted conversation: {conversation_id}")
        return True