"""
Security vulnerability scanner for code analysis.
"""

import re
import os
from typing import Dict, List, Any, Optional, Pattern
from pathlib import Path

from app.core.logging import get_logger

logger = get_logger(__name__)


class SecurityScanner:
    """
    Scans code for common security vulnerabilities and issues.
    """

    def __init__(self):
        self.vulnerability_patterns = self._load_vulnerability_patterns()
        self.supported_extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.php': 'php',
            '.rb': 'ruby',
            '.go': 'go',
            '.rs': 'rust',
            '.c': 'c',
            '.cpp': 'cpp',
            '.h': 'c'
        }

    def _load_vulnerability_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Load vulnerability patterns for different languages.
        """
        return {
            'python': [
                {
                    'id': 'PY001',
                    'title': 'Use of eval()',
                    'severity': 'critical',
                    'pattern': r'\beval\s*\(',
                    'description': 'Use of eval() can execute arbitrary code',
                    'recommendation': 'Avoid using eval(). Use ast.literal_eval() for safe evaluation or find alternative approaches.'
                },
                {
                    'id': 'PY002',
                    'title': 'Use of exec()',
                    'severity': 'critical',
                    'pattern': r'\bexec\s*\(',
                    'description': 'Use of exec() can execute arbitrary code',
                    'recommendation': 'Avoid using exec(). Consider safer alternatives.'
                },
                {
                    'id': 'PY003',
                    'title': 'SQL Injection vulnerability',
                    'severity': 'high',
                    'pattern': r'cursor\.execute\s*\(\s*["\'](.*?)["\']',
                    'description': 'Potential SQL injection through string formatting',
                    'recommendation': 'Use parameterized queries or ORM instead of string formatting.'
                },
                {
                    'id': 'PY004',
                    'title': 'Hardcoded password',
                    'severity': 'high',
                    'pattern': r'password\s*=\s*["\'][^"\']+["\']',
                    'description': 'Hardcoded password found in code',
                    'recommendation': 'Use environment variables or secure credential storage.'
                },
                {
                    'id': 'PY005',
                    'title': 'Use of pickle',
                    'severity': 'medium',
                    'pattern': r'\b(pickle|cpickle)\.',
                    'description': 'Use of pickle can lead to code execution vulnerabilities',
                    'recommendation': 'Consider using safer serialization formats like JSON.'
                },
                {
                    'id': 'PY006',
                    'title': 'Insecure random number generation',
                    'severity': 'medium',
                    'pattern': r'\brandom\.',
                    'description': 'Using random module for security-sensitive operations',
                    'recommendation': 'Use secrets module for cryptographic operations.'
                }
            ],
            'javascript': [
                {
                    'id': 'JS001',
                    'title': 'Use of eval()',
                    'severity': 'critical',
                    'pattern': r'\beval\s*\(',
                    'description': 'Use of eval() can execute arbitrary code',
                    'recommendation': 'Avoid using eval(). Use JSON.parse() or find alternative approaches.'
                },
                {
                    'id': 'JS002',
                    'title': 'InnerHTML assignment',
                    'severity': 'high',
                    'pattern': r'\.innerHTML\s*=',
                    'description': 'Direct assignment to innerHTML can lead to XSS',
                    'recommendation': 'Use textContent or sanitize input before assignment.'
                },
                {
                    'id': 'JS003',
                    'title': 'Use of document.write()',
                    'severity': 'high',
                    'pattern': r'document\.write\s*\(',
                    'description': 'document.write() can lead to XSS attacks',
                    'recommendation': 'Use modern DOM manipulation methods instead.'
                }
            ],
            'general': [
                {
                    'id': 'GEN001',
                    'title': 'Hardcoded API key',
                    'severity': 'high',
                    'pattern': r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\'][^"\']+["\']',
                    'description': 'Hardcoded API key found in code',
                    'recommendation': 'Use environment variables or secure key management.'
                },
                {
                    'id': 'GEN002',
                    'title': 'Hardcoded secret',
                    'severity': 'high',
                    'pattern': r'(?i)(secret|token)\s*[=:]\s*["\'][^"\']+["\']',
                    'description': 'Hardcoded secret found in code',
                    'recommendation': 'Use environment variables or secure secret management.'
                },
                {
                    'id': 'GEN003',
                    'title': 'Debug mode enabled',
                    'severity': 'medium',
                    'pattern': r'(?i)(debug|development)\s*[=:]\s*true',
                    'description': 'Debug mode appears to be enabled in production',
                    'recommendation': 'Disable debug mode in production environments.'
                }
            ]
        }

    async def analyze(self, project_path: str, config: Any) -> Dict[str, Any]:
        """
        Scan project for security vulnerabilities.
        """
        logger.info(f"Starting security scan for: {project_path}")

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
                issues, lines, language = await self._scan_file(file_path)
                all_issues.extend(issues)
                total_lines += lines
                languages_found.add(language)

            except Exception as e:
                logger.error(f"Failed to scan {file_path}: {e}")

        # Calculate security metrics
        metrics = self._calculate_security_metrics(all_issues, total_files)

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

    async def _scan_file(self, file_path: str) -> tuple[List[Dict[str, Any]], int, str]:
        """
        Scan a single file for security vulnerabilities.
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            lines = content.splitlines()
            line_count = len(lines)

            # Determine language
            language = self._get_language_from_extension(file_path)

            # Scan for vulnerabilities
            issues = self._scan_content(content, language, file_path)

            return issues, line_count, language

        except Exception as e:
            logger.error(f"Error scanning file {file_path}: {e}")
            return [], 0, 'unknown'

    def _get_language_from_extension(self, file_path: str) -> str:
        """
        Determine programming language from file extension.
        """
        ext = Path(file_path).suffix.lower()
        return self.supported_extensions.get(ext, 'unknown')

    def _scan_content(self, content: str, language: str, file_path: str) -> List[Dict[str, Any]]:
        """
        Scan file content for security vulnerabilities.
        """
        issues = []

        # Get patterns for the specific language
        language_patterns = self.vulnerability_patterns.get(language, [])
        general_patterns = self.vulnerability_patterns.get('general', [])

        all_patterns = language_patterns + general_patterns

        lines = content.splitlines()

        for pattern_info in all_patterns:
            pattern = pattern_info['pattern']
            try:
                regex = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
                matches = regex.finditer(content)

                for match in matches:
                    line_number = self._get_line_number(content, match.start())

                    issue = {
                        'type': 'security_vulnerability',
                        'severity': pattern_info['severity'],
                        'title': pattern_info['title'],
                        'description': pattern_info['description'],
                        'file_path': file_path,
                        'line_start': line_number,
                        'line_end': line_number,
                        'confidence': 0.9,
                        'vulnerability_id': pattern_info['id'],
                        'recommendation': pattern_info['recommendation'],
                        'code_snippet': self._get_code_snippet(lines, line_number - 1),
                        'language': language
                    }

                    issues.append(issue)

            except re.error as e:
                logger.error(f"Invalid regex pattern {pattern}: {e}")

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

    def _calculate_security_metrics(self, issues: List[Dict[str, Any]], total_files: int) -> Dict[str, Any]:
        """
        Calculate security-related metrics.
        """
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}

        for issue in issues:
            severity = issue.get('severity', 'low')
            severity_counts[severity] += 1

        total_vulnerabilities = len(issues)

        # Calculate security score (0-100, higher is better)
        if total_files == 0:
            security_score = 100.0
        else:
            # Base score reduced by vulnerabilities
            vulnerability_penalty = min(total_vulnerabilities * 2, 50)  # Max 50 point penalty
            severity_multiplier = (
                severity_counts['critical'] * 5 +
                severity_counts['high'] * 3 +
                severity_counts['medium'] * 1
            )
            security_score = max(0, 100 - vulnerability_penalty - severity_multiplier)

        return {
            'total_vulnerabilities': total_vulnerabilities,
            'critical_vulnerabilities': severity_counts['critical'],
            'high_vulnerabilities': severity_counts['high'],
            'medium_vulnerabilities': severity_counts['medium'],
            'low_vulnerabilities': severity_counts['low'],
            'security_score': round(security_score, 1),
            'vulnerabilities_per_file': round(total_vulnerabilities / total_files, 2) if total_files > 0 else 0,
            'files_with_vulnerabilities': len(set(issue['file_path'] for issue in issues))
        }

    async def check_dependencies(self, project_path: str) -> List[Dict[str, Any]]:
        """
        Check for vulnerable dependencies.
        """
        # This would integrate with safety, pip-audit, or similar tools
        # For now, return empty list
        return []

    async def check_secrets(self, project_path: str) -> List[Dict[str, Any]]:
        """
        Check for hardcoded secrets and credentials.
        """
        # This would integrate with tools like trufflehog, git-secrets, etc.
        # For now, return issues found during content scanning
        return []
