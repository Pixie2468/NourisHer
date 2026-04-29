from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime
import uuid


class UserRegister(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    password: str
    symptoms: list[str] = []

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

    @field_validator("username")
    @classmethod
    def username_valid(cls, v):
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        if not v.replace("_", "").isalnum():
            raise ValueError("Username can only contain letters, numbers, underscores")
        return v.lower()


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: "UserOut"


class UserOut(BaseModel):
    id: uuid.UUID
    email: str
    username: str
    full_name: str
    avatar_url: Optional[str]
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ChangePassword(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class RefreshTokenRequest(BaseModel):
    refresh_token: str
