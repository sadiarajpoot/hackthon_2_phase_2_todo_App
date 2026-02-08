from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import Any, List
from ..database import get_session
from ..schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskToggleResponse
from ..services.task_service import TaskService
from ..api.auth_router import get_current_user
from ..utils.logging import get_logger
from ..utils.responses import APIResponse, raise_http_exception
from ..models.user import User
from uuid import UUID

logger = get_logger(__name__)

task_router = APIRouter()


@task_router.get("/{user_id}/tasks", response_model=List[TaskResponse])
async def get_tasks(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
) -> Any:
    """
    Get all tasks for the specified user (must be the authenticated user)
    """
    try:
        # Verify that the requested user_id matches the authenticated user
        if str(current_user.id) != user_id:
            raise raise_http_exception(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this user's tasks"
            )

        logger.info(f"Getting tasks for user: {current_user.email}")

        # Create an instance of TaskService
        task_service = TaskService(db)

        # Convert user_id string to UUID
        user_uuid = UUID(user_id)

        # Get tasks for the user
        tasks = task_service.get_tasks_by_user_id(user_uuid)

        # Convert to response format
        task_responses = []
        for task in tasks:
            task_responses.append(TaskResponse(
                id=str(task.id),
                title=task.title,
                description=task.description,
                is_completed=task.is_completed,
                user_id=str(task.user_id),
                created_at=task.created_at,
                updated_at=task.updated_at,
                due_date=getattr(task, 'due_date', None)  # assuming due_date might exist
            ))

        logger.info(f"Retrieved {len(task_responses)} tasks for user: {current_user.email}")
        return task_responses

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting tasks for user {current_user.email}: {e}")
        raise_http_exception(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error getting tasks"
        )


@task_router.post("/{user_id}/tasks", response_model=TaskResponse)
async def create_task(
    user_id: str,
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
) -> Any:
    """
    Create a new task for the specified user (must be the authenticated user)
    """
    try:
        # Verify that the requested user_id matches the authenticated user
        if str(current_user.id) != user_id:
            raise raise_http_exception(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to create tasks for this user"
            )

        logger.info(f"Creating task for user: {current_user.email}")

        # Create an instance of TaskService
        task_service = TaskService(db)

        # Convert user_id string to UUID
        user_uuid = UUID(user_id)

        # Create the task model instance
        from ..models.task import Task as TaskModel
        task = TaskModel(
            title=task_data.title,
            description=task_data.description,
            user_id=user_uuid,
            is_completed=False  # Default to not completed
        )

        # Create the task
        created_task = task_service.create_task(task)

        # Convert to response format
        task_response = TaskResponse(
            id=str(created_task.id),
            title=created_task.title,
            description=created_task.description,
            is_completed=created_task.is_completed,
            user_id=str(created_task.user_id),
            created_at=created_task.created_at,
            updated_at=created_task.updated_at,
            due_date=getattr(created_task, 'due_date', None)  # assuming due_date might exist
        )

        logger.info(f"Task created successfully for user {current_user.email}: {task_response.title}")
        return task_response

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating task for user {current_user.email}: {e}")
        raise_http_exception(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error creating task"
        )


@task_router.get("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    user_id: str,
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
) -> Any:
    """
    Get a specific task by ID for the specified user (must be the authenticated user)
    """
    try:
        # Verify that the requested user_id matches the authenticated user
        if str(current_user.id) != user_id:
            raise raise_http_exception(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this user's tasks"
            )

        logger.info(f"Getting task {task_id} for user: {current_user.email}")

        # Create an instance of TaskService
        task_service = TaskService(db)

        # Get the task
        retrieved_task = task_service.get_task_by_id_and_user(task_id, UUID(user_id))

        if not retrieved_task:
            logger.warning(f"Task {task_id} not found for user: {current_user.email}")
            raise_http_exception(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        logger.info(f"Task retrieved successfully for user {current_user.email}: {retrieved_task.title}")
        return TaskResponse(
            id=str(retrieved_task.id),
            title=retrieved_task.title,
            description=retrieved_task.description,
            is_completed=retrieved_task.is_completed,
            user_id=str(retrieved_task.user_id),
            created_at=retrieved_task.created_at,
            updated_at=retrieved_task.updated_at,
            due_date=getattr(retrieved_task, 'due_date', None)
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting task {task_id} for user {current_user.email}: {e}")
        raise_http_exception(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error getting task"
        )


@task_router.put("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    user_id: str,
    task_id: UUID,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
) -> Any:
    """
    Update a specific task for the specified user (must be the authenticated user)
    """
    try:
        # Verify that the requested user_id matches the authenticated user
        if str(current_user.id) != user_id:
            raise raise_http_exception(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this user's tasks"
            )

        logger.info(f"Updating task {task_id} for user: {current_user.email}")

        # Create an instance of TaskService
        task_service = TaskService(db)

        # Prepare update data
        update_data = {}
        if task_data.title is not None:
            update_data['title'] = task_data.title
        if task_data.description is not None:
            update_data['description'] = task_data.description
        if task_data.is_completed is not None:
            update_data['is_completed'] = task_data.is_completed

        # Update the task
        updated_task = task_service.update_task(task_id, update_data)

        if not updated_task:
            logger.warning(f"Task {task_id} not found for user: {current_user.email}")
            raise_http_exception(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # Convert to response format
        task_response = TaskResponse(
            id=str(updated_task.id),
            title=updated_task.title,
            description=updated_task.description,
            is_completed=updated_task.is_completed,
            user_id=str(updated_task.user_id),
            created_at=updated_task.created_at,
            updated_at=updated_task.updated_at,
            due_date=getattr(updated_task, 'due_date', None)
        )

        logger.info(f"Task updated successfully for user {current_user.email}: {updated_task.title}")
        return task_response

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating task {task_id} for user {current_user.email}: {e}")
        raise_http_exception(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error updating task"
        )


@task_router.patch("/{user_id}/tasks/{task_id}/complete", response_model=TaskToggleResponse)
async def toggle_task_completion(
    user_id: str,
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
) -> Any:
    """
    Toggle completion status of a task for the specified user (must be the authenticated user)
    """
    try:
        # Verify that the requested user_id matches the authenticated user
        if str(current_user.id) != user_id:
            raise raise_http_exception(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to modify this user's tasks"
            )

        logger.info(f"Toggling task completion for {task_id} for user: {current_user.email}")

        # Create an instance of TaskService
        task_service = TaskService(db)

        # Toggle the task completion
        toggled_task = task_service.toggle_task_completion(task_id)

        if not toggled_task:
            logger.warning(f"Task {task_id} not found for user: {current_user.email}")
            raise_http_exception(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        logger.info(f"Task completion toggled for user {current_user.email}: {toggled_task.title}")
        return TaskToggleResponse(
            id=str(toggled_task.id),
            title=toggled_task.title,
            is_completed=toggled_task.is_completed,
            updated_at=toggled_task.updated_at
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error toggling task {task_id} for user {current_user.email}: {e}")
        raise_http_exception(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error toggling task"
        )


@task_router.delete("/{user_id}/tasks/{task_id}")
async def delete_task(
    user_id: str,
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
) -> Any:
    """
    Delete a specific task for the specified user (must be the authenticated user)
    """
    try:
        # Verify that the requested user_id matches the authenticated user
        if str(current_user.id) != user_id:
            raise raise_http_exception(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this user's tasks"
            )

        logger.info(f"Deleting task {task_id} for user: {current_user.email}")

        # Create an instance of TaskService
        task_service = TaskService(db)

        # Delete the task
        success = task_service.delete_task(task_id)

        if not success:
            logger.warning(f"Task {task_id} not found for user: {current_user.email}")
            raise_http_exception(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        logger.info(f"Task deleted successfully for user {current_user.email}: {task_id}")
        return APIResponse.success(
            data=None,
            message="Task deleted successfully"
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error deleting task {task_id} for user {current_user.email}: {e}")
        raise_http_exception(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error deleting task"
        )