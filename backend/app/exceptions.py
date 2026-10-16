"""
Centralized error handling for BankOps API.

All custom exceptions and their FastAPI handlers live here
so every endpoint returns consistent error responses.
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


# ── Custom Exceptions ─────────────────────────────────────────

class BankOpsException(Exception):
    """Base exception for all BankOps errors."""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AuthenticationError(BankOpsException):
    """Invalid credentials or token."""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class AuthorizationError(BankOpsException):
    """Insufficient permissions."""
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)


class ResourceNotFoundError(BankOpsException):
    """Requested resource does not exist."""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class ResourceConflictError(BankOpsException):
    """Resource already exists or conflicts."""
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message, status.HTTP_409_CONFLICT)


class ValidationError(BankOpsException):
    """Custom validation error."""
    def __init__(self, message: str = "Validation error"):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY)


# ── Error Response Format ─────────────────────────────────────

def error_response(message: str, status_code: int, details: dict | None = None) -> JSONResponse:
    """Build a consistent error response body."""
    body = {
        "error": {
            "message": message,
            "status_code": status_code,
        }
    }
    if details:
        body["error"]["details"] = details
    return JSONResponse(status_code=status_code, content=body)


# ── Exception Handlers ────────────────────────────────────────

async def bankops_exception_handler(request: Request, exc: BankOpsException):
    """Handle all custom BankOps exceptions."""
    return error_response(exc.message, exc.status_code)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors with detailed messages."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        })
    return error_response(
        "Request validation failed",
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        details={"errors": errors},
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Catch-all handler for unexpected errors."""
    return error_response(
        "An unexpected error occurred",
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
