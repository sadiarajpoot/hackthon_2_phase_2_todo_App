"""
Tool request and response models for MCP tools.
Defines the input and output schemas for each of the MCP tools.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from uuid import UUID
from enum import Enum


class TaskStatusEnum(str, Enum):
    """Enumeration of possible task statuses."""
    pending = "pending"
    completed = "completed"


# AddTask Tool Models
class AddTaskRequest(BaseModel):
    """
    Request model for add_task MCP tool.
    """
    user_id: str = Field(..., description="User identifier", min_length=1)
    title: str = Field(..., description="Task title", min_length=1)
    description: Optional[str] = Field(None, description="Optional task description")


class AddTaskResponse(BaseModel):
    """
    Response model for add_task MCP tool.
    """
    task_id: str = Field(..., description="ID of the created task")
    status: str = Field("created", description="Status of the operation")
    title: str = Field(..., description="Title of the created task")


# ListTasks Tool Models
class ListTasksRequest(BaseModel):
    """
    Request model for list_tasks MCP tool.
    """
    user_id: str = Field(..., description="User identifier", min_length=1)
    status: Optional[Literal["all", "pending", "completed"]] = Field(
        None,
        description="Optional status filter for tasks"
    )


class TaskObject(BaseModel):
    """
    Task object model for list_tasks response.
    """
    id: str
    title: str
    description: Optional[str] = None
    status: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class ListTasksResponse(BaseModel):
    """
    Response model for list_tasks MCP tool.
    """
    tasks: List[TaskObject] = Field(..., description="Array of task objects")


# CompleteTask Tool Models
class CompleteTaskRequest(BaseModel):
    """
    Request model for complete_task MCP tool.
    """
    user_id: str = Field(..., description="User identifier", min_length=1)
    task_id: str = Field(..., description="Task identifier", min_length=1)


class CompleteTaskResponse(BaseModel):
    """
    Response model for complete_task MCP tool.
    """
    task_id: str = Field(..., description="ID of the completed task")
    status: str = Field("completed", description="Status of the operation")
    title: str = Field(..., description="Title of the completed task")


# DeleteTask Tool Models
class DeleteTaskRequest(BaseModel):
    """
    Request model for delete_task MCP tool.
    """
    user_id: str = Field(..., description="User identifier", min_length=1)
    task_id: str = Field(..., description="Task identifier", min_length=1)


class DeleteTaskResponse(BaseModel):
    """
    Response model for delete_task MCP tool.
    """
    task_id: str = Field(..., description="ID of the deleted task")
    status: str = Field("deleted", description="Status of the operation")
    title: str = Field(..., description="Title of the deleted task")


# UpdateTask Tool Models
class UpdateTaskRequest(BaseModel):
    """
    Request model for update_task MCP tool.
    """
    user_id: str = Field(..., description="User identifier", min_length=1)
    task_id: str = Field(..., description="Task identifier", min_length=1)
    title: Optional[str] = Field(None, description="New task title", min_length=1)
    description: Optional[str] = Field(None, description="New task description")

    def __init__(self, **data):
        super().__init__(**data)
        # Validate that at least one of title or description is provided
        if not data.get("title") and not data.get("description"):
            raise ValueError("At least one of 'title' or 'description' must be provided for update")


class UpdateTaskResponse(BaseModel):
    """
    Response model for update_task MCP tool.
    """
    task_id: str = Field(..., description="ID of the updated task")
    status: str = Field("updated", description="Status of the operation")
    title: str = Field(..., description="Title of the updated task")