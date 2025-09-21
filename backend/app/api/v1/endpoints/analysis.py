"""
Analysis endpoints for the CQIA application.
"""

import logging
from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.project import Project
from app.schemas.analysis import (
    AnalysisResponse,
    AnalysisWithDetails,
    AnalysisTrigger,
    AnalysisProgress,
    IssueResponse,
    IssueUpdate,
    CodeAnalysisRequest,
    CodeAnalysisResponse,
    AnalysisMetrics,
)
from app.schemas.base import SuccessResponse, PaginatedResponse
from app.crud.analysis import analysis_crud, issue_crud
from app.crud.project import project_crud
from app.tasks.analysis_tasks import run_full_analysis, run_security_scan, run_performance_analysis, run_dependency_analysis

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=SuccessResponse[PaginatedResponse[AnalysisResponse]])
def read_analyses(
    project_id: UUID = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Retrieve analyses.
    """
    if project_id:
        # Check if user has access to project
        if not project_crud.user_has_access(db, project_id=project_id, user_id=current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        analyses = analysis_crud.get_by_project(db, project_id=project_id, skip=skip, limit=limit)
        total = analysis_crud.count_by_project(db, project_id=project_id)
    else:
        # Get analyses for user's projects
        analyses = []
        total = 0
        # This would need to be implemented based on user's project access

    return SuccessResponse(
        data=PaginatedResponse(
            items=analyses,
            total=total,
            page=skip // limit + 1,
            size=len(analyses),
            pages=(total + limit - 1) // limit
        ),
        message="Analyses retrieved successfully"
    )


@router.post("/", response_model=SuccessResponse[AnalysisResponse])
def create_analysis(
    analysis_in: AnalysisTrigger,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Create and trigger new analysis.
    """
    # Check if user has access to project
    if not project_crud.user_has_access(db, project_id=analysis_in.project_id, user_id=current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Create analysis record
    from app.schemas.analysis import AnalysisCreate
    analysis_create = AnalysisCreate(
        project_id=analysis_in.project_id,
        triggered_by=current_user.id,
        analysis_type=analysis_in.analysis_type,
        config=analysis_in.config
    )

    analysis = analysis_crud.create(db, obj_in=analysis_create)

    # Trigger background analysis task based on analysis type
    try:
        analysis_type = analysis_in.analysis_type.lower()

        if analysis_type == "full" or analysis_type == "comprehensive":
            # Get project files for analysis
            project = db.query(Project).filter(Project.id == analysis_in.project_id).first()
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )

            # Get file paths from project (this would need to be implemented based on your project structure)
            file_paths = analysis_in.config.get("file_paths", [])

            # Trigger full analysis task
            run_full_analysis.delay(
                str(analysis.id),
                str(analysis_in.project_id),
                file_paths,
                analysis_in.config
            )

        elif analysis_type == "security":
            # Trigger security scan task
            file_paths = analysis_in.config.get("file_paths", [])
            run_security_scan.delay(
                str(analysis.id),
                str(analysis_in.project_id),
                file_paths,
                analysis_in.config
            )

        elif analysis_type == "performance":
            # Trigger performance analysis task
            file_paths = analysis_in.config.get("file_paths", [])
            run_performance_analysis.delay(
                str(analysis.id),
                str(analysis_in.project_id),
                file_paths,
                analysis_in.config
            )

        elif analysis_type == "dependency":
            # Trigger dependency analysis task
            file_paths = analysis_in.config.get("file_paths", [])
            run_dependency_analysis.delay(
                str(analysis.id),
                str(analysis_in.project_id),
                file_paths,
                analysis_in.config
            )

        else:
            # Default to full analysis for unknown types
            file_paths = analysis_in.config.get("file_paths", [])
            run_full_analysis.delay(
                str(analysis.id),
                str(analysis_in.project_id),
                file_paths,
                analysis_in.config
            )

        logger.info(f"Triggered {analysis_type} analysis task for analysis {analysis.id}")

    except Exception as e:
        logger.error(f"Failed to trigger analysis task: {e}")
        # Update analysis status to failed
        analysis_crud.update_status(db, analysis.id, "failed")

    return SuccessResponse(
        data=analysis,
        message="Analysis triggered successfully"
    )


@router.get("/{analysis_id}", response_model=SuccessResponse[AnalysisWithDetails])
def read_analysis(
    analysis_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get analysis by ID.
    """
    analysis = analysis_crud.get_with_details(db, id=analysis_id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    # Check if user has access to the project
    if not project_crud.user_has_access(db, project_id=analysis["project_id"], user_id=current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    return SuccessResponse(
        data=analysis,
        message="Analysis retrieved successfully"
    )


@router.get("/{analysis_id}/progress", response_model=SuccessResponse[AnalysisProgress])
def get_analysis_progress(
    analysis_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get analysis progress.
    """
    analysis = analysis_crud.get(db, id=analysis_id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    # Check if user has access to the project
    if not project_crud.user_has_access(db, project_id=analysis.project_id, user_id=current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    progress = AnalysisProgress(
        analysis_id=str(analysis_id),
        status=analysis.status,
        progress=50,  # Placeholder - would be calculated based on actual progress
        current_step="Analyzing code",
        message="Analysis in progress",
        estimated_time_remaining=120
    )

    return SuccessResponse(
        data=progress,
        message="Analysis progress retrieved successfully"
    )


@router.get("/{analysis_id}/issues", response_model=SuccessResponse[List[IssueResponse]])
def read_analysis_issues(
    analysis_id: UUID,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get issues for analysis.
    """
    analysis = analysis_crud.get(db, id=analysis_id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    # Check if user has access to the project
    if not project_crud.user_has_access(db, project_id=analysis.project_id, user_id=current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    issues = issue_crud.get_by_analysis(db, analysis_id=analysis_id, skip=skip, limit=limit)

    return SuccessResponse(
        data=issues,
        message="Analysis issues retrieved successfully"
    )


@router.put("/{analysis_id}/issues/{issue_id}", response_model=SuccessResponse[IssueResponse])
def update_issue(
    analysis_id: UUID,
    issue_id: UUID,
    issue_in: IssueUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update issue.
    """
    analysis = analysis_crud.get(db, id=analysis_id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    # Check if user has access to the project
    if not project_crud.user_has_access(db, project_id=analysis.project_id, user_id=current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    issue = issue_crud.get(db, id=issue_id)
    if not issue or issue.analysis_id != analysis_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )

    issue = issue_crud.update(db, db_obj=issue, obj_in=issue_in)
    return SuccessResponse(
        data=issue,
        message="Issue updated successfully"
    )


@router.post("/code-analyze", response_model=SuccessResponse[CodeAnalysisResponse])
def analyze_code(
    analysis_request: CodeAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Analyze code snippet.
    """
    # This would integrate with code analysis service
    # For now, return mock response
    response = CodeAnalysisResponse(
        issues=[],
        metrics=[],
        suggestions=["Consider adding error handling", "Add input validation"],
        quality_score=85.5
    )

    return SuccessResponse(
        data=response,
        message="Code analysis completed successfully"
    )


@router.delete("/{analysis_id}", response_model=SuccessResponse[dict])
def delete_analysis(
    analysis_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Delete analysis.
    """
    analysis = analysis_crud.get(db, id=analysis_id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    # Check if user has access to the project
    if not project_crud.user_has_access(db, project_id=analysis.project_id, user_id=current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    analysis_crud.remove(db, id=analysis_id)
    return SuccessResponse(
        data={},
        message="Analysis deleted successfully"
    )
