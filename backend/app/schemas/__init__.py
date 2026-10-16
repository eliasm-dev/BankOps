"""
Pydantic schemas package.

Schemas define the shape of request/response data and provide
automatic validation for all API endpoints.
"""
from app.schemas.auth import Token, TokenPayload, LoginRequest, RefreshRequest
from app.schemas.user import (
    UserCreate, UserUpdate, UserResponse, UserListResponse,
    PasswordChange, UserRoleUpdate,
)

__all__ = [
    "Token",
    "TokenPayload",
    "LoginRequest",
    "RefreshRequest",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserListResponse",
    "PasswordChange",
    "UserRoleUpdate",
]
