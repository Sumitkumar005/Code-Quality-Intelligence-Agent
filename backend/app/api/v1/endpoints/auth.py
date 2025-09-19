"""
Authentication endpoints for the CQIA application.
"""

from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.schemas.user import UserLogin, UserResponse
from app.schemas.base import SuccessResponse

router = APIRouter()


@router.post("/login", response_model=SuccessResponse[dict])
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email},
        expires_delta=access_token_expires
    )

    return SuccessResponse(
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserResponse.from_orm(user).dict()
        },
        message="Login successful"
    )


@router.post("/login/json", response_model=SuccessResponse[dict])
def login_json(
    login_data: UserLogin,
    db: Session = Depends(get_db)
) -> Any:
    """
    JSON-based login endpoint.
    """
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email},
        expires_delta=access_token_expires
    )

    return SuccessResponse(
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserResponse.from_orm(user).dict()
        },
        message="Login successful"
    )


@router.post("/refresh-token", response_model=SuccessResponse[dict])
def refresh_access_token(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Refresh access token.
    """
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": current_user.id, "email": current_user.email},
        expires_delta=access_token_expires
    )

    return SuccessResponse(
        data={
            "access_token": access_token,
            "token_type": "bearer"
        },
        message="Token refreshed successfully"
    )


@router.post("/logout", response_model=SuccessResponse[dict])
def logout(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Logout endpoint (client-side token invalidation).
    """
    # In a stateless JWT system, logout is handled client-side
    # by removing the token from storage
    return SuccessResponse(
        data={},
        message="Logged out successfully"
    )
