"""
Q&A API endpoints for interactive code analysis
"""

from fastapi import APIRouter, HTTPException, Depends
from slowapi import Limiter
from slowapi.util import get_remote_address
import structlog
from pydantic import BaseModel

from app.services.analysis_service import AnalysisService
from app.core.dependencies import get_analysis_service

router = APIRouter()
logger = structlog.get_logger(__name__)
limiter = Limiter(key_func=get_remote_address)

class QuestionRequest(BaseModel):
    question: str
    report_id: str

class QuestionResponse(BaseModel):
    answer: str
    report_id: str

@router.post("/ask", response_model=QuestionResponse)
@limiter.limit("30/minute")
async def ask_question(
    request: QuestionRequest,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """Ask a question about the analysis results"""
    try:
        answer = await analysis_service.ask_question(request.report_id, request.question)
        
        return QuestionResponse(
            answer=answer,
            report_id=request.report_id
        )
        
    except Exception as e:
        logger.error(f"Q&A failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))