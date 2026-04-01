# app/api/v1/tasks.py
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone
from typing import Annotated, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.todo import CreateTask, UpdateTask, TaskResponse
from app.models.tasks import Task
from app.models import User
from app.models.enum import TaskStatus, TaskPriority
from app.core.database import get_db
from app.auth.auth_dependencies import get_current_user

task_router = APIRouter(prefix="/tasks", tags=["tasks"])

# -----------------------------
# CREATE TASK
# -----------------------------
@task_router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(
    task: CreateTask,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    due_date, due_time = None, None
    if task.due_at:
        due_date = task.due_at.date()
        due_time = task.due_at.time()

    task_instance = Task(
        title=task.title,
        description=task.description,
        priority=task.priority or TaskPriority.MEDIUM,
        status=TaskStatus.PENDING,
        due_at=task.due_at,
        due_date=due_date,
        due_time=due_time,
        user_id=current_user.id,
        started_at=None,
        completed_at=None,
    )

    db.add(task_instance)
    await db.commit()
    await db.refresh(task_instance)
    return task_instance


# -----------------------------
# GET ALL TASKS (ONLY USER'S TASKS)
# -----------------------------
@task_router.get("/", response_model=list[TaskResponse])
async def get_tasks(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    skip: int = 0,
    limit: int = 100,
):
    query = select(Task).where(Task.user_id == current_user.id)
    if status:
        query = query.where(Task.status == status)
    if priority:
        query = query.where(Task.priority == priority)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

# -----------------------------
# GET TASK BY ID
# -----------------------------
@task_router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# -----------------------------
# UPDATE TASK
# -----------------------------
@task_router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    updates: UpdateTask,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = updates.model_dump(exclude_unset=True)
    now = datetime.now(timezone.utc)

    # -----------------------------
    # Handle timestamps
    # -----------------------------
    if "started_at" in update_data:
        task.started_at = update_data["started_at"] or task.started_at

    if "completed_at" in update_data:
        if update_data["completed_at"] is None:
            # Clear completed_at without touching started_at
            task.completed_at = None
        else:
            if not task.started_at:
                task.started_at = now
            task.completed_at = update_data["completed_at"]
            if task.completed_at < task.started_at:
                task.completed_at = task.started_at

    if "due_at" in update_data and update_data["due_at"]:
        task.due_at = update_data["due_at"]
        task.due_date = update_data["due_at"].date()
        task.due_time = update_data["due_at"].time()

    # Apply other updates
    for key, value in update_data.items():
        if key not in ["started_at", "completed_at", "due_at"]:
            setattr(task, key, value)

    # -----------------------------
    # Auto-set status based on timestamps
    # -----------------------------
    if task.completed_at:
        task.status = TaskStatus.COMPLETED
    elif task.started_at:
        task.status = TaskStatus.IN_PROGRESS
    else:
        task.status = TaskStatus.PENDING

    await db.commit()
    await db.refresh(task)
    return task


# -----------------------------
# DELETE TASK
# -----------------------------
@task_router.delete("/{task_id}")
async def delete_task(
    task_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    await db.delete(task)
    await db.commit()
    return {"message": "Task deleted successfully", "task_id": task_id}