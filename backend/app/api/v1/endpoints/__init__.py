"""
API v1 endpoints package.
"""

from .auth import router as auth_router
from .health import router as health_router
from .users import router as users_router
from .projects import router as projects_router
from .analysis import router as analysis_router
from .reports import router as reports_router
from .conversations import router as conversations_router
from .webhooks import router as webhooks_router
from .admin import router as admin_router
from .audit import router as audit_router
from .organizations import router as organizations_router
from .qa import router as qa_router

__all__ = [
    "auth_router",
    "health_router",
    "users_router",
    "projects_router",
    "analysis_router",
    "reports_router",
    "conversations_router",
    "webhooks_router",
    "admin_router",
    "audit_router",
    "organizations_router",
    "qa_router"
]
