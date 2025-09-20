"""
Automated PR review service for code quality analysis.
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

from app.core.logging import get_logger
from app.core.config import settings
from ..analysis.orchestrator import AnalysisOrchestrator
from ..ai.agent_service import AgentService

logger = get_logger(__name__)


class PRReviewer:
    """
    Service for automated PR reviews and code quality analysis.
    """

    def __init__(self):
        self.analysis_orchestrator = AnalysisOrchestrator()
        self.ai_agent = AgentService()

    async def review_pull_request(
        self,
        repo_url: str,
        pr_number: int,
        base_branch: str = "main",
        head_branch: str = None
    ) -> Dict[str, Any]:
        """
        Perform automated review of a pull request.
        """
        try:
            logger.info(f"Starting PR review for {repo_url} PR #{pr_number}")

            # Get PR details
            pr_details = await self._get_pr_details(repo_url, pr_number)
            if not pr_details['success']:
                return pr_details

            # Get changed files
            changed_files = await self._get_changed_files(repo_url, pr_number)
            if not changed_files['success']:
                return changed_files

            # Analyze each changed file
            analysis_results = []
            for file_info in changed_files['files']:
                analysis = await self._analyze_file_changes(
                    repo_url, file_info, base_branch, head_branch
                )
                analysis_results.append(analysis)

            # Generate overall review
            review_summary = await self._generate_review_summary(analysis_results, pr_details)

            # Generate AI-powered suggestions
            ai_suggestions = await self._generate_ai_suggestions(analysis_results, pr_details)

            return {
                'success': True,
                'pr_number': pr_number,
                'pr_details': pr_details,
                'changed_files': changed_files['files'],
                'analysis_results': analysis_results,
                'review_summary': review_summary,
                'ai_suggestions': ai_suggestions,
                'reviewed_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"PR review failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'pr_number': pr_number
            }

    async def _get_pr_details(self, repo_url: str, pr_number: int) -> Dict[str, Any]:
        """
        Get pull request details.
        """
        try:
            # This would integrate with GitHub/GitLab APIs
            # For now, return mock data
            return {
                'success': True,
                'id': pr_number,
                'title': f"PR #{pr_number}",
                'description': "Pull request description",
                'author': "developer",
                'base_branch': "main",
                'head_branch': "feature-branch",
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"PR details fetch failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def _get_changed_files(self, repo_url: str, pr_number: int) -> Dict[str, Any]:
        """
        Get list of changed files in the PR.
        """
        try:
            # This would integrate with GitHub/GitLab APIs
            # For now, return mock data
            return {
                'success': True,
                'files': [
                    {
                        'filename': 'src/main.py',
                        'status': 'modified',
                        'additions': 25,
                        'deletions': 10,
                        'changes': 35
                    },
                    {
                        'filename': 'src/utils.py',
                        'status': 'added',
                        'additions': 50,
                        'deletions': 0,
                        'changes': 50
                    }
                ]
            }
        except Exception as e:
            logger.error(f"Changed files fetch failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def _analyze_file_changes(
        self,
        repo_url: str,
        file_info: Dict[str, Any],
        base_branch: str,
        head_branch: str
    ) -> Dict[str, Any]:
        """
        Analyze changes in a specific file.
        """
        try:
            # Run analysis on the file
            analysis_result = await self.analysis_orchestrator.analyze_file(
                file_path=file_info['filename'],
                content="mock content",  # Would get actual content
                language=self._detect_language(file_info['filename'])
            )

            # Generate AI review for the file
            ai_review = await self.ai_agent.analyze_code_with_ai(
                code="mock code",  # Would get actual code
                language=self._detect_language(file_info['filename']),
                analysis_type="review"
            )

            return {
                'filename': file_info['filename'],
                'status': file_info['status'],
                'additions': file_info['additions'],
                'deletions': file_info['deletions'],
                'changes': file_info['changes'],
                'analysis': analysis_result,
                'ai_review': ai_review,
                'issues': self._extract_issues(analysis_result, ai_review),
                'suggestions': self._extract_suggestions(ai_review)
            }

        except Exception as e:
            logger.error(f"File analysis failed for {file_info['filename']}: {e}")
            return {
                'filename': file_info['filename'],
                'error': str(e),
                'issues': [],
                'suggestions': []
            }

    def _detect_language(self, filename: str) -> str:
        """
        Detect programming language from filename.
        """
        extension_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.cpp': 'cpp',
            '.c': 'c',
            '.php': 'php',
            '.rb': 'ruby',
            '.swift': 'swift',
            '.kt': 'kotlin'
        }

        import os
        _, ext = os.path.splitext(filename)
        return extension_map.get(ext, 'unknown')

    def _extract_issues(self, analysis_result: Dict[str, Any], ai_review: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract issues from analysis results.
        """
        issues = []

        # Extract from traditional analysis
        if analysis_result.get('success'):
            for issue_type, results in analysis_result.get('results', {}).items():
                for issue in results.get('issues', []):
                    issues.append({
                        'type': issue_type,
                        'severity': issue.get('severity', 'medium'),
                        'title': issue.get('title', 'Issue'),
                        'description': issue.get('description', ''),
                        'line': issue.get('line', 0),
                        'column': issue.get('column', 0),
                        'file': issue.get('file', ''),
                        'suggestion': issue.get('suggestion', '')
                    })

        # Extract from AI review
        if ai_review.get('success'):
            ai_issues = ai_review.get('analysis', {}).get('issues', [])
            for issue in ai_issues:
                issues.append({
                    'type': 'ai_suggestion',
                    'severity': issue.get('severity', 'info'),
                    'title': issue.get('title', 'AI Suggestion'),
                    'description': issue.get('description', ''),
                    'line': issue.get('line', 0),
                    'column': issue.get('column', 0),
                    'file': issue.get('file', ''),
                    'suggestion': issue.get('suggestion', '')
                })

        return issues

    def _extract_suggestions(self, ai_review: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract suggestions from AI review.
        """
        suggestions = []

        if ai_review.get('success'):
            ai_suggestions = ai_review.get('improvements', {}).get('suggestions', [])
            for suggestion in ai_suggestions:
                suggestions.append({
                    'type': suggestion.get('type', 'improvement'),
                    'title': suggestion.get('title', 'Suggestion'),
                    'description': suggestion.get('description', ''),
                    'priority': suggestion.get('priority', 'medium'),
                    'effort': suggestion.get('effort', 'medium'),
                    'code_example': suggestion.get('code_example', '')
                })

        return suggestions

    async def _generate_review_summary(
        self,
        analysis_results: List[Dict[str, Any]],
        pr_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate overall review summary.
        """
        try:
            total_files = len(analysis_results)
            total_issues = sum(len(result.get('issues', [])) for result in analysis_results)
            total_suggestions = sum(len(result.get('suggestions', [])) for result in analysis_results)

            # Calculate severity distribution
            severity_counts = {'high': 0, 'medium': 0, 'low': 0, 'info': 0}
            for result in analysis_results:
                for issue in result.get('issues', []):
                    severity = issue.get('severity', 'medium')
                    if severity in severity_counts:
                        severity_counts[severity] += 1

            # Determine overall status
            if severity_counts['high'] > 0:
                overall_status = 'needs_review'
            elif severity_counts['medium'] > 5:
                overall_status = 'needs_attention'
            else:
                overall_status = 'approved'

            return {
                'total_files': total_files,
                'total_issues': total_issues,
                'total_suggestions': total_suggestions,
                'severity_distribution': severity_counts,
                'overall_status': overall_status,
                'summary': self._generate_summary_text(
                    total_files, total_issues, total_suggestions, severity_counts, overall_status
                )
            }

        except Exception as e:
            logger.error(f"Review summary generation failed: {e}")
            return {
                'total_files': 0,
                'total_issues': 0,
                'total_suggestions': 0,
                'severity_distribution': {},
                'overall_status': 'error',
                'summary': 'Error generating review summary'
            }

    def _generate_summary_text(
        self,
        total_files: int,
        total_issues: int,
        total_suggestions: int,
        severity_counts: Dict[str, int],
        overall_status: str
    ) -> str:
        """
        Generate human-readable summary text.
        """
        summary = f"Automated review of {total_files} file(s) found {total_issues} issue(s) and {total_suggestions} suggestion(s)."

        if severity_counts['high'] > 0:
            summary += f" {severity_counts['high']} high-severity issue(s) require immediate attention."
        elif severity_counts['medium'] > 0:
            summary += f" {severity_counts['medium']} medium-severity issue(s) should be addressed."
        else:
            summary += " No critical issues found."

        if overall_status == 'approved':
            summary += " Overall status: ✅ Approved"
        elif overall_status == 'needs_attention':
            summary += " Overall status: ⚠️ Needs Attention"
        else:
            summary += " Overall status: ❌ Needs Review"

        return summary

    async def _generate_ai_suggestions(
        self,
        analysis_results: List[Dict[str, Any]],
        pr_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate AI-powered suggestions for the PR.
        """
        try:
            # This would use the AI agent to provide intelligent suggestions
            return {
                'general_suggestions': [
                    'Consider adding unit tests for new functionality',
                    'Review error handling patterns',
                    'Check for potential performance improvements'
                ],
                'priority_improvements': [
                    'Add input validation',
                    'Implement proper logging',
                    'Consider security implications'
                ],
                'best_practices': [
                    'Follow consistent naming conventions',
                    'Add documentation for public APIs',
                    'Consider code reusability'
                ]
            }

        except Exception as e:
            logger.error(f"AI suggestions generation failed: {e}")
            return {
                'general_suggestions': [],
                'priority_improvements': [],
                'best_practices': []
            }

    async def check_health(self) -> bool:
        """
        Check if PR reviewer service is healthy.
        """
        try:
            # Test basic functionality
            test_result = await self._get_pr_details("test", 1)
            return test_result['success']
        except Exception:
            return False
