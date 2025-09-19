"""
CRUD operations for User model.
"""

from typing import Any, Dict, Optional, Union, List
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser:
    """CRUD operations for User model."""

    def get(self, db: Session, *, id: UUID) -> Optional[User]:
        """Get user by ID."""
        return db.query(User).filter(User.id == id).first()

    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """Get user by email."""
        return db.query(User).filter(User.email == email).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[User]:
        """Get multiple users."""
        return db.query(User).offset(skip).limit(limit).all()

    def get_with_organizations(self, db: Session, *, id: UUID) -> Optional[Dict[str, Any]]:
        """Get user with organization information."""
        user = self.get(db, id=id)
        if not user:
            return None

        # This would include organization relationships
        # For now, return basic user info
        return {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "organizations": []  # Would be populated with actual org data
        }

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """Create new user."""
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            is_active=obj_in.is_active,
            is_superuser=obj_in.is_superuser,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        """Update user."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        for field in update_data:
            if field == "password" and update_data["password"]:
                hashed_password = get_password_hash(update_data["password"])
                setattr(db_obj, "hashed_password", hashed_password)
            else:
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: UUID) -> User:
        """Remove user."""
        obj = db.query(User).get(id)
        db.delete(obj)
        db.commit()
        return obj

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        """Authenticate user."""
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: User) -> bool:
        """Check if user is active."""
        return user.is_active

    def is_superuser(self, user: User) -> bool:
        """Check if user is superuser."""
        return user.is_superuser

    def count(self, db: Session) -> int:
        """Count total users."""
        return db.query(User).count()


user_crud = CRUDUser()
