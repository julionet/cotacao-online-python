import uuid

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)


class UserResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    is_active: bool

    model_config = {"from_attributes": True}
