"""
Error Handler Service for MCP tools and chat API.
Provides centralized error handling and user-friendly error messages for the AI chatbot.
"""
from typing import Dict, Any, Optional
from enum import Enum
import logging
from fastapi import HTTPException, status
from ..models.message import MessageRole


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """
    Enumeration of different types of errors that can occur in the system.
    """
    AUTHENTICATION_ERROR = "authentication_error"
    AUTHORIZATION_ERROR = "authorization_error"
    VALIDATION_ERROR = "validation_error"
    TOOL_EXECUTION_ERROR = "tool_execution_error"
    DATABASE_ERROR = "database_error"
    EXTERNAL_SERVICE_ERROR = "external_service_error"
    CONVERSATION_ERROR = "conversation_error"
    UNKNOWN_ERROR = "unknown_error"


class ErrorHandler:
    """
    Service class for handling errors in a consistent way across the application.
    Provides appropriate error responses to users while logging technical details for debugging.
    """

    @staticmethod
    def handle_authentication_error(error_msg: str = "Authentication failed") -> HTTPException:
        """
        Handle authentication-related errors.

        Args:
            error_msg: The error message to include in the response

        Returns:
            HTTPException with appropriate status code and message
        """
        logger.warning(f"Authentication error: {error_msg}")
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_msg
        )

    @staticmethod
    def handle_authorization_error(error_msg: str = "Not authorized to perform this action") -> HTTPException:
        """
        Handle authorization-related errors.

        Args:
            error_msg: The error message to include in the response

        Returns:
            HTTPException with appropriate status code and message
        """
        logger.warning(f"Authorization error: {error_msg}")
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_msg
        )

    @staticmethod
    def handle_validation_error(error_msg: str) -> HTTPException:
        """
        Handle validation-related errors.

        Args:
            error_msg: The error message to include in the response

        Returns:
            HTTPException with appropriate status code and message
        """
        logger.info(f"Validation error: {error_msg}")
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

    @staticmethod
    def handle_database_error(error_msg: str) -> HTTPException:
        """
        Handle database-related errors.

        Args:
            error_msg: The error message to include in the response

        Returns:
            HTTPException with appropriate status code and message
        """
        logger.error(f"Database error: {error_msg}")
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="A database error occurred. Please try again later."
        )

    @staticmethod
    def handle_external_service_error(service_name: str, error_msg: str) -> str:
        """
        Handle errors from external services (like MCP tools, Cohere API, etc.).

        Args:
            service_name: The name of the external service that failed
            error_msg: The error message from the external service

        Returns:
            User-friendly error message
        """
        logger.error(f"External service {service_name} error: {error_msg}")
        return f"The {service_name} service is temporarily unavailable. Please try again in a moment."

    @staticmethod
    def handle_tool_execution_error(tool_name: str, error_msg: str) -> str:
        """
        Handle errors during MCP tool execution.

        Args:
            tool_name: The name of the tool that failed
            error_msg: The error message from the tool execution

        Returns:
            User-friendly error message
        """
        logger.error(f"MCP tool {tool_name} execution error: {error_msg}")
        return f"Sorry, I encountered an issue with the {tool_name} operation. Please try rephrasing your request."

    @staticmethod
    def handle_conversation_error(error_msg: str) -> str:
        """
        Handle errors related to conversation management.

        Args:
            error_msg: The error message from the conversation operation

        Returns:
            User-friendly error message
        """
        logger.error(f"Conversation error: {error_msg}")
        return f"Sorry, I had trouble processing your conversation. {error_msg}"

    @staticmethod
    def log_error(error_type: ErrorType, error_details: str, user_id: Optional[str] = None, conversation_id: Optional[str] = None):
        """
        Log error details with appropriate context.

        Args:
            error_type: The type of error that occurred
            error_details: Detailed information about the error
            user_id: Optional user ID for context
            conversation_id: Optional conversation ID for context
        """
        context = ""
        if user_id:
            context += f" User: {user_id}"
        if conversation_id:
            context += f" Conversation: {conversation_id}"

        logger.error(f"[{error_type.value}] Error{context}: {error_details}")

    @staticmethod
    def create_assistant_error_message(error_type: ErrorType, original_error: str = "") -> Dict[str, Any]:
        """
        Create an error message in the same format as a normal assistant response.

        Args:
            error_type: The type of error that occurred
            original_error: The original technical error (not exposed to user)

        Returns:
            Dictionary with error message in assistant response format
        """
        error_messages = {
            ErrorType.AUTHENTICATION_ERROR: "I'm sorry, but I couldn't verify your identity. Please make sure you're logged in correctly.",
            ErrorType.AUTHORIZATION_ERROR: "You don't have permission to perform this action.",
            ErrorType.VALIDATION_ERROR: "I couldn't understand your request. Please check your input and try again.",
            ErrorType.TOOL_EXECUTION_ERROR: "Sorry, I encountered an issue processing your request. Please try rephrasing your command.",
            ErrorType.DATABASE_ERROR: "Sorry, I'm experiencing technical difficulties with the database. Please try again later.",
            ErrorType.EXTERNAL_SERVICE_ERROR: "Sorry, I'm unable to connect to required services right now. Please try again later.",
            ErrorType.CONVERSATION_ERROR: "Sorry, I had trouble with your conversation. Please start a new chat or try again.",
            ErrorType.UNKNOWN_ERROR: "Sorry, an unexpected error occurred. Please try again."
        }

        message = error_messages.get(error_type, "Sorry, an unexpected error occurred. Please try again.")

        # Log the technical error for debugging
        logger.error(f"Error of type {error_type.value}: {original_error}")

        return {
            "role": MessageRole.assistant,
            "content": message,
            "error": True,
            "error_type": error_type.value
        }

    @staticmethod
    def handle_mcp_tool_failure(tool_name: str, error: Exception) -> Dict[str, Any]:
        """
        Specifically handle MCP tool failures with appropriate responses.

        Args:
            tool_name: The name of the MCP tool that failed
            error: The exception that occurred during tool execution

        Returns:
            Dictionary with error response in tool call format
        """
        logger.error(f"MCP tool '{tool_name}' failed with error: {str(error)}")

        # Different responses based on tool type
        if tool_name == "add_task":
            user_message = "Sorry, I couldn't create that task. Please check your request and try again."
        elif tool_name == "list_tasks":
            user_message = "Sorry, I couldn't retrieve your tasks right now. Please try again in a moment."
        elif tool_name == "complete_task":
            user_message = "Sorry, I couldn't mark that task as complete. Please try again."
        elif tool_name == "delete_task":
            user_message = "Sorry, I couldn't delete that task. Please try again."
        elif tool_name == "update_task":
            user_message = "Sorry, I couldn't update that task. Please try rephrasing your update request."
        else:
            user_message = f"Sorry, I encountered an issue with the {tool_name} operation. Please try again."

        return {
            "success": False,
            "error_message": user_message,
            "tool_name": tool_name,
            "original_error": str(error)
        }

    @staticmethod
    def format_user_facing_error(error: Exception, context: str = "") -> str:
        """
        Format any exception into a user-friendly error message.

        Args:
            error: The exception to format
            context: Optional context about where the error occurred

        Returns:
            User-friendly error message
        """
        error_str = str(error).lower()

        # Identify common error types and provide appropriate responses
        if "auth" in error_str or "token" in error_str or "credential" in error_str:
            return "I'm having trouble verifying your identity. Please check your login and try again."
        elif "validation" in error_str or "invalid" in error_str:
            return "I couldn't understand your request. Please check your input and try again."
        elif "connection" in error_str or "timeout" in error_str or "network" in error_str:
            return "I'm having trouble connecting to services. Please check your internet connection and try again."
        elif "database" in error_str or "db" in error_str:
            return "I'm experiencing technical difficulties with the database. Please try again later."
        elif "permission" in error_str or "forbidden" in error_str:
            return "You don't have permission to perform this action."
        elif "not found" in error_str or "does not exist" in error_str:
            return "The item you're looking for doesn't exist or can't be found."
        else:
            logger.error(f"Unrecognized error in {context}: {str(error)}")
            return "Sorry, an unexpected error occurred. Please try again or contact support if the issue persists."