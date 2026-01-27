from sqlmodel import Session, select
from typing import List, Optional
from uuid import UUID
from ..models.task import Task
from ..models.user import User
from ..schemas.task import TaskCreate, TaskUpdate, TaskResponse
from ..utils.logging import get_logger
from ..utils.responses import raise_http_exception, not_found_exception
from fastapi import HTTPException, status

logger = get_logger(__name__)


class TaskService:
    @staticmethod
    async def create_task(task_data: TaskCreate, user_id: str, db_session: Session) -> TaskResponse:
        """Create a new task for a user"""
        try:
            # Create new task
            db_task = Task(
                title=task_data.title,
                description=task_data.description,
                is_completed=task_data.is_completed,
                due_date=task_data.due_date,
                user_id=UUID(user_id)  # Convert string to UUID
            )

            db_session.add(db_task)
            db_session.commit()
            db_session.refresh(db_task)

            logger.info(f"Task created successfully for user {user_id}: {db_task.title}")

            return TaskResponse(
                id=str(db_task.id),
                title=db_task.title,
                description=db_task.description,
                is_completed=db_task.is_completed,
                user_id=str(db_task.user_id),
                created_at=db_task.created_at,
                updated_at=db_task.updated_at,
                due_date=db_task.due_date
            )

        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            raise_http_exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error during task creation"
            )

    @staticmethod
    async def get_task_by_id(task_id: str, user_id: str, db_session: Session) -> Optional[Task]:
        """Get a specific task by ID for a user"""
        try:
            task = db_session.exec(
                select(Task).where(Task.id == task_id, Task.user_id == UUID(user_id))
            ).first()

            if not task:
                logger.warning(f"Task not found for user {user_id} with id {task_id}")
                return None

            logger.info(f"Task retrieved successfully for user {user_id}: {task.title}")
            return task

        except Exception as e:
            logger.error(f"Error retrieving task {task_id} for user {user_id}: {e}")
            return None

    @staticmethod
    async def check_task_ownership(task_id: str, user_id: str, db_session: Session) -> bool:
        """Check if a user owns a specific task"""
        try:
            task = db_session.exec(
                select(Task).where(Task.id == task_id, Task.user_id == UUID(user_id))
            ).first()

            is_owner = task is not None
            if not is_owner:
                logger.warning(f"User {user_id} attempted to access task {task_id} they don't own")

            return is_owner

        except Exception as e:
            logger.error(f"Error checking task ownership for task {task_id} and user {user_id}: {e}")
            return False

    @staticmethod
    async def get_tasks_by_user(user_id: str, db_session: Session) -> List[TaskResponse]:
        """Get all tasks for a user"""
        try:
            tasks = db_session.exec(
                select(Task).where(Task.user_id == UUID(user_id))
            ).all()

            logger.info(f"Retrieved {len(tasks)} tasks for user {user_id}")
            return [
                TaskResponse(
                    id=str(task.id),
                    title=task.title,
                    description=task.description,
                    is_completed=task.is_completed,
                    user_id=str(task.user_id),
                    created_at=task.created_at,
                    updated_at=task.updated_at,
                    due_date=task.due_date
                ) for task in tasks
            ]

        except Exception as e:
            logger.error(f"Error retrieving tasks for user {user_id}: {e}")
            raise_http_exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error during task retrieval"
            )

    @staticmethod
    async def update_task(task_id: str, task_data: TaskUpdate, user_id: str, db_session: Session) -> Optional[TaskResponse]:
        """Update a specific task for a user"""
        try:
            # Get the existing task
            task = db_session.exec(
                select(Task).where(Task.id == task_id, Task.user_id == UUID(user_id))
            ).first()

            if not task:
                logger.warning(f"Task not found for user {user_id} with id {task_id}")
                return None

            # Update task fields
            update_data = task_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(task, field, value)

            db_session.add(task)
            db_session.commit()
            db_session.refresh(task)

            logger.info(f"Task updated successfully for user {user_id}: {task.title}")

            return TaskResponse(
                id=str(task.id),
                title=task.title,
                description=task.description,
                is_completed=task.is_completed,
                user_id=str(task.user_id),
                created_at=task.created_at,
                updated_at=task.updated_at,
                due_date=task.due_date
            )

        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            logger.error(f"Error updating task {task_id} for user {user_id}: {e}")
            raise_http_exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error during task update"
            )

    @staticmethod
    async def delete_task(task_id: str, user_id: str, db_session: Session) -> bool:
        """Delete a specific task for a user"""
        try:
            # Get the existing task
            task = db_session.exec(
                select(Task).where(Task.id == task_id, Task.user_id == UUID(user_id))
            ).first()

            if not task:
                logger.warning(f"Task not found for user {user_id} with id {task_id}")
                return False

            db_session.delete(task)
            db_session.commit()

            logger.info(f"Task deleted successfully for user {user_id}: {task.title}")

            return True

        except Exception as e:
            logger.error(f"Error deleting task {task_id} for user {user_id}: {e}")
            raise_http_exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error during task deletion"
            )

    @staticmethod
    async def toggle_task_completion(task_id: str, user_id: str, db_session: Session) -> Optional[TaskResponse]:
        """Toggle the completion status of a task"""
        try:
            # Get the existing task
            task = db_session.exec(
                select(Task).where(Task.id == task_id, Task.user_id == UUID(user_id))
            ).first()

            if not task:
                logger.warning(f"Task not found for user {user_id} with id {task_id}")
                return None

            # Toggle completion status
            task.is_completed = not task.is_completed
            db_session.add(task)
            db_session.commit()
            db_session.refresh(task)

            logger.info(f"Task completion toggled for user {user_id}: {task.title} (now {task.is_completed})")

            return TaskResponse(
                id=str(task.id),
                title=task.title,
                description=task.description,
                is_completed=task.is_completed,
                user_id=str(task.user_id),
                created_at=task.created_at,
                updated_at=task.updated_at,
                due_date=task.due_date
            )

        except Exception as e:
            logger.error(f"Error toggling task completion {task_id} for user {user_id}: {e}")
            raise_http_exception(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error during task toggle"
            )