"""
Authentication-related Pydantic schemas.

Defines the shape of login requests, token responses,
and token payloads.
"""
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Login request — username and password."""
    username: str = Field(..., min_length=1, max_length=80, description="Username")
    password: str = Field(..., min_length=1, max_length=128, description="Password")


class Token(BaseModel):
    """
    Token response — returned on successful login or refresh.

    Contains both access and refresh tokens.
    """
    access_token: str = Field(..., description="Short-lived JWT access token")
    refresh_token: str = Field(..., description="Long-lived JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type (always 'bearer')")
    expires_in: int = Field(..., description="Access token expiry in seconds")


class TokenPayload(BaseModel):
    """
    Decoded JWT payload — used internally by dependencies.

    Not directly exposed in API responses.
    """
    sub: str = Field(..., description="Subject (user ID as string)")
    username: str = Field(..., description="Username")
    role: str = Field(..., description="User role")
    type: str = Field(..., description="Token type")
    exp: int = Field(..., description="Expiry timestamp")


class RefreshRequest(BaseModel):
    """Refresh token request."""
    refresh_token: str = Field(..., description="Valid refresh token")
