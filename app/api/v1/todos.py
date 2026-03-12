from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone
from typing import Annotated
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

    due_date = task.due_at.date() if task.due_at else None
    due_time = task.due_at.time() if task.due_at else None

    task_instance = Task(
        title=task.title,
        description=task.description,
        priority=task.priority or TaskPriority.MEDIUM.value,
        status=TaskStatus.PENDING.value,
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
):

    result = await db.execute(
        select(Task).where(Task.user_id == current_user.id)
    )

    tasks = result.scalars().all()
    return tasks


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
        select(Task).where(
            Task.id == task_id,
            Task.user_id == current_user.id
        )
    )

    task = result.scalar_one_or_none()

    if task is None:
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
        select(Task).where(
            Task.id == task_id,
            Task.user_id == current_user.id
        )
    )

    task = result.scalar_one_or_none()

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = updates.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(task, key, value)

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
@task_router.delete("/{task_id}")
async def delete_task(
    task_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):

    result = await db.execute(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == current_user.id
        )
    )

    task = result.scalar_one_or_none()

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    await db.delete(task)
    await db.commit()

    return {
        "message": "Task deleted successfully",
        "task_id": task_id
    }