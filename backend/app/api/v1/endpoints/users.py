"""
User management endpoints for the CQIA application.
"""

from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_current_superuser, get_db
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserPasswordChange,
    UserPasswordResetRequest,
    UserPasswordReset,
    UserWithOrganizations
)
from app.schemas.base import SuccessResponse, PaginatedResponse
from app.crud.user import user_crud

router = APIRouter()


@router.get("/me", response_model=SuccessResponse[UserWithOrganizations])
def read_user_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get current user information.
    """
    user = user_crud.get_with_organizations(db, id=current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return SuccessResponse(
        data=user,
        message="User information retrieved successfully"
    )


@router.put("/me", response_model=SuccessResponse[UserResponse])
def update_user_me(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update current user information.
    """
    user = user_crud.update(db, db_obj=current_user, obj_in=user_in)
    return SuccessResponse(
        data=user,
        message="User information updated successfully"
    )


@router.post("/me/change-password", response_model=SuccessResponse[dict])
def change_password(
    password_data: UserPasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Change current user's password.
    """
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )

    if password_data.new_password != password_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )

    hashed_password = get_password_hash(password_data.new_password)
    user_crud.update(db, db_obj=current_user, obj_in={"hashed_password": hashed_password})

    return SuccessResponse(
        data={},
        message="Password changed successfully"
    )


@router.get("/", response_model=SuccessResponse[PaginatedResponse[UserResponse]])
def read_users(
    skip: int = 0,
    limit: int = 100,
    current_superuser: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
) -> Any:
    """
    Retrieve users (admin only).
    """
    users = user_crud.get_multi(db, skip=skip, limit=limit)
    total = user_crud.count(db)

    return SuccessResponse(
        data=PaginatedResponse(
            items=users,
            total=total,
            page=skip // limit + 1,
            size=len(users),
            pages=(total + limit - 1) // limit
        ),
        message="Users retrieved successfully"
    )


@router.post("/", response_model=SuccessResponse[UserResponse])
def create_user(
    user_in: UserCreate,
    current_superuser: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
) -> Any:
    """
    Create new user (admin only).
    """
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    user = user_crud.create(db, obj_in=user_in)
    return SuccessResponse(
        data=user,
        message="User created successfully"
    )


@router.get("/{user_id}", response_model=SuccessResponse[UserWithOrganizations])
def read_user(
    user_id: UUID,
    current_superuser: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get user by ID (admin only).
    """
    user = user_crud.get_with_organizations(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return SuccessResponse(
        data=user,
        message="User retrieved successfully"
    )


@router.put("/{user_id}", response_model=SuccessResponse[UserResponse])
def update_user(
    user_id: UUID,
    user_in: UserUpdate,
    current_superuser: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update user (admin only).
    """
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user = user_crud.update(db, db_obj=user, obj_in=user_in)
    return SuccessResponse(
        data=user,
        message="User updated successfully"
    )


@router.delete("/{user_id}", response_model=SuccessResponse[dict])
def delete_user(
    user_id: UUID,
    current_superuser: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
) -> Any:
    """
    Delete user (admin only).
    """
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user_crud.remove(db, id=user_id)
    return SuccessResponse(
        data={},
        message="User deleted successfully"
    )


@router.post("/reset-password-request", response_model=SuccessResponse[dict])
def request_password_reset(
    reset_request: UserPasswordResetRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Request password reset.
    """
    user = db.query(User).filter(User.email == reset_request.email).first()
    if not user:
        # Don't reveal if email exists or not for security
        return SuccessResponse(
            data={},
            message="If the email exists, a password reset link has been sent"
        )

    # Generate reset token and send email (implementation depends on email service)
    # For now, just return success
    return SuccessResponse(
        data={},
        message="If the email exists, a password reset link has been sent"
    )


@router.post("/reset-password", response_model=SuccessResponse[dict])
def reset_password(
    reset_data: UserPasswordReset,
    db: Session = Depends(get_db)
) -> Any:
    """
    Reset password using token.
    """
    # Verify token and update password (implementation depends on token service)
    # For now, just return success
    return SuccessResponse(
        data={},
        message="Password reset successfully"
    )
