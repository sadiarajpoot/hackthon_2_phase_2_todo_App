"""
update_task tool handler for MCP tools.
Implements the update_task functionality that allows AI agents to update task details.
"""
from typing import Dict, Any, List
from pydantic import BaseModel
from uuid import UUID
import logging

# Import the request/response models
from ..models.tool_requests import UpdateTaskRequest, UpdateTaskResponse

# Import the tool executor
from ..services.tool_executor import ToolExecutor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UpdateTaskHandler:
    """
    Handler for the update_task MCP tool.
    Processes requests to update task details via the MCP protocol.
    """

    def __init__(self, tool_executor: ToolExecutor):
        self.tool_executor = tool_executor

    async def handle(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Handle an update_task tool call from an AI agent.

        Args:
            arguments: Dictionary containing the tool arguments (user_id, task_id, title, description)

        Returns:
            List containing the response from the tool execution
        """
        try:
            # Validate and parse the arguments using the Pydantic model
            request = UpdateTaskRequest(**arguments)

            # Execute the tool via the ToolExecutor service
            response = await self.tool_executor.execute_update_task(request)

            # Log the successful operation
            logger.info(f"Successfully updated task {response.task_id} for user {request.user_id}")

            # Return the response in the expected format
            return [{
                "task_id": response.task_id,
                "status": response.status,
                "title": response.title
            }]

        except Exception as e:
            logger.error(f"Error in update_task handler: {str(e)}")
            raise


# For direct usage without instantiating the class
async def handle_update_task(tool_executor: ToolExecutor, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Convenience function to handle update_task tool calls.

    Args:
        tool_executor: Instance of ToolExecutor to perform the operation
        arguments: Dictionary containing the tool arguments

    Returns:
        List containing the response from the tool execution
    """
    handler = UpdateTaskHandler(tool_executor)
    return await handler.handle(arguments)