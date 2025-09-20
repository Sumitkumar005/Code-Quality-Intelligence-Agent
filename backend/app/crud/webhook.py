"""
CRUD operations for Webhook model.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from datetime import datetime, timedelta

from app.models.webhook import (
    Webhook,
    WebhookDelivery,
    WebhookEvent,
    WebhookTemplate,
    WebhookLogEntry,
    WebhookSignature
)
from app.schemas.webhook import (
    WebhookCreate,
    WebhookUpdate,
    WebhookDeliveryCreate,
    WebhookEvent,
    WebhookTemplateCreate,
    WebhookTemplateUpdate
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class CRUDWebhook:
    """CRUD operations for Webhook model."""

    def create(self, db: Session, *, obj_in: WebhookCreate, created_by: str) -> Webhook:
        """Create a new webhook."""
        try:
            db_obj = Webhook(
                id=obj_in.id if hasattr(obj_in, 'id') else None,
                name=obj_in.name,
                url=obj_in.url,
                description=obj_in.description,
                events=obj_in.events or [],
                is_active=obj_in.is_active,
                secret=obj_in.secret,
                headers=obj_in.headers or {},
                retry_policy=obj_in.retry_policy or {},
                project_id=obj_in.project_id,
                organization_id=obj_in.organization_id,
                created_by=created_by
            )
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            logger.info(f"Created webhook: {db_obj.name} (ID: {db_obj.id})")
            return db_obj
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create webhook: {e}")
            raise

    def get(self, db: Session, *, id: str) -> Optional[Webhook]:
        """Get webhook by ID."""
        return db.query(Webhook).filter(Webhook.id == id).first()

    def get_by_url(self, db: Session, *, url: str) -> Optional[Webhook]:
        """Get webhook by URL."""
        return db.query(Webhook).filter(Webhook.url == url).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        project_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        is_active: Optional[bool] = None,
        event_type: Optional[str] = None
    ) -> List[Webhook]:
        """Get multiple webhooks with optional filtering."""
        query = db.query(Webhook)

        if project_id:
            query = query.filter(Webhook.project_id == project_id)

        if organization_id:
            query = query.filter(Webhook.organization_id == organization_id)

        if is_active is not None:
            query = query.filter(Webhook.is_active == is_active)

        if event_type:
            query = query.filter(Webhook.events.contains([event_type]))

        return query.offset(skip).limit(limit).all()

    def get_multi_by_project(
        self,
        db: Session,
        *,
        project_id: str,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[Webhook]:
        """Get all webhooks for a project."""
        query = db.query(Webhook).filter(Webhook.project_id == project_id)

        if is_active is not None:
            query = query.filter(Webhook.is_active == is_active)

        return query.offset(skip).limit(limit).all()

    def get_multi_by_organization(
        self,
        db: Session,
        *,
        organization_id: str,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[Webhook]:
        """Get all webhooks for an organization."""
        query = db.query(Webhook).filter(Webhook.organization_id == organization_id)

        if is_active is not None:
            query = query.filter(Webhook.is_active == is_active)

        return query.offset(skip).limit(limit).all()

    def update(self, db: Session, *, db_obj: Webhook, obj_in: WebhookUpdate) -> Webhook:
        """Update a webhook."""
        try:
            update_data = obj_in.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_obj, field, value)

            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            logger.info(f"Updated webhook: {db_obj.name} (ID: {db_obj.id})")
            return db_obj
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to update webhook: {e}")
            raise

    def remove(self, db: Session, *, id: str) -> Optional[Webhook]:
        """Remove a webhook."""
        try:
            obj = db.query(Webhook).filter(Webhook.id == id).first()
            if obj:
                db.delete(obj)
                db.commit()
                logger.info(f"Deleted webhook: {obj.name} (ID: {obj.id})")
                return obj
            return None
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to delete webhook: {e}")
            raise

    def get_with_stats(self, db: Session, *, id: str) -> Optional[Dict[str, Any]]:
        """Get webhook with delivery statistics."""
        webhook = self.get(db, id=id)
        if not webhook:
            return None

        # Get delivery statistics
        deliveries = db.query(WebhookDelivery).filter(WebhookDelivery.webhook_id == id).all()

        total_deliveries = len(deliveries)
        successful_deliveries = len([d for d in deliveries if d.success])
        failed_deliveries = total_deliveries - successful_deliveries

        # Calculate average response time
        avg_response_time = None
        if deliveries:
            response_times = [d.duration_ms for d in deliveries if d.duration_ms]
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)

        return {
            "webhook": webhook,
            "stats": {
                "total_deliveries": total_deliveries,
                "successful_deliveries": successful_deliveries,
                "failed_deliveries": failed_deliveries,
                "average_response_time": avg_response_time
            }
        }


class CRUDWebhookDelivery:
    """CRUD operations for WebhookDelivery model."""

    def create(self, db: Session, *, obj_in: WebhookDeliveryCreate) -> WebhookDelivery:
        """Create a new webhook delivery record."""
        try:
            db_obj = WebhookDelivery(
                id=obj_in.id if hasattr(obj_in, 'id') else None,
                webhook_id=obj_in.webhook_id,
                event_type=obj_in.event_type,
                payload=obj_in.payload,
                response_status=obj_in.response_status,
                response_body=obj_in.response_body,
                response_headers=obj_in.response_headers or {},
                duration_ms=obj_in.duration_ms,
                attempt_number=obj_in.attempt_number,
                success=obj_in.success,
                error_message=obj_in.error_message,
                project_id=obj_in.project_id,
                organization_id=obj_in.organization_id
            )
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            logger.info(f"Recorded webhook delivery: {db_obj.id} (success: {db_obj.success})")
            return db_obj
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create webhook delivery: {e}")
            raise

    def get(self, db: Session, *, id: str) -> Optional[WebhookDelivery]:
        """Get webhook delivery by ID."""
        return db.query(WebhookDelivery).filter(WebhookDelivery.id == id).first()

    def get_multi_by_webhook(
        self,
        db: Session,
        *,
        webhook_id: str,
        skip: int = 0,
        limit: int = 100,
        success: Optional[bool] = None
    ) -> List[WebhookDelivery]:
        """Get all deliveries for a webhook."""
        query = db.query(WebhookDelivery).filter(WebhookDelivery.webhook_id == webhook_id)

        if success is not None:
            query = query.filter(WebhookDelivery.success == success)

        return query.order_by(desc(WebhookDelivery.delivered_at)).offset(skip).limit(limit).all()

    def get_recent_by_webhook(
        self,
        db: Session,
        *,
        webhook_id: str,
        hours: int = 24,
        limit: int = 50
    ) -> List[WebhookDelivery]:
        """Get recent deliveries for a webhook."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return db.query(WebhookDelivery).filter(
            and_(
                WebhookDelivery.webhook_id == webhook_id,
                WebhookDelivery.delivered_at >= cutoff_time
            )
        ).order_by(desc(WebhookDelivery.delivered_at)).limit(limit).all()

    def get_failed_deliveries(
        self,
        db: Session,
        *,
        webhook_id: Optional[str] = None,
        hours: int = 24,
        limit: int = 100
    ) -> List[WebhookDelivery]:
        """Get failed deliveries."""
        query = db.query(WebhookDelivery).filter(WebhookDelivery.success == False)

        if webhook_id:
            query = query.filter(WebhookDelivery.webhook_id == webhook_id)

        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        query = query.filter(WebhookDelivery.delivered_at >= cutoff_time)

        return query.order_by(desc(WebhookDelivery.delivered_at)).limit(limit).all()

    def cleanup_old_deliveries(self, db: Session, *, days_old: int = 90) -> int:
        """Clean up old delivery records."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            result = db.query(WebhookDelivery).filter(
                WebhookDelivery.delivered_at < cutoff_date
            ).delete()

            db.commit()
            logger.info(f"Cleaned up {result} old webhook deliveries")
            return result
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to cleanup old deliveries: {e}")
            raise


class CRUDWebhookEvent:
    """CRUD operations for WebhookEvent model."""

    def create(self, db: Session, *, obj_in: WebhookEvent) -> WebhookEvent:
        """Create a new webhook event."""
        try:
            db_obj = WebhookEvent(
                id=obj_in.id if hasattr(obj_in, 'id') else None,
                event_type=obj_in.event_type,
                resource_type=obj_in.resource_type,
                resource_id=obj_in.resource_id,
                action=obj_in.action,
                data=obj_in.data,
                metadata=obj_in.metadata or {},
                project_id=obj_in.project_id,
                organization_id=obj_in.organization_id,
                source=obj_in.source
            )
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            logger.info(f"Created webhook event: {db_obj.event_type} for {db_obj.resource_type}:{db_obj.resource_id}")
            return db_obj
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create webhook event: {e}")
            raise

    def get(self, db: Session, *, id: str) -> Optional[WebhookEvent]:
        """Get webhook event by ID."""
        return db.query(WebhookEvent).filter(WebhookEvent.id == id).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        event_type: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        project_id: Optional[str] = None,
        organization_id: Optional[str] = None
    ) -> List[WebhookEvent]:
        """Get multiple webhook events with optional filtering."""
        query = db.query(WebhookEvent)

        if event_type:
            query = query.filter(WebhookEvent.event_type == event_type)

        if resource_type:
            query = query.filter(WebhookEvent.resource_type == resource_type)

        if resource_id:
            query = query.filter(WebhookEvent.resource_id == resource_id)

        if project_id:
            query = query.filter(WebhookEvent.project_id == project_id)

        if organization_id:
            query = query.filter(WebhookEvent.organization_id == organization_id)

        return query.order_by(desc(WebhookEvent.occurred_at)).offset(skip).limit(limit).all()

    def get_recent_events(
        self,
        db: Session,
        *,
        hours: int = 24,
        limit: int = 100
    ) -> List[WebhookEvent]:
        """Get recent webhook events."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return db.query(WebhookEvent).filter(
            WebhookEvent.occurred_at >= cutoff_time
        ).order_by(desc(WebhookEvent.occurred_at)).limit(limit).all()

    def cleanup_old_events(self, db: Session, *, days_old: int = 30) -> int:
        """Clean up old event records."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            result = db.query(WebhookEvent).filter(
                WebhookEvent.occurred_at < cutoff_date
            ).delete()

            db.commit()
            logger.info(f"Cleaned up {result} old webhook events")
            return result
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to cleanup old events: {e}")
            raise


class CRUDWebhookTemplate:
    """CRUD operations for WebhookTemplate model."""

    def create(self, db: Session, *, obj_in: WebhookTemplateCreate, created_by: str) -> WebhookTemplate:
        """Create a new webhook template."""
        try:
            db_obj = WebhookTemplate(
                id=obj_in.id if hasattr(obj_in, 'id') else None,
                name=obj_in.name,
                description=obj_in.description,
                event_type=obj_in.event_type,
                payload_template=obj_in.payload_template,
                headers_template=obj_in.headers_template or {},
                is_active=obj_in.is_active,
                project_id=obj_in.project_id,
                organization_id=obj_in.organization_id,
                created_by=created_by
            )
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            logger.info(f"Created webhook template: {db_obj.name} (ID: {db_obj.id})")
            return db_obj
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create webhook template: {e}")
            raise

    def get(self, db: Session, *, id: str) -> Optional[WebhookTemplate]:
        """Get webhook template by ID."""
        return db.query(WebhookTemplate).filter(WebhookTemplate.id == id).first()

    def get_by_name_and_event(self, db: Session, *, name: str, event_type: str) -> Optional[WebhookTemplate]:
        """Get webhook template by name and event type."""
        return db.query(WebhookTemplate).filter(
            and_(
                WebhookTemplate.name == name,
                WebhookTemplate.event_type == event_type
            )
        ).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        event_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        project_id: Optional[str] = None,
        organization_id: Optional[str] = None
    ) -> List[WebhookTemplate]:
        """Get multiple webhook templates with optional filtering."""
        query = db.query(WebhookTemplate)

        if event_type:
            query = query.filter(WebhookTemplate.event_type == event_type)

        if is_active is not None:
            query = query.filter(WebhookTemplate.is_active == is_active)

        if project_id:
            query = query.filter(WebhookTemplate.project_id == project_id)

        if organization_id:
            query = query.filter(WebhookTemplate.organization_id == organization_id)

        return query.order_by(desc(WebhookTemplate.created_at)).offset(skip).limit(limit).all()

    def update(self, db: Session, *, db_obj: WebhookTemplate, obj_in: WebhookTemplateUpdate) -> WebhookTemplate:
        """Update a webhook template."""
        try:
            update_data = obj_in.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_obj, field, value)

            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            logger.info(f"Updated webhook template: {db_obj.name} (ID: {db_obj.id})")
            return db_obj
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to update webhook template: {e}")
            raise

    def remove(self, db: Session, *, id: str) -> Optional[WebhookTemplate]:
        """Remove a webhook template."""
        try:
            obj = db.query(WebhookTemplate).filter(WebhookTemplate.id == id).first()
            if obj:
                db.delete(obj)
                db.commit()
                logger.info(f"Deleted webhook template: {obj.name} (ID: {obj.id})")
                return obj
            return None
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to delete webhook template: {e}")
            raise

    def increment_usage(self, db: Session, *, id: str) -> Optional[WebhookTemplate]:
        """Increment usage count for a template."""
        try:
            template = self.get(db, id=id)
            if template:
                template.usage_count += 1
                db.add(template)
                db.commit()
                db.refresh(template)
                return template
            return None
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to increment template usage: {e}")
            raise


class CRUDWebhookLogEntry:
    """CRUD operations for WebhookLogEntry model."""

    def create(self, db: Session, *, obj_in: Dict[str, Any]) -> WebhookLogEntry:
        """Create a new webhook log entry."""
        try:
            db_obj = WebhookLogEntry(
                id=obj_in.get('id'),
                webhook_id=obj_in['webhook_id'],
                level=obj_in['level'],
                message=obj_in['message'],
                event_type=obj_in.get('event_type'),
                resource_id=obj_in.get('resource_id'),
                metadata=obj_in.get('metadata', {}),
                project_id=obj_in.get('project_id'),
                organization_id=obj_in.get('organization_id')
            )
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create webhook log entry: {e}")
            raise

    def get_multi_by_webhook(
        self,
        db: Session,
        *,
        webhook_id: str,
        skip: int = 0,
        limit: int = 100,
        level: Optional[str] = None
    ) -> List[WebhookLogEntry]:
        """Get log entries for a webhook."""
        query = db.query(WebhookLogEntry).filter(WebhookLogEntry.webhook_id == webhook_id)

        if level:
            query = query.filter(WebhookLogEntry.level == level)

        return query.order_by(desc(WebhookLogEntry.created_at)).offset(skip).limit(limit).all()

    def cleanup_old_logs(self, db: Session, *, days_old: int = 30) -> int:
        """Clean up old log entries."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            result = db.query(WebhookLogEntry).filter(
                WebhookLogEntry.created_at < cutoff_date
            ).delete()

            db.commit()
            logger.info(f"Cleaned up {result} old webhook log entries")
            return result
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to cleanup old logs: {e}")
            raise


# Create CRUD instances
webhook = CRUDWebhook()
webhook_delivery = CRUDWebhookDelivery()
webhook_event = CRUDWebhookEvent()
webhook_template = CRUDWebhookTemplate()
webhook_log = CRUDWebhookLogEntry()
