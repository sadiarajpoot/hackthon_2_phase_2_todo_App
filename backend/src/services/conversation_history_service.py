from typing import List, Optional
from ..models.conversation import Conversation
from ..models.message import Message
from ..services.conversation_service import ConversationService
from ..services.message_service import MessageService
from sqlmodel import Session
from uuid import UUID


class ConversationHistoryService:
    """
    Service class for managing conversation history
    """

    def __init__(self, db_session: Session, user_id: UUID):
        self.db_session = db_session
        self.user_id = user_id
        self.conversation_service = ConversationService(db_session)
        self.message_service = MessageService(db_session)

    def get_conversation_history(self, conversation_id: UUID) -> Optional[List[Message]]:
        """
        Get the history of messages for a specific conversation

        Args:
            conversation_id: ID of the conversation to get history for

        Returns:
            List of messages in the conversation, or None if conversation doesn't exist
        """
        # Verify that the conversation belongs to the user
        conversation = self.conversation_service.get_conversation_by_id_and_user(
            conversation_id, self.user_id
        )
        if not conversation:
            return None

        # Get all messages in the conversation
        messages = self.message_service.get_messages_by_conversation_id(conversation_id)
        return messages

    def get_recent_conversations(self, limit: int = 5) -> List[Conversation]:
        """
        Get the most recent conversations for the user

        Args:
            limit: Maximum number of conversations to return

        Returns:
            List of recent conversations
        """
        conversations = self.conversation_service.get_conversations_by_user_id(
            user_id=self.user_id,
            limit=limit,
            offset=0
        )
        return conversations

    def get_full_conversation_context(self, conversation_id: UUID, max_messages: int = 20) -> List[dict]:
        """
        Get the full context of a conversation (messages) formatted for AI processing

        Args:
            conversation_id: ID of the conversation to get context for
            max_messages: Maximum number of messages to return

        Returns:
            List of message dictionaries formatted for AI context
        """
        messages = self.get_conversation_history(conversation_id)
        if not messages:
            return []

        # Limit the number of messages to return
        limited_messages = messages[-max_messages:] if len(messages) > max_messages else messages

        # Format messages for AI context
        formatted_messages = []
        for message in limited_messages:
            formatted_messages.append({
                "role": message.role,
                "content": message.content,
                "timestamp": message.timestamp.isoformat(),
                "sequence_number": message.sequence_number
            })

        return formatted_messages

    def save_conversation_context(self, conversation_id: UUID, user_input: str, ai_response: str) -> bool:
        """
        Save a new interaction (user input and AI response) to the conversation

        Args:
            conversation_id: ID of the conversation to add to
            user_input: The user's message
            ai_response: The AI's response

        Returns:
            True if successfully saved, False otherwise
        """
        # Get the current message count to determine sequence number
        current_messages = self.get_conversation_history(conversation_id)
        sequence_number = len(current_messages) if current_messages else 0

        # Add user message
        user_message = self.message_service.create_message(
            conversation_id=conversation_id,
            role="user",
            content=user_input,
            sequence_number=sequence_number
        )

        # Add AI response message
        ai_message = self.message_service.create_message(
            conversation_id=conversation_id,
            role="assistant",
            content=ai_response,
            sequence_number=sequence_number + 1
        )

        # Update conversation timestamp
        self.conversation_service.update_conversation_timestamp(conversation_id)

        return user_message is not None and ai_message is not None

    def create_new_conversation(self, title: Optional[str] = None) -> Optional[Conversation]:
        """
        Create a new conversation for the user

        Args:
            title: Optional title for the conversation

        Returns:
            Created Conversation object, or None if creation failed
        """
        conversation = self.conversation_service.create_conversation(
            user_id=self.user_id,
            title=title
        )
        return conversation

    def get_or_create_conversation(self, conversation_id: Optional[UUID] = None, title: Optional[str] = None) -> Conversation:
        """
        Get an existing conversation or create a new one if it doesn't exist

        Args:
            conversation_id: ID of the conversation to get (None to create new)
            title: Title for the new conversation (if creating)

        Returns:
            Conversation object
        """
        if conversation_id:
            # Try to get existing conversation
            conversation = self.conversation_service.get_conversation_by_id_and_user(
                conversation_id, self.user_id
            )
            if conversation:
                return conversation

        # Create new conversation
        return self.create_new_conversation(title=title)

    def delete_conversation_history(self, conversation_id: UUID) -> bool:
        """
        Delete all messages in a conversation (but keep the conversation record)

        Args:
            conversation_id: ID of the conversation to clear

        Returns:
            True if successfully cleared, False otherwise
        """
        # In our model, deleting a conversation would remove both the conversation and its messages
        # If we wanted to keep the conversation record but clear messages, we'd need a different approach
        # For now, we'll return False to indicate this operation isn't directly supported
        # The entire conversation can be deleted using the conversation service
        return False

    def export_conversation_history(self, conversation_id: UUID) -> Optional[dict]:
        """
        Export conversation history in a structured format

        Args:
            conversation_id: ID of the conversation to export

        Returns:
            Dictionary containing conversation details and messages, or None if not found
        """
        conversation = self.conversation_service.get_conversation_by_id_and_user(
            conversation_id, self.user_id
        )
        if not conversation:
            return None

        messages = self.get_conversation_history(conversation_id)

        return {
            "conversation": {
                "id": str(conversation.id),
                "title": conversation.title,
                "created_at": conversation.created_at.isoformat(),
                "updated_at": conversation.updated_at.isoformat()
            },
            "messages": [
                {
                    "id": str(msg.id),
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "sequence_number": msg.sequence_number
                } for msg in messages
            ]
        }