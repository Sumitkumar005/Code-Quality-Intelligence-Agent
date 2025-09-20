"""
Q&A API endpoints for code quality questions.
"""

from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.logging import get_logger
from app.services.ai import ai_service

router = APIRouter()
logger = get_logger(__name__)


@router.post("/ask", response_model=schemas.conversation.Conversation)
def ask_question(
    *,
    db: Session = Depends(deps.get_db),
    question_in: schemas.conversation.ConversationCreate,
    background_tasks: BackgroundTasks,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Ask a question about code quality.
    """
    try:
        # Create conversation record
        conversation = crud.conversation.create(
            db=db, obj_in=question_in, user_id=current_user.id
        )

        # Get AI response in background
        background_tasks.add_task(
            process_question,
            db=db,
            conversation_id=conversation.id,
            question=question_in.message,
            project_id=question_in.project_id,
            user_id=current_user.id
        )

        return conversation

    except Exception as e:
        logger.error(f"Failed to process question: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process question",
        )


@router.get("/conversations", response_model=schemas.conversation.ConversationListResponse)
def list_conversations(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    project_id: Optional[str] = Query(None),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    List Q&A conversations.
    """
    conversations = crud.conversation.get_multi(
        db=db,
        user_id=current_user.id,
        project_id=project_id,
        skip=skip,
        limit=limit
    )

    total = len(conversations)  # In production, use a count query

    return schemas.conversation.ConversationListResponse(
        conversations=conversations,
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.get("/conversations/{conversation_id}", response_model=schemas.conversation.Conversation)
def get_conversation(
    *,
    db: Session = Depends(deps.get_db),
    conversation_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get a specific conversation.
    """
    conversation = crud.conversation.get(db=db, id=conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    # Check if user owns this conversation
    if conversation.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    return conversation


@router.post("/conversations/{conversation_id}/messages", response_model=schemas.conversation.ConversationMessage)
def add_message_to_conversation(
    *,
    db: Session = Depends(deps.get_db),
    conversation_id: str,
    message_in: schemas.conversation.ConversationMessageCreate,
    background_tasks: BackgroundTasks,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Add a message to a conversation.
    """
    conversation = crud.conversation.get(db=db, id=conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    # Check if user owns this conversation
    if conversation.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    # Add message
    message = crud.conversation.create_message(
        db=db, obj_in=message_in, conversation_id=conversation_id
    )

    # Get AI response if this is a user message
    if message_in.role == "user":
        background_tasks.add_task(
            process_followup_question,
            db=db,
            conversation_id=conversation_id,
            message_id=message.id,
            question=message_in.content,
            project_id=conversation.project_id,
            user_id=current_user.id
        )

    return message


@router.get("/conversations/{conversation_id}/messages", response_model=List[schemas.conversation.ConversationMessage])
def get_conversation_messages(
    *,
    db: Session = Depends(deps.get_db),
    conversation_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get messages for a conversation.
    """
    conversation = crud.conversation.get(db=db, id=conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    # Check if user owns this conversation
    if conversation.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    messages = crud.conversation.get_messages(
        db=db, conversation_id=conversation_id, skip=skip, limit=limit
    )

    return messages


@router.delete("/conversations/{conversation_id}")
def delete_conversation(
    *,
    db: Session = Depends(deps.get_db),
    conversation_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a conversation.
    """
    conversation = crud.conversation.get(db=db, id=conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    # Check if user owns this conversation
    if conversation.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    crud.conversation.remove(db=db, id=conversation_id)
    return {"message": "Conversation deleted successfully"}


@router.post("/feedback", response_model=schemas.conversation.ConversationFeedback)
def submit_feedback(
    *,
    db: Session = Depends(deps.get_db),
    feedback_in: schemas.conversation.ConversationFeedbackCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Submit feedback on a conversation or message.
    """
    feedback = crud.conversation.create_feedback(
        db=db, obj_in=feedback_in, user_id=current_user.id
    )
    return feedback


@router.get("/search", response_model=schemas.conversation.ConversationSearchResponse)
def search_conversations(
    *,
    db: Session = Depends(deps.get_db),
    query: str = Query(..., min_length=1),
    project_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Search through conversations.
    """
    conversations = crud.conversation.search(
        db=db,
        user_id=current_user.id,
        query=query,
        project_id=project_id,
        skip=skip,
        limit=limit
    )

    total = len(conversations)  # In production, use a count query

    return schemas.conversation.ConversationSearchResponse(
        conversations=conversations,
        total=total,
        query=query,
        page=skip // limit + 1,
        size=limit
    )


@router.get("/suggestions", response_model=List[str])
def get_suggestions(
    *,
    db: Session = Depends(deps.get_db),
    project_id: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=20),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get suggested questions based on project context.
    """
    try:
        suggestions = ai_service.get_suggestions(
            user_id=current_user.id,
            project_id=project_id,
            limit=limit
        )
        return suggestions
    except Exception as e:
        logger.error(f"Failed to get suggestions: {e}")
        return []


@router.post("/analyze-code")
def analyze_code_snippet(
    *,
    db: Session = Depends(deps.get_db),
    analysis_in: schemas.conversation.CodeAnalysisCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Analyze a code snippet for quality issues.
    """
    try:
        # This would integrate with the analysis services
        # For now, return a mock response
        result = {
            "analysis_id": "mock-analysis-id",
            "status": "completed",
            "issues": [],
            "suggestions": [
                "Consider adding error handling",
                "This function could be optimized",
                "Add documentation for better maintainability"
            ],
            "score": 85.0
        }

        return result

    except Exception as e:
        logger.error(f"Failed to analyze code: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze code",
        )


@router.get("/trending-topics", response_model=List[schemas.conversation.TrendingTopic])
def get_trending_topics(
    *,
    db: Session = Depends(deps.get_db),
    project_id: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=20),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get trending topics/questions.
    """
    try:
        # Mock trending topics
        topics = [
            {
                "topic": "Error handling best practices",
                "count": 25,
                "trend": "up"
            },
            {
                "topic": "Code optimization techniques",
                "count": 18,
                "trend": "stable"
            },
            {
                "topic": "Security vulnerabilities",
                "count": 15,
                "trend": "up"
            }
        ]

        return topics[:limit]

    except Exception as e:
        logger.error(f"Failed to get trending topics: {e}")
        return []


async def process_question(
    db: Session,
    conversation_id: str,
    question: str,
    project_id: Optional[str] = None,
    user_id: str = None
) -> None:
    """
    Process a question and generate AI response.
    """
    try:
        # Get AI response
        response = await ai_service.process_question(
            question=question,
            project_id=project_id,
            user_id=user_id
        )

        # Update conversation with AI response
        crud.conversation.update_response(
            db=db,
            conversation_id=conversation_id,
            response=response
        )

    except Exception as e:
        logger.error(f"Failed to process question {conversation_id}: {e}")
        # Update conversation with error
        crud.conversation.update_response(
            db=db,
            conversation_id=conversation_id,
            response="I apologize, but I encountered an error while processing your question. Please try again."
        )


async def process_followup_question(
    db: Session,
    conversation_id: str,
    message_id: str,
    question: str,
    project_id: Optional[str] = None,
    user_id: str = None
) -> None:
    """
    Process a follow-up question and generate AI response.
    """
    try:
        # Get AI response
        response = await ai_service.process_question(
            question=question,
            project_id=project_id,
            user_id=user_id,
            conversation_id=conversation_id
        )

        # Add AI response as a message
        message_in = schemas.conversation.ConversationMessageCreate(
            role="assistant",
            content=response,
            metadata={"type": "ai_response"}
        )

        crud.conversation.create_message(
            db=db, obj_in=message_in, conversation_id=conversation_id
        )

    except Exception as e:
        logger.error(f"Failed to process follow-up question {message_id}: {e}")
        # Add error message
        error_message = schemas.conversation.ConversationMessageCreate(
            role="assistant",
            content="I apologize, but I encountered an error while processing your question. Please try again.",
            metadata={"type": "error", "error": str(e)}
        )

        crud.conversation.create_message(
            db=db, obj_in=error_message, conversation_id=conversation_id
        )
