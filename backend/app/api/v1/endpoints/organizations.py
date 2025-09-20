"""
Organizations API endpoints.
"""

from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/", response_model=schemas.organization.Organization)
def create_organization(
    *,
    db: Session = Depends(deps.get_db),
    organization_in: schemas.organization.OrganizationCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create a new organization.
    """
    # Check if organization with this name already exists
    organization = crud.organization.get_by_name(db, name=organization_in.name)
    if organization:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An organization with this name already exists",
        )

    organization = crud.organization.create(
        db=db, obj_in=organization_in, created_by=current_user.id
    )

    # Add creator as organization admin
    member_in = schemas.organization.OrganizationMemberCreate(
        organization_id=organization.id,
        user_id=current_user.id,
        role="admin",
        permissions=["read", "write", "admin"]
    )
    crud.organization_member.create(db=db, obj_in=member_in, invited_by=current_user.id)

    return organization


@router.get("/", response_model=schemas.organization.OrganizationListResponse)
def list_organizations(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve organizations.
    """
    organizations = crud.organization.get_multi(
        db=db, skip=skip, limit=limit, is_active=is_active, search=search
    )
    total = len(organizations)  # In production, use a count query

    return schemas.organization.OrganizationListResponse(
        organizations=organizations,
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.get("/{organization_id}", response_model=schemas.organization.OrganizationDetailResponse)
def get_organization(
    *,
    db: Session = Depends(deps.get_db),
    organization_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get organization by ID.
    """
    organization = crud.organization.get(db=db, id=organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    # Check if user has access to this organization
    member = crud.organization_member.get_by_org_and_user(
        db=db, organization_id=organization_id, user_id=current_user.id
    )
    if not member and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    # Get members and webhooks
    members = crud.organization_member.get_multi_by_organization(
        db=db, organization_id=organization_id
    )
    webhooks = crud.organization_webhook.get_multi_by_organization(
        db=db, organization_id=organization_id
    )

    # Get settings and billing (mock data for now)
    settings = schemas.organization.OrganizationSettings()
    billing = None  # Would be populated from billing service

    return schemas.organization.OrganizationDetailResponse(
        organization=organization,
        members=members,
        webhooks=webhooks,
        settings=settings,
        billing=billing
    )


@router.put("/{organization_id}", response_model=schemas.organization.Organization)
def update_organization(
    *,
    db: Session = Depends(deps.get_db),
    organization_id: str,
    organization_in: schemas.organization.OrganizationUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an organization.
    """
    organization = crud.organization.get(db=db, id=organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    # Check if user has admin access
    member = crud.organization_member.get_by_org_and_user(
        db=db, organization_id=organization_id, user_id=current_user.id
    )
    if not member or member.role != "admin":
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )

    # Check if name is being changed and if it conflicts
    if organization_in.name and organization_in.name != organization.name:
        existing_org = crud.organization.get_by_name(db, name=organization_in.name)
        if existing_org:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An organization with this name already exists",
            )

    organization = crud.organization.update(db=db, db_obj=organization, obj_in=organization_in)
    return organization


@router.delete("/{organization_id}")
def delete_organization(
    *,
    db: Session = Depends(deps.get_db),
    organization_id: str,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete an organization.
    """
    organization = crud.organization.get(db=db, id=organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    organization = crud.organization.remove(db=db, id=organization_id)
    return {"message": "Organization deleted successfully"}


@router.get("/{organization_id}/stats", response_model=schemas.organization.OrganizationStatsResponse)
def get_organization_stats(
    *,
    db: Session = Depends(deps.get_db),
    organization_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get organization statistics.
    """
    organization = crud.organization.get(db=db, id=organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    # Check if user has access to this organization
    member = crud.organization_member.get_by_org_and_user(
        db=db, organization_id=organization_id, user_id=current_user.id
    )
    if not member and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    # Get organization with stats
    org_data = crud.organization.get_with_stats(db=db, id=organization_id)
    if not org_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    # Mock recent activity and top projects
    recent_activity = []
    top_projects = []

    return schemas.organization.OrganizationStatsResponse(
        stats=org_data["stats"],
        recent_activity=recent_activity,
        top_projects=top_projects
    )


@router.post("/{organization_id}/members", response_model=schemas.organization.OrganizationMember)
def add_organization_member(
    *,
    db: Session = Depends(deps.get_db),
    organization_id: str,
    member_in: schemas.organization.OrganizationMemberCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Add a member to an organization.
    """
    organization = crud.organization.get(db=db, id=organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    # Check if user has admin access
    member = crud.organization_member.get_by_org_and_user(
        db=db, organization_id=organization_id, user_id=current_user.id
    )
    if not member or member.role != "admin":
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )

    # Check if user is already a member
    existing_member = crud.organization_member.get_by_org_and_user(
        db=db, organization_id=organization_id, user_id=member_in.user_id
    )
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this organization",
        )

    member = crud.organization_member.create(
        db=db, obj_in=member_in, invited_by=current_user.id
    )
    return member


@router.get("/{organization_id}/members", response_model=schemas.organization.OrganizationMemberListResponse)
def list_organization_members(
    *,
    db: Session = Depends(deps.get_db),
    organization_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    List organization members.
    """
    organization = crud.organization.get(db=db, id=organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    # Check if user has access to this organization
    member = crud.organization_member.get_by_org_and_user(
        db=db, organization_id=organization_id, user_id=current_user.id
    )
    if not member and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    members = crud.organization_member.get_multi_by_organization(
        db=db, organization_id=organization_id, skip=skip, limit=limit
    )
    total = len(members)  # In production, use a count query

    return schemas.organization.OrganizationMemberListResponse(
        members=members,
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.put("/{organization_id}/members/{member_id}", response_model=schemas.organization.OrganizationMember)
def update_organization_member(
    *,
    db: Session = Depends(deps.get_db),
    organization_id: str,
    member_id: str,
    member_in: schemas.organization.OrganizationMemberUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an organization member.
    """
    organization = crud.organization.get(db=db, id=organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    # Check if user has admin access
    member = crud.organization_member.get_by_org_and_user(
        db=db, organization_id=organization_id, user_id=current_user.id
    )
    if not member or member.role != "admin":
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )

    db_member = crud.organization_member.get(db=db, id=member_id)
    if not db_member or db_member.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization member not found",
        )

    member = crud.organization_member.update(db=db, db_obj=db_member, obj_in=member_in)
    return member


@router.delete("/{organization_id}/members/{member_id}")
def remove_organization_member(
    *,
    db: Session = Depends(deps.get_db),
    organization_id: str,
    member_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Remove a member from an organization.
    """
    organization = crud.organization.get(db=db, id=organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    # Check if user has admin access
    member = crud.organization_member.get_by_org_and_user(
        db=db, organization_id=organization_id, user_id=current_user.id
    )
    if not member or member.role != "admin":
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )

    db_member = crud.organization_member.get(db=db, id=member_id)
    if not db_member or db_member.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization member not found",
        )

    # Prevent removing the last admin
    if db_member.role == "admin":
        admin_count = db.query(models.OrganizationMember).filter(
            models.OrganizationMember.organization_id == organization_id,
            models.OrganizationMember.role == "admin"
        ).count()
        if admin_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove the last admin from the organization",
            )

    crud.organization_member.remove(db=db, id=member_id)
    return {"message": "Organization member removed successfully"}


@router.post("/{organization_id}/webhooks", response_model=schemas.organization.OrganizationWebhook)
def create_organization_webhook(
    *,
    db: Session = Depends(deps.get_db),
    organization_id: str,
    webhook_in: schemas.organization.OrganizationWebhookCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create a webhook for an organization.
    """
    organization = crud.organization.get(db=db, id=organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    # Check if user has access to this organization
    member = crud.organization_member.get_by_org_and_user(
        db=db, organization_id=organization_id, user_id=current_user.id
    )
    if not member and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    webhook = crud.organization_webhook.create(
        db=db, obj_in=webhook_in, created_by=current_user.id
    )
    return webhook


@router.get("/{organization_id}/webhooks", response_model=schemas.organization.OrganizationWebhookListResponse)
def list_organization_webhooks(
    *,
    db: Session = Depends(deps.get_db),
    organization_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    is_active: Optional[bool] = Query(None),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    List webhooks for an organization.
    """
    organization = crud.organization.get(db=db, id=organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    # Check if user has access to this organization
    member = crud.organization_member.get_by_org_and_user(
        db=db, organization_id=organization_id, user_id=current_user.id
    )
    if not member and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    webhooks = crud.organization_webhook.get_multi_by_organization(
        db=db, organization_id=organization_id, skip=skip, limit=limit, is_active=is_active
    )
    total = len(webhooks)  # In production, use a count query

    return schemas.organization.OrganizationWebhookListResponse(
        webhooks=webhooks,
        total=total,
        page=skip // limit + 1,
        size=limit
    )
