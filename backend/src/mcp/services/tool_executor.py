"""
ToolExecutor service for MCP tools.
Handles the execution of tool calls against the database with proper validation and authentication.
"""
from typing import Optional
from uuid import UUID
import uuid
from datetime import datetime
from sqlmodel import Session, select
from ..models.task import Task, TaskStatus
from ..services.task_service import TaskService
from ..middleware.auth import get_current_user, TokenData
from ..database import get_session
import logging

# Import tool request/response models
from ..models.task import Task as TaskModel
from ..models.user import User
from ..database import get_session
from ..services.task_service import TaskService
from ..middleware.auth import verify_token
from ..utils.logging import logger

# Import tool request/response models
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


class ToolExecutor:
    """
    Service class for executing MCP tool calls with proper validation, authentication, and error handling.
    """

    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.task_service = TaskService(db_session)

    async def execute_add_task(self, request: AddTaskRequest) -> AddTaskResponse:
        """
        Execute the add_task tool call.

        Args:
            request: AddTaskRequest containing user_id, title, and optional description

        Returns:
            AddTaskResponse with task_id, status, and title
        """
        try:
            # Validate that the user_id in the request matches the authenticated user
            # In a real implementation, you'd have the authenticated user context from the session
            # For now, we'll assume the request user_id is valid

            # Validate inputs
            if not request.title or not request.title.strip():
                raise ValueError("Task title cannot be empty")

            # Create the task
            task = TaskModel(
                title=request.title,
                description=request.description,
                user_id=UUID(request.user_id) if isinstance(request.user_id, str) else request.user_id,
                status=TaskStatus.pending
            )

            # Use the existing task service to create the task
            created_task = self.task_service.create_task(task)

            logger.info(f"Successfully created task {created_task.id} for user {request.user_id}")

            return AddTaskResponse(
                task_id=str(created_task.id),
                status="created",
                title=created_task.title
            )

        except Exception as e:
            logger.error(f"Error in execute_add_task: {str(e)}")
            raise

    async def execute_list_tasks(self, request: ListTasksRequest) -> ListTasksResponse:
        """
        Execute the list_tasks tool call.

        Args:
            request: ListTasksRequest containing user_id and optional status filter

        Returns:
            ListTasksResponse with array of task objects
        """
        try:
            # Validate that the user_id in the request matches the authenticated user
            user_uuid = UUID(request.user_id) if isinstance(request.user_id, str) else request.user_id

            # Get tasks for the user
            tasks = self.task_service.get_tasks_by_user_id(user_uuid)

            # Apply status filter if provided
            if request.status:
                if request.status.lower() == "pending":
                    tasks = [task for task in tasks if task.status == TaskStatus.pending]
                elif request.status.lower() == "completed":
                    tasks = [task for task in tasks if task.status == TaskStatus.completed]
                # If status is "all" or any other value, return all tasks (no filter applied)

            logger.info(f"Retrieved {len(tasks)} tasks for user {request.user_id}")

            # Convert to response format
            task_objects = []
            for task in tasks:
                task_objects.append({
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "status": task.status.value,
                    "created_at": task.created_at.isoformat() if task.created_at else None,
                    "updated_at": task.updated_at.isoformat() if task.updated_at else None
                })

            return ListTasksResponse(tasks=task_objects)

        except Exception as e:
            logger.error(f"Error in execute_list_tasks: {str(e)}")
            raise

    async def execute_complete_task(self, request: CompleteTaskRequest) -> CompleteTaskResponse:
        """
        Execute the complete_task tool call.

        Args:
            request: CompleteTaskRequest containing user_id and task_id

        Returns:
            CompleteTaskResponse with task_id, status, and title
        """
        try:
            # Validate inputs
            user_uuid = UUID(request.user_id) if isinstance(request.user_id, str) else request.user_id
            task_uuid = UUID(request.task_id) if isinstance(request.task_id, str) else request.task_id

            # Get the task to verify it exists and belongs to the user
            task = self.task_service.get_task_by_id_and_user(task_uuid, user_uuid)
            if not task:
                raise ValueError(f"Task {request.task_id} not found or does not belong to user {request.user_id}")

            # Update the task status to completed
            update_data = {"status": TaskStatus.completed}
            updated_task = self.task_service.update_task(task.id, update_data)

            logger.info(f"Successfully completed task {request.task_id} for user {request.user_id}")

            return CompleteTaskResponse(
                task_id=str(updated_task.id),
                status="completed",
                title=updated_task.title
            )

        except Exception as e:
            logger.error(f"Error in execute_complete_task: {str(e)}")
            raise

    async def execute_delete_task(self, request: DeleteTaskRequest) -> DeleteTaskResponse:
        """
        Execute the delete_task tool call.

        Args:
            request: DeleteTaskRequest containing user_id and task_id

        Returns:
            DeleteTaskResponse with task_id, status, and title
        """
        try:
            # Validate inputs
            user_uuid = UUID(request.user_id) if isinstance(request.user_id, str) else request.user_id
            task_uuid = UUID(request.task_id) if isinstance(request.task_id, str) else request.task_id

            # Get the task to verify it exists and belongs to the user
            task = self.task_service.get_task_by_id_and_user(task_uuid, user_uuid)
            if not task:
                raise ValueError(f"Task {request.task_id} not found or does not belong to user {request.user_id}")

            # Store task details before deletion for the response
            task_title = task.title
            task_id = str(task.id)

            # Delete the task
            success = self.task_service.delete_task(task_uuid)
            if not success:
                raise ValueError(f"Failed to delete task {request.task_id}")

            logger.info(f"Successfully deleted task {request.task_id} for user {request.user_id}")

            return DeleteTaskResponse(
                task_id=task_id,
                status="deleted",
                title=task_title
            )

        except Exception as e:
            logger.error(f"Error in execute_delete_task: {str(e)}")
            raise

    async def execute_update_task(self, request: UpdateTaskRequest) -> UpdateTaskResponse:
        """
        Execute the update_task tool call.

        Args:
            request: UpdateTaskRequest containing user_id, task_id, and optional title/description

        Returns:
            UpdateTaskResponse with task_id, status, and title
        """
        try:
            # Validate inputs
            user_uuid = UUID(request.user_id) if isinstance(request.user_id, str) else request.user_id
            task_uuid = UUID(request.task_id) if isinstance(request.task_id, str) else request.task_id

            # At least one of title or description must be provided
            if not request.title and not request.description:
                raise ValueError("At least one of title or description must be provided for update")

            # Get the task to verify it exists and belongs to the user
            task = self.task_service.get_task_by_id_and_user(task_uuid, user_uuid)
            if not task:
                raise ValueError(f"Task {request.task_id} not found or does not belong to user {request.user_id}")

            # Prepare update data
            update_data = {}
            if request.title is not None:
                update_data["title"] = request.title
            if request.description is not None:
                update_data["description"] = request.description

            # Update the task
            updated_task = self.task_service.update_task(task.id, update_data)

            logger.info(f"Successfully updated task {request.task_id} for user {request.user_id}")

            return UpdateTaskResponse(
                task_id=str(updated_task.id),
                status="updated",
                title=updated_task.title
            )

        except Exception as e:
            logger.error(f"Error in execute_update_task: {str(e)}")
            raise

    def validate_user_access(self, user_id: str, task_user_id: UUID) -> bool:
        """
        Validate that the user_id matches the task's owner.

        Args:
            user_id: User ID from the request
            task_user_id: User ID of the task owner

        Returns:
            True if user has access to the task, False otherwise
        """
        try:
            request_user_uuid = UUID(user_id) if isinstance(user_id, str) else user_id
            return request_user_uuid == task_user_id
        except ValueError:
            return False