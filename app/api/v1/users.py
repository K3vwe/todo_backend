from fastapi import APIRouter, HTTPException
from datetime import datetime
from app.schemas.user import CreateUser, UserUpdate, UserResponse

users = APIRouter(prefix="/users", tags={"users"})

# In Memory User Database
users_db = []

# -----------------------------
# CREATE TASK
# -----------------------------
@users.post('/', response_model=UserResponse)
def create_user(user: CreateUser):
    new_user = {
        "id": len(users_db) + 1,
        "fullname": user.fullname,
        "username": user.username,
        "email": user.email,
        "hashed_password": user.hashed_password,
        "created_at": datetime.now()
    }

    users_db.append(new_user)
    return new_user


# -----------------------------
# GET USER BY ID
# -----------------------------
@users.get('/{user_id}', response_model=UserResponse)
def get_user(user_id: int):
    user = next((user for user in users_db if user["id"] == user_id), None)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

# -----------------------------
# UPDATE TASK
# -----------------------------
@users.patch('/{user_id}', response_model=UserResponse)
def user_update(user_id: int, user_update: UserUpdate):

    #Get user from database
    user = next((user for user in users_db if user["id"] == user_id), None)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update only provided fields
    for key, value in user_update.model_dump(exclude_unset=True).items():
        user[key] = value
        # Optional: auto-set timestamps based on user update
    user["updated_at"] = datetime.now()

    return user


# -----------------------------
# DELETE TASK
# -----------------------------
@users.delete('/{user_id}')
def user_delete(user_id: int):

    # Get the user index from the database
    index = next((i for i, t in enumerate(users_db) if t["id"] == user_id), None)

    if index is None:
        raise HTTPException(status_code=404, detail="User does not exist")
    
    users_db.pop(index)
    return {"Message": "User Deleted Sucessfully", "User_id": user_id}


