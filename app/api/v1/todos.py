from fastapi import APIRouter
from datetime import datetime
from app.models.enum import TaskStatus
from app.schemas.todo import CreateTask, UpdateTask, TaskResponse

router = APIRouter(prefix="/tasks", tags=["tasks"])

tasks_db = []

@router.post("/newtask", response_model=TaskResponse)
def create_task(task: CreateTask):
    new_task = {
        "id": len(tasks_db) + 1,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "status": TaskStatus.PENDING,  # default starting status
        "due_at": task.due_at or datetime.now(),  # fallback if None
        "created_at": datetime.now(),
        "started_at": None,
        "completed_at": None
    }

    tasks_db.append(new_task)
    return (new_task)

@router.get('/tasks', response_model=list[TaskResponse])
def get_tasks():
    return(tasks_db)