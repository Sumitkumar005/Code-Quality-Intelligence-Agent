"""
Test analyzer for assessing test coverage and quality.
"""

import os
from typing import Dict, List, Any, Optional
from pathlib import Path
import re

from app.core.logging import get_logger

logger = get_logger(__name__)


class TestAnalyzer:
    """
    Analyzes test coverage and test code quality.
    """

    def __init__(self):
        self.supported_extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.go': 'go'
        }
        self.test_patterns = {
            'python': [r'test_.*\.py', r'.*_test\.py'],
            'javascript': [r'.*\.test\.js', r'.*\.spec\.js', r'.*test.*\.js'],
            'typescript': [r'.*\.test\.ts', r'.*\.spec\.ts', r'.*test.*\.ts'],
            'java': [r'.*Test\.java', r'.*Tests\.java'],
            'go': [r'.*_test\.go']
        }

    async def analyze(self, project_path: str, config: Any) -> Dict[str, Any]:
        """
        Analyze project for test coverage and quality.
        """
        logger.info(f"Starting test analysis for: {project_path}")

        source_files = self._find_source_files(project_path)
        test_files = self._find_test_files(project_path)

        total_files = len(source_files)
        total_test_files = len(test_files)

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
        test_lines = 0
        languages_found = set()

        # Analyze source files for testability
        for file_path in source_files:
            try:
                issues, lines, language = await self._analyze_source_file(file_path)
                all_issues.extend(issues)
                total_lines += lines
                languages_found.add(language)
            except Exception as e:
                logger.error(f"Failed to analyze {file_path}: {e}")

        # Analyze test files
        test_stats = {'test_functions': 0, 'assertions': 0, 'test_files': total_test_files}
        for test_file in test_files:
            try:
                stats, lines = await self._analyze_test_file(test_file)
                test_lines += lines
                test_stats['test_functions'] += stats.get('test_functions', 0)
                test_stats['assertions'] += stats.get('assertions', 0)
            except Exception as e:
                logger.error(f"Failed to analyze test file {test_file}: {e}")

        # Calculate test coverage metrics
        coverage = self._calculate_test_coverage(total_files, total_test_files, test_stats)

        # Generate test-related issues
        test_issues = self._generate_test_issues(source_files, test_files, test_stats)
        all_issues.extend(test_issues)

        metrics = {
            'total_source_files': total_files,
            'total_test_files': total_test_files,
            'test_functions': test_stats['test_functions'],
            'test_assertions': test_stats['assertions'],
            'test_coverage_percent': coverage,
            'test_to_source_ratio': round(total_test_files / total_files, 2) if total_files > 0 else 0
        }

        return {
            'success': True,
            'issues': all_issues,
            'metrics': metrics,
            'files_analyzed': total_files + total_test_files,
            'lines_analyzed': total_lines + test_lines,
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
                # Skip test files and common directories
                if (not any(pattern in str(file_path) for pattern in ['test', 'spec'])
                    and not any(part.startswith('.') or part in {'__pycache__', 'venv', 'env', 'node_modules', 'build', 'dist'}
                              for part in file_path.parts)):
                    source_files.append(str(file_path))

        return source_files

    def _find_test_files(self, project_path: str) -> List[str]:
        """
        Find all test files in the project.
        """
        test_files = []
        path = Path(project_path)

        for file_path in path.rglob('*'):
            if file_path.is_file():
                file_str = str(file_path).lower()
                for language, patterns in self.test_patterns.items():
                    if any(re.match(pattern, file_str) for pattern in patterns):
                        test_files.append(str(file_path))
                        break

        return test_files

    async def _analyze_source_file(self, file_path: str) -> tuple[List[Dict[str, Any]], int, str]:
        """
        Analyze a source file for testability issues.
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            lines = content.splitlines()
            line_count = len(lines)
            language = self._get_language_from_extension(file_path)

            issues = []

            if language == 'python':
                issues = self._analyze_python_testability(content, file_path, lines)
            # Add other language analysis as needed

            return issues, line_count, language

        except Exception as e:
            logger.error(f"Error analyzing source file {file_path}: {e}")
            return [], 0, 'unknown'

    async def _analyze_test_file(self, file_path: str) -> tuple[Dict[str, int], int]:
        """
        Analyze a test file for test quality metrics.
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            lines = content.splitlines()
            line_count = len(lines)

            stats = {'test_functions': 0, 'assertions': 0}

            # Count test functions and assertions
            language = self._get_language_from_extension(file_path)

            if language == 'python':
                stats['test_functions'] = len(re.findall(r'def test_', content))
                stats['assertions'] = len(re.findall(r'assert\s+', content))
            elif language in ['javascript', 'typescript']:
                stats['test_functions'] = len(re.findall(r'(describe|it|test)\s*\(', content))
                stats['assertions'] = len(re.findall(r'expect\s*\(', content))

            return stats, line_count

        except Exception as e:
            logger.error(f"Error analyzing test file {file_path}: {e}")
            return {'test_functions': 0, 'assertions': 0}, 0

    def _get_language_from_extension(self, file_path: str) -> str:
        """
        Determine programming language from file extension.
        """
        ext = Path(file_path).suffix.lower()
        return self.supported_extensions.get(ext, 'unknown')

    def _analyze_python_testability(self, content: str, file_path: str, lines: List[str]) -> List[Dict[str, Any]]:
        """
        Analyze Python code for testability issues.
        """
        issues = []

        # Check for hardcoded values that might need mocking
        hardcoded_patterns = [
            r'\bopen\s*\(',
            r'\brequests\.\w+\s*\(',
            r'\bos\.\w+\s*\(',
            r'\bdatetime\.datetime\.now\s*\('
        ]

        for pattern in hardcoded_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                line_number = self._get_line_number(content, match.start())
                issues.append({
                    'type': 'testability_issue',
                    'severity': 'low',
                    'title': 'Hardcoded dependency detected',
                    'description': 'Code contains hardcoded dependencies that may be difficult to test',
                    'file_path': file_path,
                    'line_start': line_number,
                    'line_end': line_number,
                    'confidence': 0.6,
                    'recommendation': 'Consider dependency injection or mocking for better testability'
                })

        return issues

    def _calculate_test_coverage(self, source_files: int, test_files: int, test_stats: Dict[str, int]) -> float:
        """
        Calculate estimated test coverage percentage.
        """
        if source_files == 0:
            return 0.0

        # Simple heuristic: assume each test function covers some source code
        test_functions = test_stats.get('test_functions', 0)

        # Estimate coverage based on test-to-source ratio and test function count
        ratio_coverage = min(test_files / source_files * 50, 50)  # Max 50% from file ratio
        function_coverage = min(test_functions * 2, 50)  # Max 50% from test functions

        coverage = ratio_coverage + function_coverage
        return round(min(coverage, 100.0), 1)

    def _generate_test_issues(self, source_files: List[str], test_files: List[str], test_stats: Dict[str, int]) -> List[Dict[str, Any]]:
        """
        Generate issues related to testing.
        """
        issues = []

        # Check for missing tests
        if len(test_files) == 0:
            issues.append({
                'type': 'testing_issue',
                'severity': 'high',
                'title': 'No test files found',
                'description': 'Project contains no test files',
                'file_path': source_files[0] if source_files else '',
                'line_start': 1,
                'line_end': 1,
                'confidence': 1.0,
                'recommendation': 'Add unit tests to ensure code quality and prevent regressions'
            })

        # Check test-to-source ratio
        ratio = len(test_files) / len(source_files) if source_files else 0
        if ratio < 0.1:  # Less than 1 test file per 10 source files
            issues.append({
                'type': 'testing_issue',
                'severity': 'medium',
                'title': 'Low test coverage',
                'description': f'Test-to-source file ratio is {ratio:.2f}',
                'file_path': source_files[0] if source_files else '',
                'line_start': 1,
                'line_end': 1,
                'confidence': 0.8,
                'recommendation': 'Consider adding more test files to improve coverage'
            })

        # Check for test functions
        if test_stats.get('test_functions', 0) == 0 and test_files:
            issues.append({
                'type': 'testing_issue',
                'severity': 'medium',
                'title': 'Test files contain no test functions',
                'description': 'Test files exist but contain no actual test functions',
                'file_path': test_files[0],
                'line_start': 1,
                'line_end': 1,
                'confidence': 0.9,
                'recommendation': 'Add proper test functions to test files'
            })

        return issues

    def _get_line_number(self, content: str, position: int) -> int:
        """
        Get line number from character position in content.
        """
        return content[:position].count('\n') + 1
