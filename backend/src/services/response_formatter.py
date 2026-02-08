from typing import Optional
from ..agents.mcp_tools import TaskOperationResult


class ResponseFormatter:
    """
    Service class for formatting responses from task operations
    """

    @staticmethod
    def format_task_operation_response(result: TaskOperationResult) -> str:
        """
        Format the response for a task operation result

        Args:
            result: The result of a task operation

        Returns:
            Formatted response string
        """
        if result.success:
            if result.operation == "create":
                return result.message
            elif result.operation == "list":
                return result.message
            elif result.operation == "update":
                return result.message
            elif result.operation == "complete":
                return result.message
            elif result.operation == "delete":
                return result.message
            else:
                return result.message
        else:
            return result.message

    @staticmethod
    def format_friendly_confirmation(operation: str, task_title: Optional[str] = None, task_id: Optional[str] = None) -> str:
        """
        Create a friendly confirmation message for successful operations

        Args:
            operation: The type of operation performed
            task_title: The title of the task (if applicable)
            task_id: The ID of the task (if applicable)

        Returns:
            Friendly confirmation message
        """
        if operation == "create":
            if task_title:
                return f"Great! I've created the task '{task_title}' for you."
            else:
                return "Task created successfully!"
        elif operation == "update":
            if task_title:
                return f"Got it! I've updated your task to '{task_title}'."
            else:
                return "Task updated successfully!"
        elif operation == "complete":
            if task_title:
                return f"Excellent! I've marked '{task_title}' as completed."
            else:
                return "Task marked as completed!"
        elif operation == "delete":
            if task_title:
                return f"Done! I've deleted the task '{task_title}'."
            else:
                return "Task deleted successfully!"
        elif operation == "list":
            return "Here are your tasks as requested."
        else:
            return "Operation completed successfully!"

    @staticmethod
    def format_error_message(error_type: str, details: Optional[str] = None) -> str:
        """
        Format an error message for the user

        Args:
            error_type: The type of error
            details: Additional details about the error

        Returns:
            Formatted error message
        """
        if error_type == "invalid_command":
            return "I'm sorry, I didn't understand that command. You can ask me to add, list, update, complete, or delete tasks."
        elif error_type == "task_not_found":
            return "I couldn't find that task. Please check the task ID and try again."
        elif error_type == "permission_denied":
            return "You don't have permission to perform that action on this task."
        elif error_type == "validation_error":
            return f"I couldn't process your request: {details or 'Invalid input provided.'}"
        else:
            return f"An error occurred: {details or 'Something went wrong.'}"

    @staticmethod
    def format_welcome_message() -> str:
        """
        Format a welcome message for new users

        Returns:
            Welcome message string
        """
        return "Hello! I'm your AI task assistant. You can ask me to add, list, update, complete, or delete tasks. For example, say 'Add a task to buy groceries'."

    @staticmethod
    def format_help_message() -> str:
        """
        Format a help message with available commands

        Returns:
            Help message string
        """
        return """
Here's how you can interact with me:

• To create a task: "Add a task to buy groceries" or "Create a task to call mom"
• To list tasks: "Show all tasks" or "List my tasks"
• To update a task: "Update task 1 to 'Call mom tomorrow'"
• To complete a task: "Mark task 1 as complete" or "Complete task 1"
• To delete a task: "Delete task 1" or "Remove task 1"

Try any of these commands to get started!
        """.strip()