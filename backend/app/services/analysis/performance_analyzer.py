"""
Performance analyzer for code analysis.
"""

import re
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

from app.core.logging import get_logger

logger = get_logger(__name__)


class PerformanceAnalyzer:
    """
    Analyzes code for performance issues and inefficiencies.
    """

    def __init__(self):
        self.performance_patterns = self._load_performance_patterns()
        self.supported_extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust'
        }

    def _load_performance_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Load performance issue patterns for different languages.
        """
        return {
            'python': [
                {
                    'id': 'PERF001',
                    'title': 'Inefficient list concatenation in loop',
                    'severity': 'medium',
                    'pattern': r'(\w+)\s*\+=\s*\[.*?\]',
                    'description': 'Using += with lists in loops is inefficient',
                    'recommendation': 'Use list.extend() or list comprehension instead.'
                },
                {
                    'id': 'PERF002',
                    'title': 'Use of range(len())',
                    'severity': 'low',
                    'pattern': r'for\s+\w+\s+in\s+range\(len\(\w+\)\):',
                    'description': 'Using range(len()) is less efficient than direct iteration',
                    'recommendation': 'Use direct iteration: for item in iterable:'
                },
                {
                    'id': 'PERF003',
                    'title': 'Multiple list() calls',
                    'severity': 'low',
                    'pattern': r'list\(\w+\)\s*\[\s*\d+\s*\]',
                    'description': 'Converting to list multiple times is inefficient',
                    'recommendation': 'Store list conversion in a variable.'
                },
                {
                    'id': 'PERF004',
                    'title': 'Inefficient string concatenation',
                    'severity': 'medium',
                    'pattern': r'\w+\s*\+=\s*["\'][^"\']*["\']',
                    'description': 'String concatenation in loops is inefficient',
                    'recommendation': 'Use str.join() or io.StringIO for multiple concatenations.'
                }
            ],
            'javascript': [
                {
                    'id': 'PERF005',
                    'title': 'Inefficient DOM queries in loop',
                    'severity': 'high',
                    'pattern': r'for\s*\([^)]+\)\s*\{[^}]*document\.querySelector',
                    'description': 'DOM queries inside loops are expensive',
                    'recommendation': 'Cache DOM queries outside loops.'
                },
                {
                    'id': 'PERF006',
                    'title': 'Memory leak: missing cleanup',
                    'severity': 'medium',
                    'pattern': r'addEventListener\s*\([^,]+,\s*[^,]+\)\s*;?\s*$',
                    'description': 'Event listeners may not be cleaned up',
                    'recommendation': 'Remove event listeners when components unmount.'
                }
            ],
            'general': [
                {
                    'id': 'PERF007',
                    'title': 'N+1 query pattern',
                    'severity': 'high',
                    'pattern': r'(?i)(select|query).*\b(id|key)\b.*\bfor\b',
                    'description': 'Potential N+1 query problem',
                    'recommendation': 'Use batch queries or joins to avoid N+1 problems.'
                },
                {
                    'id': 'PERF008',
                    'title': 'Large data structure in memory',
                    'severity': 'medium',
                    'pattern': r'\blist\s*\([^)]*\)\s*\*\s*\d{3,}',
                    'description': 'Creating very large data structures',
                    'recommendation': 'Consider using generators or streaming for large datasets.'
                }
            ]
        }

    async def analyze(self, project_path: str, config: Any) -> Dict[str, Any]:
        """
        Analyze project for performance issues.
        """
        logger.info(f"Starting performance analysis for: {project_path}")

        source_files = self._find_source_files(project_path)
        total_files = len(source_files)

        if total_files == 0:
            return {
                'success': True,
                'issues': [],
                'metrics': {},
                'files_analyzed': 0,
                'lines_analyzed': 0,
                'languages': []
            }

        all_issues = []
        total_lines = 0
        languages_found = set()

        for file_path in source_files:
            try:
                issues, lines, language = await self._analyze_file(file_path)
                all_issues.extend(issues)
                total_lines += lines
                languages_found.add(language)

            except Exception as e:
                logger.error(f"Failed to analyze {file_path}: {e}")

        # Calculate performance metrics
        metrics = self._calculate_performance_metrics(all_issues, total_files)

        return {
            'success': True,
            'issues': all_issues,
            'metrics': metrics,
            'files_analyzed': total_files,
            'lines_analyzed': total_lines,
            'languages': list(languages_found)
        }

    def _find_source_files(self, project_path: str) -> List[str]:
        """
        Find all source code files in the project.
        """
        source_files = []
        path = Path(project_path)

        for file_path in path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                # Skip common directories
                if not any(part.startswith('.') or part in {'__pycache__', 'venv', 'env', 'node_modules', 'build', 'dist'}
                          for part in file_path.parts):
                    source_files.append(str(file_path))

        return source_files

    async def _analyze_file(self, file_path: str) -> tuple[List[Dict[str, Any]], int, str]:
        """
        Analyze a single file for performance issues.
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            lines = content.splitlines()
            line_count = len(lines)

            # Determine language
            language = self._get_language_from_extension(file_path)

            # Scan for performance issues
            issues = self._scan_performance_issues(content, language, file_path, lines)

            return issues, line_count, language

        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {e}")
            return [], 0, 'unknown'

    def _get_language_from_extension(self, file_path: str) -> str:
        """
        Determine programming language from file extension.
        """
        ext = Path(file_path).suffix.lower()
        return self.supported_extensions.get(ext, 'unknown')

    def _scan_performance_issues(self, content: str, language: str, file_path: str, lines: List[str]) -> List[Dict[str, Any]]:
        """
        Scan file content for performance issues.
        """
        issues = []

        # Get patterns for the specific language
        language_patterns = self.performance_patterns.get(language, [])
        general_patterns = self.performance_patterns.get('general', [])

        all_patterns = language_patterns + general_patterns

        for pattern_info in all_patterns:
            pattern = pattern_info['pattern']
            try:
                regex = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
                matches = regex.finditer(content)

                for match in matches:
                    line_number = self._get_line_number(content, match.start())

                    issue = {
                        'type': 'performance_issue',
                        'severity': pattern_info['severity'],
                        'title': pattern_info['title'],
                        'description': pattern_info['description'],
                        'file_path': file_path,
                        'line_start': line_number,
                        'line_end': line_number,
                        'confidence': 0.8,
                        'issue_id': pattern_info['id'],
                        'recommendation': pattern_info['recommendation'],
                        'code_snippet': self._get_code_snippet(lines, line_number - 1),
                        'language': language,
                        'category': 'performance'
                    }

                    issues.append(issue)

            except re.error as e:
                logger.error(f"Invalid regex pattern {pattern}: {e}")

        # Additional analysis for specific patterns
        issues.extend(self._analyze_complexity_patterns(content, language, file_path, lines))

        return issues

    def _analyze_complexity_patterns(self, content: str, language: str, file_path: str, lines: List[str]) -> List[Dict[str, Any]]:
        """
        Analyze for complex performance patterns.
        """
        issues = []

        if language == 'python':
            issues.extend(self._analyze_python_performance(content, file_path, lines))

        return issues

    def _analyze_python_performance(self, content: str, file_path: str, lines: List[str]) -> List[Dict[str, Any]]:
        """
        Analyze Python-specific performance issues.
        """
        issues = []

        # Check for inefficient comprehensions
        comprehension_pattern = r'\[.*?\s+for\s+.*?\s+in\s+.*?\s+if\s+.*?\]'
        matches = re.finditer(comprehension_pattern, content, re.DOTALL)
        for match in matches:
            line_number = self._get_line_number(content, match.start())
            if len(match.group()) > 200:  # Very long comprehension
                issues.append({
                    'type': 'performance_issue',
                    'severity': 'low',
                    'title': 'Complex list comprehension',
                    'description': 'Very long list comprehension may be hard to read and maintain',
                    'file_path': file_path,
                    'line_start': line_number,
                    'line_end': line_number,
                    'confidence': 0.6,
                    'recommendation': 'Consider breaking complex comprehensions into multiple lines or using traditional loops',
                    'code_snippet': self._get_code_snippet(lines, line_number - 1),
                    'language': 'python',
                    'category': 'readability'
                })

        return issues

    def _get_line_number(self, content: str, position: int) -> int:
        """
        Get line number from character position in content.
        """
        return content[:position].count('\n') + 1

    def _get_code_snippet(self, lines: List[str], line_index: int, context: int = 2) -> str:
        """
        Get code snippet around the issue line.
        """
        start = max(0, line_index - context)
        end = min(len(lines), line_index + context + 1)

        snippet_lines = []
        for i in range(start, end):
            marker = ">>> " if i == line_index else "    "
            snippet_lines.append(f"{marker}{i + 1:4d}: {lines[i]}")

        return "\n".join(snippet_lines)

    def _calculate_performance_metrics(self, issues: List[Dict[str, Any]], total_files: int) -> Dict[str, Any]:
        """
        Calculate performance-related metrics.
        """
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}

        for issue in issues:
            severity = issue.get('severity', 'low')
            severity_counts[severity] += 1

        total_issues = len(issues)

        # Calculate performance score (0-100, higher is better)
        if total_files == 0:
            performance_score = 100.0
        else:
            # Base score reduced by performance issues
            issue_penalty = min(total_issues * 1.5, 40)  # Max 40 point penalty
            severity_multiplier = (
                severity_counts['critical'] * 5 +
                severity_counts['high'] * 3 +
                severity_counts['medium'] * 1
            )
            performance_score = max(0, 100 - issue_penalty - severity_multiplier)

        return {
            'total_performance_issues': total_issues,
            'critical_performance_issues': severity_counts['critical'],
            'high_performance_issues': severity_counts['high'],
            'medium_performance_issues': severity_counts['medium'],
            'low_performance_issues': severity_counts['low'],
            'performance_score': round(performance_score, 1),
            'issues_per_file': round(total_issues / total_files, 2) if total_files > 0 else 0,
            'files_with_performance_issues': len(set(issue['file_path'] for issue in issues))
        }
