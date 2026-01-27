from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    is_completed: bool = False
    due_date: Optional[datetime] = None


class TaskCreate(TaskBase):
    title: str  # Required field for creation

    class Config:
        from_attributes = True


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    due_date: Optional[datetime] = None


class TaskInDB(TaskBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskResponse(TaskInDB):
    pass


class TaskToggleResponse(BaseModel):
    id: UUID
    title: str
    is_completed: bool
    updated_at: datetime

    class Config:
        from_attributes = True