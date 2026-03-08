from fastapi import APIRouter, HTTPException, Depends, status
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.schemas.user import CreateUser, UserUpdate, UserResponse
from app.models.users import User
from app.core.database import get_db
from app.auth.auth_dependencies import get_current_user
from app.auth.utils import get_password_hash

# Router setup
users = APIRouter(prefix="/users", tags=["users"])

# -----------------------------
# CREATE USER
# -----------------------------
@users.post('/', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: CreateUser, db: AsyncSession = Depends(get_db)):
    # Check if username/email already exists
    existing_user = await db.execute(
        select(User).where((User.username == user.username) | (User.email == user.email))
    )
    if existing_user.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username or email already exists")

    # Hash password server-side
    hashed_password = get_password_hash(user.password)
    
    user_instance = User(
        fullname=user.fullname,
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )

    # Just add and commit — no db.begin()
    db.add(user_instance)
    await db.commit()           # commit the transaction
    await db.refresh(user_instance)  # refresh to get DB-generated fields (id, timestamps)

    return user_instance

# -----------------------------
# GET USER BY ID
# -----------------------------
@users.get('/{user_id}', response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

# -----------------------------
# UPDATE USER (ownership check)
# -----------------------------
@users.patch('/{user_id}', response_model=UserResponse)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    if str(current_user.id) != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this user")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_update.model_dump(exclude_unset=True)
    if 'password' in update_data:
        update_data['hashed_password'] = get_password_hash(update_data.pop('password'))

    for key, value in update_data.items():
        setattr(user, key, value)

    await db.commit()       # commit changes
    await db.refresh(user)  # refresh to reflect updated fields
    return user


# -----------------------------
# DELETE USER (ownership check)
# -----------------------------
@users.delete('/{user_id}', status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    if str(current_user.id) != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this user")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(user)
    await db.commit()  # commit the deletion

    return {"detail": f"User {user_id} deleted successfully"}




# from fastapi import APIRouter, HTTPException, Depends
# from datetime import datetime
# from app.schemas.user import CreateUser, UserUpdate, UserResponse
# from sqlalchemy.ext.asyncio import AsyncSession
# from app.models.users import User
# from app.core.database import get_db
# from sqlalchemy import select

# users = APIRouter(prefix="/users", tags={"users"})

# # -----------------------------
# # CREATE USER
# # -----------------------------
# @users.post('/', response_model=UserResponse, status_code=201)
# async def create_user(user: CreateUser, db: AsyncSession = Depends(get_db)):
#     new_user = {
#         "fullname": user.fullname,
#         "username": user.username,
#         "email": user.email,
#         "hashed_password": user.hashed_password,
#     }
#     user_instance = User(**new_user)

#     async with db.begin():
#         db.add(user_instance)
#         await db.flush()

#     await db.refresh(user_instance)

#     return user_instance

# # -----------------------------
# # GET USER BY ID
# # -----------------------------
# @users.get('/{user_id}', response_model=UserResponse)
# async def get_user(user_id: str, db: AsyncSession = Depends(get_db)):

#     async with db.begin():
#         # Get User obj from db
#         user = (await db.execute(select(User).where(User.id==user_id))).scalar_one_or_none()

#         # check if user exists
#         if user is None:
#             raise HTTPException(status_code=404, detail="User does not exist")
        
#         return user
    
    
# # -----------------------------
# # UPDATE USER
# # -----------------------------
# @users.patch('/{user_id}', response_model=UserResponse, status_code = 200)
# async def user_update(user_id: str, user_update: UserUpdate, db: AsyncSession = Depends(get_db)):

#     async with db.begin():
#         # Get User obj from db
#         user = (await db.execute(select(User).where(User.id==user_id))).scalar_one_or_none()

#         # check if user exists
#         if user is None:
#             raise HTTPException(status_code=404, detail="User does not exist")
        
#         # Update only provided fields
#         for key, value in user_update.model_dump(exclude_unset=True).items():
#             setattr(user, key, value)
        
#         return user

# # -----------------------------
# # DELETE USER
# # -----------------------------
# @users.delete('/{user_id}')
# async def user_delete(user_id: str, db: AsyncSession=Depends(get_db)):

#     # Delete user from db transaction
#     async with db.begin():
#         # Get User obj from db
#         user = (await db.execute(select(User).where(User.id==user_id))).scalar_one_or_none()

#         # check if user exists
#         if user is None:
#             raise HTTPException(status_code=404, detail="User does not exist")
        
#         # delete user from db
#         await db.delete(user)

#     return {"detail": f"User {user_id} deleted successfully"}