"""
User management router — CRUD operations for system users.

All endpoints require admin role.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Role
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserListResponse, PasswordChange, UserRoleUpdate
from app.schemas.auth import Token
from app.dependencies import require_admin, get_current_user
from app.security.password import hash_password, verify_password
from app.exceptions import ResourceNotFoundError, ResourceConflictError, ValidationError

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("", response_model=UserListResponse)
def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: str | None = Query(None, description="Search by username or full name"),
    role_id: int | None = Query(None, description="Filter by role ID"),
    is_active: bool | None = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    """
    List all users with pagination, search, and filtering.

    Requires admin role.
    """
    query = db.query(User)

    # Apply filters
    if search:
        search_lower = f"%{search.lower()}%"
        query = query.filter(
            (User.username.ilike(search_lower)) | (User.full_name.ilike(search_lower))
        )
    if role_id is not None:
        query = query.filter(User.role_id == role_id)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    # Count total for pagination
    total = query.count()

    # Apply pagination
    users = query.order_by(User.username).offset((page - 1) * page_size).limit(page_size).all()

    # Build response with role names
    items = []
    for user in users:
        items.append(UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role_id=user.role_id,
            role_name=user.role.name if user.role else "",
            is_active=user.is_active,
            must_change_password=user.must_change_password,
            last_login=user.last_login,
            created_at=user.created_at,
            updated_at=user.updated_at,
        ))

    return UserListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.post("", response_model=UserResponse, status_code=201)
def create_user(
    body: UserCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    """
    Create a new user account.

    Requires admin role.
    Password is hashed with bcrypt before storage.
    """
    # Check for existing username
    if db.query(User).filter(User.username == body.username).first():
        raise ResourceConflictError(f"Username '{body.username}' already exists")

    # Check for existing email
    if db.query(User).filter(User.email == body.email).first():
        raise ResourceConflictError(f"Email '{body.email}' already exists")

    # Verify role exists
    role = db.query(Role).filter(Role.id == body.role_id).first()
    if role is None:
        raise ValidationError(f"Role ID {body.role_id} does not exist")

    # Create user with hashed password
    user = User(
        username=body.username,
        email=body.email,
        full_name=body.full_name,
        hashed_password=hash_password(body.password),
        role_id=body.role_id,
        is_active=True,
        must_change_password=True,  # Force password change on first login
    )
    db.add(user)
    db.commit()
    db.refresh(user)

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


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    """Get a specific user by ID. Requires admin role."""
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise ResourceNotFoundError(f"User with ID {user_id} not found")

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role_id=user.role_id,
        role_name=user.role.name if user.role else "",
        is_active=user.is_active,
        must_change_password=user.must_change_password,
        last_login=user.last_login,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    body: UserUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    """Update a user's profile. Requires admin role."""
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise ResourceNotFoundError(f"User with ID {user_id} not found")

    # Check email uniqueness if changing
    if body.email and body.email != user.email:
        if db.query(User).filter(User.email == body.email).first():
            raise ResourceConflictError(f"Email '{body.email}' already exists")
        user.email = body.email

    if body.full_name is not None:
        user.full_name = body.full_name
    if body.is_active is not None:
        user.is_active = body.is_active
    if body.must_change_password is not None:
        user.must_change_password = body.must_change_password

    db.commit()
    db.refresh(user)

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


@router.put("/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: int,
    body: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    """Change a user's role. Requires admin role."""
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise ResourceNotFoundError(f"User with ID {user_id} not found")

    role = db.query(Role).filter(Role.id == body.role_id).first()
    if role is None:
        raise ValidationError(f"Role ID {body.role_id} does not exist")

    user.role_id = body.role_id
    db.commit()
    db.refresh(user)

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


@router.post("/{user_id}/reset-password", response_model=UserResponse)
def reset_user_password(
    user_id: int,
    new_password: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    """
    Reset a user's password (admin only).

    The user will be required to change the password on next login.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise ResourceNotFoundError(f"User with ID {user_id} not found")

    user.hashed_password = hash_password(new_password)
    user.must_change_password = True
    db.commit()
    db.refresh(user)

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


@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    """
    Delete a user account (admin only).

    Cannot delete your own account.
    """
    if user_id == current_user["user_id"]:
        raise ValidationError("Cannot delete your own account")

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise ResourceNotFoundError(f"User with ID {user_id} not found")

    db.delete(user)
    db.commit()
    return None


@router.post("/change-password", response_model=dict)
def change_own_password(
    body: PasswordChange,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Change your own password.

    Requires current password for verification.
    """
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if user is None:
        raise ResourceNotFoundError("User not found")

    if not verify_password(body.current_password, user.hashed_password):
        raise ValidationError("Current password is incorrect")

    user.hashed_password = hash_password(body.new_password)
    user.must_change_password = False
    db.commit()

    return {"message": "Password changed successfully"}
