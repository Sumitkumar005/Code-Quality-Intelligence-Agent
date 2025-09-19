"""
CRUD operations for Analysis model.
"""

from typing import Any, Dict, Optional, Union, List
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.analysis import Analysis, Issue, AnalysisArtifact
from app.schemas.analysis import AnalysisCreate, AnalysisUpdate, IssueCreate, IssueUpdate


class CRUDAnalysis:
    """CRUD operations for Analysis model."""

    def get(self, db: Session, *, id: UUID) -> Optional[Analysis]:
        """Get analysis by ID."""
        return db.query(Analysis).filter(Analysis.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Analysis]:
        """Get multiple analyses."""
        return db.query(Analysis).offset(skip).limit(limit).all()

    def get_by_project(
        self, db: Session, *, project_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Analysis]:
        """Get analyses for a specific project."""
        return db.query(Analysis).filter(Analysis.project_id == project_id).offset(skip).limit(limit).all()

    def get_with_details(self, db: Session, *, id: UUID) -> Optional[Dict[str, Any]]:
        """Get analysis with detailed information."""
        analysis = self.get(db, id=id)
        if not analysis:
            return None

        issues = db.query(Issue).filter(Issue.analysis_id == id).all()
        artifacts = db.query(AnalysisArtifact).filter(AnalysisArtifact.analysis_id == id).all()

        return {
            "id": analysis.id,
            "project_id": analysis.project_id,
            "triggered_by": analysis.triggered_by,
            "status": analysis.status,
            "started_at": analysis.started_at,
            "completed_at": analysis.completed_at,
            "duration_seconds": analysis.duration_seconds,
            "quality_score": analysis.quality_score,
            "coverage_percentage": analysis.coverage_percentage,
            "lines_of_code": analysis.lines_of_code,
            "files_analyzed": analysis.files_analyzed,
            "total_issues": analysis.total_issues,
            "critical_issues": analysis.critical_issues,
            "high_issues": analysis.high_issues,
            "medium_issues": analysis.medium_issues,
            "low_issues": analysis.low_issues,
            "results": analysis.results,
            "config": analysis.config,
            "error_message": analysis.error_message,
            "error_details": analysis.error_details,
            "created_at": analysis.created_at,
            "updated_at": analysis.updated_at,
            "issues": issues,
            "artifacts": artifacts
        }

    def create(self, db: Session, *, obj_in: AnalysisCreate) -> Analysis:
        """Create new analysis."""
        db_obj = Analysis(
            project_id=obj_in.project_id,
            triggered_by=obj_in.triggered_by,
            commit_hash=obj_in.commit_hash,
            branch=obj_in.branch,
            analysis_type=obj_in.analysis_type,
            config=obj_in.config,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: Analysis, obj_in: Union[AnalysisUpdate, Dict[str, Any]]
    ) -> Analysis:
        """Update analysis."""
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

    def remove(self, db: Session, *, id: UUID) -> Analysis:
        """Remove analysis."""
        obj = db.query(Analysis).get(id)
        db.delete(obj)
        db.commit()
        return obj

    def count(self, db: Session) -> int:
        """Count total analyses."""
        return db.query(Analysis).count()

    def count_by_project(self, db: Session, *, project_id: UUID) -> int:
        """Count analyses for a specific project."""
        return db.query(Analysis).filter(Analysis.project_id == project_id).count()


class CRUDIssue:
    """CRUD operations for Issue model."""

    def get(self, db: Session, *, id: UUID) -> Optional[Issue]:
        """Get issue by ID."""
        return db.query(Issue).filter(Issue.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Issue]:
        """Get multiple issues."""
        return db.query(Issue).offset(skip).limit(limit).all()

    def get_by_analysis(
        self, db: Session, *, analysis_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Issue]:
        """Get issues for a specific analysis."""
        return db.query(Issue).filter(Issue.analysis_id == analysis_id).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: IssueCreate) -> Issue:
        """Create new issue."""
        db_obj = Issue(
            analysis_id=obj_in.analysis_id,
            rule_id=obj_in.rule_id,
            rule_name=obj_in.rule_name,
            category=obj_in.category,
            severity=obj_in.severity,
            file_path=obj_in.file_path,
            line_number=obj_in.line_number,
            column_number=obj_in.column_number,
            function_name=obj_in.function_name,
            message=obj_in.message,
            description=obj_in.description,
            code_snippet=obj_in.code_snippet,
            confidence=obj_in.confidence,
            effort_minutes=obj_in.effort_minutes,
            tags=obj_in.tags,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: Issue, obj_in: Union[IssueUpdate, Dict[str, Any]]
    ) -> Issue:
        """Update issue."""
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

    def remove(self, db: Session, *, id: UUID) -> Issue:
        """Remove issue."""
        obj = db.query(Issue).get(id)
        db.delete(obj)
        db.commit()
        return obj

    def count(self, db: Session) -> int:
        """Count total issues."""
        return db.query(Issue).count()

    def count_by_analysis(self, db: Session, *, analysis_id: UUID) -> int:
        """Count issues for a specific analysis."""
        return db.query(Issue).filter(Issue.analysis_id == analysis_id).count()


class CRUDAnalysisArtifact:
    """CRUD operations for AnalysisArtifact model."""

    def get(self, db: Session, *, id: UUID) -> Optional[AnalysisArtifact]:
        """Get artifact by ID."""
        return db.query(AnalysisArtifact).filter(AnalysisArtifact.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[AnalysisArtifact]:
        """Get multiple artifacts."""
        return db.query(AnalysisArtifact).offset(skip).limit(limit).all()

    def get_by_analysis(
        self, db: Session, *, analysis_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[AnalysisArtifact]:
        """Get artifacts for a specific analysis."""
        return db.query(AnalysisArtifact).filter(AnalysisArtifact.analysis_id == analysis_id).offset(skip).limit(limit).all()

    def create(self, db: Session, *, analysis_id: UUID, obj_in: Any) -> AnalysisArtifact:
        """Create new artifact."""
        db_obj = AnalysisArtifact(
            analysis_id=analysis_id,
            name=obj_in.name,
            artifact_type=obj_in.artifact_type,
            file_path=obj_in.file_path,
            file_size=obj_in.file_size,
            content=obj_in.content,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: UUID) -> AnalysisArtifact:
        """Remove artifact."""
        obj = db.query(AnalysisArtifact).get(id)
        db.delete(obj)
        db.commit()
        return obj


analysis_crud = CRUDAnalysis()
issue_crud = CRUDIssue()
artifact_crud = CRUDAnalysisArtifact()
