"""
Input validation utilities for the chat API.
Provides centralized validation for all API endpoints and request parameters.
"""
from typing import Dict, Any, Optional
from uuid import UUID
import re
from datetime import datetime


def validate_user_id(user_id: str) -> bool:
    """
    Validate that a user_id is in the correct UUID format.

    Args:
        user_id: The user ID to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        UUID(user_id)
        return True
    except ValueError:
        return False


def validate_conversation_id(conversation_id: str) -> bool:
    """
    Validate that a conversation_id is in the correct UUID format.

    Args:
        conversation_id: The conversation ID to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        UUID(conversation_id)
        return True
    except ValueError:
        return False


def validate_task_id(task_id: str) -> bool:
    """
    Validate that a task_id is in the correct UUID format.

    Args:
        task_id: The task ID to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        UUID(task_id)
        return True
    except ValueError:
        return False


def validate_chat_message(message: str) -> tuple[bool, Optional[str]]:
    """
    Validate a chat message for proper content and length.

    Args:
        message: The message content to validate

    Returns:
        Tuple of (is_valid, error_message_if_any)
    """
    if not message or not message.strip():
        return False, "Message cannot be empty"

    if len(message.strip()) > 10000:  # 10k character limit
        return False, "Message exceeds 10,000 character limit"

    # Check for potentially harmful content
    dangerous_patterns = [
        r"(?i)(drop\s+table)",  # SQL injection
        r"(?i)(delete\s+from)",  # SQL deletion
        r"(?i)(exec\s*\()",  # Execution commands
        r"(?i)(system\s*\()",  # System calls
        r"(?i)(import\s+os)",  # OS imports
        r"(?i)(import\s+subprocess)",  # Subprocess imports
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, message):
            return False, "Message contains potentially harmful content"

    return True, None


def validate_add_task_request(data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate the request data for adding a task.

    Args:
        data: The request data containing task details

    Returns:
        Tuple of (is_valid, error_message_if_any)
    """
    # Check required fields
    if "user_id" not in data or not data["user_id"]:
        return False, "Missing required parameter: user_id"

    if "title" not in data or not data["title"]:
        return False, "Missing required parameter: title"

    # Validate user_id format
    user_id = data["user_id"]
    if not validate_user_id(str(user_id)):
        return False, "Invalid user_id format"

    # Validate title
    title = data["title"]
    if not isinstance(title, str) or not title.strip():
        return False, "Title must be a non-empty string"

    if len(title.strip()) > 200:
        return False, "Title must be 200 characters or less"

    # Validate optional description
    if "description" in data and data["description"] is not None:
        description = data["description"]
        if not isinstance(description, str):
            return False, "Description must be a string if provided"

        if len(description) > 1000:
            return False, "Description must be 1000 characters or less"

    return True, None


def validate_list_tasks_request(data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate the request data for listing tasks.

    Args:
        data: The request data containing filters

    Returns:
        Tuple of (is_valid, error_message_if_any)
    """
    # Required parameters
    if "user_id" not in data or not data["user_id"]:
        return False, "Missing required parameter: user_id"

    # Validate user_id format
    user_id = data["user_id"]
    if not validate_user_id(str(user_id)):
        return False, "Invalid user_id format"

    # Validate optional status filter
    if "status" in data and data["status"]:
        status_val = data["status"]
        if not isinstance(status_val, str):
            return False, "Status must be a string if provided"

        valid_statuses = ["all", "pending", "completed"]
        if status_val.lower() not in valid_statuses:
            return False, f"Status must be one of: {', '.join(valid_statuses)}, got: {status_val}"

    # Validate optional limit
    if "limit" in data and data["limit"]:
        try:
            limit = int(data["limit"])
            if limit <= 0 or limit > 100:
                return False, "Limit must be between 1 and 100"
        except ValueError:
            return False, "Limit must be a valid integer"

    # Validate optional offset
    if "offset" in data and data["offset"]:
        try:
            offset = int(data["offset"])
            if offset < 0:
                return False, "Offset must be a non-negative integer"
        except ValueError:
            return False, "Offset must be a valid integer"

    return True, None


def validate_complete_task_request(data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate the request data for completing a task.

    Args:
        data: The request data containing task details

    Returns:
        Tuple of (is_valid, error_message_if_any)
    """
    # Check required fields
    if "user_id" not in data or not data["user_id"]:
        return False, "Missing required parameter: user_id"

    if "task_id" not in data or not data["task_id"]:
        return False, "Missing required parameter: task_id"

    # Validate user_id format
    user_id = data["user_id"]
    if not validate_user_id(str(user_id)):
        return False, "Invalid user_id format"

    # Validate task_id format
    task_id = data["task_id"]
    if not validate_task_id(str(task_id)):
        return False, "Invalid task_id format"

    return True, None


def validate_delete_task_request(data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate the request data for deleting a task.

    Args:
        data: The request data containing task details

    Returns:
        Tuple of (is_valid, error_message_if_any)
    """
    # Check required fields
    if "user_id" not in data or not data["user_id"]:
        return False, "Missing required parameter: user_id"

    if "task_id" not in data or not data["task_id"]:
        return False, "Missing required parameter: task_id"

    # Validate user_id format
    user_id = data["user_id"]
    if not validate_user_id(str(user_id)):
        return False, "Invalid user_id format"

    # Validate task_id format
    task_id = data["task_id"]
    if not validate_task_id(str(task_id)):
        return False, "Invalid task_id format"

    return True, None


def validate_update_task_request(data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate the request data for updating a task.

    Args:
        data: The request data containing task update details

    Returns:
        Tuple of (is_valid, error_message_if_any)
    """
    # Check required fields
    if "user_id" not in data or not data["user_id"]:
        return False, "Missing required parameter: user_id"

    if "task_id" not in data or not data["task_id"]:
        return False, "Missing required parameter: task_id"

    # At least one of title or description must be provided
    has_title = "title" in data and data["title"] is not None
    has_description = "description" in data and data["description"] is not None

    if not (has_title or has_description):
        return False, "At least one field (title, description) must be provided for update"

    # Validate user_id format
    user_id = data["user_id"]
    if not validate_user_id(str(user_id)):
        return False, "Invalid user_id format"

    # Validate task_id format
    task_id = data["task_id"]
    if not validate_task_id(str(task_id)):
        return False, "Invalid task_id format"

    # Validate title if provided
    if has_title:
        title = data["title"]
        if not isinstance(title, str) or not title.strip():
            return False, "Title must be a non-empty string if provided"
        if len(title.strip()) > 200:
            return False, "Title must be 200 characters or less"

    # Validate description if provided
    if has_description:
        description = data["description"]
        if not isinstance(description, str):
            return False, "Description must be a string if provided"
        if len(description) > 1000:
            return False, "Description must be 1000 characters or less"

    return True, None


def validate_chat_request(data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate the request data for the chat endpoint.

    Args:
        data: The request data containing chat details

    Returns:
        Tuple of (is_valid, error_message_if_any)
    """
    # Check required fields
    if "message" not in data or not data["message"]:
        return False, "Missing required parameter: message"

    # Validate message content
    message_valid, message_error = validate_chat_message(data["message"])
    if not message_valid:
        return False, message_error

    # Validate optional conversation_id if provided
    if "conversation_id" in data and data["conversation_id"]:
        conversation_id = str(data["conversation_id"])
        if not validate_conversation_id(conversation_id):
            return False, "Invalid conversation_id format"

    return True, None


def sanitize_input(input_str: str) -> str:
    """
    Sanitize user input to prevent injection attacks.

    Args:
        input_str: The input string to sanitize

    Returns:
        Sanitized input string
    """
    if not input_str:
        return input_str

    # Remove potential SQL injection patterns
    sanitized = re.sub(r"(?i)(union|select|insert|update|delete|drop|create|alter|exec|system)\s", " ", input_str)

    # Remove potential script tags
    sanitized = re.sub(r"<script[^>]*>.*?</script>", "", sanitized, flags=re.IGNORECASE)

    # Escape HTML characters to prevent XSS
    sanitized = sanitized.replace("<", "&lt;").replace(">", "&gt;")

    return sanitized.strip()


class ValidationService:
    """
    Class for validating API requests with appropriate error messages.
    """

    @staticmethod
    def validate_tool_call(tool_name: str, params: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate a tool call with its parameters.

        Args:
            tool_name: The name of the tool being called
            params: The parameters being passed to the tool

        Returns:
            Tuple of (is_valid, error_message_if_any)
        """
        if not isinstance(tool_name, str) or not tool_name.strip():
            return False, "Tool name must be a non-empty string"

        if not isinstance(params, dict):
            return False, "Parameters must be a dictionary"

        # Validate based on tool name
        if tool_name == "add_task":
            return validate_add_task_request(params)
        elif tool_name == "list_tasks":
            return validate_list_tasks_request(params)
        elif tool_name == "complete_task":
            return validate_complete_task_request(params)
        elif tool_name == "delete_task":
            return validate_delete_task_request(params)
        elif tool_name == "update_task":
            return validate_update_task_request(params)
        else:
            return False, f"Unknown tool: {tool_name}"

    @staticmethod
    def validate_user_owns_resource(user_id: UUID, resource_user_id: UUID) -> bool:
        """
        Validate that a user owns a specific resource.

        Args:
            user_id: The ID of the requesting user
            resource_user_id: The ID of the user who owns the resource

        Returns:
            True if user owns the resource, False otherwise
        """
        return user_id == resource_user_id

    @staticmethod
    def validate_conversation_belongs_to_user(conversation_id: UUID, user_id: UUID, db_session) -> bool:
        """
        Validate that a conversation belongs to a specific user.

        Args:
            conversation_id: The ID of the conversation
            user_id: The ID of the user
            db_session: Database session to query

        Returns:
            True if conversation belongs to user, False otherwise
        """
        from sqlmodel import select
        from ..models.conversation import Conversation

        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        result = db_session.exec(statement)
        conversation = result.first()

        return conversation is not None

    @staticmethod
    def validate_task_belongs_to_user(task_id: UUID, user_id: UUID, db_session) -> bool:
        """
        Validate that a task belongs to a specific user.

        Args:
            task_id: The ID of the task
            user_id: The ID of the user
            db_session: Database session to query

        Returns:
            True if task belongs to user, False otherwise
        """
        from sqlmodel import select
        from ..models.task import Task

        statement = select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )
        result = db_session.exec(statement)
        task = result.first()

        return task is not None