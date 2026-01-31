from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional
from uuid import UUID
# Base schema shared across operations
class UserBase(BaseModel):
    username: str = Field(..., max_length=50)
    fullname: str = Field(..., max_length=50)
    email: EmailStr

# Schema used when creating a user
class CreateUser(UserBase):
    profile_url: Optional[str] = None
    hashed_password: str = Field(min_length=8)

# Schema used when returning user data (hides password)
class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

# Schema used when updating a user (all fields optional)
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, max_length=50)
    fullname: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = None
    hashed_password: Optional[str] = Field(None, min_length=6)
    profile_url: Optional[str] = None