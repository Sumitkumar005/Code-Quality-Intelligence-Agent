"""
Conversation model and related database entities for AI chat functionality.
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Text, ForeignKey, Boolean, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from .base import CQIA_Base


class Conversation(CQIA_Base):
    """Conversation model for AI chat sessions."""

    __tablename__ = "conversations"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    project_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE")
    )

    # Conversation metadata
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # AI model information
    ai_model: Mapped[str] = mapped_column(String(100), default="gpt-4", nullable=False)
    temperature: Mapped[float] = mapped_column(Float, default=0.7, nullable=False)

    # Usage tracking
    message_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Settings
    settings: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="conversations")
    project: Mapped[Optional["Project"]] = relationship("Project", back_populates="conversations")
    messages: Mapped[List["ConversationMessage"]] = relationship(
        "ConversationMessage", back_populates="conversation", cascade="all, delete-orphan"
    )

    @property
    def last_message_at(self) -> Optional[datetime]:
        """Get timestamp of last message."""
        if self.messages:
            return max(msg.created_at for msg in self.messages)
        return None

    def add_message(self, role: str, content: str, metadata: Optional[dict] = None) -> "ConversationMessage":
        """Add a new message to the conversation."""
        message = ConversationMessage(
            conversation_id=self.id,
            role=role,
            content=content,
            metadata=metadata or {}
        )
        self.messages.append(message)
        self.message_count += 1
        return message

    def get_messages(self, limit: Optional[int] = None) -> List["ConversationMessage"]:
        """Get conversation messages, optionally limited."""
        messages = sorted(self.messages, key=lambda x: x.created_at)
        if limit:
            return messages[-limit:]
        return messages

    def get_context(self, max_tokens: int = 4000) -> List["ConversationMessage"]:
        """Get conversation context for AI, respecting token limits."""
        messages = self.get_messages()
        # Simple token estimation (rough approximation)
        total_tokens = 0
        context_messages = []

        for message in reversed(messages):
            # Rough token count estimation
            message_tokens = len(message.content.split()) * 1.3  # Rough approximation
            if total_tokens + message_tokens > max_tokens:
                break
            context_messages.insert(0, message)
            total_tokens += message_tokens

        return context_messages


class ConversationMessage(CQIA_Base):
    """Individual message in a conversation."""

    __tablename__ = "conversation_messages"

    conversation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )

    # Message content
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # user, assistant, system
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Metadata
    token_count: Mapped[Optional[int]] = mapped_column(Integer)
    message_metadata: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Relationships
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")

    @property
    def is_user_message(self) -> bool:
        """Check if this is a user message."""
        return self.role == "user"

    @property
    def is_assistant_message(self) -> bool:
        """Check if this is an assistant message."""
        return self.role == "assistant"

    @property
    def is_system_message(self) -> bool:
        """Check if this is a system message."""
        return self.role == "system"


class ConversationTemplate(CQIA_Base):
    """Template for conversation starters and system prompts."""

    __tablename__ = "conversation_templates"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(50), default="general", nullable=False)

    # Template content
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    user_prompt_template: Mapped[Optional[str]] = mapped_column(Text)
    context_instructions: Mapped[Optional[str]] = mapped_column(Text)

    # Configuration
    config: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Usage tracking
    usage_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    def increment_usage(self):
        """Increment usage count."""
        self.usage_count += 1

    def create_conversation(self, user_id: str, project_id: Optional[str] = None) -> Conversation:
        """Create a new conversation from this template."""
        return Conversation(
            user_id=user_id,
            project_id=project_id,
            title=self.name,
            ai_model=self.config.get("model", "gpt-4"),
            temperature=self.config.get("temperature", 0.7),
            settings=self.config
        )
