"""
Context Management for AI Agent

This module handles context management for the AI agent, including:
- Codebase context retrieval
- File relationship mapping
- Context caching and optimization
- Context-aware prompt generation
"""

import asyncio
import hashlib
import json
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from pathlib import Path
import logging

from ..core.database import get_db
from ..models.project import Project
from ..models.analysis import Analysis
from ..services.git.git_service import GitService
from ..services.storage.file_storage import FileStorageService

logger = logging.getLogger(__name__)


@dataclass
class ContextItem:
    """Represents a single context item."""
    content: str
    file_path: str
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    relevance_score: float = 0.0
    last_accessed: datetime = field(default_factory=datetime.now)


@dataclass
class ContextCache:
    """Context cache for performance optimization."""
    items: Dict[str, ContextItem] = field(default_factory=dict)
    max_size: int = 1000
    ttl_seconds: int = 3600  # 1 hour

    def get(self, key: str) -> Optional[ContextItem]:
        """Get item from cache if not expired."""
        if key not in self.items:
            return None

        item = self.items[key]
        if datetime.now() - item.last_accessed > timedelta(seconds=self.ttl_seconds):
            del self.items[key]
            return None

        item.last_accessed = datetime.now()
        return item

    def set(self, key: str, item: ContextItem) -> None:
        """Set item in cache, evict if necessary."""
        if len(self.items) >= self.max_size:
            # Simple LRU eviction - remove oldest accessed
            oldest_key = min(self.items.keys(),
                           key=lambda k: self.items[k].last_accessed)
            del self.items[oldest_key]

        self.items[key] = item
        item.last_accessed = datetime.now()

    def clear(self) -> None:
        """Clear all cached items."""
        self.items.clear()


class ContextManager:
    """
    Manages context for AI agent interactions.

    Provides context-aware information including:
    - Current file context
    - Related files and dependencies
    - Project structure
    - Recent changes
    - Analysis history
    """

    def __init__(self):
        self.cache = ContextCache()
        self.git_service = GitService()
        self.file_storage = FileStorageService()

    def _generate_cache_key(self, project_id: str, context_type: str, **kwargs) -> str:
        """Generate a cache key for context items."""
        key_data = f"{project_id}:{context_type}"
        for k, v in sorted(kwargs.items()):
            key_data += f":{k}:{v}"
        return hashlib.md5(key_data.encode()).hexdigest()

    async def get_project_context(self, project_id: str) -> Dict[str, Any]:
        """
        Get comprehensive project context.

        Args:
            project_id: Project identifier

        Returns:
            Dictionary containing project context
        """
        cache_key = self._generate_cache_key(project_id, "project_context")

        if cached := self.cache.get(cache_key):
            return json.loads(cached.content)

        async with get_db() as db:
            # Get project information
            project = await db.get(Project, project_id)
            if not project:
                return {}

            context = {
                "project_id": str(project.id),
                "project_name": project.name,
                "description": project.description,
                "languages": project.languages or [],
                "repository_url": project.repository_url,
                "default_branch": project.default_branch,
                "settings": project.settings or {},
                "created_at": project.created_at.isoformat(),
                "updated_at": project.updated_at.isoformat(),
            }

            # Get recent analyses
            recent_analyses = await db.query(Analysis).filter(
                Analysis.project_id == project_id
            ).order_by(Analysis.created_at.desc()).limit(5)

            context["recent_analyses"] = [
                {
                    "id": str(analysis.id),
                    "status": analysis.status,
                    "analysis_type": analysis.analysis_type,
                    "created_at": analysis.created_at.isoformat(),
                    "completed_at": analysis.completed_at.isoformat() if analysis.completed_at else None,
                }
                for analysis in recent_analyses
            ]

            # Get project structure
            context["structure"] = await self._get_project_structure(project_id)

            # Cache the context
            cache_item = ContextItem(
                content=json.dumps(context),
                file_path=f"project:{project_id}",
                metadata={"type": "project_context"}
            )
            self.cache.set(cache_key, cache_item)

            return context

    async def get_file_context(
        self,
        project_id: str,
        file_path: str,
        include_dependencies: bool = True,
        include_related: bool = True
    ) -> Dict[str, Any]:
        """
        Get context for a specific file.

        Args:
            project_id: Project identifier
            file_path: Path to the file
            include_dependencies: Whether to include dependency information
            include_related: Whether to include related files

        Returns:
            Dictionary containing file context
        """
        cache_key = self._generate_cache_key(
            project_id, "file_context",
            file_path=file_path,
            include_deps=include_dependencies,
            include_related=include_related
        )

        if cached := self.cache.get(cache_key):
            return json.loads(cached.content)

        context = {
            "file_path": file_path,
            "project_id": project_id,
        }

        try:
            # Get file content
            file_content = await self.file_storage.read_file(project_id, file_path)
            context["content"] = file_content

            # Get file metadata
            file_info = await self.file_storage.get_file_info(project_id, file_path)
            context["metadata"] = file_info

            if include_dependencies:
                context["dependencies"] = await self._get_file_dependencies(
                    project_id, file_path
                )

            if include_related:
                context["related_files"] = await self._get_related_files(
                    project_id, file_path
                )

            # Get recent changes for this file
            context["recent_changes"] = await self._get_recent_changes(
                project_id, file_path
            )

        except Exception as e:
            logger.error(f"Error getting file context for {file_path}: {e}")
            context["error"] = str(e)

        # Cache the context
        cache_item = ContextItem(
            content=json.dumps(context),
            file_path=file_path,
            metadata={"type": "file_context"}
        )
        self.cache.set(cache_key, cache_item)

        return context

    async def get_codebase_context(
        self,
        project_id: str,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get relevant codebase context based on a query.

        Args:
            project_id: Project identifier
            query: Search query
            limit: Maximum number of results

        Returns:
            List of relevant code snippets with context
        """
        cache_key = self._generate_cache_key(
            project_id, "codebase_context",
            query=query, limit=limit
        )

        if cached := self.cache.get(cache_key):
            return json.loads(cached.content)

        # This would typically use vector search or semantic search
        # For now, we'll use a simple file-based search
        context_results = []

        try:
            # Get project structure
            structure = await self._get_project_structure(project_id)

            # Search through files for relevant content
            for file_path in structure.get("files", []):
                if len(context_results) >= limit:
                    break

                try:
                    file_context = await self.get_file_context(project_id, file_path)
                    content = file_context.get("content", "")

                    # Simple relevance scoring based on query terms
                    query_terms = query.lower().split()
                    content_lower = content.lower()

                    relevance_score = sum(
                        1 for term in query_terms
                        if term in content_lower
                    ) / len(query_terms)

                    if relevance_score > 0:
                        context_results.append({
                            "file_path": file_path,
                            "content": content[:500] + "..." if len(content) > 500 else content,
                            "relevance_score": relevance_score,
                            "line_count": len(content.splitlines()),
                        })

                except Exception as e:
                    logger.debug(f"Error processing file {file_path}: {e}")
                    continue

            # Sort by relevance score
            context_results.sort(key=lambda x: x["relevance_score"], reverse=True)

        except Exception as e:
            logger.error(f"Error getting codebase context: {e}")

        # Cache the results
        cache_item = ContextItem(
            content=json.dumps(context_results),
            file_path=f"codebase:{project_id}",
            metadata={"type": "codebase_context", "query": query}
        )
        self.cache.set(cache_key, cache_item)

        return context_results

    async def get_conversation_context(
        self,
        project_id: str,
        conversation_id: str,
        max_context_items: int = 5
    ) -> Dict[str, Any]:
        """
        Get context from previous conversation messages.

        Args:
            project_id: Project identifier
            conversation_id: Conversation identifier
            max_context_items: Maximum number of context items to include

        Returns:
            Dictionary containing conversation context
        """
        cache_key = self._generate_cache_key(
            project_id, "conversation_context",
            conversation_id=conversation_id,
            max_items=max_context_items
        )

        if cached := self.cache.get(cache_key):
            return json.loads(cached.content)

        # This would typically query the conversation database
        # For now, return a placeholder structure
        context = {
            "conversation_id": conversation_id,
            "project_id": project_id,
            "previous_messages": [],
            "current_topics": [],
            "referenced_files": [],
        }

        # Cache the context
        cache_item = ContextItem(
            content=json.dumps(context),
            file_path=f"conversation:{conversation_id}",
            metadata={"type": "conversation_context"}
        )
        self.cache.set(cache_key, cache_item)

        return context

    async def _get_project_structure(self, project_id: str) -> Dict[str, Any]:
        """Get project directory structure."""
        # This would typically analyze the git repository or file system
        return {
            "directories": [],
            "files": [],
            "languages": {},
            "total_lines": 0,
        }

    async def _get_file_dependencies(
        self,
        project_id: str,
        file_path: str
    ) -> List[Dict[str, Any]]:
        """Get file dependencies and imports."""
        # This would typically parse the file to extract imports
        return []

    async def _get_related_files(
        self,
        project_id: str,
        file_path: str
    ) -> List[Dict[str, Any]]:
        """Get files related to the given file."""
        # This would typically use static analysis or naming patterns
        return []

    async def _get_recent_changes(
        self,
        project_id: str,
        file_path: str
    ) -> List[Dict[str, Any]]:
        """Get recent changes for a file."""
        # This would typically query git history
        return []

    def clear_cache(self, project_id: Optional[str] = None) -> None:
        """
        Clear context cache.

        Args:
            project_id: If provided, clear only cache for this project
        """
        if project_id:
            # Clear project-specific cache entries
            keys_to_remove = [
                key for key in self.cache.items.keys()
                if key.startswith(project_id)
            ]
            for key in keys_to_remove:
                del self.cache.items[key]
        else:
            self.cache.clear()

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "total_items": len(self.cache.items),
            "max_size": self.cache.max_size,
            "ttl_seconds": self.cache.ttl_seconds,
        }


# Global context manager instance
context_manager = ContextManager()


async def get_project_context(project_id: str) -> Dict[str, Any]:
    """Convenience function to get project context."""
    return await context_manager.get_project_context(project_id)


async def get_file_context(
    project_id: str,
    file_path: str,
    **kwargs
) -> Dict[str, Any]:
    """Convenience function to get file context."""
    return await context_manager.get_file_context(project_id, file_path, **kwargs)


async def get_codebase_context(
    project_id: str,
    query: str,
    **kwargs
) -> List[Dict[str, Any]]:
    """Convenience function to get codebase context."""
    return await context_manager.get_codebase_context(project_id, query, **kwargs)


async def get_conversation_context(
    project_id: str,
    conversation_id: str,
    **kwargs
) -> Dict[str, Any]:
    """Convenience function to get conversation context."""
    return await context_manager.get_conversation_context(
        project_id, conversation_id, **kwargs
    )
