"""
Validation Service for the chat API.
Provides centralized validation for all inputs to the API endpoints and MCP tools.
"""
from typing import Dict, Any, Optional, Tuple
from uuid import UUID
import re
from datetime import datetime


class ValidationService:
    """
    Service class for validating inputs to the chat API and MCP tools.
    Ensures all requests meet the required format and constraints before processing.
    """

    @staticmethod
    def validate_user_id(user_id: str) -> tuple[bool, Optional[str]]:
        """
        Validate that a user_id is in the correct UUID format.

        Args:
            user_id: The user ID to validate

        Returns:
            Tuple of (is_valid, error_message_if_any)
        """
        try:
            UUID(user_id)
            return True, None
        except ValueError:
            return False, f"Invalid user_id format: {user_id}. Must be a valid UUID."

    @staticmethod
    def validate_conversation_id(conversation_id: str) -> tuple[bool, Optional[str]]:
        """
        Validate that a conversation_id is in the correct UUID format.

        Args:
            conversation_id: The conversation ID to validate

        Returns:
            Tuple of (is_valid, error_message_if_any)
        """
        try:
            UUID(conversation_id)
            return True, None
        except ValueError:
            return False, f"Invalid conversation_id format: {conversation_id}. Must be a valid UUID."

    @staticmethod
    def validate_task_id(task_id: str) -> tuple[bool, Optional[str]]:
        """
        Validate that a task_id is in the correct UUID format.

        Args:
            task_id: The task ID to validate

        Returns:
            Tuple of (is_valid, error_message_if_any)
        """
        try:
            UUID(task_id)
            return True, None
        except ValueError:
            return False, f"Invalid task_id format: {task_id}. Must be a valid UUID."

    @staticmethod
    def validate_add_task_params(params: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate parameters for the add_task operation.

        Args:
            params: Dictionary containing user_id, title, and optional description

        Returns:
            Tuple of (is_valid, error_message_if_any)
        """
        # Required parameters
        if "user_id" not in params:
            return False, "Missing required parameter: user_id"

        if "title" not in params:
            return False, "Missing required parameter: title"

        # Validate user_id format
        user_id = params["user_id"]
        if not isinstance(user_id, str) or not user_id.strip():
            return False, "user_id must be a non-empty string"

        is_valid_user_id, user_error = ValidationService.validate_user_id(user_id)
        if not is_valid_user_id:
            return False, user_error

        # Validate title
        title = params["title"]
        if not isinstance(title, str) or not title.strip():
            return False, "Title must be a non-empty string"

        if len(title.strip()) > 200:
            return False, "Title must be 200 characters or less"

        # Validate optional description
        if "description" in params and params["description"] is not None:
            description = params["description"]
            if not isinstance(description, str):
                return False, "Description must be a string if provided"

            if len(description) > 1000:
                return False, "Description must be 1000 characters or less"

        return True, None

    @staticmethod
    def validate_list_tasks_params(params: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate parameters for the list_tasks operation.

        Args:
            params: Dictionary containing user_id and optional status filter

        Returns:
            Tuple of (is_valid, error_message_if_any)
        """
        # Required parameters
        if "user_id" not in params:
            return False, "Missing required parameter: user_id"

        # Validate user_id format
        user_id = params["user_id"]
        if not isinstance(user_id, str) or not user_id.strip():
            return False, "user_id must be a non-empty string"

        is_valid_user_id, user_error = ValidationService.validate_user_id(user_id)
        if not is_valid_user_id:
            return False, user_error

        # Validate optional status parameter
        if "status" in params and params["status"] is not None:
            status_val = params["status"]
            if not isinstance(status_val, str):
                return False, "Status must be a string if provided"

            valid_statuses = ["all", "pending", "completed"]
            if status_val.lower() not in valid_statuses:
                return False, f"Status must be one of: {', '.join(valid_statuses)}, got: {status_val}"

        return True, None

    @staticmethod
    def validate_complete_task_params(params: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate parameters for the complete_task operation.

        Args:
            params: Dictionary containing user_id and task_id

        Returns:
            Tuple of (is_valid, error_message_if_any)
        """
        # Required parameters
        if "user_id" not in params:
            return False, "Missing required parameter: user_id"

        if "task_id" not in params:
            return False, "Missing required parameter: task_id"

        # Validate user_id format
        user_id = params["user_id"]
        if not isinstance(user_id, str) or not user_id.strip():
            return False, "user_id must be a non-empty string"

        is_valid_user_id, user_error = ValidationService.validate_user_id(user_id)
        if not is_valid_user_id:
            return False, user_error

        # Validate task_id format
        task_id = params["task_id"]
        if not isinstance(task_id, str) or not task_id.strip():
            return False, "task_id must be a non-empty string"

        is_valid_task_id, task_error = ValidationService.validate_task_id(task_id)
        if not is_valid_task_id:
            return False, task_error

        return True, None

    @staticmethod
    def validate_delete_task_params(params: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate parameters for the delete_task operation.

        Args:
            params: Dictionary containing user_id and task_id

        Returns:
            Tuple of (is_valid, error_message_if_any)
        """
        # Required parameters
        if "user_id" not in params:
            return False, "Missing required parameter: user_id"

        if "task_id" not in params:
            return False, "Missing required parameter: task_id"

        # Validate user_id format
        user_id = params["user_id"]
        if not isinstance(user_id, str) or not user_id.strip():
            return False, "user_id must be a non-empty string"

        is_valid_user_id, user_error = ValidationService.validate_user_id(user_id)
        if not is_valid_user_id:
            return False, user_error

        # Validate task_id format
        task_id = params["task_id"]
        if not isinstance(task_id, str) or not task_id.strip():
            return False, "task_id must be a non-empty string"

        is_valid_task_id, task_error = ValidationService.validate_task_id(task_id)
        if not is_valid_task_id:
            return False, task_error

        return True, None

    @staticmethod
    def validate_update_task_params(params: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate parameters for the update_task operation.

        Args:
            params: Dictionary containing user_id, task_id, and optional title/description

        Returns:
            Tuple of (is_valid, error_message_if_any)
        """
        # Required parameters
        if "user_id" not in params:
            return False, "Missing required parameter: user_id"

        if "task_id" not in params:
            return False, "Missing required parameter: task_id"

        # At least one of title or description must be provided for updates
        has_title = "title" in params and params["title"] is not None
        has_description = "description" in params and params["description"] is not None

        if not (has_title or has_description):
            return False, "At least one of 'title' or 'description' must be provided for update"

        # Validate user_id format
        user_id = params["user_id"]
        if not isinstance(user_id, str) or not user_id.strip():
            return False, "user_id must be a non-empty string"

        is_valid_user_id, user_error = ValidationService.validate_user_id(user_id)
        if not is_valid_user_id:
            return False, user_error

        # Validate task_id format
        task_id = params["task_id"]
        if not isinstance(task_id, str) or not task_id.strip():
            return False, "task_id must be a non-empty string"

        is_valid_task_id, task_error = ValidationService.validate_task_id(task_id)
        if not is_valid_task_id:
            return False, task_error

        # Validate title if provided
        if has_title:
            title = params["title"]
            if not isinstance(title, str) or not title.strip():
                return False, "Title must be a non-empty string if provided"

            if len(title.strip()) > 200:
                return False, "Title must be 200 characters or less"

        # Validate description if provided
        if has_description:
            description = params["description"]
            if not isinstance(description, str):
                return False, "Description must be a string if provided"

            if len(description) > 1000:
                return False, "Description must be 1000 characters or less"

        return True, None

    @staticmethod
    def validate_chat_message_content(message: str) -> tuple[bool, Optional[str]]:
        """
        Validate the content of a chat message.

        Args:
            message: The message content to validate

        Returns:
            Tuple of (is_valid, error_message_if_any)
        """
        if not message or not message.strip():
            return False, "Message content cannot be empty"

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
            return ValidationService.validate_add_task_params(params)
        elif tool_name == "list_tasks":
            return ValidationService.validate_list_tasks_params(params)
        elif tool_name == "complete_task":
            return ValidationService.validate_complete_task_params(params)
        elif tool_name == "delete_task":
            return ValidationService.validate_delete_task_params(params)
        elif tool_name == "update_task":
            return ValidationService.validate_update_task_params(params)
        else:
            return False, f"Unknown tool: {tool_name}"

    @staticmethod
    def validate_user_owns_resource(user_id: UUID, resource_user_id: UUID) -> bool:
        """
        Validate that a user owns a specific resource.

        Args:
            user_id: The ID of the user making the request
            resource_user_id: The ID of the user who owns the resource

        Returns:
            True if user owns the resource, False otherwise
        """
        return user_id == resource_user_id

    @staticmethod
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