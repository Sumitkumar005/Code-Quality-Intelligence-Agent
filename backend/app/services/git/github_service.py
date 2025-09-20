"""
GitHub service for GitHub API integration.
"""

import aiohttp
import json
from typing import Dict, List, Any, Optional
import asyncio
from datetime import datetime

from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class GitHubService:
    """
    Service for GitHub API integration.
    """

    def __init__(self, token: Optional[str] = None):
        self.token = token or settings.GITHUB_TOKEN
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "CQIA/2.0"
        }

    async def get_repository_info(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Get repository information from GitHub.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/repos/{owner}/{repo}",
                    headers=self.headers,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'success': True,
                            'id': data['id'],
                            'name': data['name'],
                            'full_name': data['full_name'],
                            'description': data['description'],
                            'language': data['language'],
                            'languages_url': data['languages_url'],
                            'default_branch': data['default_branch'],
                            'created_at': data['created_at'],
                            'updated_at': data['updated_at'],
                            'pushed_at': data['pushed_at'],
                            'size': data['size'],
                            'stars': data['stargazers_count'],
                            'forks': data['forks_count'],
                            'open_issues': data['open_issues_count'],
                            'topics': data.get('topics', []),
                            'license': data.get('license', {}).get('name') if data.get('license') else None
                        }
                    else:
                        error_data = await response.json()
                        return {
                            'success': False,
                            'error': f"GitHub API error: {error_data.get('message', 'Unknown error')}",
                            'status_code': response.status
                        }

        except Exception as e:
            logger.error(f"GitHub repository info fetch failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def get_repository_languages(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Get repository languages from GitHub.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/repos/{owner}/{repo}/languages",
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
                            'error': f"GitHub API error: {error_data.get('message', 'Unknown error')}",
                            'status_code': response.status
                        }

        except Exception as e:
            logger.error(f"GitHub languages fetch failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def get_repository_commits(
        self,
        owner: str,
        repo: str,
        branch: str = "main",
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Get repository commits from GitHub.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/repos/{owner}/{repo}/commits",
                    headers=self.headers,
                    params={'sha': branch, 'per_page': min(limit, 100)},
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        commits = []
                        for commit in data[:limit]:
                            commits.append({
                                'sha': commit['sha'],
                                'message': commit['commit']['message'],
                                'author': commit['commit']['author']['name'],
                                'author_email': commit['commit']['author']['email'],
                                'date': commit['commit']['author']['date'],
                                'url': commit['html_url']
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
                            'error': f"GitHub API error: {error_data.get('message', 'Unknown error')}",
                            'status_code': response.status
                        }

        except Exception as e:
            logger.error(f"GitHub commits fetch failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def get_pull_requests(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Get pull requests from GitHub.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/repos/{owner}/{repo}/pulls",
                    headers=self.headers,
                    params={'state': state, 'per_page': min(limit, 100)},
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        prs = []
                        for pr in data[:limit]:
                            prs.append({
                                'id': pr['id'],
                                'number': pr['number'],
                                'title': pr['title'],
                                'body': pr['body'],
                                'state': pr['state'],
                                'author': pr['user']['login'],
                                'created_at': pr['created_at'],
                                'updated_at': pr['updated_at'],
                                'head_branch': pr['head']['ref'],
                                'base_branch': pr['base']['ref'],
                                'url': pr['html_url'],
                                'additions': pr.get('additions', 0),
                                'deletions': pr.get('deletions', 0),
                                'changed_files': pr.get('changed_files', 0)
                            })

                        return {
                            'success': True,
                            'pull_requests': prs,
                            'total_count': len(prs)
                        }
                    else:
                        error_data = await response.json()
                        return {
                            'success': False,
                            'error': f"GitHub API error: {error_data.get('message', 'Unknown error')}",
                            'status_code': response.status
                        }

        except Exception as e:
            logger.error(f"GitHub PRs fetch failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def create_webhook(
        self,
        owner: str,
        repo: str,
        webhook_url: str,
        events: List[str] = None
    ) -> Dict[str, Any]:
        """
        Create a webhook for the repository.
        """
        try:
            if events is None:
                events = ['push', 'pull_request', 'issues']

            payload = {
                'name': 'web',
                'active': True,
                'events': events,
                'config': {
                    'url': webhook_url,
                    'content_type': 'json',
                    'insecure_ssl': '0'
                }
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/repos/{owner}/{repo}/hooks",
                    headers=self.headers,
                    json=payload,
                    timeout=30
                ) as response:
                    if response.status in [200, 201]:
                        data = await response.json()
                        return {
                            'success': True,
                            'webhook_id': data['id'],
                            'url': data['config']['url'],
                            'events': data['events']
                        }
                    else:
                        error_data = await response.json()
                        return {
                            'success': False,
                            'error': f"GitHub API error: {error_data.get('message', 'Unknown error')}",
                            'status_code': response.status
                        }

        except Exception as e:
            logger.error(f"GitHub webhook creation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def get_issues(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Get issues from GitHub.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/repos/{owner}/{repo}/issues",
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
                                'number': issue['number'],
                                'title': issue['title'],
                                'body': issue['body'],
                                'state': issue['state'],
                                'author': issue['user']['login'],
                                'created_at': issue['created_at'],
                                'updated_at': issue['updated_at'],
                                'labels': [label['name'] for label in issue.get('labels', [])],
                                'url': issue['html_url']
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
                            'error': f"GitHub API error: {error_data.get('message', 'Unknown error')}",
                            'status_code': response.status
                        }

        except Exception as e:
            logger.error(f"GitHub issues fetch failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def check_health(self) -> bool:
        """
        Check if GitHub service is healthy.
        """
        try:
            # Test with a public repository
            result = await self.get_repository_info("octocat", "Hello-World")
            return result['success']
        except Exception:
            return False
