from fastapi import APIRouter
from app.api.v1.todos import task_router
from app.api.v1.users import users

v1_router = APIRouter(prefix='/v1')

v1_router.include_router(task_router)
v1_router.include_router(users)