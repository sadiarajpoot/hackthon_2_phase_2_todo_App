"""
Message service for managing chat messages.
Handles creation, retrieval, and updates of message data.
"""
from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from ..models.conversation import Message as MessageModel

class MessageService:
    """
    Service class for managing message data with database operations.
    """

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create_message(self, message: MessageModel) -> MessageModel:
        """
        Create a new message in the database.

        Args:
            message: The message object to create

        Returns:
            Created message object
        """
        # Calculate sequence number based on existing messages in conversation
        statement = select(MessageModel).where(
            MessageModel.conversation_id == message.conversation_id
        ).order_by(MessageModel.sequence_number.desc())

        last_message = self.db_session.exec(statement).first()
        message.sequence_number = (last_message.sequence_number + 1) if last_message else 1

        self.db_session.add(message)
        self.db_session.commit()
        self.db_session.refresh(message)

        logger.info(f"Created new message: {message.id} in conversation: {message.conversation_id}")
        return message

    def get_message_by_id(self, message_id: UUID) -> Optional[MessageModel]:
        """
        Get a message by its ID.

        Args:
            message_id: The ID of the message

        Returns:
            Message object if found, None otherwise
        """
        statement = select(MessageModel).where(MessageModel.id == message_id)
        message = self.db_session.exec(statement).first()
        return message

    def get_messages_by_conversation_id(self, conversation_id: UUID) -> List[MessageModel]:
        """
        Get all messages for a specific conversation ordered by sequence number.

        Args:
            conversation_id: The ID of the conversation

        Returns:
            List of message objects ordered by sequence
        """
        statement = select(MessageModel).where(
            MessageModel.conversation_id == conversation_id
        ).order_by(MessageModel.sequence_number.asc())

        messages = self.db_session.exec(statement).all()
        return messages

    def update_message(self, message_id: UUID, update_data: dict) -> Optional[MessageModel]:
        """
        Update a message with new data.

        Args:
            message_id: The ID of the message to update
            update_data: Dictionary with fields to update

        Returns:
            Updated message object if successful, None otherwise
        """
        message = self.get_message_by_id(message_id)
        if not message:
            return None

        # Update allowed fields
        allowed_fields = {"content", "updated_at"}
        for field, value in update_data.items():
            if field in allowed_fields:
                setattr(message, field, value)

        self.db_session.add(message)
        self.db_session.commit()
        self.db_session.refresh(message)

        logger.info(f"Updated message: {message_id}")
        return message

    def delete_message(self, message_id: UUID) -> bool:
        """
        Delete a message by its ID.

        Args:
            message_id: The ID of the message to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        message = self.get_message_by_id(message_id)
        if not message:
            return False

        self.db_session.delete(message)
        self.db_session.commit()

        logger.info(f"Deleted message: {message_id}")
        return True