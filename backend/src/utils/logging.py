"""
Logging utilities for the chat API.
Provides centralized logging functionality for all chat operations.
"""
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional
from datetime import datetime
import json
from functools import wraps
from uuid import UUID
from pathlib import Path


def setup_logging():
    """Set up logging configuration for the application"""

    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Create logger
    logger = logging.getLogger("todo_app")
    logger.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Create file handler with rotation
    file_handler = RotatingFileHandler(
        "logs/app.log",
        maxBytes=1024*1024*5,  # 5 MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


# Global logger instance
app_logger = setup_logging()


def get_logger(name: str = None):
    """Get a logger instance"""
    if name:
        return app_logger.getChild(name)
    return app_logger


def log_chat_interaction(user_id: str, conversation_id: Optional[str],
                         message_content: str, response_content: str,
                         tool_calls: Optional[list] = None):
    """
    Log a chat interaction with user, conversation, and content details.

    Args:
        user_id: The ID of the user involved in the interaction
        conversation_id: The ID of the conversation (if applicable)
        message_content: The user's message content
        response_content: The AI's response content
        tool_calls: List of tool calls made during the interaction
    """
    logger = get_logger("chat_api")

    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "interaction_type": "chat",
        "user_id": user_id,
        "conversation_id": conversation_id,
        "message_length": len(message_content),
        "response_length": len(response_content),
        "tool_calls_count": len(tool_calls) if tool_calls else 0,
        "message_preview": message_content[:50] + "..." if len(message_content) > 50 else message_content,
        "response_preview": response_content[:50] + "..." if len(response_content) > 50 else response_content
    }

    logger.info(f"Chat interaction: {json.dumps(log_data, indent=2)}")


def log_tool_execution(tool_name: str, user_id: str, arguments: dict,
                       result: dict, success: bool = True):
    """
    Log an MCP tool execution with details.

    Args:
        tool_name: Name of the tool being executed
        user_id: ID of the user requesting the tool execution
        arguments: Arguments passed to the tool
        result: Result returned by the tool
        success: Whether the execution was successful
    """
    logger = get_logger("chat_api")

    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "interaction_type": "tool_execution",
        "tool_name": tool_name,
        "user_id": user_id,
        "arguments": arguments,
        "result": result,
        "success": success
    }

    status = "SUCCESS" if success else "FAILED"
    logger.info(f"MCP tool {tool_name} execution {status}: {json.dumps(log_data, indent=2)}")


def log_conversation_event(event_type: str, user_id: str, conversation_id: str,
                          details: Optional[dict] = None):
    """
    Log a conversation-related event.

    Args:
        event_type: Type of conversation event (create, update, access, etc.)
        user_id: ID of the user involved
        conversation_id: ID of the conversation
        details: Additional details about the event
    """
    logger = get_logger("chat_api")

    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "user_id": user_id,
        "conversation_id": conversation_id,
        "details": details or {}
    }

    logger.info(f"Conversation {event_type} event: {json.dumps(log_data, indent=2)}")


def log_api_request(endpoint: str, user_id: str, method: str,
                    request_body: dict, response_status: int,
                    processing_time_ms: float):
    """
    Log an API request with timing and details.

    Args:
        endpoint: The API endpoint that was called
        user_id: ID of the user making the request
        method: HTTP method (GET, POST, etc.)
        request_body: The request body content
        response_status: HTTP response status code
        processing_time_ms: Time taken to process the request in milliseconds
    """
    logger = get_logger("chat_api")

    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "interaction_type": "api_request",
        "endpoint": endpoint,
        "user_id": user_id,
        "method": method,
        "response_status": response_status,
        "processing_time_ms": processing_time_ms,
        "request_size": len(json.dumps(request_body)) if request_body else 0
    }

    logger.info(f"API request to {endpoint}: {json.dumps(log_data, indent=2)}")


def chat_api_logger(func):
    """
    Decorator to log chat API function calls with execution time and parameters.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = datetime.utcnow()
        logger = get_logger(f"chat_api.{func.__name__}")

        try:
            result = func(*args, **kwargs)

            # Calculate execution time
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds() * 1000  # Convert to milliseconds

            logger.info(f"Function {func.__name__} executed successfully in {execution_time:.2f}ms")
            return result
        except Exception as e:
            # Calculate execution time even for failed requests
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds() * 1000  # Convert to milliseconds

            logger.error(f"Function {func.__name__} failed after {execution_time:.2f}ms: {str(e)}")
            raise

    return wrapper


class ChatLogger:
    """
    Centralized logger class for chat-specific operations.
    Provides structured logging for all chat interactions and system operations.
    """

    def __init__(self):
        self.logger = get_logger("chat_api")

    def log_user_message(self, user_id: UUID, conversation_id: UUID, message: str):
        """
        Log a user message to the conversation.

        Args:
            user_id: The ID of the user sending the message
            conversation_id: The ID of the conversation
            message: The content of the message
        """
        self.logger.info(
            f"User {user_id} sent message to conversation {conversation_id}: {message[:100]}{'...' if len(message) > 100 else ''}"
        )

    def log_assistant_response(self, user_id: UUID, conversation_id: UUID, response: str, tool_calls: list):
        """
        Log an assistant response to the conversation.

        Args:
            user_id: The ID of the user receiving the response
            conversation_id: The ID of the conversation
            response: The content of the response
            tool_calls: List of tools called to generate the response
        """
        self.logger.info(
            f"Assistant responded to user {user_id} in conversation {conversation_id} with {len(tool_calls)} tool calls: {response[:100]}{'...' if len(response) > 100 else ''}"
        )

    def log_task_operation(self, operation: str, user_id: UUID, task_details: dict, success: bool = True):
        """
        Log a task operation (create, update, complete, delete).

        Args:
            operation: The type of operation (create, update, complete, delete)
            user_id: The ID of the user performing the operation
            task_details: Details about the task being operated on
            success: Whether the operation was successful
        """
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"Task {operation} operation for user {user_id} {status}: {task_details}")

    def log_error(self, error_type: str, user_id: Optional[UUID], error_details: str, context: Optional[str] = None):
        """
        Log an error with context and user information.

        Args:
            error_type: Type of error (validation, database, tool_execution, etc.)
            user_id: The ID of the user involved (if applicable)
            error_details: Details about the error
            context: Additional context about where the error occurred
        """
        user_info = f" for user {user_id}" if user_id else ""
        context_info = f" in {context}" if context else ""

        self.logger.error(f"{error_type} error{user_info}{context_info}: {error_details}")

    def log_security_event(self, event_type: str, user_id: UUID, details: str):
        """
        Log a security-related event.

        Args:
            event_type: Type of security event (auth_success, auth_failure, unauthorized_access, etc.)
            user_id: The ID of the user involved
            details: Details about the security event
        """
        self.logger.warning(f"Security {event_type} for user {user_id}: {details}")