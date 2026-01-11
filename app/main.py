from fastapi import FastAPI
from app.api.v1 import todos

app = FastAPI()

app.include_router(todos.router, prefix="/api/v1")