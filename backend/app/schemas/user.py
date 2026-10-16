"""
User-related Pydantic schemas.

Defines the shape of user data in API requests and responses.
Passwords are never included in response schemas.
"""
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


class UserBase(BaseModel):
    """Base user fields shared across schemas."""
    username: str = Field(..., min_length=3, max_length=80, description="Unique username")
    email: EmailStr = Field(..., description="Email address")
    full_name: str = Field(..., min_length=1, max_length=120, description="Full name")


class UserCreate(UserBase):
    """Schema for creating a new user (admin only)."""
    password: str = Field(..., min_length=8, max_length=128, description="Password (min 8 chars)")
    role_id: int = Field(..., ge=1, description="Role ID (1=admin, 2=dba, 3=viewer)")


class UserUpdate(BaseModel):
    """Schema for updating a user (admin only). All fields optional."""
    email: EmailStr | None = None
    full_name: str | None = Field(None, max_length=120)
    is_active: bool | None = None
    must_change_password: bool | None = None


class UserRoleUpdate(BaseModel):
    """Schema for changing a user's role (admin only)."""
    role_id: int = Field(..., ge=1, description="New role ID")


class PasswordChange(BaseModel):
    """Schema for changing own password."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password (min 8 chars)")


class UserResponse(UserBase):
    """Schema for user data in API responses (no password)."""
    id: int
    role_id: int
    role_name: str = Field(..., description="Role name (admin, dba, viewer)")
    is_active: bool
    must_change_password: bool
    last_login: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    """Paginated list of users."""
    items: list[UserResponse]
    total: int
    page: int
    page_size: int
    pages: int
