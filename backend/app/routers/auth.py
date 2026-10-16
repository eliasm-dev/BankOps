"""
Authentication router — login, logout, refresh, and current user info.

Endpoints:
    POST /api/auth/login    — Authenticate and get tokens
    POST /api/auth/logout   — Invalidate current token
    POST /api/auth/refresh  — Get new access token
    GET  /api/auth/me       — Get current user profile
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import LoginRequest, Token, RefreshRequest
from app.schemas.user import UserResponse
from app.services.auth_service import authenticate_user, logout_user, refresh_access_token
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/login", response_model=Token, status_code=200)
def login(request: Request, body: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate with username and password.

    Returns a JWT access token and refresh token on success.
    Returns 401 on invalid credentials.
    """
    ip = request.client.host if request.client else ""
    return authenticate_user(db, body.username, body.password, ip)


@router.post("/logout", status_code=200)
def logout(
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Logout — invalidates the current access token.

    The token is added to a blacklist and cannot be used again.
    """
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else ""
    logout_user(db, token, current_user["user_id"])
    return {"message": "Logged out successfully"}


@router.post("/refresh", response_model=Token)
def refresh(body: RefreshRequest, db: Session = Depends(get_db)):
    """
    Exchange a valid refresh token for a new access token.

    The refresh token remains valid until it expires.
    """
    return refresh_access_token(db, body.refresh_token)


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get the profile of the currently authenticated user.

    Requires a valid access token.
    """
    from app.models import User
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if user is None:
        from app.exceptions import ResourceNotFoundError
        raise ResourceNotFoundError("User not found")

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role_id=user.role_id,
        role_name=user.role.name,
        is_active=user.is_active,
        must_change_password=user.must_change_password,
        last_login=user.last_login,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )
