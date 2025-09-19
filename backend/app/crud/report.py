"""
CRUD operations for Report model.
"""

from typing import Any, Dict, Optional, Union, List
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.report import Report, ReportTemplate
from app.schemas.report import ReportCreate, ReportUpdate, ReportTemplateCreate, ReportTemplateUpdate


class CRUDReport:
    """CRUD operations for Report model."""

    def get(self, db: Session, *, id: UUID) -> Optional[Report]:
        """Get report by ID."""
        return db.query(Report).filter(Report.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Report]:
        """Get multiple reports."""
        return db.query(Report).offset(skip).limit(limit).all()

    def get_by_analysis(
        self, db: Session, *, analysis_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Report]:
        """Get reports for a specific analysis."""
        return db.query(Report).filter(Report.analysis_id == analysis_id).offset(skip).limit(limit).all()

    def get_with_details(self, db: Session, *, id: UUID) -> Optional[Dict[str, Any]]:
        """Get report with detailed information."""
        report = self.get(db, id=id)
        if not report:
            return None

        return {
            "id": report.id,
            "analysis_id": report.analysis_id,
            "generated_by": report.generated_by,
            "title": report.title,
            "report_type": report.report_type,
            "format": report.format,
            "content": report.content,
            "summary": report.summary,
            "file_path": report.file_path,
            "file_size": report.file_size,
            "download_url": report.download_url,
            "is_public": report.is_public,
            "is_archived": report.is_archived,
            "config": report.config,
            "created_at": report.created_at,
            "updated_at": report.updated_at,
        }

    def create(self, db: Session, *, obj_in: ReportCreate) -> Report:
        """Create new report."""
        db_obj = Report(
            analysis_id=obj_in.analysis_id,
            generated_by=obj_in.generated_by,
            title=obj_in.title,
            report_type=obj_in.report_type,
            format=obj_in.format,
            config=obj_in.config,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: Report, obj_in: Union[ReportUpdate, Dict[str, Any]]
    ) -> Report:
        """Update report."""
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

    def remove(self, db: Session, *, id: UUID) -> Report:
        """Remove report."""
        obj = db.query(Report).get(id)
        db.delete(obj)
        db.commit()
        return obj

    def count(self, db: Session) -> int:
        """Count total reports."""
        return db.query(Report).count()


class CRUDReportTemplate:
    """CRUD operations for ReportTemplate model."""

    def get(self, db: Session, *, id: UUID) -> Optional[ReportTemplate]:
        """Get template by ID."""
        return db.query(ReportTemplate).filter(ReportTemplate.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ReportTemplate]:
        """Get multiple templates."""
        return db.query(ReportTemplate).offset(skip).limit(limit).all()

    def get_active(self, db: Session) -> List[ReportTemplate]:
        """Get active templates."""
        return db.query(ReportTemplate).filter(ReportTemplate.is_active == True).all()

    def get_default(self, db: Session) -> Optional[ReportTemplate]:
        """Get default template."""
        return db.query(ReportTemplate).filter(ReportTemplate.is_default == True).first()

    def create(self, db: Session, *, obj_in: ReportTemplateCreate) -> ReportTemplate:
        """Create new template."""
        db_obj = ReportTemplate(
            name=obj_in.name,
            description=obj_in.description,
            template_type=obj_in.template_type,
            template_content=obj_in.template_content,
            template_config=obj_in.template_config,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: ReportTemplate, obj_in: Union[ReportTemplateUpdate, Dict[str, Any]]
    ) -> ReportTemplate:
        """Update template."""
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

    def remove(self, db: Session, *, id: UUID) -> ReportTemplate:
        """Remove template."""
        obj = db.query(ReportTemplate).get(id)
        db.delete(obj)
        db.commit()
        return obj


report_crud = CRUDReport()
report_template_crud = CRUDReportTemplate()
