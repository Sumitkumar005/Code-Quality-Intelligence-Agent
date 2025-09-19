"""
Base service class for the CQIA application.
"""

from typing import Generic, TypeVar, Optional, List, Any, Dict
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import APIException
from app.core.logging import get_logger

logger = get_logger(__name__)

T = TypeVar('T')


class BaseService(ABC, Generic[T]):
    """
    Base service class providing common CRUD operations.
    """

    def __init__(self, db: Session):
        self.db = db

    @abstractmethod
    def get_model(self):
        """Return the SQLAlchemy model class."""
        pass

    def get(self, id: Any) -> Optional[T]:
        """
        Get a single record by ID.
        """
        try:
            stmt = select(self.get_model()).where(self.get_model().id == id)
            result = self.db.execute(stmt).scalar_one_or_none()
            return result
        except SQLAlchemyError as e:
            logger.error(f"Error getting {self.get_model().__name__} with id {id}: {e}")
            raise APIException(
                status_code=500,
                detail=f"Database error while retrieving {self.get_model().__name__}"
            )

    def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[T]:
        """
        Get multiple records with optional filtering.
        """
        try:
            stmt = select(self.get_model())

            if filters:
                for key, value in filters.items():
                    if hasattr(self.get_model(), key):
                        stmt = stmt.where(getattr(self.get_model(), key) == value)

            stmt = stmt.offset(skip).limit(limit)
            result = self.db.execute(stmt).scalars().all()
            return list(result)
        except SQLAlchemyError as e:
            logger.error(f"Error getting multiple {self.get_model().__name__}: {e}")
            raise APIException(
                status_code=500,
                detail=f"Database error while retrieving {self.get_model().__name__} records"
            )

    def create(self, obj_in: Dict[str, Any]) -> T:
        """
        Create a new record.
        """
        try:
            obj_data = obj_in.dict() if hasattr(obj_in, 'dict') else obj_in
            db_obj = self.get_model()(**obj_data)
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            logger.info(f"Created {self.get_model().__name__} with id {db_obj.id}")
            return db_obj
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error creating {self.get_model().__name__}: {e}")
            raise APIException(
                status_code=500,
                detail=f"Database error while creating {self.get_model().__name__}"
            )

    def update(self, db_obj: T, obj_in: Dict[str, Any]) -> T:
        """
        Update an existing record.
        """
        try:
            obj_data = obj_in.dict() if hasattr(obj_in, 'dict') else obj_in
            update_data = {k: v for k, v in obj_data.items() if v is not None}

            stmt = (
                update(self.get_model())
                .where(self.get_model().id == db_obj.id)
                .values(**update_data)
            )
            self.db.execute(stmt)
            self.db.commit()

            # Refresh the object
            self.db.refresh(db_obj)
            logger.info(f"Updated {self.get_model().__name__} with id {db_obj.id}")
            return db_obj
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating {self.get_model().__name__} with id {db_obj.id}: {e}")
            raise APIException(
                status_code=500,
                detail=f"Database error while updating {self.get_model().__name__}"
            )

    def remove(self, id: Any) -> T:
        """
        Delete a record by ID.
        """
        try:
            obj = self.get(id)
            if not obj:
                raise APIException(
                    status_code=404,
                    detail=f"{self.get_model().__name__} not found"
                )

            stmt = delete(self.get_model()).where(self.get_model().id == id)
            self.db.execute(stmt)
            self.db.commit()
            logger.info(f"Deleted {self.get_model().__name__} with id {id}")
            return obj
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting {self.get_model().__name__} with id {id}: {e}")
            raise APIException(
                status_code=500,
                detail=f"Database error while deleting {self.get_model().__name__}"
            )

    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count records with optional filtering.
        """
        try:
            stmt = select(self.get_model())

            if filters:
                for key, value in filters.items():
                    if hasattr(self.get_model(), key):
                        stmt = stmt.where(getattr(self.get_model(), key) == value)

            result = self.db.execute(stmt).scalars().all()
            return len(result)
        except SQLAlchemyError as e:
            logger.error(f"Error counting {self.get_model().__name__}: {e}")
            raise APIException(
                status_code=500,
                detail=f"Database error while counting {self.get_model().__name__}"
            )
