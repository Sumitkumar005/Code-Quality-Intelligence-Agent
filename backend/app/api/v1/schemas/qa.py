"""
Q&A schemas for API v1.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class QARequest(BaseModel):
    """Q&A request schema."""
    project_id: str = Field(..., description="Project ID")
    question: str = Field(..., description="Question to ask")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    conversation_id: Optional[str] = Field(None, description="Conversation ID")
    analysis_id: Optional[str] = Field(None, description="Analysis ID for context")
    include_code_snippets: bool = Field(default=True, description="Include code snippets in response")
    max_context_files: int = Field(default=5, description="Maximum number of context files")


class QAResponse(BaseModel):
    """Q&A response schema."""
    answer: str = Field(..., description="AI-generated answer")
    conversation_id: str = Field(..., description="Conversation ID")
    message_id: str = Field(..., description="Message ID")
    confidence: float = Field(..., description="Confidence score")
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="Source references")
    suggestions: List[str] = Field(default_factory=list, description="Suggested follow-up questions")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ConversationResponse(BaseModel):
    """Conversation response schema."""
    id: str = Field(..., description="Conversation ID")
    project_id: str = Field(..., description="Project ID")
    title: Optional[str] = Field(None, description="Conversation title")
    context: Dict[str, Any] = Field(default_factory=dict, description="Conversation context")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    message_count: int = Field(default=0, description="Number of messages")


class MessageResponse(BaseModel):
    """Message response schema."""
    id: str = Field(..., description="Message ID")
    conversation_id: str = Field(..., description="Conversation ID")
    role: str = Field(..., description="Message role (user/assistant)")
    content: str = Field(..., description="Message content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Message metadata")
    created_at: datetime = Field(..., description="Creation timestamp")


class InsightResponse(BaseModel):
    """Insight response schema."""
    id: str = Field(..., description="Insight ID")
    project_id: str = Field(..., description="Project ID")
    analysis_id: Optional[str] = Field(None, description="Analysis ID")
    type: str = Field(..., description="Insight type")
    title: str = Field(..., description="Insight title")
    description: str = Field(..., description="Insight description")
    severity: str = Field(..., description="Insight severity")
    confidence: float = Field(..., description="Confidence score")
    actionable: bool = Field(..., description="Is insight actionable")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(..., description="Creation timestamp")
