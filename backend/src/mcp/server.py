"""
MCP (Model Context Protocol) server implementation for AI agent task management tools.
This server provides standardized tool calls that allow AI agents to manage user tasks.
"""
import asyncio
from typing import Any, Dict, List, Optional
from uuid import UUID
import logging

# Import the python-mcp library
try:
    from mcp.server import Server
    from mcp.types import Tool, ArgumentsSchema
except ImportError:
    raise ImportError("python-mcp library is required. Install with: pip install python-mcp")

# Import existing services and models from Phase II
from ..models.task import Task
from ..services.task_service import TaskService
from .services.tool_executor import ToolExecutor
from .models.tool_requests import (
    AddTaskRequest, AddTaskResponse,
    ListTasksRequest, ListTasksResponse,
    CompleteTaskRequest, CompleteTaskResponse,
    DeleteTaskRequest, DeleteTaskResponse,
    UpdateTaskRequest, UpdateTaskResponse
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the MCP server instance
server = Server("mcp-task-manager")


@server.list_tools()
def list_tools() -> List[Tool]:
    """List all available tools for AI agents to use."""
    return [
        Tool(
            name="add_task",
            description="Create a new task for a user",
            input_schema=AddTaskRequest.model_json_schema()
        ),
        Tool(
            name="list_tasks",
            description="Retrieve user's tasks with optional status filtering",
            input_schema=ListTasksRequest.model_json_schema()
        ),
        Tool(
            name="complete_task",
            description="Mark a task as completed",
            input_schema=CompleteTaskRequest.model_json_schema()
        ),
        Tool(
            name="delete_task",
            description="Delete a task",
            input_schema=DeleteTaskRequest.model_json_schema()
        ),
        Tool(
            name="update_task",
            description="Update task title or description",
            input_schema=UpdateTaskRequest.model_json_schema()
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Handle tool calls from AI agents.

    Args:
        name: Name of the tool to call
        arguments: Arguments for the tool

    Returns:
        List of results from the tool call
    """
    logger.info(f"Received tool call: {name} with args: {arguments}")

    # Initialize the tool executor with database session
    # Note: In a real implementation, you'd get the session from your database setup
    # For now, we'll mock it or use a session factory
    from ..database import get_session

    # For this example, we'll use a synchronous approach
    # In production, you'd want to properly handle async database operations
    try:
        # Create tool executor instance
        with next(get_session()) as session:
            tool_executor = ToolExecutor(session)

            if name == "add_task":
                request = AddTaskRequest(**arguments)
                result = await tool_executor.execute_add_task(request)
                return [result.model_dump()]

            elif name == "list_tasks":
                request = ListTasksRequest(**arguments)
                result = await tool_executor.execute_list_tasks(request)
                return [result.model_dump()]

            elif name == "complete_task":
                request = CompleteTaskRequest(**arguments)
                result = await tool_executor.execute_complete_task(request)
                return [result.model_dump()]

            elif name == "delete_task":
                request = DeleteTaskRequest(**arguments)
                result = await tool_executor.execute_delete_task(request)
                return [result.model_dump()]

            elif name == "update_task":
                request = UpdateTaskRequest(**arguments)
                result = await tool_executor.execute_update_task(request)
                return [result.model_dump()]

            else:
                raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        logger.error(f"Error executing tool {name}: {str(e)}")
        raise


# Placeholder for startup/shutdown events
@server.on_startup()
async def startup():
    """Initialize resources when the server starts."""
    logger.info("MCP Task Manager server starting up...")
    # Any initialization code goes here


@server.on_shutdown()
async def shutdown():
    """Clean up resources when the server shuts down."""
    logger.info("MCP Task Manager server shutting down...")
    # Any cleanup code goes here


# Async main function to run the server
async def main():
    """Main entry point for the MCP server."""
    # This would typically connect to an MCP broker
    # For now, this is just a placeholder
    logger.info("Starting MCP Task Manager server...")

    # Keep the server running
    try:
        # In a real implementation, you'd connect to the MCP broker here
        # await server.run()  # This is pseudocode - actual implementation depends on python-mcp API
        pass
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server error: {e}")


if __name__ == "__main__":
    # Run the server
    asyncio.run(main())