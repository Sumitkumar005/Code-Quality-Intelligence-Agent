"""
Background Notification Tasks

This module contains Celery tasks for sending various types of notifications
including email notifications, webhook notifications, and in-app notifications.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from celery import Celery

from ..core.celery_app import celery_app
from ..services.notifications.notification_manager import NotificationManager
from ..services.notifications.email_service import EmailService
from ..models.analysis import Analysis
from ..models.project import Project
from ..models.report import Report
from ..models.user import User

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def send_analysis_completion_notification(
    self,
    analysis_id: str,
    user_id: str,
    notification_type: str = "email"
) -> Dict[str, Any]:
    """
    Send notification when analysis is completed.

    Args:
        analysis_id: Analysis identifier
        user_id: User identifier to notify
        notification_type: Type of notification to send

    Returns:
        Dictionary containing notification results
    """
    logger.info(f"Starting analysis completion notification for analysis {analysis_id}")

    try:
        notification_manager = NotificationManager()

        # Get notification preferences (this would typically come from user settings)
        notification_config = {
            "email": True,
            "webhook": False,
            "in_app": True
        }

        # Send notification based on type
        if notification_type == "email" and notification_config.get("email"):
            result = notification_manager.send_analysis_notification(
                analysis_id=analysis_id,
                user_id=user_id,
                notification_method="email"
            )
        elif notification_type == "webhook" and notification_config.get("webhook"):
            result = notification_manager.send_analysis_notification(
                analysis_id=analysis_id,
                user_id=user_id,
                notification_method="webhook"
            )
        else:
            result = notification_manager.send_analysis_notification(
                analysis_id=analysis_id,
                user_id=user_id,
                notification_method="in_app"
            )

        logger.info(f"Completed analysis completion notification for analysis {analysis_id}")
        return {
            "analysis_id": analysis_id,
            "user_id": user_id,
            "status": "completed",
            "notification_type": notification_type,
            "result": result
        }

    except Exception as e:
        logger.error(f"Error in analysis completion notification {analysis_id}: {e}")
        raise self.retry(countdown=60, exc=e)


@celery_app.task(bind=True, max_retries=3)
def send_report_generation_notification(
    self,
    report_id: str,
    user_id: str,
    notification_type: str = "email"
) -> Dict[str, Any]:
    """
    Send notification when report generation is completed.

    Args:
        report_id: Report identifier
        user_id: User identifier to notify
        notification_type: Type of notification to send

    Returns:
        Dictionary containing notification results
    """
    logger.info(f"Starting report generation notification for report {report_id}")

    try:
        notification_manager = NotificationManager()

        # Get notification preferences
        notification_config = {
            "email": True,
            "webhook": False,
            "in_app": True
        }

        # Send notification based on type
        if notification_type == "email" and notification_config.get("email"):
            result = notification_manager.send_report_notification(
                report_id=report_id,
                user_id=user_id,
                notification_method="email"
            )
        elif notification_type == "webhook" and notification_config.get("webhook"):
            result = notification_manager.send_report_notification(
                report_id=report_id,
                user_id=user_id,
                notification_method="webhook"
            )
        else:
            result = notification_manager.send_report_notification(
                report_id=report_id,
                user_id=user_id,
                notification_method="in_app"
            )

        logger.info(f"Completed report generation notification for report {report_id}")
        return {
            "report_id": report_id,
            "user_id": user_id,
            "status": "completed",
            "notification_type": notification_type,
            "result": result
        }

    except Exception as e:
        logger.error(f"Error in report generation notification {report_id}: {e}")
        raise self.retry(countdown=60, exc=e)


@celery_app.task(bind=True, max_retries=3)
def send_security_alert_notification(
    self,
    analysis_id: str,
    user_id: str,
    severity: str = "high",
    notification_type: str = "email"
) -> Dict[str, Any]:
    """
    Send security alert notification for critical findings.

    Args:
        analysis_id: Analysis identifier
        user_id: User identifier to notify
        severity: Severity level of the alert
        notification_type: Type of notification to send

    Returns:
        Dictionary containing notification results
    """
    logger.info(f"Starting security alert notification for analysis {analysis_id}")

    try:
        notification_manager = NotificationManager()

        # Security alerts should always be sent via email regardless of preferences
        result = notification_manager.send_security_alert(
            analysis_id=analysis_id,
            user_id=user_id,
            severity=severity,
            notification_method=notification_type
        )

        logger.info(f"Completed security alert notification for analysis {analysis_id}")
        return {
            "analysis_id": analysis_id,
            "user_id": user_id,
            "status": "completed",
            "severity": severity,
            "notification_type": notification_type,
            "result": result
        }

    except Exception as e:
        logger.error(f"Error in security alert notification {analysis_id}: {e}")
        raise self.retry(countdown=30, exc=e)  # Retry sooner for security alerts


@celery_app.task
def send_weekly_digest_notification(
    user_id: str,
    week_start_date: str,
    notification_type: str = "email"
) -> Dict[str, Any]:
    """
    Send weekly digest notification with summary of activities.

    Args:
        user_id: User identifier to notify
        week_start_date: Start date of the week for the digest
        notification_type: Type of notification to send

    Returns:
        Dictionary containing notification results
    """
    logger.info(f"Starting weekly digest notification for user {user_id}")

    try:
        notification_manager = NotificationManager()

        # Generate weekly digest data
        digest_data = {
            "week_start": week_start_date,
            "analyses_completed": 0,
            "reports_generated": 0,
            "security_issues": 0,
            "projects_monitored": 0
        }

        # Send digest notification
        result = notification_manager.send_weekly_digest(
            user_id=user_id,
            digest_data=digest_data,
            notification_method=notification_type
        )

        logger.info(f"Completed weekly digest notification for user {user_id}")
        return {
            "user_id": user_id,
            "status": "completed",
            "week_start": week_start_date,
            "notification_type": notification_type,
            "result": result
        }

    except Exception as e:
        logger.error(f"Error in weekly digest notification {user_id}: {e}")
        return {
            "user_id": user_id,
            "status": "failed",
            "error": str(e)
        }


@celery_app.task
def send_project_status_notification(
    project_id: str,
    user_id: str,
    status_type: str,
    notification_type: str = "email"
) -> Dict[str, Any]:
    """
    Send project status change notification.

    Args:
        project_id: Project identifier
        user_id: User identifier to notify
        status_type: Type of status change
        notification_type: Type of notification to send

    Returns:
        Dictionary containing notification results
    """
    logger.info(f"Starting project status notification for project {project_id}")

    try:
        notification_manager = NotificationManager()

        # Send project status notification
        result = notification_manager.send_project_notification(
            project_id=project_id,
            user_id=user_id,
            status_type=status_type,
            notification_method=notification_type
        )

        logger.info(f"Completed project status notification for project {project_id}")
        return {
            "project_id": project_id,
            "user_id": user_id,
            "status": "completed",
            "status_type": status_type,
            "notification_type": notification_type,
            "result": result
        }

    except Exception as e:
        logger.error(f"Error in project status notification {project_id}: {e}")
        return {
            "project_id": project_id,
            "user_id": user_id,
            "status": "failed",
            "error": str(e)
        }


@celery_app.task(bind=True, max_retries=3)
def send_system_maintenance_notification(
    self,
    user_id: str,
    maintenance_type: str,
    scheduled_time: str,
    notification_type: str = "email"
) -> Dict[str, Any]:
    """
    Send system maintenance notification.

    Args:
        user_id: User identifier to notify
        maintenance_type: Type of maintenance
        scheduled_time: Scheduled time for maintenance
        notification_type: Type of notification to send

    Returns:
        Dictionary containing notification results
    """
    logger.info(f"Starting system maintenance notification for user {user_id}")

    try:
        notification_manager = NotificationManager()

        # Send maintenance notification
        result = notification_manager.send_maintenance_notification(
            user_id=user_id,
            maintenance_type=maintenance_type,
            scheduled_time=scheduled_time,
            notification_method=notification_type
        )

        logger.info(f"Completed system maintenance notification for user {user_id}")
        return {
            "user_id": user_id,
            "status": "completed",
            "maintenance_type": maintenance_type,
            "scheduled_time": scheduled_time,
            "notification_type": notification_type,
            "result": result
        }

    except Exception as e:
        logger.error(f"Error in system maintenance notification {user_id}: {e}")
        raise self.retry(countdown=120, exc=e)  # Retry later for maintenance notifications


@celery_app.task
def send_batch_notifications(
    notification_requests: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Send multiple notifications in batch.

    Args:
        notification_requests: List of notification requests

    Returns:
        Dictionary containing batch notification results
    """
    logger.info(f"Starting batch notification processing for {len(notification_requests)} requests")

    try:
        notification_manager = NotificationManager()
        results = []

        for request in notification_requests:
            try:
                notification_type = request.get("notification_type", "email")
                result = notification_manager.send_notification(
                    notification_type=notification_type,
                    **request
                )
                results.append({
                    "request_id": request.get("id"),
                    "status": "completed",
                    "result": result
                })
            except Exception as e:
                logger.error(f"Error processing notification request {request.get('id')}: {e}")
                results.append({
                    "request_id": request.get("id"),
                    "status": "failed",
                    "error": str(e)
                })

        logger.info(f"Completed batch notification processing")
        return {
            "status": "completed",
            "total_requests": len(notification_requests),
            "successful": len([r for r in results if r["status"] == "completed"]),
            "failed": len([r for r in results if r["status"] == "failed"]),
            "results": results
        }

    except Exception as e:
        logger.error(f"Error in batch notification processing: {e}")
        return {
            "status": "failed",
            "error": str(e),
            "total_requests": len(notification_requests)
        }


@celery_app.task
def send_custom_notification(
    user_id: str,
    subject: str,
    message: str,
    notification_type: str = "email",
    priority: str = "normal"
) -> Dict[str, Any]:
    """
    Send custom notification to user.

    Args:
        user_id: User identifier to notify
        subject: Notification subject
        message: Notification message
        notification_type: Type of notification to send
        priority: Priority level of the notification

    Returns:
        Dictionary containing notification results
    """
    logger.info(f"Starting custom notification for user {user_id}")

    try:
        notification_manager = NotificationManager()

        # Send custom notification
        result = notification_manager.send_custom_notification(
            user_id=user_id,
            subject=subject,
            message=message,
            notification_method=notification_type,
            priority=priority
        )

        logger.info(f"Completed custom notification for user {user_id}")
        return {
            "user_id": user_id,
            "status": "completed",
            "subject": subject,
            "notification_type": notification_type,
            "priority": priority,
            "result": result
        }

    except Exception as e:
        logger.error(f"Error in custom notification {user_id}: {e}")
        return {
            "user_id": user_id,
            "status": "failed",
            "error": str(e)
        }


@celery_app.task
def send_notification_digest(
    user_id: str,
    time_period: str = "daily",
    notification_type: str = "email"
) -> Dict[str, Any]:
    """
    Send notification digest for a time period.

    Args:
        user_id: User identifier to notify
        time_period: Time period for digest (daily, weekly, monthly)
        notification_type: Type of notification to send

    Returns:
        Dictionary containing notification results
    """
    logger.info(f"Starting {time_period} digest notification for user {user_id}")

    try:
        notification_manager = NotificationManager()

        # Generate digest data based on time period
        digest_data = {
            "time_period": time_period,
            "notifications": [],
            "summary": {}
        }

        # Send digest notification
        result = notification_manager.send_digest_notification(
            user_id=user_id,
            digest_data=digest_data,
            time_period=time_period,
            notification_method=notification_type
        )

        logger.info(f"Completed {time_period} digest notification for user {user_id}")
        return {
            "user_id": user_id,
            "status": "completed",
            "time_period": time_period,
            "notification_type": notification_type,
            "result": result
        }

    except Exception as e:
        logger.error(f"Error in {time_period} digest notification {user_id}: {e}")
        return {
            "user_id": user_id,
            "status": "failed",
            "error": str(e)
        }


@celery_app.task
def cleanup_notification_history(days_old: int = 90) -> Dict[str, Any]:
    """
    Clean up old notification history records.

    Args:
        days_old: Number of days old notifications to clean up

    Returns:
        Dictionary containing cleanup statistics
    """
    logger.info(f"Starting cleanup task for notifications older than {days_old} days")

    try:
        notification_manager = NotificationManager()

        # Clean up old notifications
        result = notification_manager.cleanup_old_notifications(days_old=days_old)

        logger.info(f"Completed notification cleanup task. Cleaned {result.get('deleted_count', 0)} old notifications")
        return {
            "status": "completed",
            "deleted_count": result.get("deleted_count", 0),
            "cutoff_date": result.get("cutoff_date")
        }

    except Exception as e:
        logger.error(f"Error in notification cleanup task: {e}")
        return {
            "status": "failed",
            "error": str(e)
        }


@celery_app.task
def resend_failed_notifications(
    max_retries: int = 3,
    notification_type: str = "all"
) -> Dict[str, Any]:
    """
    Resend failed notifications.

    Args:
        max_retries: Maximum number of retries to attempt
        notification_type: Type of notifications to resend

    Returns:
        Dictionary containing resend results
    """
    logger.info(f"Starting resend task for failed notifications (max_retries: {max_retries})")

    try:
        notification_manager = NotificationManager()

        # Resend failed notifications
        result = notification_manager.resend_failed_notifications(
            max_retries=max_retries,
            notification_type=notification_type
        )

        logger.info(f"Completed resend task for failed notifications")
        return {
            "status": "completed",
            "resent_count": result.get("resent_count", 0),
            "failed_count": result.get("failed_count", 0),
            "notification_type": notification_type
        }

    except Exception as e:
        logger.error(f"Error in resend failed notifications task: {e}")
        return {
            "status": "failed",
            "error": str(e)
        }
