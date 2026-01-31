from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from app.schemas.user import CreateUser, UserUpdate, UserResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.users import User
from app.core.database import get_db
from sqlalchemy import select

users = APIRouter(prefix="/users", tags={"users"})

# -----------------------------
# CREATE USER
# -----------------------------
@users.post('/', response_model=UserResponse, status_code=201)
async def create_user(user: CreateUser, db: AsyncSession = Depends(get_db)):
    new_user = {
        "fullname": user.fullname,
        "username": user.username,
        "email": user.email,
        "hashed_password": user.hashed_password,
    }
    user_instance = User(**new_user)

    async with db.begin():
        db.add(user_instance)
        await db.flush()

    await db.refresh(user_instance)

    return user_instance

# -----------------------------
# GET USER BY ID
# -----------------------------
@users.get('/{user_id}', response_model=UserResponse)
async def get_user(user_id: str, db: AsyncSession = Depends(get_db)):

    async with db.begin():
        # Get User obj from db
        user = (await db.execute(select(User).where(User.id==user_id))).scalar_one_or_none()

        # check if user exists
        if user is None:
            raise HTTPException(status_code=404, detail="User does not exist")
        
        return user
    
    
# -----------------------------
# UPDATE TASK
# -----------------------------
@users.patch('/{user_id}', response_model=UserResponse, status_code = 200)
async def user_update(user_id: str, user_update: UserUpdate, db: AsyncSession = Depends(get_db)):

    async with db.begin():
        # Get User obj from db
        user = (await db.execute(select(User).where(User.id==user_id))).scalar_one_or_none()

        # check if user exists
        if user is None:
            raise HTTPException(status_code=404, detail="User does not exist")
        
        # Update only provided fields
        for key, value in user_update.model_dump(exclude_unset=True).items():
            setattr(user, key, value)
        
        return user

# -----------------------------
# DELETE USER
# -----------------------------
@users.delete('/{user_id}')
async def user_delete(user_id: str, db: AsyncSession=Depends(get_db)):

    # Delete user from db transaction
    async with db.begin():
        # Get User obj from db
        user = (await db.execute(select(User).where(User.id==user_id))).scalar_one_or_none()

        # check if user exists
        if user is None:
            raise HTTPException(status_code=404, detail="User does not exist")
        
        # delete user from db
        await db.delete(user)

    return {"detail": f"User {user_id} deleted successfully"}



