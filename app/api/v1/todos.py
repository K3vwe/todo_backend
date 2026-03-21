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
# app/api/v1/todos.py
@task_router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(
    task: CreateTask,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    # Better way to handle due_at
    due_date = None
    due_time = None
    if task.due_at:
        due_date = task.due_at.date()
        due_time = task.due_at.time()

    task_instance = Task(
        title=task.title,
        description=task.description,
        priority=task.priority or TaskPriority.MEDIUM,  # Use enum directly
        status=TaskStatus.PENDING,  # Use enum directly
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
# app/api/v1/todos.py
from typing import Optional

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

    # Handle status changes
    if "status" in update_data:
        old_status = task.status
        new_status = update_data["status"]
        
        # Set timestamps based on status change
        if new_status == TaskStatus.IN_PROGRESS and old_status != TaskStatus.IN_PROGRESS:
            task.started_at = datetime.now(timezone.utc)
        elif new_status == TaskStatus.COMPLETED and old_status != TaskStatus.COMPLETED:
            task.completed_at = datetime.now(timezone.utc)
            # Optionally, if task is completed, ensure started_at is set
            if not task.started_at:
                task.started_at = datetime.now(timezone.utc)
        elif new_status == TaskStatus.PENDING:
            # Reset timestamps if going back to pending
            task.started_at = None
            task.completed_at = None

    # Handle due_at updates
    if "due_at" in update_data and update_data["due_at"]:
        task.due_date = update_data["due_at"].date()
        task.due_time = update_data["due_at"].time()

    # Apply all updates
    for key, value in update_data.items():
        if key not in ["status", "due_at"]:  # Already handled
            setattr(task, key, value)

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