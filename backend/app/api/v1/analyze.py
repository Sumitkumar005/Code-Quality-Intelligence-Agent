"""
Analysis API endpoints
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
import structlog
from typing import List, Optional
import uuid

from app.models.schemas import AnalyzeRequest, AnalyzeResponse
from app.services.analysis_service import AnalysisService
from app.core.dependencies import get_analysis_service

router = APIRouter()
logger = structlog.get_logger(__name__)
limiter = Limiter(key_func=get_remote_address)

@router.post("/analyze", response_model=AnalyzeResponse)
# @limiter.limit("10/minute")  # Temporarily disabled for testing
async def analyze_repository(
    analyze_request: AnalyzeRequest,
    background_tasks: BackgroundTasks,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    Analyze a code repository for quality issues

    Accepts local paths or GitHub URLs and returns a report ID for tracking progress.
    """
    try:
        logger.info(f"Starting analysis for: {analyze_request.input}")

        # Generate unique report ID
        report_id = str(uuid.uuid4())

        # Start background analysis
        background_tasks.add_task(
            analysis_service.analyze_repository_background,
            report_id,
            analyze_request.dict()
        )

        return AnalyzeResponse(
            report_id=report_id,
            status="processing",
            message="Analysis started successfully"
        )

    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analyze/{report_id}/status")
async def get_analysis_status(
    report_id: str,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """Get the status of an ongoing analysis"""
    try:
        status = await analysis_service.get_analysis_status(report_id)
        if not status:
            raise HTTPException(status_code=404, detail="Report not found")

        return status

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/analyze/{report_id}")
async def cancel_analysis(
    report_id: str,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """Cancel an ongoing analysis"""
    try:
        success = await analysis_service.cancel_analysis(report_id)
        if not success:
            raise HTTPException(status_code=404, detail="Report not found or already completed")

        return {"message": "Analysis cancelled successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel analysis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analyze/supported-languages")
async def get_supported_languages():
    """Get list of supported programming languages"""
    return {
        "languages": [
            {"name": "Python", "extensions": [".py"], "features": ["ast", "security", "complexity"]},
            {"name": "JavaScript", "extensions": [".js", ".jsx"], "features": ["ast", "security", "complexity"]},
            {"name": "TypeScript", "extensions": [".ts", ".tsx"], "features": ["ast", "security", "complexity"]},
            {"name": "Java", "extensions": [".java"], "features": ["ast", "complexity"]},
            {"name": "Go", "extensions": [".go"], "features": ["ast", "complexity"]},
            {"name": "Rust", "extensions": [".rs"], "features": ["ast", "complexity"]},
        ]
    }
