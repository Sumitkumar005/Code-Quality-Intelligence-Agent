"""
GitLab service for GitLab API integration.
"""

import aiohttp
import json
from typing import Dict, List, Any, Optional
import asyncio
from datetime import datetime

from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class GitLabService:
    """
    Service for GitLab API integration.
    """

    def __init__(self, token: Optional[str] = None, base_url: Optional[str] = None):
        self.token = token or settings.GITLAB_TOKEN
        self.base_url = base_url or settings.GITLAB_BASE_URL or "https://gitlab.com/api/v4"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    async def get_project_info(self, project_id: str) -> Dict[str, Any]:
        """
        Get project information from GitLab.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/projects/{project_id}",
                    headers=self.headers,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'success': True,
                            'id': data['id'],
                            'name': data['name'],
                            'path_with_namespace': data['path_with_namespace'],
                            'description': data['description'],
                            'default_branch': data['default_branch'],
                            'created_at': data['created_at'],
                            'last_activity_at': data['last_activity_at'],
                            'visibility': data['visibility'],
                            'star_count': data['star_count'],
                            'forks_count': data['forks_count'],
                            'open_issues_count': data['open_issues_count'],
                            'topics': data.get('topics', []),
                            'languages': await self.get_project_languages(project_id)
                        }
                    else:
                        error_data = await response.json()
                        return {
                            'success': False,
                            'error': f"GitLab API error: {error_data.get('message', 'Unknown error')}",
                            'status_code': response.status
                        }

        except Exception as e:
            logger.error(f"GitLab project info fetch failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def get_project_languages(self, project_id: str) -> Dict[str, Any]:
        """
        Get project languages from GitLab.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/projects/{project_id}/languages",
                    headers=self.headers,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'success': True,
                            'languages': data
                        }
                    else:
                        error_data = await response.json()
                        return {
                            'success': False,
                            'error': f"GitLab API error: {error_data.get('message', 'Unknown error')}",
                            'status_code': response.status
                        }

        except Exception as e:
            logger.error(f"GitLab languages fetch failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def get_project_commits(
        self,
        project_id: str,
        branch: str = "main",
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Get project commits from GitLab.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/projects/{project_id}/repository/commits",
                    headers=self.headers,
                    params={'ref_name': branch, 'per_page': min(limit, 100)},
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        commits = []
                        for commit in data[:limit]:
                            commits.append({
                                'id': commit['id'],
                                'short_id': commit['short_id'],
                                'title': commit['title'],
                                'message': commit['message'],
                                'author_name': commit['author_name'],
                                'author_email': commit['author_email'],
                                'created_at': commit['created_at'],
                                'web_url': commit['web_url']
                            })

                        return {
                            'success': True,
                            'commits': commits,
                            'total_count': len(commits)
                        }
                    else:
                        error_data = await response.json()
                        return {
                            'success': False,
                            'error': f"GitLab API error: {error_data.get('message', 'Unknown error')}",
                            'status_code': response.status
                        }

        except Exception as e:
            logger.error(f"GitLab commits fetch failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def get_merge_requests(
        self,
        project_id: str,
        state: str = "opened",
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Get merge requests from GitLab.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/projects/{project_id}/merge_requests",
                    headers=self.headers,
                    params={'state': state, 'per_page': min(limit, 100)},
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        mrs = []
                        for mr in data[:limit]:
                            mrs.append({
                                'id': mr['id'],
                                'iid': mr['iid'],
                                'title': mr['title'],
                                'description': mr['description'],
                                'state': mr['state'],
                                'author': mr['author']['name'],
                                'created_at': mr['created_at'],
                                'updated_at': mr['updated_at'],
                                'source_branch': mr['source_branch'],
                                'target_branch': mr['target_branch'],
                                'web_url': mr['web_url'],
                                'work_in_progress': mr['work_in_progress'],
                                'merge_status': mr['merge_status']
                            })

                        return {
                            'success': True,
                            'merge_requests': mrs,
                            'total_count': len(mrs)
                        }
                    else:
                        error_data = await response.json()
                        return {
                            'success': False,
                            'error': f"GitLab API error: {error_data.get('message', 'Unknown error')}",
                            'status_code': response.status
                        }

        except Exception as e:
            logger.error(f"GitLab MRs fetch failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def get_project_issues(
        self,
        project_id: str,
        state: str = "opened",
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Get project issues from GitLab.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/projects/{project_id}/issues",
                    headers=self.headers,
                    params={'state': state, 'per_page': min(limit, 100)},
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        issues = []
                        for issue in data[:limit]:
                            issues.append({
                                'id': issue['id'],
                                'iid': issue['iid'],
                                'title': issue['title'],
                                'description': issue['description'],
                                'state': issue['state'],
                                'author': issue['author']['name'],
                                'created_at': issue['created_at'],
                                'updated_at': issue['updated_at'],
                                'labels': issue.get('labels', []),
                                'web_url': issue['web_url'],
                                'confidential': issue.get('confidential', False)
                            })

                        return {
                            'success': True,
                            'issues': issues,
                            'total_count': len(issues)
                        }
                    else:
                        error_data = await response.json()
                        return {
                            'success': False,
                            'error': f"GitLab API error: {error_data.get('message', 'Unknown error')}",
                            'status_code': response.status
                        }

        except Exception as e:
            logger.error(f"GitLab issues fetch failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def create_webhook(
        self,
        project_id: str,
        webhook_url: str,
        events: List[str] = None
    ) -> Dict[str, Any]:
        """
        Create a webhook for the project.
        """
        try:
            if events is None:
                events = ['push_events', 'merge_requests_events', 'issues_events']

            payload = {
                'url': webhook_url,
                'push_events': 'push_events' in events,
                'merge_requests_events': 'merge_requests_events' in events,
                'issues_events': 'issues_events' in events,
                'enable_ssl_verification': True
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/projects/{project_id}/hooks",
                    headers=self.headers,
                    json=payload,
                    timeout=30
                ) as response:
                    if response.status in [200, 201]:
                        data = await response.json()
                        return {
                            'success': True,
                            'webhook_id': data['id'],
                            'url': data['url'],
                            'events': events
                        }
                    else:
                        error_data = await response.json()
                        return {
                            'success': False,
                            'error': f"GitLab API error: {error_data.get('message', 'Unknown error')}",
                            'status_code': response.status
                        }

        except Exception as e:
            logger.error(f"GitLab webhook creation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def get_project_branches(self, project_id: str) -> Dict[str, Any]:
        """
        Get project branches from GitLab.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/projects/{project_id}/repository/branches",
                    headers=self.headers,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        branches = []
                        for branch in data:
                            branches.append({
                                'name': branch['name'],
                                'protected': branch['protected'],
                                'default': branch['default'],
                                'developers_can_push': branch['developers_can_push'],
                                'developers_can_merge': branch['developers_can_merge'],
                                'commit': {
                                    'id': branch['commit']['id'],
                                    'short_id': branch['commit']['short_id'],
                                    'title': branch['commit']['title'],
                                    'message': branch['commit']['message']
                                }
                            })

                        return {
                            'success': True,
                            'branches': branches,
                            'total_count': len(branches)
                        }
                    else:
                        error_data = await response.json()
                        return {
                            'success': False,
                            'error': f"GitLab API error: {error_data.get('message', 'Unknown error')}",
                            'status_code': response.status
                        }

        except Exception as e:
            logger.error(f"GitLab branches fetch failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def check_health(self) -> bool:
        """
        Check if GitLab service is healthy.
        """
        try:
            # Test with GitLab API
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/projects",
                    headers=self.headers,
                    params={'per_page': 1},
                    timeout=10
                ) as response:
                    return response.status == 200
        except Exception:
            return False
