"""
Database models for the CQIA application.
"""

from .base import CQIA_Base
from .user import User, Organization, OrganizationMember
from .project import Project, ProjectWebhook
from .analysis import Analysis, Issue, AnalysisArtifact, AnalysisStatus, AnalysisType
from .report import Report, ReportTemplate
from .conversation import Conversation, ConversationMessage, ConversationTemplate
from .audit import AuditLog, AuditLogArchive, AUDIT_ACTIONS, RESOURCE_TYPES

__all__ = [
    # Base model
    "CQIA_Base",

    # User management
    "User",
    "Organization",
    "OrganizationMember",

    # Project management
    "Project",
    "ProjectWebhook",

    # Analysis and quality
    "Analysis",
    "Issue",
    "AnalysisArtifact",
    "AnalysisStatus",
    "AnalysisType",

    # Reporting
    "Report",
    "ReportTemplate",

    # AI Conversations
    "Conversation",
    "ConversationMessage",
    "ConversationTemplate",

    # Audit and logging
    "AuditLog",
    "AuditLogArchive",
    "AUDIT_ACTIONS",
    "RESOURCE_TYPES",
]
