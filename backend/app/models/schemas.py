"""
Pydantic schemas for API requests and responses
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class AnalyzeRequest(BaseModel):
    input: str = Field(..., description="Path to code or GitHub URL")
    options: Optional[Dict[str, Any]] = Field(default_factory=dict)
    data: Optional[Dict[str, Any]] = Field(default_factory=dict)

class AnalyzeResponse(BaseModel):
    report_id: str
    status: str
    message: str

class QARequest(BaseModel):
    question: str = Field(..., description="Question about the codebase")
    session_id: Optional[str] = Field(None, description="Q&A session ID")
    report_id: Optional[str] = Field(None, description="Analysis report ID")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)

class QAResponse(BaseModel):
    answer: str
    session_id: str
    question_id: str
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    sources: Optional[List[str]] = Field(default_factory=list)

class QASession(BaseModel):
    session_id: str
    report_id: Optional[str] = None
    created_at: datetime
    last_activity: datetime
    question_count: int = 0
    
class IssueSchema(BaseModel):
    file: str
    type: str
    severity: str
    line: int
    message: str
    suggestion: str

class AnalysisSummary(BaseModel):
    total_files: int
    total_lines: int
    languages: List[str]
    quality_score: int

class AnalysisResult(BaseModel):
    report_id: str
    status: str
    summary: AnalysisSummary
    issues: List[IssueSchema]
    recommendations: List[str]