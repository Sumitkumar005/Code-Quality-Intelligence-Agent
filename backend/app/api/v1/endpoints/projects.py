"""
Project management endpoints for the CQIA application.
"""

from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.project import Project
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectWithDetails,
    ProjectSummary,
    ProjectWebhookCreate,
    ProjectWebhookUpdate,
    ProjectWebhookResponse,
    ProjectAnalysisTrigger
)
from app.schemas.base import SuccessResponse, PaginatedResponse
from app.crud.project import project_crud

router = APIRouter()


@router.get("/", response_model=SuccessResponse[PaginatedResponse[ProjectResponse]])
def read_projects(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Retrieve projects for current user.
    """
    projects = project_crud.get_user_projects(db, user_id=current_user.id, skip=skip, limit=limit)
    total = project_crud.count_user_projects(db, user_id=current_user.id)

    return SuccessResponse(
        data=PaginatedResponse(
            items=projects,
            total=total,
            page=skip // limit + 1,
            size=len(projects),
            pages=(total + limit - 1) // limit
        ),
        message="Projects retrieved successfully"
    )


@router.post("/", response_model=SuccessResponse[ProjectResponse])
def create_project(
    project_in: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Create new project.
    """
    project = project_crud.create_with_owner(db, obj_in=project_in, owner_id=current_user.id)
    return SuccessResponse(
        data=project,
        message="Project created successfully"
    )


@router.get("/{project_id}", response_model=SuccessResponse[ProjectWithDetails])
def read_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get project by ID.
    """
    project = project_crud.get_with_details(db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Check if user has access to this project
    if not project_crud.user_has_access(db, project_id=project_id, user_id=current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    return SuccessResponse(
        data=project,
        message="Project retrieved successfully"
    )


@router.put("/{project_id}", response_model=SuccessResponse[ProjectResponse])
def update_project(
    project_id: UUID,
    project_in: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update project.
    """
    project = project_crud.get(db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Check if user has access to this project
    if not project_crud.user_has_access(db, project_id=project_id, user_id=current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    project = project_crud.update(db, db_obj=project, obj_in=project_in)
    return SuccessResponse(
        data=project,
        message="Project updated successfully"
    )


@router.delete("/{project_id}", response_model=SuccessResponse[dict])
def delete_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Delete project.
    """
    project = project_crud.get(db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Check if user has access to this project
    if not project_crud.user_has_access(db, project_id=project_id, user_id=current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    project_crud.remove(db, id=project_id)
    return SuccessResponse(
        data={},
        message="Project deleted successfully"
    )


@router.post("/{project_id}/analyze", response_model=SuccessResponse[dict])
def trigger_analysis(
    project_id: UUID,
    analysis_trigger: ProjectAnalysisTrigger,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Trigger analysis for project.
    """
    project = project_crud.get(db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Check if user has access to this project
    if not project_crud.user_has_access(db, project_id=project_id, user_id=current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Trigger analysis (would integrate with analysis service)
    analysis_id = "analysis-id-placeholder"  # Would be generated by analysis service

    return SuccessResponse(
        data={"analysis_id": analysis_id},
        message="Analysis triggered successfully"
    )


@router.get("/{project_id}/summary", response_model=SuccessResponse[ProjectSummary])
def get_project_summary(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get project summary with metrics.
    """
    project = project_crud.get(db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Check if user has access to this project
    if not project_crud.user_has_access(db, project_id=project_id, user_id=current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    summary = project_crud.get_summary(db, project_id=project_id)
    return SuccessResponse(
        data=summary,
        message="Project summary retrieved successfully"
    )


@router.post("/{project_id}/webhooks", response_model=SuccessResponse[ProjectWebhookResponse])
def create_webhook(
    project_id: UUID,
    webhook_in: ProjectWebhookCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Create webhook for project.
    """
    project = project_crud.get(db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Check if user has access to this project
    if not project_crud.user_has_access(db, project_id=project_id, user_id=current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    webhook = project_crud.create_webhook(db, project_id=project_id, webhook_in=webhook_in)
    return SuccessResponse(
        data=webhook,
        message="Webhook created successfully"
    )


@router.get("/{project_id}/webhooks", response_model=SuccessResponse[List[ProjectWebhookResponse]])
def list_webhooks(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    List webhooks for project.
    """
    project = project_crud.get(db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Check if user has access to this project
    if not project_crud.user_has_access(db, project_id=project_id, user_id=current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    webhooks = project_crud.get_webhooks(db, project_id=project_id)
    return SuccessResponse(
        data=webhooks,
        message="Webhooks retrieved successfully"
    )
