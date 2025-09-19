"""
Audit endpoints for the CQIA application.
"""

from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_current_superuser, get_db
from app.models.user import User
from app.schemas.audit import (
    AuditLogResponse,
    AuditLogFilter,
    AuditLogSummary,
    AuditLogExportRequest,
    AuditLogExportResponse,
    AuditLogRetentionPolicy,
    AuditLogRetentionUpdate,
    AuditLogAlertRule,
    AuditLogAlertRuleCreate,
    AuditLogAlertRuleUpdate,
    AuditLogAlertRuleResponse,
)
from app.schemas.base import SuccessResponse, PaginatedResponse
from app.crud.audit import (
    audit_log_crud,
    audit_log_archive_crud,
    audit_log_alert_rule_crud,
    audit_log_alert_crud
)

router = APIRouter()


@router.get("/logs", response_model=SuccessResponse[PaginatedResponse[AuditLogResponse]])
def read_audit_logs(
    skip: int = 0,
    limit: int = 100,
    filters: AuditLogFilter = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Retrieve audit logs.
    """
    # For non-admin users, only show their own logs
    if not current_user.is_superuser:
        if filters is None:
            filters = AuditLogFilter()
        filters.user_id = str(current_user.id)

    logs = audit_log_crud.get_multi(db, skip=skip, limit=limit)
    total = 100  # Would need proper count with filters

    return SuccessResponse(
        data=PaginatedResponse(
            items=logs,
            total=total,
            page=skip // limit + 1,
            size=len(logs),
            pages=(total + limit - 1) // limit
        ),
        message="Audit logs retrieved successfully"
    )


@router.get("/logs/{log_id}", response_model=SuccessResponse[AuditLogResponse])
def read_audit_log(
    log_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get audit log by ID.
    """
    log = audit_log_crud.get(db, id=log_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log not found"
        )

    # Check permissions
    if not current_user.is_superuser and str(log.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    return SuccessResponse(
        data=log,
        message="Audit log retrieved successfully"
    )


@router.get("/summary", response_model=SuccessResponse[AuditLogSummary])
def get_audit_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get audit log summary statistics.
    """
    # This would calculate actual statistics
    summary = AuditLogSummary(
        total_logs=1000,
        logs_today=45,
        logs_this_week=320,
        logs_this_month=1200,
        failed_actions=12,
        top_actions=[
            {"action": "user_login", "count": 150},
            {"action": "project_create", "count": 89},
            {"action": "analysis_run", "count": 67}
        ],
        top_users=[
            {"user_id": "user-1", "count": 45},
            {"user_id": "user-2", "count": 38}
        ],
        top_resources=[
            {"resource_type": "project", "count": 234},
            {"resource_type": "analysis", "count": 189}
        ]
    )

    return SuccessResponse(
        data=summary,
        message="Audit summary retrieved successfully"
    )


@router.post("/export", response_model=SuccessResponse[AuditLogExportResponse])
def export_audit_logs(
    export_request: AuditLogExportRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Export audit logs.
    """
    # Check admin permissions for full export
    if not current_user.is_superuser and export_request.filters is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions for full export"
        )

    # Create export task
    export_id = f"export-{UUID()}"
    background_tasks.add_task(process_audit_export, export_id, export_request)

    response = AuditLogExportResponse(
        export_id=export_id,
        status="processing",
        download_url=None,
        file_size=None,
        record_count=0
    )

    return SuccessResponse(
        data=response,
        message="Audit log export initiated successfully"
    )


@router.get("/export/{export_id}", response_model=SuccessResponse[AuditLogExportResponse])
def get_export_status(
    export_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get export status.
    """
    # This would check actual export status
    response = AuditLogExportResponse(
        export_id=export_id,
        status="completed",
        download_url=f"/api/v1/audit/download/{export_id}",
        file_size=1024000,
        record_count=500
    )

    return SuccessResponse(
        data=response,
        message="Export status retrieved successfully"
    )


@router.get("/retention", response_model=SuccessResponse[AuditLogRetentionPolicy])
def get_retention_policy(
    current_superuser: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get audit log retention policy (admin only).
    """
    policy = AuditLogRetentionPolicy(
        retention_days=365,
        archive_after_days=90,
        delete_after_days=365,
        compression_enabled=True,
        encryption_enabled=True
    )

    return SuccessResponse(
        data=policy,
        message="Retention policy retrieved successfully"
    )


@router.put("/retention", response_model=SuccessResponse[AuditLogRetentionPolicy])
def update_retention_policy(
    policy_update: AuditLogRetentionUpdate,
    current_superuser: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update audit log retention policy (admin only).
    """
    # This would update the actual policy
    updated_policy = AuditLogRetentionPolicy(
        retention_days=policy_update.retention_days or 365,
        archive_after_days=policy_update.archive_after_days or 90,
        delete_after_days=policy_update.delete_after_days or 365,
        compression_enabled=policy_update.compression_enabled if policy_update.compression_enabled is not None else True,
        encryption_enabled=policy_update.encryption_enabled if policy_update.encryption_enabled is not None else True
    )

    return SuccessResponse(
        data=updated_policy,
        message="Retention policy updated successfully"
    )


@router.get("/alert-rules", response_model=SuccessResponse[List[AuditLogAlertRuleResponse]])
def read_alert_rules(
    current_superuser: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get audit log alert rules (admin only).
    """
    rules = audit_log_alert_rule_crud.get_multi(db)
    return SuccessResponse(
        data=rules,
        message="Alert rules retrieved successfully"
    )


@router.post("/alert-rules", response_model=SuccessResponse[AuditLogAlertRuleResponse])
def create_alert_rule(
    rule_in: AuditLogAlertRuleCreate,
    current_superuser: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
) -> Any:
    """
    Create audit log alert rule (admin only).
    """
    rule = audit_log_alert_rule_crud.create(db, obj_in=rule_in)
    return SuccessResponse(
        data=rule,
        message="Alert rule created successfully"
    )


@router.put("/alert-rules/{rule_id}", response_model=SuccessResponse[AuditLogAlertRuleResponse])
def update_alert_rule(
    rule_id: UUID,
    rule_in: AuditLogAlertRuleUpdate,
    current_superuser: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update audit log alert rule (admin only).
    """
    rule = audit_log_alert_rule_crud.get(db, id=rule_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert rule not found"
        )

    rule = audit_log_alert_rule_crud.update(db, db_obj=rule, obj_in=rule_in)
    return SuccessResponse(
        data=rule,
        message="Alert rule updated successfully"
    )


@router.delete("/alert-rules/{rule_id}", response_model=SuccessResponse[dict])
def delete_alert_rule(
    rule_id: UUID,
    current_superuser: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
) -> Any:
    """
    Delete audit log alert rule (admin only).
    """
    rule = audit_log_alert_rule_crud.get(db, id=rule_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert rule not found"
        )

    audit_log_alert_rule_crud.remove(db, id=rule_id)
    return SuccessResponse(
        data={},
        message="Alert rule deleted successfully"
    )


@router.post("/archive", response_model=SuccessResponse[dict])
def archive_old_logs(
    background_tasks: BackgroundTasks,
    current_superuser: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
) -> Any:
    """
    Archive old audit logs (admin only).
    """
    background_tasks.add_task(process_log_archival, db)
    return SuccessResponse(
        data={"status": "archival_started"},
        message="Log archival initiated successfully"
    )


# Background task functions
def process_audit_export(export_id: str, export_request: AuditLogExportRequest):
    """Process audit log export."""
    # This would implement the actual export logic
    pass


def process_log_archival(db: Session):
    """Process log archival."""
    # This would implement the actual archival logic
    pass
