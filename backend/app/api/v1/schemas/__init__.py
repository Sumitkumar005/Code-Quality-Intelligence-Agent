"""
API v1 schemas package.
"""

from .auth import (
    LoginRequest, LoginResponse, RefreshTokenRequest, RefreshTokenResponse,
    UserResponse, TokenData, UserCreate, UserUpdate
)
from .project import (
    ProjectResponse, ProjectCreate, ProjectUpdate, ProjectListResponse,
    ProjectWithStats
)
from .analysis import (
    AnalysisRequest, AnalysisResponse, AnalysisStatusResponse,
    IssueResponse, MetricResponse, AnalysisListResponse
)
from .report import (
    ReportRequest, ReportResponse, ReportListResponse, ReportExportRequest,
    ReportExportResponse
)
from .qa import (
    QARequest, QAResponse, ConversationResponse, MessageResponse,
    InsightResponse
)
from .common import (
    PaginationParams, PaginatedResponse, ErrorResponse, SuccessResponse,
    HealthResponse, StatusResponse
)

__all__ = [
    # Auth schemas
    "LoginRequest", "LoginResponse", "RefreshTokenRequest", "RefreshTokenResponse",
    "UserResponse", "TokenData", "UserCreate", "UserUpdate",

    # Project schemas
    "ProjectResponse", "ProjectCreate", "ProjectUpdate", "ProjectListResponse",
    "ProjectWithStats",

    # Analysis schemas
    "AnalysisRequest", "AnalysisResponse", "AnalysisStatusResponse",
    "IssueResponse", "MetricResponse", "AnalysisListResponse",

    # Report schemas
    "ReportRequest", "ReportResponse", "ReportListResponse", "ReportExportRequest",
    "ReportExportResponse",

    # QA schemas
    "QARequest", "QAResponse", "ConversationResponse", "MessageResponse",
    "InsightResponse",

    # Common schemas
    "PaginationParams", "PaginatedResponse", "ErrorResponse", "SuccessResponse",
    "HealthResponse", "StatusResponse"
]
