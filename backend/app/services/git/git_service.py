"""
Git service for repository operations.
"""

import subprocess
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
import asyncio

from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class GitService:
    """
    Service for Git repository operations.
    """

    def __init__(self):
        self.git_command = "git"

    async def clone_repository(
        self,
        repo_url: str,
        target_path: str,
        branch: str = "main"
    ) -> Dict[str, Any]:
        """
        Clone a Git repository.
        """
        try:
            # Ensure target directory exists
            os.makedirs(target_path, exist_ok=True)

            # Clone command
            cmd = [self.git_command, "clone", "--branch", branch, repo_url, target_path]

            result = await self._run_git_command(cmd)

            return {
                'success': True,
                'path': target_path,
                'branch': branch,
                'url': repo_url
            }

        except Exception as e:
            logger.error(f"Repository clone failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'url': repo_url,
                'path': target_path
            }

    async def get_repository_info(self, repo_path: str) -> Dict[str, Any]:
        """
        Get information about a Git repository.
        """
        try:
            # Get remote URL
            remote_cmd = [self.git_command, "-C", repo_path, "remote", "get-url", "origin"]
            remote_result = await self._run_git_command(remote_cmd)
            remote_url = remote_result.stdout.strip() if remote_result.returncode == 0 else None

            # Get current branch
            branch_cmd = [self.git_command, "-C", repo_path, "branch", "--show-current"]
            branch_result = await self._run_git_command(branch_cmd)
            current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else None

            # Get latest commit
            commit_cmd = [self.git_command, "-C", repo_path, "log", "-1", "--oneline"]
            commit_result = await self._run_git_command(commit_cmd)
            latest_commit = commit_result.stdout.strip() if commit_result.returncode == 0 else None

            # Get repository size
            size = self._get_repo_size(repo_path)

            return {
                'success': True,
                'remote_url': remote_url,
                'current_branch': current_branch,
                'latest_commit': latest_commit,
                'size_mb': size,
                'path': repo_path
            }

        except Exception as e:
            logger.error(f"Failed to get repository info: {e}")
            return {
                'success': False,
                'error': str(e),
                'path': repo_path
            }

    async def get_commit_history(
        self,
        repo_path: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get commit history for a repository.
        """
        try:
            cmd = [
                self.git_command, "-C", repo_path, "log",
                f"--max-count={limit}",
                "--pretty=format:%H|%an|%ae|%ad|%s",
                "--date=iso"
            ]

            result = await self._run_git_command(cmd)

            if result.returncode != 0:
                return []

            commits = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.split('|', 4)
                    if len(parts) >= 5:
                        commits.append({
                            'hash': parts[0],
                            'author_name': parts[1],
                            'author_email': parts[2],
                            'date': parts[3],
                            'message': parts[4]
                        })

            return commits

        except Exception as e:
            logger.error(f"Failed to get commit history: {e}")
            return []

    async def get_file_changes(
        self,
        repo_path: str,
        since_commit: str = None
    ) -> List[Dict[str, Any]]:
        """
        Get file changes in the repository.
        """
        try:
            if since_commit:
                cmd = [self.git_command, "-C", repo_path, "diff", "--name-status", since_commit]
            else:
                cmd = [self.git_command, "-C", repo_path, "status", "--porcelain"]

            result = await self._run_git_command(cmd)

            if result.returncode != 0:
                return []

            changes = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.split('\t', 1)
                    if len(parts) >= 2:
                        status, filename = parts
                        changes.append({
                            'status': status.strip(),
                            'file': filename.strip()
                        })

            return changes

        except Exception as e:
            logger.error(f"Failed to get file changes: {e}")
            return []

    async def create_commit(
        self,
        repo_path: str,
        message: str,
        files: List[str] = None
    ) -> Dict[str, Any]:
        """
        Create a Git commit.
        """
        try:
            # Add files
            if files:
                add_cmd = [self.git_command, "-C", repo_path, "add"] + files
                await self._run_git_command(add_cmd)
            else:
                # Add all changes
                add_cmd = [self.git_command, "-C", repo_path, "add", "."]
                await self._run_git_command(add_cmd)

            # Commit
            commit_cmd = [self.git_command, "-C", repo_path, "commit", "-m", message]
            result = await self._run_git_command(commit_cmd)

            if result.returncode == 0:
                # Get commit hash
                hash_cmd = [self.git_command, "-C", repo_path, "rev-parse", "HEAD"]
                hash_result = await self._run_git_command(hash_cmd)
                commit_hash = hash_result.stdout.strip() if hash_result.returncode == 0 else None

                return {
                    'success': True,
                    'commit_hash': commit_hash,
                    'message': message
                }
            else:
                return {
                    'success': False,
                    'error': result.stderr.strip()
                }

        except Exception as e:
            logger.error(f"Commit creation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def push_changes(
        self,
        repo_path: str,
        remote: str = "origin",
        branch: str = None
    ) -> Dict[str, Any]:
        """
        Push changes to remote repository.
        """
        try:
            if branch is None:
                # Get current branch
                branch_cmd = [self.git_command, "-C", repo_path, "branch", "--show-current"]
                branch_result = await self._run_git_command(branch_cmd)
                branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "main"

            cmd = [self.git_command, "-C", repo_path, "push", remote, branch]
            result = await self._run_git_command(cmd)

            return {
                'success': result.returncode == 0,
                'remote': remote,
                'branch': branch,
                'error': result.stderr.strip() if result.returncode != 0 else None
            }

        except Exception as e:
            logger.error(f"Push failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _get_repo_size(self, repo_path: str) -> float:
        """
        Calculate repository size in MB.
        """
        try:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(repo_path):
                # Skip .git directory for size calculation
                if '.git' in dirnames:
                    dirnames.remove('.git')

                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except OSError:
                        pass

            return round(total_size / (1024 * 1024), 2)  # Convert to MB

        except Exception:
            return 0.0

    async def _run_git_command(self, cmd: List[str]) -> subprocess.CompletedProcess:
        """
        Run a Git command asynchronously.
        """
        try:
            # Run command in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            )
            return result

        except subprocess.TimeoutExpired:
            raise Exception("Git command timed out")
        except Exception as e:
            raise Exception(f"Git command failed: {e}")

    async def check_health(self) -> bool:
        """
        Check if Git is available and working.
        """
        try:
            result = await self._run_git_command([self.git_command, "--version"])
            return result.returncode == 0
        except Exception:
            return False
