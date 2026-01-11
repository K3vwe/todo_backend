from fastapi import APIRouter, HTTPException
from datetime import datetime
from app.models.enum import TaskStatus
from app.schemas.todo import CreateTask, UpdateTask, TaskResponse

router = APIRouter(prefix="/tasks", tags=["tasks"])

# In memory database
tasks_db = []


# -----------------------------
# CREATE TASK
# -----------------------------
@router.post("/", response_model=TaskResponse, status_code=201)
def create_task(task: CreateTask):
    new_task = {
        "id": len(tasks_db) + 1,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "status": TaskStatus.PENDING.value,  # default starting status
        "due_at": task.due_at or datetime.now(),  # fallback if None
        "created_at": datetime.now(),
        "started_at": None,
        "completed_at": None
    }

    tasks_db.append(new_task)
    return (new_task)

# -----------------------------
# GET ALL TASKS
# -----------------------------
@router.get('/', response_model=list[TaskResponse])
def get_tasks():
    return(tasks_db)

# -----------------------------
# GET TASK BY ID
# -----------------------------
@router.get('/{task_id}', response_model=TaskResponse)
def get_task(task_id: int):
    task = next((t for t in tasks_db if t["id"] == task_id), None)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# -----------------------------
# UPDATE TASK
# -----------------------------
@router.patch('/{task_id}', response_model=TaskResponse)
def update_task(task_id: int, updates: UpdateTask):
    # Get tasks from database 
    task = next((task for task in tasks_db if task["id"] == task_id), None)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update only provided fields
    for key, value in updates.model_dump(exclude_unset=True).items():
        task[key] = value

    # Optional: auto-set timestamps based on status
    if "status" in updates.model_dump(exclude_unset=True):
        if task["status"] == TaskStatus.IN_PROGRESS.value:
            task["started_at"] = datetime.now() 
        elif task["status"] == TaskStatus.COMPLETED.value:
            task["completed_at"] = datetime.now()

    return task

# -----------------------------
# DELETE TASK
# -----------------------------
@router.delete('/{task_id}')
def delete_task(task_id: int):
    index = next((i for i, t in enumerate(tasks_db) if t["id"] == task_id), None)

    if index is None:
        raise HTTPException(status_code=404, detail="Task not found")

    tasks_db.pop(index)
    return {"message": "Task deleted successfully", "task_id": task_id}