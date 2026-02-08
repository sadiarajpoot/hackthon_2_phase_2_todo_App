"""
Chat API endpoint for the AI chatbot.
Handles user messages and orchestrates the AI agent with MCP tools.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List
from uuid import UUID
import uuid
from datetime import datetime
import logging
from sqlmodel import Session

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import necessary modules
from ..database import get_session
from ..middleware.auth import get_current_user, TokenData
from ..models.conversation import Conversation as ConversationModel, Message as MessageModel, MessageRole
from ..models.task import Task
from ..services.conversation_service import ConversationService
from ..services.message_service import MessageService
from ..services.task_service import TaskService
from ..services.tool_executor import ToolExecutor

# Create the router
router = APIRouter(tags=["chat"])

# Define request/response models that match the specification
from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None  # Optional - if null, creates new conversation
    message: str  # Required - the user's message/command

class ToolCall(BaseModel):
    name: str
    arguments: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    conversation_id: str
    response: str
    tool_calls: List[ToolCall]

@router.post("/api/{user_id}/chat", response_model=ChatResponse)
async def chat_endpoint(
    user_id: str,
    request: ChatRequest,
    db_session: Session = Depends(get_session),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Handle chat messages from users and return AI responses.

    This endpoint receives user messages, processes them with an AI agent
    that can call MCP tools to perform task operations, and returns
    intelligent responses to the user.
    """
    try:
        # Validate that the user_id in the path matches the authenticated user
        # Extract user ID from the token - try different possible attributes
        token_user_id = getattr(current_user, 'user_id', None)
        if token_user_id is None:
            token_user_id = getattr(current_user, 'id', None)
        if token_user_id is None:
            token_user_id = getattr(current_user, 'sub', None)
        if token_user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: user ID not found in token"
            )

        token_user_id_str = str(token_user_id)

        if token_user_id_str != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Unauthorized: Token user ID ({token_user_id_str}) does not match requested user ID ({user_id})"
            )

        logger.info(f"Processing chat message for user: {user_id}")

        # Convert user_id to UUID for database operations
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )

        # Initialize services
        conversation_service = ConversationService(db_session)
        message_service = MessageService(db_session)
        task_service = TaskService(db_session)
        tool_executor = ToolExecutor(db_session)

        # Get or create conversation
        conversation = None
        if request.conversation_id:
            # Try to get existing conversation
            try:
                conversation_uuid = UUID(request.conversation_id)
                conversation = conversation_service.get_conversation_by_id_and_user(conversation_uuid, user_uuid)
                if not conversation:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Conversation not found or does not belong to user"
                    )
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid conversation ID format"
                )
        else:
            # Create new conversation
            conversation = conversation_service.create_conversation(
                user_id=user_uuid,
                title=f"Chat started {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
            )

        # Get conversation history for context
        conversation_history = message_service.get_messages_by_conversation_id(conversation.id)

        # Create user message record
        from uuid import uuid4
        message_uuid = uuid4()
        user_message = MessageModel(
            conversation_id=conversation.id,
            role=MessageRole.user,
            content=request.message,
            sequence_number=len(conversation_history) + 1
        )
        db_session.add(user_message)
        db_session.commit()
        db_session.refresh(user_message)

        # Initialize the Cohere chat agent
        from ..agents.cohere_agent import CohereChatAgent
        chat_agent = CohereChatAgent(db_session)

        # Process the message with the AI agent, including conversation history for context
        result = await chat_agent.process_message(
            user_id=user_id,  # Pass the user_id string
            message=request.message,
            conversation_history=[{
                "role": msg.role.value if hasattr(msg.role, 'value') else str(msg.role),
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat() if msg.timestamp else None
            } for msg in conversation_history]
        )

        response_text = result["response"]
        tool_calls = result["tool_calls"]

        # Create assistant message record
        assistant_message = MessageModel(
            conversation_id=conversation.id,
            role=MessageRole.assistant,
            content=response_text,
            sequence_number=len(conversation_history) + 2
        )
        db_session.add(assistant_message)
        db_session.commit()
        db_session.refresh(assistant_message)

        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        db_session.add(conversation)
        db_session.commit()

        # Return response
        return ChatResponse(
            conversation_id=str(conversation.id),
            response=response_text,
            tool_calls=tool_calls
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error processing chat request"
        )

# Additional endpoint to get conversation history
@router.get("/api/{user_id}/conversations/{conversation_id}", response_model=Dict[str, Any])
async def get_conversation_history(
    user_id: str,
    conversation_id: str,
    db_session: Session = Depends(get_session),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get the history of messages for a specific conversation.

    Args:
        user_id: The ID of the user
        conversation_id: The ID of the conversation
        db_session: Database session dependency
        current_user: Authenticated user data

    Returns:
        Dictionary with conversation details and message history
    """
    try:
        # Validate user_id matches authenticated user
        token_user_id = getattr(current_user, 'user_id', None)
        if token_user_id is None:
            token_user_id = getattr(current_user, 'id', None)
        if token_user_id is None:
            token_user_id = getattr(current_user, 'sub', None)
        if token_user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: user ID not found in token"
            )

        token_user_id_str = str(token_user_id)

        if token_user_id_str != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Unauthorized: Token user ID does not match requested user ID"
            )

        # Validate UUIDs
        user_uuid = UUID(user_id)
        conv_uuid = UUID(conversation_id)

        conversation_service = ConversationService(db_session)
        message_service = MessageService(db_session)

        # Get conversation
        conversation = conversation_service.get_conversation_by_id_and_user(conv_uuid, user_uuid)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found or doesn't belong to user")

        # Get messages
        messages = message_service.get_messages_by_conversation_id(conversation.id)

        return {
            "conversation_id": str(conversation.id),
            "title": conversation.title,
            "created_at": conversation.created_at.isoformat() if conversation.created_at else None,
            "updated_at": conversation.updated_at.isoformat() if conversation.updated_at else None,
            "messages": [
                {
                    "id": str(msg.id),
                    "role": str(msg.role),
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
                    "sequence_number": msg.sequence_number
                }
                for msg in messages
            ]
        }

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    except Exception as e:
        logger.error(f"Error getting conversation history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Endpoint to list all conversations for a user
@router.get("/api/{user_id}/conversations", response_model=List[Dict[str, Any]])
async def list_user_conversations(
    user_id: str,
    db_session: Session = Depends(get_session),
    current_user: TokenData = Depends(get_current_user)
):
    """
    List all conversations for a specific user.

    Args:
        user_id: The ID of the user
        db_session: Database session dependency
        current_user: Authenticated user data

    Returns:
        List of conversation summaries
    """
    try:
        # Validate user_id matches authenticated user
        token_user_id = getattr(current_user, 'user_id', None)
        if token_user_id is None:
            token_user_id = getattr(current_user, 'id', None)
        if token_user_id is None:
            token_user_id = getattr(current_user, 'sub', None)
        if token_user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: user ID not found in token"
            )

        token_user_id_str = str(token_user_id)

        if token_user_id_str != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Unauthorized: Token user ID does not match requested user ID"
            )

        # Validate UUID
        user_uuid = UUID(user_id)

        conversation_service = ConversationService(db_session)

        # Get conversations
        conversations = conversation_service.get_conversations_by_user_id(user_uuid)

        return [
            {
                "id": str(conv.id),
                "title": conv.title,
                "created_at": conv.created_at.isoformat() if conv.created_at else None,
                "updated_at": conv.updated_at.isoformat() if conv.updated_at else None
            }
            for conv in conversations
        ]

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    except Exception as e:
        logger.error(f"Error listing conversations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")