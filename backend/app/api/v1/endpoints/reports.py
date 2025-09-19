"""
Reports endpoints for the CQIA application.
"""

from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.report import (
    ReportResponse,
    ReportWithDetails,
    ReportGenerationRequest,
    ReportGenerationResponse,
    ReportTemplateResponse,
    ReportTemplateCreate,
    ReportTemplateUpdate,
    DashboardData,
    AnalyticsData,
    ReportExportRequest,
)
from app.schemas.base import SuccessResponse, PaginatedResponse
from app.crud.report import report_crud, report_template_crud
from app.crud.analysis import analysis_crud
from app.crud.project import project_crud

router = APIRouter()


@router.get("/", response_model=SuccessResponse[PaginatedResponse[ReportResponse]])
def read_reports(
    analysis_id: UUID = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Retrieve reports.
    """
    if analysis_id:
        # Check if user has access to the analysis
        analysis = analysis_crud.get(db, id=analysis_id)
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis not found"
            )
        if not project_crud.user_has_access(db, project_id=analysis.project_id, user_id=current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        reports = report_crud.get_by_analysis(db, analysis_id=analysis_id, skip=skip, limit=limit)
        total = len(reports)  # Would need proper count method
    else:
        # Get all user's reports
        reports = report_crud.get_multi(db, skip=skip, limit=limit)
        total = report_crud.count(db)

    return SuccessResponse(
        data=PaginatedResponse(
            items=reports,
            total=total,
            page=skip // limit + 1,
            size=len(reports),
            pages=(total + limit - 1) // limit
        ),
        message="Reports retrieved successfully"
    )


@router.post("/generate", response_model=SuccessResponse[ReportGenerationResponse])
def generate_report(
    report_request: ReportGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Generate new report.
    """
    # Check if user has access to the analysis
    analysis = analysis_crud.get(db, id=report_request.analysis_id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    if not project_crud.user_has_access(db, project_id=analysis.project_id, user_id=current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Create report record
    from app.schemas.report import ReportCreate
    report_create = ReportCreate(
        analysis_id=report_request.analysis_id,
        generated_by=current_user.id,
        title=report_request.title or f"Analysis Report - {analysis.id}",
        format=report_request.format,
        config=report_request.config
    )

    report = report_crud.create(db, obj_in=report_create)

    # Trigger background report generation
    background_tasks.add_task(generate_report_task, report.id, report_request)

    response = ReportGenerationResponse(
        report_id=str(report.id),
        status="generating",
        download_url=None,
        estimated_completion=None
    )

    return SuccessResponse(
        data=response,
        message="Report generation started successfully"
    )


@router.get("/{report_id}", response_model=SuccessResponse[ReportWithDetails])
def read_report(
    report_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get report by ID.
    """
    report = report_crud.get_with_details(db, id=report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )

    # Check if user has access to the analysis
    analysis = analysis_crud.get(db, id=report["analysis_id"])
    if not analysis or not project_crud.user_has_access(db, project_id=analysis.project_id, user_id=current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    return SuccessResponse(
        data=report,
        message="Report retrieved successfully"
    )


@router.post("/{report_id}/export", response_model=SuccessResponse[dict])
def export_report(
    report_id: UUID,
    export_request: ReportExportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Export report.
    """
    report = report_crud.get(db, id=report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )

    # Check if user has access to the analysis
    analysis = analysis_crud.get(db, id=report.analysis_id)
    if not analysis or not project_crud.user_has_access(db, project_id=analysis.project_id, user_id=current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Generate export URL (placeholder)
    export_url = f"/api/v1/reports/{report_id}/download?format={export_request.format}"

    return SuccessResponse(
        data={"export_url": export_url},
        message="Report export initiated successfully"
    )


@router.get("/templates", response_model=SuccessResponse[List[ReportTemplateResponse]])
def read_report_templates(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get available report templates.
    """
    templates = report_template_crud.get_active(db)
    return SuccessResponse(
        data=templates,
        message="Report templates retrieved successfully"
    )


@router.post("/templates", response_model=SuccessResponse[ReportTemplateResponse])
def create_report_template(
    template_in: ReportTemplateCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Create report template.
    """
    template = report_template_crud.create(db, obj_in=template_in)
    return SuccessResponse(
        data=template,
        message="Report template created successfully"
    )


@router.get("/dashboard", response_model=SuccessResponse[DashboardData])
def get_dashboard_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get dashboard data.
    """
    # This would aggregate data from various sources
    dashboard_data = DashboardData(
        total_projects=0,  # Would be calculated
        total_analyses=0,  # Would be calculated
        total_issues=0,    # Would be calculated
        average_quality_score=None,  # Would be calculated
        recent_analyses=[],  # Would be populated
        quality_trends=[],   # Would be populated
        top_issues=[]        # Would be populated
    )

    return SuccessResponse(
        data=dashboard_data,
        message="Dashboard data retrieved successfully"
    )


@router.get("/analytics", response_model=SuccessResponse[AnalyticsData])
def get_analytics_data(
    timeframe: str = "30d",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get analytics data.
    """
    # This would aggregate analytics data
    analytics_data = AnalyticsData(
        timeframe=timeframe,
        metrics={},      # Would be populated
        trends=[],       # Would be populated
        comparisons={}   # Would be populated
    )

    return SuccessResponse(
        data=analytics_data,
        message="Analytics data retrieved successfully"
    )


@router.delete("/{report_id}", response_model=SuccessResponse[dict])
def delete_report(
    report_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Delete report.
    """
    report = report_crud.get(db, id=report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )

    # Check if user has access to the analysis
    analysis = analysis_crud.get(db, id=report.analysis_id)
    if not analysis or not project_crud.user_has_access(db, project_id=analysis.project_id, user_id=current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    report_crud.remove(db, id=report_id)
    return SuccessResponse(
        data={},
        message="Report deleted successfully"
    )


# Background task function
def generate_report_task(report_id: UUID, report_request: ReportGenerationRequest):
    """
    Background task to generate report.
    """
    # This would integrate with the actual report generation service
    # For now, just a placeholder
    pass
