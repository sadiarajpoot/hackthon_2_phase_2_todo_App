"""
list_tasks tool handler for MCP tools.
Implements the list_tasks functionality that allows AI agents to retrieve user tasks.
"""
from typing import Dict, Any, List
from pydantic import BaseModel
from uuid import UUID
import logging

# Import the request/response models
from ..models.tool_requests import ListTasksRequest, ListTasksResponse

# Import the tool executor
from ..services.tool_executor import ToolExecutor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ListTasksHandler:
    """
    Handler for the list_tasks MCP tool.
    Processes requests to list user's tasks via the MCP protocol.
    """

    def __init__(self, tool_executor: ToolExecutor):
        self.tool_executor = tool_executor

    async def handle(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Handle a list_tasks tool call from an AI agent.

        Args:
            arguments: Dictionary containing the tool arguments (user_id, status filter)

        Returns:
            List containing the response from the tool execution
        """
        try:
            # Validate and parse the arguments using the Pydantic model
            request = ListTasksRequest(**arguments)

            # Execute the tool via the ToolExecutor service
            response = await self.tool_executor.execute_list_tasks(request)

            # Log the successful operation
            logger.info(f"Successfully retrieved {len(response.tasks)} tasks for user {request.user_id}")

            # Return the response in the expected format
            return [{
                "tasks": response.tasks
            }]

        except Exception as e:
            logger.error(f"Error in list_tasks handler: {str(e)}")
            raise


# For direct usage without instantiating the class
async def handle_list_tasks(tool_executor: ToolExecutor, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Convenience function to handle list_tasks tool calls.

    Args:
        tool_executor: Instance of ToolExecutor to perform the operation
        arguments: Dictionary containing the tool arguments

    Returns:
        List containing the response from the tool execution
    """
    handler = ListTasksHandler(tool_executor)
    return await handler.handle(arguments)