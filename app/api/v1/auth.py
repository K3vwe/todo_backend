# app/api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi.security import OAuth2PasswordRequestForm
from app.models.users import User
from app.core.database import get_db
from app.auth.utils import verify_password, create_access_token
from app.schemas.user import UserResponse
from app.schemas.auth import TokenResponse

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    # Get user from database
    user = (await db.execute(select(User).where(User.username == form_data.username))).scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    # Return the same structure as signup
    return {
        "user": user,
        "access_token": access_token,
        "token_type": "bearer"
    }