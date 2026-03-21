# app/api/v1/users.py
from fastapi import APIRouter, HTTPException, Depends, status
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.schemas.user import CreateUser, UserUpdate, UserResponse, UserWithToken
from app.models.users import User
from app.core.database import get_db
from app.auth.auth_dependencies import get_current_user  # This should work now
from app.auth.utils import get_password_hash, create_access_token
import uuid  # Add this

# Router setup
users = APIRouter(prefix="/users", tags=["users"])

# -----------------------------
# CREATE USER (returns token)
# -----------------------------
@users.post('/', response_model=UserWithToken, status_code=status.HTTP_201_CREATED)
async def create_user(user: CreateUser, db: AsyncSession = Depends(get_db)):
    # Check if username/email already exists
    existing_user = await db.execute(
        select(User).where((User.username == user.username) | (User.email == user.email))
    )
    if existing_user.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username or email already exists")

    # Hash password server-side
    hashed_password = get_password_hash(user.password)
    
    # Create user instance with all fields
    user_instance = User(
        fullname=user.fullname,
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        profile_url=user.profile_url
    )

    # Add and commit the new user
    db.add(user_instance)
    await db.commit()
    await db.refresh(user_instance)

    # Create access token for the new user
    access_token = create_access_token(data={"sub": str(user_instance.id)})
    
    # Return user data with token
    return {
        "user": user_instance,
        "access_token": access_token,
        "token_type": "bearer"
    }

# -----------------------------
# GET USER BY ID
# -----------------------------
@users.get('/{user_id}', response_model=UserResponse)
async def get_user(
    user_id: uuid.UUID,  # Changed from str to uuid.UUID
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    # Only allow fetching your own user record
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this user")
    
    user = await db.get(User, user_id)  # Simpler way to get by ID
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

# -----------------------------
# UPDATE USER (ownership check)
# -----------------------------
@users.patch('/{user_id}', response_model=UserResponse)
async def update_user(
    user_id: uuid.UUID,  # Changed from str to uuid.UUID
    user_update: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this user")

    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_update.model_dump(exclude_unset=True)
    if 'password' in update_data:
        update_data['hashed_password'] = get_password_hash(update_data.pop('password'))

    for key, value in update_data.items():
        setattr(user, key, value)

    await db.commit()
    await db.refresh(user)
    return user

# -----------------------------
# DELETE USER (ownership check)
# -----------------------------
@users.delete('/{user_id}', status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: uuid.UUID,  # Changed from str to uuid.UUID
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this user")

    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(user)
    await db.commit()

    return {"detail": f"User {user_id} deleted successfully"}