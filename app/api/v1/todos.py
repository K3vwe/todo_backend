from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone
from app.models.enum import TaskStatus, TaskPriority
from app.schemas.todo import CreateTask, UpdateTask, TaskResponse
from app.models.tasks import Task
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from sqlalchemy import select, insert
from uuid import UUID

task_router = APIRouter(prefix="/tasks", tags=["tasks"])

# -----------------------------
# CREATE TASK
# -----------------------------
@task_router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(task: CreateTask, db: AsyncSession = Depends(get_db)):

    # Convert Optional Date and Time into Separate Date and Time
    due_date = task.due_at.date() if task.due_at else None
    due_time = task.due_at.time() if task.due_at else None

    new_task = {
        "title": task.title,
        "description": task.description,
        "priority": task.priority or TaskPriority.MEDIUM.value,
        "status": TaskStatus.PENDING.value,  # default starting status
        "due_at": task.due_at,  # fallback if None
        "due_date":due_date,
        "due_time":due_time,
        "created_at": datetime.now(),
        "started_at": None,
        "completed_at": None
    }

    task_instance = Task(**new_task)

    db.add(task_instance)
    await db.commit()
    await db.refresh(task_instance)

# -----------------------------
# GET ALL TASKS
# -----------------------------
@task_router.get('/', response_model=list[TaskResponse])
async def get_tasks(db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(Task))
    tasks = result.scalars().all()
    return(tasks)

# -----------------------------
# GET TASK BY ID
# -----------------------------
@task_router.get('/{task_id}', response_model=TaskResponse)
async def get_task(task_id: UUID, db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalars().first()
    # task = next((t for t in tasks_db if t["id"] == task_id), None)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# -----------------------------
# UPDATE TASK
# -----------------------------
@task_router.patch('/{task_id}', response_model=TaskResponse)
async def update_task(task_id: UUID,  updates: UpdateTask, db: AsyncSession = Depends(get_db)):

    # Get tasks from database 
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalars().first()

    # task = next((task for task in tasks_db if task["id"] == task_id), None)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update only provided fields
    update_data = updates.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)  # ✅ correct attribute access

    # Optional: auto-set timestamps based on status
    if "status" in update_data:
        if task.status == TaskStatus.IN_PROGRESS:
            task.started_at = datetime.now(timezone.utc)
        elif task.status == TaskStatus.COMPLETED:
            task.completed_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(task)

    return task

# -----------------------------
# DELETE TASK
# -----------------------------
@task_router.delete('/{task_id}')
async def delete_task(task_id: UUID, db: AsyncSession = Depends(get_db)):

    # Get tasks from database 
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalars().first()

    # index = next((i for i, t in enumerate(tasks_db) if t["id"] == task_id), None)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    # Delete the object
    await db.delete(task)
    await db.commit()

    return {"message": "Task deleted successfully", "task_id": task_id}