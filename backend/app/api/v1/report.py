"""
Report API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from slowapi import Limiter
from slowapi.util import get_remote_address
import structlog

router = APIRouter()
logger = structlog.get_logger(__name__)
limiter = Limiter(key_func=get_remote_address)

from fastapi import HTTPException

@router.get("/report/{report_id}")
async def get_report(report_id: str):
    """Get analysis report"""
    # Use analysis service to get report data
    from app.core.dependencies import get_analysis_service
    analysis_service = get_analysis_service()
    report = await analysis_service.get_analysis_status(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return report
