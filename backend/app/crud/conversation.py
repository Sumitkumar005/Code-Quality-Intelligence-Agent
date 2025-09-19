"""
CRUD operations for Conversation model.
"""

from typing import Any, Dict, Optional, Union, List
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.conversation import Conversation, ConversationMessage, ConversationTemplate
from app.schemas.conversation import ConversationCreate, ConversationUpdate, ConversationMessageCreate


class CRUDConversation:
    """CRUD operations for Conversation model."""

    def get(self, db: Session, *, id: UUID) -> Optional[Conversation]:
        """Get conversation by ID."""
        return db.query(Conversation).filter(Conversation.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Conversation]:
        """Get multiple conversations."""
        return db.query(Conversation).offset(skip).limit(limit).all()

    def get_by_user(
        self, db: Session, *, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Conversation]:
        """Get conversations for a specific user."""
        return db.query(Conversation).filter(Conversation.user_id == user_id).offset(skip).limit(limit).all()

    def get_with_messages(self, db: Session, *, id: UUID) -> Optional[Dict[str, Any]]:
        """Get conversation with messages."""
        conversation = self.get(db, id=id)
        if not conversation:
            return None

        messages = db.query(ConversationMessage).filter(ConversationMessage.conversation_id == id).all()

        return {
            "id": conversation.id,
            "user_id": conversation.user_id,
            "project_id": conversation.project_id,
            "title": conversation.title,
            "description": conversation.description,
            "ai_model": conversation.ai_model,
            "temperature": conversation.temperature,
            "is_active": conversation.is_active,
            "is_archived": conversation.is_archived,
            "message_count": conversation.message_count,
            "token_count": conversation.token_count,
            "settings": conversation.settings,
            "created_at": conversation.created_at,
            "updated_at": conversation.updated_at,
            "last_message_at": conversation.last_message_at,
            "messages": messages
        }

    def create(self, db: Session, *, obj_in: ConversationCreate) -> Conversation:
        """Create new conversation."""
        db_obj = Conversation(
            user_id=obj_in.user_id,
            project_id=obj_in.project_id,
            title=obj_in.title,
            description=obj_in.description,
            ai_model=obj_in.ai_model,
            temperature=obj_in.temperature,
            settings=obj_in.settings,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: Conversation, obj_in: Union[ConversationUpdate, Dict[str, Any]]
    ) -> Conversation:
        """Update conversation."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        for field in update_data:
            setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: UUID) -> Conversation:
        """Remove conversation."""
        obj = db.query(Conversation).get(id)
        db.delete(obj)
        db.commit()
        return obj

    def count(self, db: Session) -> int:
        """Count total conversations."""
        return db.query(Conversation).count()


class CRUDConversationMessage:
    """CRUD operations for ConversationMessage model."""

    def get(self, db: Session, *, id: UUID) -> Optional[ConversationMessage]:
        """Get message by ID."""
        return db.query(ConversationMessage).filter(ConversationMessage.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ConversationMessage]:
        """Get multiple messages."""
        return db.query(ConversationMessage).offset(skip).limit(limit).all()

    def get_by_conversation(
        self, db: Session, *, conversation_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[ConversationMessage]:
        """Get messages for a specific conversation."""
        return db.query(ConversationMessage).filter(ConversationMessage.conversation_id == conversation_id).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: ConversationMessageCreate) -> ConversationMessage:
        """Create new message."""
        db_obj = ConversationMessage(
            conversation_id=obj_in.conversation_id,
            role=obj_in.role,
            content=obj_in.content,
            token_count=obj_in.token_count,
            metadata=obj_in.metadata,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: UUID) -> ConversationMessage:
        """Remove message."""
        obj = db.query(ConversationMessage).get(id)
        db.delete(obj)
        db.commit()
        return obj


class CRUDConversationTemplate:
    """CRUD operations for ConversationTemplate model."""

    def get(self, db: Session, *, id: UUID) -> Optional[ConversationTemplate]:
        """Get template by ID."""
        return db.query(ConversationTemplate).filter(ConversationTemplate.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ConversationTemplate]:
        """Get multiple templates."""
        return db.query(ConversationTemplate).offset(skip).limit(limit).all()

    def get_active(self, db: Session) -> List[ConversationTemplate]:
        """Get active templates."""
        return db.query(ConversationTemplate).filter(ConversationTemplate.is_active == True).all()

    def create(self, db: Session, *, obj_in: Any) -> ConversationTemplate:
        """Create new template."""
        db_obj = ConversationTemplate(
            name=obj_in.name,
            description=obj_in.description,
            category=obj_in.category,
            system_prompt=obj_in.system_prompt,
            user_prompt_template=obj_in.user_prompt_template,
            context_instructions=obj_in.context_instructions,
            config=obj_in.config,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: ConversationTemplate, obj_in: Any) -> ConversationTemplate:
        """Update template."""
        update_data = obj_in.dict(exclude_unset=True)

        for field in update_data:
            setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: UUID) -> ConversationTemplate:
        """Remove template."""
        obj = db.query(ConversationTemplate).get(id)
        db.delete(obj)
        db.commit()
        return obj


conversation_crud = CRUDConversation()
conversation_message_crud = CRUDConversationMessage()
conversation_template_crud = CRUDConversationTemplate()
