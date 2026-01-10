from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.enum import TaskStatus

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str

class CreateTask(TaskBase):
    due_at: Optional[datetime] = None

class TaskResponse(TaskBase):
    id: int
    status: TaskStatus
    due_at: Optional[datetime] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config: 
        orm_mode = True

class UpdateTask(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[TaskStatus] = None
    due_at: Optional[datetime] = None