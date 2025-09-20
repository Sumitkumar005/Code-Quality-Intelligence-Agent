"""
Data access layer for CQIA.
Provides repository pattern implementation for database operations.
"""

import structlog
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Generic, TypeVar, Type
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from sqlalchemy.exc import SQLAlchemyError

from ..core.exceptions import DatabaseError, NotFoundError
from ..models.base import Base

logger = structlog.get_logger(__name__)

T = TypeVar('T', bound=Base)


class BaseRepository(Generic[T]):
    """
    Base repository class providing common database operations.

    Args:
        model: SQLAlchemy model class
        db: Database session
    """

    def __init__(self, model: Type[T], db: Session):
        self.model = model
        self.db = db
        self.logger = logger.bind(repository=self.__class__.__name__)

    def create(self, obj_data: Dict[str, Any]) -> T:
        """
        Create a new record.

        Args:
            obj_data: Dictionary of object attributes

        Returns:
            Created object

        Raises:
            DatabaseError: If creation fails
        """
        try:
            obj = self.model(**obj_data)
            self.db.add(obj)
            self.db.flush()  # Flush to get the ID without committing
            self.logger.info("Object created", object_type=self.model.__name__, id=obj.id)
            return obj
        except SQLAlchemyError as e:
            self.logger.error("Failed to create object", error=str(e))
            raise DatabaseError(f"Failed to create {self.model.__name__}: {str(e)}")

    def get_by_id(self, id: Any) -> Optional[T]:
        """
        Get object by ID.

        Args:
            id: Object ID

        Returns:
            Object if found, None otherwise
        """
        try:
            obj = self.db.query(self.model).filter(self.model.id == id).first()
            if obj:
                self.logger.debug("Object found", object_type=self.model.__name__, id=id)
            else:
                self.logger.debug("Object not found", object_type=self.model.__name__, id=id)
            return obj
        except SQLAlchemyError as e:
            self.logger.error("Failed to get object by ID", error=str(e))
            raise DatabaseError(f"Failed to get {self.model.__name__} by ID: {str(e)}")

    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """
        Get all objects with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of objects
        """
        try:
            objects = self.db.query(self.model).offset(skip).limit(limit).all()
            self.logger.debug("Retrieved objects",
                            object_type=self.model.__name__,
                            count=len(objects),
                            skip=skip,
                            limit=limit)
            return objects
        except SQLAlchemyError as e:
            self.logger.error("Failed to get all objects", error=str(e))
            raise DatabaseError(f"Failed to get all {self.model.__name__}: {str(e)}")

    def update(self, id: Any, update_data: Dict[str, Any]) -> Optional[T]:
        """
        Update object by ID.

        Args:
            id: Object ID
            update_data: Dictionary of fields to update

        Returns:
            Updated object if found, None otherwise

        Raises:
            DatabaseError: If update fails
        """
        try:
            obj = self.db.query(self.model).filter(self.model.id == id).first()
            if not obj:
                self.logger.debug("Object not found for update",
                                object_type=self.model.__name__, id=id)
                return None

            for field, value in update_data.items():
                if hasattr(obj, field):
                    setattr(obj, field, value)

            self.db.flush()
            self.logger.info("Object updated", object_type=self.model.__name__, id=id)
            return obj
        except SQLAlchemyError as e:
            self.logger.error("Failed to update object", error=str(e))
            raise DatabaseError(f"Failed to update {self.model.__name__}: {str(e)}")

    def delete(self, id: Any) -> bool:
        """
        Delete object by ID.

        Args:
            id: Object ID

        Returns:
            True if object was deleted, False if not found

        Raises:
            DatabaseError: If deletion fails
        """
        try:
            obj = self.db.query(self.model).filter(self.model.id == id).first()
            if not obj:
                self.logger.debug("Object not found for deletion",
                                object_type=self.model.__name__, id=id)
                return False

            self.db.delete(obj)
            self.db.flush()
            self.logger.info("Object deleted", object_type=self.model.__name__, id=id)
            return True
        except SQLAlchemyError as e:
            self.logger.error("Failed to delete object", error=str(e))
            raise DatabaseError(f"Failed to delete {self.model.__name__}: {str(e)}")

    def exists(self, id: Any) -> bool:
        """
        Check if object exists by ID.

        Args:
            id: Object ID

        Returns:
            True if exists, False otherwise
        """
        try:
            exists = self.db.query(self.model.id).filter(self.model.id == id).first() is not None
            self.logger.debug("Existence check", object_type=self.model.__name__, id=id, exists=exists)
            return exists
        except SQLAlchemyError as e:
            self.logger.error("Failed to check object existence", error=str(e))
            raise DatabaseError(f"Failed to check {self.model.__name__} existence: {str(e)}")

    def count(self) -> int:
        """
        Count total number of objects.

        Returns:
            Total count
        """
        try:
            count = self.db.query(func.count(self.model.id)).scalar()
            self.logger.debug("Count query", object_type=self.model.__name__, count=count)
            return count
        except SQLAlchemyError as e:
            self.logger.error("Failed to count objects", error=str(e))
            raise DatabaseError(f"Failed to count {self.model.__name__}: {str(e)}")


class UserRepository(BaseRepository):
    """Repository for User model operations."""

    def get_by_email(self, email: str) -> Optional[T]:
        """Get user by email."""
        try:
            return self.db.query(self.model).filter(self.model.email == email).first()
        except SQLAlchemyError as e:
            self.logger.error("Failed to get user by email", error=str(e))
            raise DatabaseError(f"Failed to get user by email: {str(e)}")

    def get_by_username(self, username: str) -> Optional[T]:
        """Get user by username."""
        try:
            return self.db.query(self.model).filter(self.model.username == username).first()
        except SQLAlchemyError as e:
            self.logger.error("Failed to get user by username", error=str(e))
            raise DatabaseError(f"Failed to get user by username: {str(e)}")


class ProjectRepository(BaseRepository):
    """Repository for Project model operations."""

    def get_by_organization(self, organization_id: Any, skip: int = 0, limit: int = 100) -> List[T]:
        """Get projects by organization."""
        try:
            return self.db.query(self.model).filter(
                self.model.organization_id == organization_id
            ).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            self.logger.error("Failed to get projects by organization", error=str(e))
            raise DatabaseError(f"Failed to get projects by organization: {str(e)}")

    def get_by_repository_url(self, repository_url: str) -> Optional[T]:
        """Get project by repository URL."""
        try:
            return self.db.query(self.model).filter(
                self.model.repository_url == repository_url
            ).first()
        except SQLAlchemyError as e:
            self.logger.error("Failed to get project by repository URL", error=str(e))
            raise DatabaseError(f"Failed to get project by repository URL: {str(e)}")


class AnalysisRepository(BaseRepository):
    """Repository for Analysis model operations."""

    def get_by_project(self, project_id: Any, skip: int = 0, limit: int = 100) -> List[T]:
        """Get analyses by project."""
        try:
            return self.db.query(self.model).filter(
                self.model.project_id == project_id
            ).order_by(desc(self.model.created_at)).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            self.logger.error("Failed to get analyses by project", error=str(e))
            raise DatabaseError(f"Failed to get analyses by project: {str(e)}")

    def get_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[T]:
        """Get analyses by status."""
        try:
            return self.db.query(self.model).filter(
                self.model.status == status
            ).order_by(desc(self.model.created_at)).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            self.logger.error("Failed to get analyses by status", error=str(e))
            raise DatabaseError(f"Failed to get analyses by status: {str(e)}")


class ReportRepository(BaseRepository):
    """Repository for Report model operations."""

    def get_by_project(self, project_id: Any, skip: int = 0, limit: int = 100) -> List[T]:
        """Get reports by project."""
        try:
            return self.db.query(self.model).filter(
                self.model.project_id == project_id
            ).order_by(desc(self.model.generated_at)).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            self.logger.error("Failed to get reports by project", error=str(e))
            raise DatabaseError(f"Failed to get reports by project: {str(e)}")

    def get_by_analysis(self, analysis_id: Any) -> List[T]:
        """Get reports by analysis."""
        try:
            return self.db.query(self.model).filter(
                self.model.analysis_id == analysis_id
            ).order_by(desc(self.model.generated_at)).all()
        except SQLAlchemyError as e:
            self.logger.error("Failed to get reports by analysis", error=str(e))
            raise DatabaseError(f"Failed to get reports by analysis: {str(e)}")


class AuditRepository(BaseRepository):
    """Repository for Audit model operations."""

    def get_by_user(self, user_id: Any, skip: int = 0, limit: int = 100) -> List[T]:
        """Get audit logs by user."""
        try:
            return self.db.query(self.model).filter(
                self.model.user_id == user_id
            ).order_by(desc(self.model.created_at)).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            self.logger.error("Failed to get audit logs by user", error=str(e))
            raise DatabaseError(f"Failed to get audit logs by user: {str(e)}")

    def get_by_organization(self, organization_id: Any, skip: int = 0, limit: int = 100) -> List[T]:
        """Get audit logs by organization."""
        try:
            return self.db.query(self.model).filter(
                self.model.organization_id == organization_id
            ).order_by(desc(self.model.created_at)).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            self.logger.error("Failed to get audit logs by organization", error=str(e))
            raise DatabaseError(f"Failed to get audit logs by organization: {str(e)}")

    def get_by_action(self, action: str, skip: int = 0, limit: int = 100) -> List[T]:
        """Get audit logs by action."""
        try:
            return self.db.query(self.model).filter(
                self.model.action == action
            ).order_by(desc(self.model.created_at)).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            self.logger.error("Failed to get audit logs by action", error=str(e))
            raise DatabaseError(f"Failed to get audit logs by action: {str(e)}")


# Repository factory function
def get_repository(model: Type[T], db: Session) -> BaseRepository[T]:
    """
    Factory function to get appropriate repository for a model.

    Args:
        model: SQLAlchemy model class
        db: Database session

    Returns:
        Repository instance for the model
    """
    model_name = model.__name__

    # Map model names to repository classes
    repository_map = {
        'User': UserRepository,
        'Project': ProjectRepository,
        'Analysis': AnalysisRepository,
        'Report': ReportRepository,
        'AuditLog': AuditRepository,
    }

    repository_class = repository_map.get(model_name, BaseRepository)
    return repository_class(model, db)
