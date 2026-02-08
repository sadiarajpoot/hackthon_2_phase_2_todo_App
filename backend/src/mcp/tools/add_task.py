"""
add_task tool handler for MCP tools.
Implements the add_task functionality that allows AI agents to create new tasks.
"""
from typing import Dict, Any, List
from pydantic import BaseModel
from uuid import UUID
import logging

# Import the request/response models
from ..models.tool_requests import AddTaskRequest, AddTaskResponse

# Import the tool executor
from ..services.tool_executor import ToolExecutor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AddTaskHandler:
    """
    Handler for the add_task MCP tool.
    Processes requests to create new tasks via the MCP protocol.
    """

    def __init__(self, tool_executor: ToolExecutor):
        self.tool_executor = tool_executor

    async def handle(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Handle an add_task tool call from an AI agent.

        Args:
            arguments: Dictionary containing the tool arguments (user_id, title, description)

        Returns:
            List containing the response from the tool execution
        """
        try:
            # Validate and parse the arguments using the Pydantic model
            request = AddTaskRequest(**arguments)

            # Execute the tool via the ToolExecutor service
            response = await self.tool_executor.execute_add_task(request)

            # Log the successful operation
            logger.info(f"Successfully added task '{response.title}' with ID {response.task_id} for user {request.user_id}")

            # Return the response in the expected format
            return [{
                "task_id": response.task_id,
                "status": response.status,
                "title": response.title
            }]

        except Exception as e:
            logger.error(f"Error in add_task handler: {str(e)}")
            raise


# For direct usage without instantiating the class
async def handle_add_task(tool_executor: ToolExecutor, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Convenience function to handle add_task tool calls.

    Args:
        tool_executor: Instance of ToolExecutor to perform the operation
        arguments: Dictionary containing the tool arguments

    Returns:
        List containing the response from the tool execution
    """
    handler = AddTaskHandler(tool_executor)
    return await handler.handle(arguments)