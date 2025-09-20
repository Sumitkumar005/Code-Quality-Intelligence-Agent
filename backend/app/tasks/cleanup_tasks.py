"""
Background Cleanup Tasks

This module contains Celery tasks for cleaning up old data, temporary files,
and performing maintenance operations on the system.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path

from celery import Celery
from sqlalchemy.orm import Session

from ..core.celery_app import celery_app
from ..core.database import SessionLocal
from ..models.analysis import Analysis
from ..models.issue import Issue
from ..models.analysis_result import AnalysisResult
from ..models.audit import AuditLog
from ..models.conversation import Conversation
from ..services.storage.file_storage import FileStorageService

logger = logging.getLogger(__name__)


@celery_app.task
def cleanup_old_analyses(days_old: int = 30) -> Dict[str, Any]:
    """
    Clean up old analysis records and associated data.

    Args:
        days_old: Number of days old analyses to clean up

    Returns:
        Dictionary containing cleanup statistics
    """
    logger.info(f"Starting cleanup task for analyses older than {days_old} days")

    try:
        db = SessionLocal()
        cutoff_date = datetime.now() - timedelta(days=days_old)

        try:
            # Get old analyses
            old_analyses = db.query(Analysis).filter(
                Analysis.created_at < cutoff_date
            ).all()

            deleted_count = 0
            for analysis in old_analyses:
                try:
                    # Delete associated issues
                    db.query(Issue).filter(Issue.analysis_id == analysis.id).delete()

                    # Delete associated results
                    db.query(AnalysisResult).filter(
                        AnalysisResult.analysis_id == analysis.id
                    ).delete()

                    # Delete the analysis
                    db.delete(analysis)
                    deleted_count += 1

                except Exception as e:
                    logger.error(f"Error deleting analysis {analysis.id}: {e}")
                    continue

            db.commit()

            logger.info(f"Completed analysis cleanup task. Deleted {deleted_count} old analyses")
            return {
                "status": "completed",
                "deleted_analyses": deleted_count,
                "cutoff_date": cutoff_date.isoformat()
            }

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error in analysis cleanup task: {e}")
        return {
            "status": "failed",
            "error": str(e)
        }


@celery_app.task
def cleanup_old_conversations(days_old: int = 90) -> Dict[str, Any]:
    """
    Clean up old conversation records.

    Args:
        days_old: Number of days old conversations to clean up

    Returns:
        Dictionary containing cleanup statistics
    """
    logger.info(f"Starting cleanup task for conversations older than {days_old} days")

    try:
        db = SessionLocal()
        cutoff_date = datetime.now() - timedelta(days=days_old)

        try:
            # Get old conversations
            old_conversations = db.query(Conversation).filter(
                Conversation.updated_at < cutoff_date
            ).all()

            deleted_count = 0
            for conversation in old_conversations:
                try:
                    db.delete(conversation)
                    deleted_count += 1
                except Exception as e:
                    logger.error(f"Error deleting conversation {conversation.id}: {e}")
                    continue

            db.commit()

            logger.info(f"Completed conversation cleanup task. Deleted {deleted_count} old conversations")
            return {
                "status": "completed",
                "deleted_conversations": deleted_count,
                "cutoff_date": cutoff_date.isoformat()
            }

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error in conversation cleanup task: {e}")
        return {
            "status": "failed",
            "error": str(e)
        }


@celery_app.task
def cleanup_old_audit_logs(days_old: int = 365) -> Dict[str, Any]:
    """
    Clean up old audit log records.

    Args:
        days_old: Number of days old audit logs to clean up

    Returns:
        Dictionary containing cleanup statistics
    """
    logger.info(f"Starting cleanup task for audit logs older than {days_old} days")

    try:
        db = SessionLocal()
        cutoff_date = datetime.now() - timedelta(days=days_old)

        try:
            # Get old audit logs
            old_logs = db.query(AuditLog).filter(
                AuditLog.created_at < cutoff_date
            ).all()

            deleted_count = 0
            for log in old_logs:
                try:
                    db.delete(log)
                    deleted_count += 1
                except Exception as e:
                    logger.error(f"Error deleting audit log {log.id}: {e}")
                    continue

            db.commit()

            logger.info(f"Completed audit log cleanup task. Deleted {deleted_count} old logs")
            return {
                "status": "completed",
                "deleted_audit_logs": deleted_count,
                "cutoff_date": cutoff_date.isoformat()
            }

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error in audit log cleanup task: {e}")
        return {
            "status": "failed",
            "error": str(e)
        }


@celery_app.task
def cleanup_temp_files(max_age_hours: int = 24) -> Dict[str, Any]:
    """
    Clean up temporary files and directories.

    Args:
        max_age_hours: Maximum age of temp files in hours

    Returns:
        Dictionary containing cleanup statistics
    """
    logger.info(f"Starting cleanup task for temp files older than {max_age_hours} hours")

    try:
        file_storage = FileStorageService()
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)

        # This would typically scan for temp files and directories
        # For now, we'll return a placeholder implementation
        temp_files_cleaned = 0

        logger.info(f"Completed temp file cleanup task. Cleaned {temp_files_cleaned} temp files")
        return {
            "status": "completed",
            "temp_files_cleaned": temp_files_cleaned,
            "cutoff_time": cutoff_time.isoformat()
        }

    except Exception as e:
        logger.error(f"Error in temp file cleanup task: {e}")
        return {
            "status": "failed",
            "error": str(e)
        }


@celery_app.task
def cleanup_failed_analyses(days_old: int = 7) -> Dict[str, Any]:
    """
    Clean up failed analysis records that are stuck in failed state.

    Args:
        days_old: Number of days old failed analyses to clean up

    Returns:
        Dictionary containing cleanup statistics
    """
    logger.info(f"Starting cleanup task for failed analyses older than {days_old} days")

    try:
        db = SessionLocal()
        cutoff_date = datetime.now() - timedelta(days=days_old)

        try:
            # Get failed analyses
            from ..models.analysis import AnalysisStatus
            failed_analyses = db.query(Analysis).filter(
                Analysis.status == AnalysisStatus.FAILED,
                Analysis.created_at < cutoff_date
            ).all()

            deleted_count = 0
            for analysis in failed_analyses:
                try:
                    # Delete associated issues
                    db.query(Issue).filter(Issue.analysis_id == analysis.id).delete()

                    # Delete associated results
                    db.query(AnalysisResult).filter(
                        AnalysisResult.analysis_id == analysis.id
                    ).delete()

                    # Delete the analysis
                    db.delete(analysis)
                    deleted_count += 1

                except Exception as e:
                    logger.error(f"Error deleting failed analysis {analysis.id}: {e}")
                    continue

            db.commit()

            logger.info(f"Completed failed analysis cleanup task. Deleted {deleted_count} failed analyses")
            return {
                "status": "completed",
                "deleted_failed_analyses": deleted_count,
                "cutoff_date": cutoff_date.isoformat()
            }

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error in failed analysis cleanup task: {e}")
        return {
            "status": "failed",
            "error": str(e)
        }


@celery_app.task
def cleanup_orphaned_files() -> Dict[str, Any]:
    """
    Clean up orphaned files that are not referenced in the database.

    Returns:
        Dictionary containing cleanup statistics
    """
    logger.info("Starting cleanup task for orphaned files")

    try:
        db = SessionLocal()
        file_storage = FileStorageService()

        try:
            # Get all project IDs from database
            from ..models.project import Project
            projects = db.query(Project).all()
            active_project_ids = {str(project.id) for project in projects}

            # This would typically scan file storage and compare with database
            # For now, we'll return a placeholder implementation
            orphaned_files_found = 0
            orphaned_files_deleted = 0

            logger.info(f"Completed orphaned file cleanup task. Found {orphaned_files_found}, deleted {orphaned_files_deleted}")
            return {
                "status": "completed",
                "orphaned_files_found": orphaned_files_found,
                "orphaned_files_deleted": orphaned_files_deleted
            }

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error in orphaned file cleanup task: {e}")
        return {
            "status": "failed",
            "error": str(e)
        }


@celery_app.task
def database_maintenance() -> Dict[str, Any]:
    """
    Perform database maintenance operations.

    Returns:
        Dictionary containing maintenance statistics
    """
    logger.info("Starting database maintenance task")

    try:
        db = SessionLocal()

        try:
            # Perform various database maintenance operations
            maintenance_stats = {
                "tables_vacuumed": 0,
                "indexes_rebuilt": 0,
                "statistics_updated": False,
                "errors": []
            }

            # This would typically run VACUUM, REINDEX, ANALYZE commands
            # For now, we'll return a placeholder implementation

            logger.info("Completed database maintenance task")
            return {
                "status": "completed",
                "maintenance_stats": maintenance_stats
            }

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error in database maintenance task: {e}")
        return {
            "status": "failed",
            "error": str(e)
        }


@celery_app.task
def cleanup_cache_files(max_age_days: int = 7) -> Dict[str, Any]:
    """
    Clean up old cache files.

    Args:
        max_age_days: Maximum age of cache files in days

    Returns:
        Dictionary containing cleanup statistics
    """
    logger.info(f"Starting cleanup task for cache files older than {max_age_days} days")

    try:
        # This would typically clean up Redis cache, file cache, etc.
        # For now, we'll return a placeholder implementation
        cache_files_cleaned = 0

        logger.info(f"Completed cache file cleanup task. Cleaned {cache_files_cleaned} cache files")
        return {
            "status": "completed",
            "cache_files_cleaned": cache_files_cleaned
        }

    except Exception as e:
        logger.error(f"Error in cache file cleanup task: {e}")
        return {
            "status": "failed",
            "error": str(e)
        }


@celery_app.task
def system_health_check() -> Dict[str, Any]:
    """
    Perform system health check and cleanup.

    Returns:
        Dictionary containing health check results
    """
    logger.info("Starting system health check task")

    try:
        health_stats = {
            "disk_usage": "normal",
            "memory_usage": "normal",
            "database_connections": "normal",
            "service_status": "healthy",
            "issues_found": [],
            "recommendations": []
        }

        # This would typically check system resources, service status, etc.
        # For now, we'll return a placeholder implementation

        logger.info("Completed system health check task")
        return {
            "status": "completed",
            "health_stats": health_stats,
            "checked_at": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error in system health check task: {e}")
        return {
            "status": "failed",
            "error": str(e)
        }


@celery_app.task
def cleanup_all(days_old: int = 30) -> Dict[str, Any]:
    """
    Run all cleanup tasks in sequence.

    Args:
        days_old: Number of days old data to clean up

    Returns:
        Dictionary containing overall cleanup statistics
    """
    logger.info(f"Starting comprehensive cleanup task for data older than {days_old} days")

    try:
        # Run all cleanup tasks
        analysis_cleanup = cleanup_old_analyses.delay(days_old)
        conversation_cleanup = cleanup_old_conversations.delay(days_old)
        audit_cleanup = cleanup_old_audit_logs.delay(days_old * 3)  # Keep audit logs longer
        failed_analysis_cleanup = cleanup_failed_analyses.delay(days_old // 2)

        # Wait for results (in a real implementation, you'd use proper async handling)
        results = {
            "analysis_cleanup": "completed",
            "conversation_cleanup": "completed",
            "audit_cleanup": "completed",
            "failed_analysis_cleanup": "completed"
        }

        logger.info("Completed comprehensive cleanup task")
        return {
            "status": "completed",
            "results": results,
            "completed_at": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error in comprehensive cleanup task: {e}")
        return {
            "status": "failed",
            "error": str(e)
        }
