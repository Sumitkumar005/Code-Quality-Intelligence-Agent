"""
CRUD operations for Organization model.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from datetime import datetime, timedelta

from app.models.organization import (
    Organization,
    OrganizationMember,
    OrganizationInvite,
    OrganizationWebhook,
    OrganizationWebhookDelivery
)
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationMemberCreate,
    OrganizationMemberUpdate,
    OrganizationInviteCreate,
    OrganizationWebhookCreate,
    OrganizationWebhookUpdate
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class CRUDOrganization:
    """CRUD operations for Organization model."""

    def create(self, db: Session, *, obj_in: OrganizationCreate, created_by: str) -> Organization:
        """Create a new organization."""
        try:
            db_obj = Organization(
                id=obj_in.id if hasattr(obj_in, 'id') else None,
                name=obj_in.name,
                description=obj_in.description,
                website=obj_in.website,
                contact_email=obj_in.contact_email,
                settings=obj_in.settings or {},
                created_by=created_by
            )
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            logger.info(f"Created organization: {db_obj.name} (ID: {db_obj.id})")
            return db_obj
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create organization: {e}")
            raise

    def get(self, db: Session, *, id: str) -> Optional[Organization]:
        """Get organization by ID."""
        return db.query(Organization).filter(Organization.id == id).first()

    def get_by_name(self, db: Session, *, name: str) -> Optional[Organization]:
        """Get organization by name."""
        return db.query(Organization).filter(Organization.name == name).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> List[Organization]:
        """Get multiple organizations with optional filtering."""
        query = db.query(Organization)

        if is_active is not None:
            query = query.filter(Organization.is_active == is_active)

        if search:
            query = query.filter(
                or_(
                    Organization.name.ilike(f"%{search}%"),
                    Organization.description.ilike(f"%{search}%")
                )
            )

        return query.offset(skip).limit(limit).all()

    def update(self, db: Session, *, db_obj: Organization, obj_in: OrganizationUpdate) -> Organization:
        """Update an organization."""
        try:
            update_data = obj_in.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_obj, field, value)

            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            logger.info(f"Updated organization: {db_obj.name} (ID: {db_obj.id})")
            return db_obj
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to update organization: {e}")
            raise

    def remove(self, db: Session, *, id: str) -> Optional[Organization]:
        """Remove an organization."""
        try:
            obj = db.query(Organization).filter(Organization.id == id).first()
            if obj:
                db.delete(obj)
                db.commit()
                logger.info(f"Deleted organization: {obj.name} (ID: {obj.id})")
                return obj
            return None
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to delete organization: {e}")
            raise

    def get_with_stats(self, db: Session, *, id: str) -> Optional[Dict[str, Any]]:
        """Get organization with statistics."""
        org = self.get(db, id=id)
        if not org:
            return None

        # Get member count
        member_count = db.query(func.count(OrganizationMember.id)).filter(
            OrganizationMember.organization_id == id
        ).scalar()

        # Get project count
        project_count = db.query(func.count("Project.id")).filter(
            "Project.organization_id" == id
        ).scalar() or 0

        # Get webhook count
        webhook_count = db.query(func.count(OrganizationWebhook.id)).filter(
            OrganizationWebhook.organization_id == id
        ).scalar()

        return {
            "organization": org,
            "stats": {
                "member_count": member_count,
                "project_count": project_count,
                "webhook_count": webhook_count
            }
        }


class CRUDOrganizationMember:
    """CRUD operations for OrganizationMember model."""

    def create(self, db: Session, *, obj_in: OrganizationMemberCreate, invited_by: Optional[str] = None) -> OrganizationMember:
        """Create a new organization member."""
        try:
            db_obj = OrganizationMember(
                id=obj_in.id if hasattr(obj_in, 'id') else None,
                organization_id=obj_in.organization_id,
                user_id=obj_in.user_id,
                role=obj_in.role,
                permissions=obj_in.permissions or [],
                invited_by=invited_by
            )
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            logger.info(f"Added member {db_obj.user_id} to organization {db_obj.organization_id}")
            return db_obj
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create organization member: {e}")
            raise

    def get(self, db: Session, *, id: str) -> Optional[OrganizationMember]:
        """Get organization member by ID."""
        return db.query(OrganizationMember).filter(OrganizationMember.id == id).first()

    def get_by_org_and_user(self, db: Session, *, organization_id: str, user_id: str) -> Optional[OrganizationMember]:
        """Get organization member by organization and user ID."""
        return db.query(OrganizationMember).filter(
            and_(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.user_id == user_id
            )
        ).first()

    def get_multi_by_organization(
        self,
        db: Session,
        *,
        organization_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[OrganizationMember]:
        """Get all members of an organization."""
        return db.query(OrganizationMember).filter(
            OrganizationMember.organization_id == organization_id
        ).offset(skip).limit(limit).all()

    def update(self, db: Session, *, db_obj: OrganizationMember, obj_in: OrganizationMemberUpdate) -> OrganizationMember:
        """Update an organization member."""
        try:
            update_data = obj_in.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_obj, field, value)

            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            logger.info(f"Updated organization member: {db_obj.id}")
            return db_obj
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to update organization member: {e}")
            raise

    def remove(self, db: Session, *, id: str) -> Optional[OrganizationMember]:
        """Remove an organization member."""
        try:
            obj = db.query(OrganizationMember).filter(OrganizationMember.id == id).first()
            if obj:
                db.delete(obj)
                db.commit()
                logger.info(f"Removed member {obj.user_id} from organization {obj.organization_id}")
                return obj
            return None
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to remove organization member: {e}")
            raise


class CRUDOrganizationInvite:
    """CRUD operations for OrganizationInvite model."""

    def create(self, db: Session, *, obj_in: OrganizationInviteCreate, invited_by: str) -> OrganizationInvite:
        """Create a new organization invite."""
        try:
            db_obj = OrganizationInvite(
                id=obj_in.id if hasattr(obj_in, 'id') else None,
                organization_id=obj_in.organization_id,
                email=obj_in.email,
                role=obj_in.role,
                permissions=obj_in.permissions or [],
                message=obj_in.message,
                token=obj_in.token if hasattr(obj_in, 'token') else None,
                expires_at=obj_in.expires_at,
                invited_by=invited_by
            )
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            logger.info(f"Created invite for {db_obj.email} to organization {db_obj.organization_id}")
            return db_obj
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create organization invite: {e}")
            raise

    def get(self, db: Session, *, id: str) -> Optional[OrganizationInvite]:
        """Get organization invite by ID."""
        return db.query(OrganizationInvite).filter(OrganizationInvite.id == id).first()

    def get_by_token(self, db: Session, *, token: str) -> Optional[OrganizationInvite]:
        """Get organization invite by token."""
        return db.query(OrganizationInvite).filter(OrganizationInvite.token == token).first()

    def get_by_org_and_email(self, db: Session, *, organization_id: str, email: str) -> Optional[OrganizationInvite]:
        """Get organization invite by organization and email."""
        return db.query(OrganizationInvite).filter(
            and_(
                OrganizationInvite.organization_id == organization_id,
                OrganizationInvite.email == email
            )
        ).first()

    def get_multi_by_organization(
        self,
        db: Session,
        *,
        organization_id: str,
        skip: int = 0,
        limit: int = 100,
        include_expired: bool = False
    ) -> List[OrganizationInvite]:
        """Get all invites for an organization."""
        query = db.query(OrganizationInvite).filter(
            OrganizationInvite.organization_id == organization_id
        )

        if not include_expired:
            query = query.filter(OrganizationInvite.expires_at > datetime.utcnow())

        return query.offset(skip).limit(limit).all()

    def update(self, db: Session, *, db_obj: OrganizationInvite, accepted_at: Optional[datetime] = None) -> OrganizationInvite:
        """Update an organization invite."""
        try:
            if accepted_at:
                db_obj.accepted_at = accepted_at

            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            logger.info(f"Updated organization invite: {db_obj.id}")
            return db_obj
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to update organization invite: {e}")
            raise

    def remove(self, db: Session, *, id: str) -> Optional[OrganizationInvite]:
        """Remove an organization invite."""
        try:
            obj = db.query(OrganizationInvite).filter(OrganizationInvite.id == id).first()
            if obj:
                db.delete(obj)
                db.commit()
                logger.info(f"Deleted organization invite: {obj.id}")
                return obj
            return None
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to delete organization invite: {e}")
            raise

    def cleanup_expired(self, db: Session) -> int:
        """Clean up expired invites."""
        try:
            result = db.query(OrganizationInvite).filter(
                and_(
                    OrganizationInvite.expires_at <= datetime.utcnow(),
                    OrganizationInvite.accepted_at.is_(None)
                )
            ).delete()

            db.commit()
            logger.info(f"Cleaned up {result} expired organization invites")
            return result
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to cleanup expired invites: {e}")
            raise


class CRUDOrganizationWebhook:
    """CRUD operations for OrganizationWebhook model."""

    def create(self, db: Session, *, obj_in: OrganizationWebhookCreate, created_by: str) -> OrganizationWebhook:
        """Create a new organization webhook."""
        try:
            db_obj = OrganizationWebhook(
                id=obj_in.id if hasattr(obj_in, 'id') else None,
                organization_id=obj_in.organization_id,
                name=obj_in.name,
                url=obj_in.url,
                description=obj_in.description,
                events=obj_in.events or [],
                is_active=obj_in.is_active,
                secret=obj_in.secret,
                headers=obj_in.headers or {},
                retry_policy=obj_in.retry_policy or {},
                created_by=created_by
            )
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            logger.info(f"Created webhook {db_obj.name} for organization {db_obj.organization_id}")
            return db_obj
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create organization webhook: {e}")
            raise

    def get(self, db: Session, *, id: str) -> Optional[OrganizationWebhook]:
        """Get organization webhook by ID."""
        return db.query(OrganizationWebhook).filter(OrganizationWebhook.id == id).first()

    def get_multi_by_organization(
        self,
        db: Session,
        *,
        organization_id: str,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[OrganizationWebhook]:
        """Get all webhooks for an organization."""
        query = db.query(OrganizationWebhook).filter(
            OrganizationWebhook.organization_id == organization_id
        )

        if is_active is not None:
            query = query.filter(OrganizationWebhook.is_active == is_active)

        return query.offset(skip).limit(limit).all()

    def update(self, db: Session, *, db_obj: OrganizationWebhook, obj_in: OrganizationWebhookUpdate) -> OrganizationWebhook:
        """Update an organization webhook."""
        try:
            update_data = obj_in.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_obj, field, value)

            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            logger.info(f"Updated organization webhook: {db_obj.id}")
            return db_obj
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to update organization webhook: {e}")
            raise

    def remove(self, db: Session, *, id: str) -> Optional[OrganizationWebhook]:
        """Remove an organization webhook."""
        try:
            obj = db.query(OrganizationWebhook).filter(OrganizationWebhook.id == id).first()
            if obj:
                db.delete(obj)
                db.commit()
                logger.info(f"Deleted organization webhook: {obj.id}")
                return obj
            return None
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to delete organization webhook: {e}")
            raise


# Create CRUD instances
organization = CRUDOrganization()
organization_member = CRUDOrganizationMember()
organization_invite = CRUDOrganizationInvite()
organization_webhook = CRUDOrganizationWebhook()
