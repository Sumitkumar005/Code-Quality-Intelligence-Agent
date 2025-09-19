"""
Pydantic schemas for conversation-related operations.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import Field

from .base import CQIA_BaseModel, CQIA_BaseCreate, CQIA_BaseUpdate, CQIA_BaseResponse


class ConversationMessageBase(CQIA_BaseModel):
    """Base conversation message schema."""

    role: str = Field(..., description="Message role (user/assistant/system)")
    content: str = Field(..., description="Message content")
    token_count: Optional[int] = Field(None, description="Token count")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Message metadata")


class ConversationMessageCreate(ConversationMessageBase, CQIA_BaseCreate):
    """Schema for creating a conversation message."""

    conversation_id: str = Field(..., description="Conversation ID")


class ConversationMessageResponse(ConversationMessageBase, CQIA_BaseResponse):
    """Schema for conversation message response data."""

    conversation_id: str = Field(..., description="Conversation ID")

    # Computed properties
    is_user_message: bool = Field(..., description="Is user message")
    is_assistant_message: bool = Field(..., description="Is assistant message")
    is_system_message: bool = Field(..., description="Is system message")


class ConversationTemplateBase(CQIA_BaseModel):
    """Base conversation template schema."""

    name: str = Field(..., description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    category: str = Field("general", description="Template category")
    system_prompt: str = Field(..., description="System prompt")
    user_prompt_template: Optional[str] = Field(None, description="User prompt template")
    context_instructions: Optional[str] = Field(None, description="Context instructions")
    config: Dict[str, Any] = Field(default_factory=dict, description="Template configuration")


class ConversationTemplateCreate(ConversationTemplateBase, CQIA_BaseCreate):
    """Schema for creating a conversation template."""

    pass


class ConversationTemplateUpdate(CQIA_BaseUpdate):
    """Schema for updating a conversation template."""

    name: Optional[str] = Field(None, description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    system_prompt: Optional[str] = Field(None, description="System prompt")
    user_prompt_template: Optional[str] = Field(None, description="User prompt template")
    context_instructions: Optional[str] = Field(None, description="Context instructions")
    config: Optional[Dict[str, Any]] = Field(None, description="Template configuration")
    is_active: Optional[bool] = Field(None, description="Active status")


class ConversationTemplateResponse(ConversationTemplateBase, CQIA_BaseResponse):
    """Schema for conversation template response data."""

    is_active: bool = Field(..., description="Active status")
    is_default: bool = Field(..., description="Default template")
    usage_count: int = Field(..., description="Usage count")


class ConversationBase(CQIA_BaseModel):
    """Base conversation schema."""

    user_id: str = Field(..., description="User ID")
    project_id: Optional[str] = Field(None, description="Project ID")
    title: str = Field(..., description="Conversation title")
    description: Optional[str] = Field(None, description="Conversation description")
    ai_model: str = Field("gpt-4", description="AI model")
    temperature: float = Field(0.7, description="Temperature setting")


class ConversationCreate(ConversationBase, CQIA_BaseCreate):
    """Schema for creating a conversation."""

    settings: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Conversation settings")


class ConversationUpdate(CQIA_BaseUpdate):
    """Schema for updating a conversation."""

    title: Optional[str] = Field(None, description="Conversation title")
    description: Optional[str] = Field(None, description="Conversation description")
    ai_model: Optional[str] = Field(None, description="AI model")
    temperature: Optional[float] = Field(None, description="Temperature setting")
    settings: Optional[Dict[str, Any]] = Field(None, description="Conversation settings")
    is_active: Optional[bool] = Field(None, description="Active status")
    is_archived: Optional[bool] = Field(None, description="Archive status")


class ConversationResponse(ConversationBase, CQIA_BaseResponse):
    """Schema for conversation response data."""

    is_active: bool = Field(..., description="Active status")
    is_archived: bool = Field(..., description="Archive status")
    message_count: int = Field(..., description="Message count")
    token_count: int = Field(..., description="Token count")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Conversation settings")

    # Computed properties
    last_message_at: Optional[datetime] = Field(None, description="Last message timestamp")


class ConversationWithMessages(ConversationResponse):
    """Conversation response with messages."""

    messages: List[ConversationMessageResponse] = Field(default_factory=list, description="Conversation messages")


class AIQueryRequest(CQIA_BaseModel):
    """Schema for AI query requests."""

    query: str = Field(..., description="User query")
    conversation_id: Optional[str] = Field(None, description="Existing conversation ID")
    project_id: Optional[str] = Field(None, description="Project context")
    analysis_id: Optional[str] = Field(None, description="Analysis context")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")


class AIQueryResponse(CQIA_BaseModel):
    """Schema for AI query responses."""

    conversation_id: str = Field(..., description="Conversation ID")
    message_id: str = Field(..., description="Message ID")
    response: str = Field(..., description="AI response")
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="Response sources")
    confidence: Optional[float] = Field(None, description="Response confidence")
    token_usage: Optional[Dict[str, int]] = Field(None, description="Token usage statistics")


class ConversationContext(CQIA_BaseModel):
    """Schema for conversation context."""

    conversation_id: str = Field(..., description="Conversation ID")
    messages: List[ConversationMessageResponse] = Field(..., description="Context messages")
    project_info: Optional[Dict[str, Any]] = Field(None, description="Project information")
    analysis_info: Optional[Dict[str, Any]] = Field(None, description="Analysis information")
    codebase_context: Optional[Dict[str, Any]] = Field(None, description="Codebase context")


class AIInsightsRequest(CQIA_BaseModel):
    """Schema for AI insights requests."""

    project_id: str = Field(..., description="Project ID")
    analysis_id: Optional[str] = Field(None, description="Analysis ID")
    focus_areas: Optional[List[str]] = Field(None, description="Focus areas")
    insight_types: Optional[List[str]] = Field(None, description="Insight types")


class AIInsightsResponse(CQIA_BaseModel):
    """Schema for AI insights responses."""

    insights: List[Dict[str, Any]] = Field(default_factory=list, description="Generated insights")
    recommendations: List[Dict[str, Any]] = Field(default_factory=list, description="Recommendations")
    trends: List[Dict[str, Any]] = Field(default_factory=list, description="Trend analysis")
    priorities: List[Dict[str, Any]] = Field(default_factory=list, description="Priority items")


class CodeExplanationRequest(CQIA_BaseModel):
    """Schema for code explanation requests."""

    code: str = Field(..., description="Code to explain")
    language: str = Field(..., description="Programming language")
    context: Optional[str] = Field(None, description="Additional context")
    analysis_id: Optional[str] = Field(None, description="Related analysis")


class CodeExplanationResponse(CQIA_BaseModel):
    """Schema for code explanation responses."""

    explanation: str = Field(..., description="Code explanation")
    complexity: Optional[str] = Field(None, description="Complexity assessment")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")
    related_issues: List[Dict[str, Any]] = Field(default_factory=list, description="Related issues")
