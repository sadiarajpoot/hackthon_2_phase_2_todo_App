"""
complete_task tool handler for MCP tools.
Implements the complete_task functionality that allows AI agents to mark tasks as complete.
"""
from typing import Dict, Any, List
from pydantic import BaseModel
from uuid import UUID
import logging

# Import the request/response models
from ..models.tool_requests import CompleteTaskRequest, CompleteTaskResponse

# Import the tool executor
from ..services.tool_executor import ToolExecutor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CompleteTaskHandler:
    """
    Handler for the complete_task MCP tool.
    Processes requests to mark tasks as completed via the MCP protocol.
    """

    def __init__(self, tool_executor: ToolExecutor):
        self.tool_executor = tool_executor

    async def handle(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Handle a complete_task tool call from an AI agent.

        Args:
            arguments: Dictionary containing the tool arguments (user_id, task_id)

        Returns:
            List containing the response from the tool execution
        """
        try:
            # Validate and parse the arguments using the Pydantic model
            request = CompleteTaskRequest(**arguments)

            # Execute the tool via the ToolExecutor service
            response = await self.tool_executor.execute_complete_task(request)

            # Log the successful operation
            logger.info(f"Successfully completed task {response.task_id} for user {request.user_id}")

            # Return the response in the expected format
            return [{
                "task_id": response.task_id,
                "status": response.status,
                "title": response.title
            }]

        except Exception as e:
            logger.error(f"Error in complete_task handler: {str(e)}")
            raise


# For direct usage without instantiating the class
async def handle_complete_task(tool_executor: ToolExecutor, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Convenience function to handle complete_task tool calls.

    Args:
        tool_executor: Instance of ToolExecutor to perform the operation
        arguments: Dictionary containing the tool arguments

    Returns:
        List containing the response from the tool execution
    """
    handler = CompleteTaskHandler(tool_executor)
    return await handler.handle(arguments)