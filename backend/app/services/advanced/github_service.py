"""
GitHub Integration Service - Analyze any public repository
"""
import requests
import base64
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

class GitHubService:
    """Service to analyze GitHub repositories"""
    
    def __init__(self, github_token: Optional[str] = None):
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        self.base_url = "https://api.github.com"
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'CQIA-Code-Quality-Agent'
        }
        if self.github_token:
            self.headers['Authorization'] = f'token {self.github_token}'
    
    def analyze_repository(self, repo_url: str) -> Dict[str, Any]:
        """Analyze a GitHub repository"""
        try:
            # Parse repository URL
            repo_info = self._parse_repo_url(repo_url)
            if not repo_info:
                raise ValueError("Invalid GitHub repository URL")
            
            owner, repo = repo_info['owner'], repo_info['repo']
            
            # Get repository information
            repo_data = self._get_repo_info(owner, repo)
            
            # Get file tree
            file_tree = self._get_file_tree(owner, repo)
            
            # Download and analyze code files
            code_files = self._download_code_files(owner, repo, file_tree)
            
            return {
                "repository": repo_data,
                "files": code_files,
                "stats": {
                    "total_files": len(code_files),
                    "total_size": sum(len(content) for content in code_files.values()),
                    "languages": self._detect_languages(code_files)
                }
            }
            
        except Exception as e:
            raise Exception(f"Failed to analyze repository: {str(e)}")
    
    def _parse_repo_url(self, url: str) -> Optional[Dict[str, str]]:
        """Parse GitHub repository URL"""
        # Handle different URL formats
        if 'github.com' not in url:
            return None
        
        # Extract owner/repo from URL
        parts = url.replace('https://', '').replace('http://', '').split('/')
        
        try:
            github_index = next(i for i, part in enumerate(parts) if 'github.com' in part)
            owner = parts[github_index + 1]
            repo = parts[github_index + 2].replace('.git', '')
            
            return {'owner': owner, 'repo': repo}
        except (IndexError, StopIteration):
            return None
    
    def _get_repo_info(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get repository information"""
        url = f"{self.base_url}/repos/{owner}/{repo}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 404:
            raise Exception("Repository not found or private")
        elif response.status_code != 200:
            raise Exception(f"GitHub API error: {response.status_code}")
        
        data = response.json()
        return {
            "name": data["name"],
            "full_name": data["full_name"],
            "description": data.get("description", ""),
            "language": data.get("language", ""),
            "stars": data["stargazers_count"],
            "forks": data["forks_count"],
            "size": data["size"],
            "created_at": data["created_at"],
            "updated_at": data["updated_at"],
            "topics": data.get("topics", [])
        }
    
    def _get_file_tree(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """Get repository file tree"""
        url = f"{self.base_url}/repos/{owner}/{repo}/git/trees/HEAD?recursive=1"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            raise Exception(f"Failed to get file tree: {response.status_code}")
        
        data = response.json()
        
        # Filter for code files only
        code_extensions = {'.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.go', '.rs', '.cs', '.cpp', '.c', '.php', '.rb'}
        
        code_files = []
        for item in data.get("tree", []):
            if item["type"] == "blob":  # It's a file
                file_path = item["path"]
                if any(file_path.endswith(ext) for ext in code_extensions):
                    # Skip large files and common directories to ignore
                    if (item["size"] < 100000 and  # Less than 100KB
                        not any(skip in file_path for skip in ['node_modules', '.git', 'vendor', 'build', 'dist'])):
                        code_files.append({
                            "path": file_path,
                            "sha": item["sha"],
                            "size": item["size"]
                        })
        
        # Limit to 50 files for demo (avoid rate limits)
        return code_files[:50]
    
    def _download_code_files(self, owner: str, repo: str, file_list: List[Dict[str, Any]]) -> Dict[str, str]:
        """Download code files content"""
        files_content = {}
        
        for file_info in file_list:
            try:
                # Get file content
                url = f"{self.base_url}/repos/{owner}/{repo}/contents/{file_info['path']}"
                response = requests.get(url, headers=self.headers)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Decode base64 content
                    if data.get("encoding") == "base64":
                        content = base64.b64decode(data["content"]).decode('utf-8', errors='ignore')
                        files_content[file_info['path']] = content
                
                # Rate limiting - be nice to GitHub API
                import time
                time.sleep(0.1)  # 100ms delay between requests
                
            except Exception as e:
                print(f"Failed to download {file_info['path']}: {e}")
                continue
        
        return files_content
    
    def _detect_languages(self, files: Dict[str, str]) -> List[str]:
        """Detect programming languages from files"""
        lang_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.jsx': 'JavaScript',
            '.ts': 'TypeScript', 
            '.tsx': 'TypeScript',
            '.java': 'Java',
            '.go': 'Go',
            '.rs': 'Rust',
            '.cs': 'C#',
            '.cpp': 'C++',
            '.c': 'C',
            '.php': 'PHP',
            '.rb': 'Ruby'
        }
        
        languages = set()
        for file_path in files.keys():
            ext = Path(file_path).suffix.lower()
            if ext in lang_map:
                languages.add(lang_map[ext])
        
        return list(languages)
    
    def get_trending_repos(self, language: str = "", limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending repositories for analysis"""
        # Search for popular repositories
        query = f"stars:>1000"
        if language:
            query += f" language:{language}"
        
        url = f"{self.base_url}/search/repositories"
        params = {
            'q': query,
            'sort': 'stars',
            'order': 'desc',
            'per_page': limit
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            return [{
                "name": repo["name"],
                "full_name": repo["full_name"],
                "description": repo.get("description", ""),
                "language": repo.get("language", ""),
                "stars": repo["stargazers_count"],
                "url": repo["html_url"]
            } for repo in data.get("items", [])]
        
        return []

# Global GitHub service
github_service = GitHubService()