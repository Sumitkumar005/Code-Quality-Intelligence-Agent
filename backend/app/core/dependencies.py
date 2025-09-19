"""
Dependency injection for FastAPI
"""

from app.services.analysis_service import AnalysisService

# Global service instances
_analysis_service = None

def get_analysis_service() -> AnalysisService:
    """Get analysis service instance"""
    global _analysis_service
    if _analysis_service is None:
        _analysis_service = AnalysisService()
    return _analysis_service

def get_qa_service():
    """Get QA service instance (fallback to analysis service)"""
    return get_analysis_service()