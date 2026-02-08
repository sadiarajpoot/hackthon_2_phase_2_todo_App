"""
MCP Tools Service for task operations.
Handles the execution of MCP tool calls from the AI agent with proper validation and error handling.
"""
from typing import Dict, Any, List, Optional
from sqlmodel import Session
from uuid import UUID
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ToolExecutor:
    """
    Service class to execute MCP tool calls from the AI agent with proper validation and error handling.
    """

    def __init__(self, db_session: Session):
        self.db_session = db_session

        # Import services
        from ..services.task_service import TaskService
        from ..services.conversation_service import ConversationService
        from ..services.message_service import MessageService

        self.task_service = TaskService(db_session)
        self.conversation_service = ConversationService(db_session)
        self.message_service = MessageService(db_session)

    async def execute_add_task(self, user_id: str, title: str, description: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute the add_task MCP tool call.

        Args:
            user_id: The ID of the user requesting the task creation
            title: The title of the task to create
            description: Optional description for the task

        Returns:
            Dictionary with task_id, status, and title
        """
        try:
            logger.info(f"Executing add_task for user: {user_id}")

            # Validate inputs
            if not title or not title.strip():
                raise ValueError("Title is required and cannot be empty")

            # Convert user_id string to UUID
            from uuid import UUID as UUID_TYPE
            user_uuid = UUID_TYPE(user_id)

            # Create task model
            from ..models.task import Task as TaskModel, TaskStatus
            task = TaskModel(
                title=title.strip(),
                description=description,
                user_id=user_uuid,
                status=TaskStatus.pending  # Default to pending
            )

            # Create the task using the task service
            created_task = self.task_service.create_task(task)

            logger.info(f"Task created successfully: {created_task.title}")

            return {
                "task_id": str(created_task.id),
                "status": "created",
                "title": created_task.title
            }

        except ValueError as e:
            logger.error(f"Validation error in add_task: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error executing add_task: {str(e)}")
            raise

    async def execute_list_tasks(self, user_id: str, status_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute the list_tasks MCP tool call.

        Args:
            user_id: The ID of the user whose tasks to retrieve
            status_filter: Optional status to filter by (pending, completed, all)

        Returns:
            Dictionary with task list and count
        """
        try:
            logger.info(f"Executing list_tasks for user: {user_id} with filter: {status_filter}")

            # Convert user_id string to UUID
            from uuid import UUID as UUID_TYPE
            user_uuid = UUID_TYPE(user_id)

            # Get tasks based on filter
            if status_filter == "completed":
                tasks = self.task_service.get_tasks_by_user_id_and_status(user_uuid, "completed")
            elif status_filter == "pending":
                tasks = self.task_service.get_tasks_by_user_id_and_status(user_uuid, "pending")
            else:
                # Get all tasks
                tasks = self.task_service.get_tasks_by_user_id(user_uuid)

            # Format tasks for response
            task_list = []
            for task in tasks:
                task_list.append({
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "is_completed": task.status == "completed",
                    "created_at": task.created_at.isoformat() if task.created_at else None
                })

            logger.info(f"Retrieved {len(task_list)} tasks for user: {user_id}")

            return {
                "tasks": task_list,
                "task_count": len(task_list)
            }

        except Exception as e:
            logger.error(f"Error executing list_tasks: {str(e)}")
            raise

    async def execute_complete_task(self, user_id: str, task_id: str) -> Dict[str, Any]:
        """
        Execute the complete_task MCP tool call.

        Args:
            user_id: The ID of the user requesting the task completion
            task_id: The ID of the task to mark as complete

        Returns:
            Dictionary with task_id, status, and title
        """
        try:
            logger.info(f"Executing complete_task for user: {user_id}, task: {task_id}")

            # Convert IDs to UUIDs
            from uuid import UUID as UUID_TYPE
            user_uuid = UUID_TYPE(user_id)
            task_uuid = UUID_TYPE(task_id)

            # Get the task to verify it belongs to the user
            task = self.task_service.get_task_by_id_and_user(task_uuid, user_uuid)
            if not task:
                raise ValueError(f"Task {task_id} not found or does not belong to user")

            # Complete the task
            completed_task = self.task_service.complete_task(task_uuid)

            if not completed_task:
                raise ValueError(f"Failed to complete task {task_id}")

            logger.info(f"Task completed successfully: {completed_task.title}")

            return {
                "task_id": str(completed_task.id),
                "status": "completed",
                "title": completed_task.title
            }

        except ValueError as e:
            logger.error(f"Validation error in complete_task: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error executing complete_task: {str(e)}")
            raise

    async def execute_delete_task(self, user_id: str, task_id: str) -> Dict[str, Any]:
        """
        Execute the delete_task MCP tool call.

        Args:
            user_id: The ID of the user requesting the task deletion
            task_id: The ID of the task to delete

        Returns:
            Dictionary with task_id, status, and title
        """
        try:
            logger.info(f"Executing delete_task for user: {user_id}, task: {task_id}")

            # Convert IDs to UUIDs
            from uuid import UUID as UUID_TYPE
            user_uuid = UUID_TYPE(user_id)
            task_uuid = UUID_TYPE(task_id)

            # Get the task to verify it belongs to the user
            task = self.task_service.get_task_by_id_and_user(task_uuid, user_uuid)
            if not task:
                raise ValueError(f"Task {task_id} not found or does not belong to user")

            # Delete the task
            success = self.task_service.delete_task(task_uuid)

            if not success:
                raise ValueError(f"Failed to delete task {task_id}")

            logger.info(f"Task deleted successfully: {task.title}")

            return {
                "task_id": str(task.id),
                "status": "deleted",
                "title": task.title
            }

        except ValueError as e:
            logger.error(f"Validation error in delete_task: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error executing delete_task: {str(e)}")
            raise

    async def execute_update_task(self, user_id: str, task_id: str, title: Optional[str] = None, description: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute the update_task MCP tool call.

        Args:
            user_id: The ID of the user requesting the task update
            task_id: The ID of the task to update
            title: Optional new title for the task
            description: Optional new description for the task

        Returns:
            Dictionary with task_id, status, and title
        """
        try:
            logger.info(f"Executing update_task for user: {user_id}, task: {task_id}")

            # Convert IDs to UUIDs
            from uuid import UUID as UUID_TYPE
            user_uuid = UUID_TYPE(user_id)
            task_uuid = UUID_TYPE(task_id)

            # Get the task to verify it belongs to the user
            task = self.task_service.get_task_by_id_and_user(task_uuid, user_uuid)
            if not task:
                raise ValueError(f"Task {task_id} not found or does not belong to user")

            # Prepare update data
            update_data = {}
            if title is not None:
                update_data["title"] = title.strip() if title.strip() else task.title
            if description is not None:
                update_data["description"] = description

            # Update the task
            updated_task = self.task_service.update_task(task_uuid, update_data)

            if not updated_task:
                raise ValueError(f"Failed to update task {task_id}")

            logger.info(f"Task updated successfully: {updated_task.title}")

            return {
                "task_id": str(updated_task.id),
                "status": "updated",
                "title": updated_task.title
            }

        except ValueError as e:
            logger.error(f"Validation error in update_task: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error executing update_task: {str(e)}")
            raise