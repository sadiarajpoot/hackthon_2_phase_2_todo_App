"""
Task Service for handling task-related operations.
Manages task creation, retrieval, updates, and deletions for the chat API and MCP tools.
"""
from typing import List, Optional
from sqlmodel import Session, select
from uuid import UUID
import uuid
from datetime import datetime
from ..models.task import Task as TaskModel, TaskStatus


class TaskService:
    """
    Service class for managing tasks in the database.
    Handles creation, retrieval, updates, and deletions of task records.
    """

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create_task(self, task: TaskModel) -> TaskModel:
        """
        Create a new task.

        Args:
            task: Task object to create with title, description, user_id, and initial status

        Returns:
            Created Task object with ID assigned
        """
        # Ensure the task has a unique ID
        if not task.id:
            task.id = uuid.uuid4()

        # Set default status if not provided
        if not hasattr(task, 'status') or task.status is None:
            task.status = TaskStatus.pending

        self.db_session.add(task)
        self.db_session.commit()
        self.db_session.refresh(task)
        return task

    def get_task_by_id(self, task_id: UUID) -> Optional[TaskModel]:
        """
        Get a task by its ID.

        Args:
            task_id: ID of the task to retrieve

        Returns:
            Task object if found, None otherwise
        """
        statement = select(TaskModel).where(TaskModel.id == task_id)
        result = self.db_session.exec(statement)
        return result.first()

    def get_task_by_id_and_user(self, task_id: UUID, user_id: UUID) -> Optional[TaskModel]:
        """
        Get a task by its ID and user ID (for authorization).

        Args:
            task_id: ID of the task to retrieve
            user_id: ID of the user who owns the task

        Returns:
            Task object if found and owned by user, None otherwise
        """
        statement = select(TaskModel).where(
            TaskModel.id == task_id,
            TaskModel.user_id == user_id
        )
        result = self.db_session.exec(statement)
        return result.first()

    def get_tasks_by_user_id(self, user_id: UUID) -> List[TaskModel]:
        """
        Get all tasks for a specific user.

        Args:
            user_id: ID of the user whose tasks to retrieve

        Returns:
            List of Task objects belonging to the user
        """
        statement = select(TaskModel).where(TaskModel.user_id == user_id)
        result = self.db_session.exec(statement)
        return result.all()

    def get_tasks_by_user_id_and_status(self, user_id: UUID, status: str) -> List[TaskModel]:
        """
        Get all tasks for a user with a specific completion status.

        Args:
            user_id: ID of the user whose tasks to retrieve
            status: Status to filter by ('completed', 'pending', etc.)

        Returns:
            List of Task objects with the specified status
        """
        from ..models.task import TaskStatus
        # Convert string status to enum if needed
        status_enum = TaskStatus(status) if status in ["pending", "completed"] else TaskStatus.pending

        statement = select(TaskModel).where(
            TaskModel.user_id == user_id,
            TaskModel.status == status_enum
        )
        result = self.db_session.exec(statement)
        return result.all()

    def update_task(self, task_id: UUID, update_data: dict) -> Optional[TaskModel]:
        """
        Update a task with new data.

        Args:
            task_id: ID of the task to update
            update_data: Dictionary of fields to update

        Returns:
            Updated Task object if successful, None if task not found
        """
        task = self.get_task_by_id(task_id)
        if not task:
            return None

        # Update task fields with provided data
        for field, value in update_data.items():
            if hasattr(task, field):
                setattr(task, field, value)

        # Update the timestamp
        task.updated_at = datetime.utcnow()

        self.db_session.add(task)
        self.db_session.commit()
        self.db_session.refresh(task)
        return task

    def delete_task(self, task_id: UUID) -> bool:
        """
        Delete a task.

        Args:
            task_id: ID of the task to delete

        Returns:
            True if deletion was successful, False if task not found
        """
        task = self.get_task_by_id(task_id)
        if not task:
            return False

        self.db_session.delete(task)
        self.db_session.commit()
        return True

    def complete_task(self, task_id: UUID) -> Optional[TaskModel]:
        """
        Mark a task as completed.

        Args:
            task_id: ID of the task to mark as completed

        Returns:
            Updated Task object if successful, None if task not found
        """
        return self.update_task(task_id, {"status": TaskStatus.completed})

    def toggle_task_completion(self, task_id: UUID) -> Optional[TaskModel]:
        """
        Toggle the completion status of a task.

        Args:
            task_id: ID of the task to toggle

        Returns:
            Updated Task object if successful, None if task not found
        """
        task = self.get_task_by_id(task_id)
        if not task:
            return None

        # Toggle the status
        new_status = TaskStatus.completed if task.status != TaskStatus.completed else TaskStatus.pending
        return self.update_task(task_id, {"status": new_status})

    def count_tasks_by_user(self, user_id: UUID) -> int:
        """
        Count the number of tasks for a user.

        Args:
            user_id: ID of the user whose tasks to count

        Returns:
            Number of tasks belonging to the user
        """
        statement = select(TaskModel).where(TaskModel.user_id == user_id)
        result = self.db_session.exec(statement)
        tasks = result.all()
        return len(tasks)