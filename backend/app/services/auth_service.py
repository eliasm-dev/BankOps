"""
Authentication service — handles login, logout, token refresh.

Separates business logic from HTTP route handlers.
"""
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models import User, LoginHistory, AuditLog
from app.security.password import verify_password
from app.security.jwt import (
    create_access_token, create_refresh_token,
    verify_token, blacklist_token, extract_jti,
)
from app.exceptions import AuthenticationError, ResourceNotFoundError


def authenticate_user(db: Session, username: str, password: str, ip_address: str = "") -> dict:
    """
    Authenticate a user with username and password.

    Returns a token dict on success.
    Raises AuthenticationError on failure.
    Records login attempt in login_history and audit_logs.
    """
    # Find user by username
    user = db.query(User).filter(User.username == username).first()

    # Verify password (constant-time comparison via bcrypt)
    if user is None or not verify_password(password, user.hashed_password):
        # Record failed attempt
        record_login_attempt(db, username, False, "Invalid username or password", ip_address)
        raise AuthenticationError("Invalid username or password")

    # Check if account is active
    if not user.is_active:
        record_login_attempt(db, username, False, "Account is disabled", ip_address)
        raise AuthenticationError("Account is disabled — contact administrator")

    # Update last login timestamp
    user.last_login = datetime.now(timezone.utc)

    # Record successful login
    record_login_attempt(db, username, True, "", ip_address)

    # Create tokens
    access_token = create_access_token(user.id, user.username, user.role.name)
    refresh_token = create_refresh_token(user.id)

    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 30 * 60,  # 30 minutes in seconds
    }


def logout_user(db: Session, token: str, user_id: int):
    """
    Logout a user by blacklisting their token.

    The token's JTI is added to the blacklist, making it
    immediately invalid for future requests.
    """
    jti = extract_jti(token)
    if jti:
        blacklist_token(jti)

    # Audit log
    audit = AuditLog(
        user_id=user_id,
        action="user.logout",
        resource_type="user",
        resource_id=str(user_id),
        description="User logged out",
    )
    db.add(audit)
    db.commit()


def refresh_access_token(db: Session, refresh_token: str) -> dict:
    """
    Exchange a valid refresh token for a new access token.

    Raises AuthenticationError if refresh token is invalid.
    """
    payload = verify_token(refresh_token, expected_type="refresh")
    user_id = int(payload["sub"])

    # Verify user still exists and is active
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise AuthenticationError("User not found")
    if not user.is_active:
        raise AuthenticationError("Account is disabled")

    # Create new access token
    access_token = create_access_token(user.id, user.username, user.role.name)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,  # reuse the same refresh token
        "token_type": "bearer",
        "expires_in": 30 * 60,
    }


def record_login_attempt(
    db: Session, username: str, success: bool, failure_reason: str, ip_address: str
):
    """Record a login attempt in the login_history table."""
    history = LoginHistory(
        username=username,
        success=success,
        failure_reason=failure_reason if not success else "",
        ip_address=ip_address,
        user_agent="BankOps API",
    )
    db.add(history)
    db.commit()
