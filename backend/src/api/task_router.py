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


@task_router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
) -> Any:
    """
    Get all tasks for the authenticated user
    """
    try:
        logger.info(f"Getting tasks for user: {current_user.email}")

        tasks = await TaskService.get_tasks_by_user(str(current_user.id), db)

        logger.info(f"Retrieved {len(tasks)} tasks for user: {current_user.email}")
        return tasks

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting tasks for user {current_user.email}: {e}")
        raise_http_exception(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error getting tasks"
        )


@task_router.post("/", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
) -> Any:
    """
    Create a new task for the authenticated user
    """
    try:
        logger.info(f"Creating task for user: {current_user.email}")

        # Create the task
        task_response = await TaskService.create_task(task_data, str(current_user.id), db)

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


@task_router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
) -> Any:
    """
    Get a specific task by ID for the authenticated user
    """
    try:
        logger.info(f"Getting task {task_id} for user: {current_user.email}")

        # Get the task
        task = await TaskService.get_task_by_id(str(task_id), str(current_user.id), db)

        if not task:
            logger.warning(f"Task {task_id} not found for user: {current_user.email}")
            raise_http_exception(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        logger.info(f"Task retrieved successfully for user {current_user.email}: {task.title}")
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
        logger.error(f"Unexpected error getting task {task_id} for user {current_user.email}: {e}")
        raise_http_exception(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error getting task"
        )


@task_router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
) -> Any:
    """
    Update a specific task for the authenticated user
    """
    try:
        logger.info(f"Updating task {task_id} for user: {current_user.email}")

        # Update the task
        updated_task = await TaskService.update_task(str(task_id), task_data, str(current_user.id), db)

        if not updated_task:
            logger.warning(f"Task {task_id} not found for user: {current_user.email}")
            raise_http_exception(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        logger.info(f"Task updated successfully for user {current_user.email}: {updated_task.title}")
        return updated_task

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating task {task_id} for user {current_user.email}: {e}")
        raise_http_exception(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error updating task"
        )


@task_router.patch("/{task_id}/toggle", response_model=TaskToggleResponse)
async def toggle_task_completion(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
) -> Any:
    """
    Toggle completion status of a task for the authenticated user
    """
    try:
        logger.info(f"Toggling task completion for {task_id} for user: {current_user.email}")

        # Toggle the task completion
        toggled_task = await TaskService.toggle_task_completion(str(task_id), str(current_user.id), db)

        if not toggled_task:
            logger.warning(f"Task {task_id} not found for user: {current_user.email}")
            raise_http_exception(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        logger.info(f"Task completion toggled for user {current_user.email}: {toggled_task.title}")
        return TaskToggleResponse(
            id=toggled_task.id,
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


@task_router.delete("/{task_id}")
async def delete_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
) -> Any:
    """
    Delete a specific task for the authenticated user
    """
    try:
        logger.info(f"Deleting task {task_id} for user: {current_user.email}")

        # Delete the task
        success = await TaskService.delete_task(str(task_id), str(current_user.id), db)

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