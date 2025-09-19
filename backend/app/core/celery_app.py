"""
Celery application configuration for background task processing.
Handles analysis tasks, report generation, and other async operations.
"""

from celery import Celery
from celery.schedules import crontab
import logging

from .config import settings

logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    "cqia",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.analysis_tasks", "app.tasks.report_tasks", "app.tasks.cleanup_tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer=settings.CELERY_TASK_SERIALIZER,
    result_serializer=settings.CELERY_RESULT_SERIALIZER,
    accept_content=settings.CELERY_ACCEPT_CONTENT,
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,  # Tasks acknowledged after completion
    worker_prefetch_multiplier=1,  # Fair task distribution
    task_default_queue="cqia",
    task_routes={
        "app.tasks.analysis_tasks.*": {"queue": "analysis"},
        "app.tasks.report_tasks.*": {"queue": "reports"},
        "app.tasks.cleanup_tasks.*": {"queue": "cleanup"},
    },
    beat_schedule={
        # Clean up old analysis results daily at 2 AM
        "cleanup-old-analyses": {
            "task": "app.tasks.cleanup_tasks.cleanup_old_analyses",
            "schedule": crontab(hour=2, minute=0),
        },
        # Generate daily summary reports at 6 AM
        "generate-daily-reports": {
            "task": "app.tasks.report_tasks.generate_daily_summary",
            "schedule": crontab(hour=6, minute=0),
        },
        # Update repository statistics hourly
        "update-repo-stats": {
            "task": "app.tasks.analysis_tasks.update_repository_stats",
            "schedule": crontab(minute=0),
        },
    },
)

# Task base class for shared functionality
class CQIA_Task(celery_app.Task):
    """Base task class with error handling and logging."""

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure."""
        logger.error(f"Task {task_id} failed: {exc}")
        # Could send notifications, update database, etc.
        super().on_failure(exc, task_id, args, kwargs, einfo)

    def on_success(self, retval, task_id, args, kwargs):
        """Handle task success."""
        logger.info(f"Task {task_id} completed successfully")
        super().on_success(retval, task_id, args, kwargs)

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Handle task retry."""
        logger.warning(f"Task {task_id} retrying: {exc}")
        super().on_retry(exc, task_id, args, kwargs, einfo)


# Update task classes
celery_app.Task = CQIA_Task


# Task result handling
@celery_app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery setup."""
    logger.info(f"Request: {self.request!r}")


# Health check task
@celery_app.task(bind=True)
def health_check(self):
    """Health check task for monitoring."""
    return {
        "status": "healthy",
        "timestamp": self.request.eta or self.request.received,
        "worker": self.request.hostname,
    }


# Utility functions
def get_task_result(task_id: str):
    """Get result of a Celery task."""
    result = celery_app.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None,
        "error": str(result.info) if result.failed() else None,
    }


def revoke_task(task_id: str, terminate: bool = False):
    """Revoke a Celery task."""
    celery_app.control.revoke(task_id, terminate=terminate)


def get_active_tasks():
    """Get information about active tasks."""
    inspect = celery_app.control.inspect()
    return {
        "active": inspect.active(),
        "scheduled": inspect.scheduled(),
        "reserved": inspect.reserved(),
    }


def get_worker_stats():
    """Get worker statistics."""
    inspect = celery_app.control.inspect()
    return inspect.stats()


# Task monitoring
def setup_task_monitoring():
    """Setup task monitoring and metrics collection."""
    from celery.events import EventReceiver
    from kombu import Connection

    def process_event(event):
        """Process Celery events for monitoring."""
        logger.debug(f"Celery event: {event}")

    try:
        with Connection(settings.CELERY_BROKER_URL) as connection:
            receiver = EventReceiver(connection, handlers={
                '*': process_event
            })
            receiver.capture(limit=None, timeout=None, wakeup=True)
    except Exception as e:
        logger.error(f"Failed to setup task monitoring: {e}")


if __name__ == "__main__":
    celery_app.start()
