"""
CRUD operations for Audit model.
"""

from typing import Any, Dict, Optional, Union, List
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.audit import AuditLog, AuditLogArchive, AuditLogAlertRule, AuditLogAlert
from app.schemas.audit import (
    AuditLogBase,
    AuditLogCreate,
    AuditLogUpdate,
    AuditLogArchiveBase,
    AuditLogAlertRuleCreate,
    AuditLogAlertRuleUpdate,
    AuditLogAlert,
)


class CRUDAuditLog:
    """CRUD operations for AuditLog model."""

    def get(self, db: Session, *, id: UUID) -> Optional[AuditLog]:
        """Get audit log by ID."""
        return db.query(AuditLog).filter(AuditLog.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[AuditLog]:
        """Get multiple audit logs."""
        return db.query(AuditLog).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: AuditLogCreate) -> AuditLog:
        """Create new audit log."""
        db_obj = AuditLog(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: AuditLog, obj_in: Union[AuditLogBase, Dict[str, Any]]
    ) -> AuditLog:
        """Update audit log."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        for field in update_data:
            setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: UUID) -> AuditLog:
        """Remove audit log."""
        obj = db.query(AuditLog).get(id)
        db.delete(obj)
        db.commit()
        return obj


class CRUDAuditLogArchive:
    """CRUD operations for AuditLogArchive model."""

    def get(self, db: Session, *, id: UUID) -> Optional[AuditLogArchive]:
        """Get archive by ID."""
        return db.query(AuditLogArchive).filter(AuditLogArchive.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[AuditLogArchive]:
        """Get multiple archives."""
        return db.query(AuditLogArchive).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: AuditLogArchiveBase) -> AuditLogArchive:
        """Create new archive."""
        db_obj = AuditLogArchive(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: UUID) -> AuditLogArchive:
        """Remove archive."""
        obj = db.query(AuditLogArchive).get(id)
        db.delete(obj)
        db.commit()
        return obj


class CRUDAuditLogAlertRule:
    """CRUD operations for AuditLogAlertRule model."""

    def get(self, db: Session, *, id: UUID) -> Optional[AuditLogAlertRule]:
        """Get alert rule by ID."""
        return db.query(AuditLogAlertRule).filter(AuditLogAlertRule.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[AuditLogAlertRule]:
        """Get multiple alert rules."""
        return db.query(AuditLogAlertRule).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: AuditLogAlertRuleCreate) -> AuditLogAlertRule:
        """Create new alert rule."""
        db_obj = AuditLogAlertRule(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: AuditLogAlertRule, obj_in: Union[AuditLogAlertRuleUpdate, Dict[str, Any]]
    ) -> AuditLogAlertRule:
        """Update alert rule."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        for field in update_data:
            setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: UUID) -> AuditLogAlertRule:
        """Remove alert rule."""
        obj = db.query(AuditLogAlertRule).get(id)
        db.delete(obj)
        db.commit()
        return obj


class CRUDAuditLogAlert:
    """CRUD operations for AuditLogAlert model."""

    def get(self, db: Session, *, id: UUID) -> Optional[AuditLogAlert]:
        """Get alert by ID."""
        return db.query(AuditLogAlert).filter(AuditLogAlert.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[AuditLogAlert]:
        """Get multiple alerts."""
        return db.query(AuditLogAlert).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: AuditLogAlert) -> AuditLogAlert:
        """Create new alert."""
        db_obj = AuditLogAlert(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: UUID) -> AuditLogAlert:
        """Remove alert."""
        obj = db.query(AuditLogAlert).get(id)
        db.delete(obj)
        db.commit()
        return obj


audit_log_crud = CRUDAuditLog()
audit_log_archive_crud = CRUDAuditLogArchive()
audit_log_alert_rule_crud = CRUDAuditLogAlertRule()
audit_log_alert_crud = CRUDAuditLogAlert()
