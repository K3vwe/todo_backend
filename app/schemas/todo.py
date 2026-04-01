from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from app.models.enum import TaskPriority
from uuid import UUID

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None

class CreateTask(TaskBase):
    due_at: Optional[datetime] = None

class TaskResponse(TaskBase):
    id: UUID
    user_id: UUID
    status: str  # derived, returned to client
    due_at: Optional[datetime] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class UpdateTask(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None  
    due_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None  