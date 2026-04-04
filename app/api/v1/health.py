from fastapi import APIRouter

health_router = APIRouter()

@health_router.get("/health")
def health():
    return {"status": "ok"}

@health_router.get("/ready")
def ready():
    # You can later check DB, cache, etc.
    return {"status": "ready"}