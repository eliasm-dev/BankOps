"""
FastAPI dependencies for authentication and authorization.

These dependencies are used as route parameters to enforce
authentication and role-based access control.

Usage:
    @router.get("/admin-only")
    def admin_route(current_user: dict = Depends(require_role("admin"))):
        ...
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.security.jwt import verify_token
from app.exceptions import AuthenticationError, AuthorizationError

# HTTPBearer extracts the Bearer token from the Authorization header
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict:
    """
    Dependency that extracts and validates the JWT from the request.

    Returns a dict with user_id, username, and role.
    Raises AuthenticationError if token is missing or invalid.
    """
    if credentials is None:
        raise AuthenticationError("Authentication required — no token provided")

    token = credentials.credentials
    payload = verify_token(token, expected_type="access")

    return {
        "user_id": int(payload["sub"]),
        "username": payload["username"],
        "role": payload["role"],
    }


def require_role(*allowed_roles: str):
    """
    Factory that creates a dependency requiring specific roles.

    Usage:
        @router.post("/databases")
        def create_db(user: dict = Depends(require_role("admin", "dba"))):
            ...

    Raises AuthenticationError if user not logged in.
    Raises AuthorizationError if user's role is not in allowed_roles.
    """
    async def role_checker(
        current_user: dict = Depends(get_current_user),
    ) -> dict:
        if current_user["role"] not in allowed_roles:
            raise AuthorizationError(
                f"Access denied — requires one of: {', '.join(allowed_roles)}"
            )
        return current_user
    return role_checker


# Convenience role dependencies (used across routers)
require_admin = require_role("admin")
require_dba = require_role("admin", "dba")
require_any = require_role("admin", "dba", "viewer")
