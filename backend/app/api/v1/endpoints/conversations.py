"""
Conversations endpoints for the CQIA application.
"""

from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.conversation import (
    ConversationResponse,
    ConversationWithMessages,
    ConversationCreate,
    ConversationUpdate,
    ConversationMessageResponse,
    AIQueryRequest,
    AIQueryResponse,
    ConversationTemplateResponse,
    AIInsightsRequest,
    AIInsightsResponse,
    CodeExplanationRequest,
    CodeExplanationResponse,
)
from app.schemas.base import SuccessResponse, PaginatedResponse
from app.crud.conversation import (
    conversation_crud,
    conversation_message_crud,
    conversation_template_crud
)

router = APIRouter()


@router.get("/", response_model=SuccessResponse[PaginatedResponse[ConversationResponse]])
def read_conversations(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Retrieve user's conversations.
    """
    conversations = conversation_crud.get_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    total = conversation_crud.count()  # Would need user-specific count

    return SuccessResponse(
        data=PaginatedResponse(
            items=conversations,
            total=total,
            page=skip // limit + 1,
            size=len(conversations),
            pages=(total + limit - 1) // limit
        ),
        message="Conversations retrieved successfully"
    )


@router.post("/", response_model=SuccessResponse[ConversationResponse])
def create_conversation(
    conversation_in: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Create new conversation.
    """
    conversation_in.user_id = current_user.id
    conversation = conversation_crud.create(db, obj_in=conversation_in)
    return SuccessResponse(
        data=conversation,
        message="Conversation created successfully"
    )


@router.get("/{conversation_id}", response_model=SuccessResponse[ConversationWithMessages])
def read_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get conversation by ID.
    """
    conversation = conversation_crud.get_with_messages(db, id=conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Check if user owns this conversation
    if conversation["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    return SuccessResponse(
        data=conversation,
        message="Conversation retrieved successfully"
    )


@router.put("/{conversation_id}", response_model=SuccessResponse[ConversationResponse])
def update_conversation(
    conversation_id: UUID,
    conversation_in: ConversationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update conversation.
    """
    conversation = conversation_crud.get(db, id=conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Check if user owns this conversation
    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    conversation = conversation_crud.update(db, db_obj=conversation, obj_in=conversation_in)
    return SuccessResponse(
        data=conversation,
        message="Conversation updated successfully"
    )


@router.post("/{conversation_id}/messages", response_model=SuccessResponse[AIQueryResponse])
def send_message(
    conversation_id: UUID,
    message_in: AIQueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Send message to conversation.
    """
    conversation = conversation_crud.get(db, id=conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Check if user owns this conversation
    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Create user message
    from app.schemas.conversation import ConversationMessageCreate
    user_message = ConversationMessageCreate(
        conversation_id=conversation_id,
        role="user",
        content=message_in.query,
        metadata=message_in.context
    )
    conversation_message_crud.create(db, obj_in=user_message)

    # Generate AI response (placeholder)
    ai_response_content = f"I understand you asked: '{message_in.query}'. This is a placeholder response from the AI assistant."

    # Create AI message
    ai_message = ConversationMessageCreate(
        conversation_id=conversation_id,
        role="assistant",
        content=ai_response_content,
        token_count=len(ai_response_content.split())  # Rough estimate
    )
    ai_message_obj = conversation_message_crud.create(db, obj_in=ai_message)

    response = AIQueryResponse(
        conversation_id=str(conversation_id),
        message_id=str(ai_message_obj.id),
        response=ai_response_content,
        sources=[],  # Would be populated with actual sources
        confidence=0.85,
        token_usage={"prompt": 50, "completion": 100, "total": 150}
    )

    return SuccessResponse(
        data=response,
        message="Message sent successfully"
    )


@router.get("/templates", response_model=SuccessResponse[List[ConversationTemplateResponse]])
def read_conversation_templates(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get available conversation templates.
    """
    templates = conversation_template_crud.get_active(db)
    return SuccessResponse(
        data=templates,
        message="Conversation templates retrieved successfully"
    )


@router.post("/insights", response_model=SuccessResponse[AIInsightsResponse])
def get_ai_insights(
    insights_request: AIInsightsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get AI insights for project/analysis.
    """
    # This would integrate with AI insights service
    insights_response = AIInsightsResponse(
        insights=[
            {
                "type": "quality",
                "title": "Code Quality Improvement",
                "description": "Consider implementing more comprehensive error handling",
                "priority": "medium",
                "confidence": 0.8
            }
        ],
        recommendations=[
            "Add input validation to all public methods",
            "Implement comprehensive logging",
            "Consider adding unit tests for critical paths"
        ],
        trends=[
            {
                "metric": "code_quality",
                "trend": "improving",
                "change_percentage": 15.5,
                "period": "last_30_days"
            }
        ],
        priorities=[
            {
                "item": "Security vulnerabilities",
                "priority": "high",
                "description": "Address 3 high-priority security issues"
            }
        ]
    )

    return SuccessResponse(
        data=insights_response,
        message="AI insights generated successfully"
    )


@router.post("/explain-code", response_model=SuccessResponse[CodeExplanationResponse])
def explain_code(
    explanation_request: CodeExplanationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get AI explanation for code.
    """
    # This would integrate with AI code explanation service
    explanation_response = CodeExplanationResponse(
        explanation="This code appears to be a function that processes user input and validates it against certain criteria. The function includes error handling and returns a boolean result.",
        complexity="medium",
        suggestions=[
            "Consider adding more specific error messages",
            "The function could benefit from input sanitization",
            "Consider breaking down into smaller, more focused functions"
        ],
        related_issues=[
            {
                "id": "issue-1",
                "title": "Missing input validation",
                "severity": "medium",
                "description": "Input parameters should be validated before processing"
            }
        ]
    )

    return SuccessResponse(
        data=explanation_response,
        message="Code explanation generated successfully"
    )


@router.delete("/{conversation_id}", response_model=SuccessResponse[dict])
def delete_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Delete conversation.
    """
    conversation = conversation_crud.get(db, id=conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Check if user owns this conversation
    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    conversation_crud.remove(db, id=conversation_id)
    return SuccessResponse(
        data={},
        message="Conversation deleted successfully"
    )
