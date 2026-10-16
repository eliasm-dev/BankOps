"""
JWT token creation, verification, and blacklist management.

Access tokens are short-lived (30 min default).
Refresh tokens are longer-lived (7 days default).
Token blacklist enables immediate logout.
"""
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from jose import JWTError, jwt

from app.config import settings


# In-memory token blacklist (use Redis in production)
_token_blacklist: set[str] = set()


def create_access_token(user_id: int, username: str, role: str) -> str:
    """
    Create a short-lived JWT access token.

    The token contains the user's ID, username, and role.
    Expires after ACCESS_TOKEN_EXPIRE_MINUTES.
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),          # subject (user ID)
        "username": username,
        "role": role,
        "type": "access",
        "iat": now,                    # issued at
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
        "jti": str(uuid4()),           # unique token ID for blacklisting
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(user_id: int) -> str:
    """
    Create a long-lived JWT refresh token.

    Used to obtain a new access token without re-login.
    Expires after REFRESH_TOKEN_EXPIRE_DAYS.
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "iat": now,
        "exp": now + timedelta(days=settings.refresh_token_expire_days),
        "jti": str(uuid4()),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def verify_token(token: str, expected_type: str = "access") -> dict:
    """
    Verify a JWT token and return its payload.

    Raises AuthenticationError if token is invalid, expired,
    blacklisted, or wrong type.
    """
    from app.exceptions import AuthenticationError

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError:
        raise AuthenticationError("Invalid or expired token")

    # Check token type
    if payload.get("type") != expected_type:
        raise AuthenticationError(f"Invalid token type — expected {expected_type}")

    # Check blacklist
    if payload.get("jti") in _token_blacklist:
        raise AuthenticationError("Token has been revoked")

    return payload


def blacklist_token(jti: str):
    """Add a token's JTI to the blacklist (logout)."""
    _token_blacklist.add(jti)


def is_token_blacklisted(jti: str) -> bool:
    """Check if a token is blacklisted."""
    return jti in _token_blacklist


def extract_jti(token: str) -> str | None:
    """Extract JTI from a token without full verification."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            options={"verify_exp": False},
        )
        return payload.get("jti")
    except JWTError:
        return None
