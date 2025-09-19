"""
Main API router for v1 endpoints.
"""

from fastapi import APIRouter

from .endpoints import (
    auth,
    projects,
    analysis,
    reports,
    qa,
    webhooks,
    admin,
    health,
    users,
    organizations,
    conversations,
    audit,
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(qa.router, prefix="/qa", tags=["qa"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
