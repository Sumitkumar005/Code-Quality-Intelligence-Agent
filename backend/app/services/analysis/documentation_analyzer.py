"""
Documentation analyzer for assessing code documentation quality.
"""

import os
from typing import Dict, List, Any, Optional
from pathlib import Path
import re

from app.core.logging import get_logger

logger = get_logger(__name__)


class DocumentationAnalyzer:
    """
    Analyzes code documentation coverage and quality.
    """

    def __init__(self):
        self.supported_extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.go': 'go'
        }

    async def analyze(self, project_path: str, config: Any) -> Dict[str, Any]:
        """
        Analyze project for documentation quality.
        """
        logger.info(f"Starting documentation analysis for: {project_path}")

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
        documented_functions = 0
        total_functions = 0

        for file_path in source_files:
            try:
                issues, lines, language, doc_stats = await self._analyze_file(file_path)
                all_issues.extend(issues)
                total_lines += lines
                languages_found.add(language)
                documented_functions += doc_stats.get('documented_functions', 0)
                total_functions += doc_stats.get('total_functions', 0)

            except Exception as e:
                logger.error(f"Failed to analyze {file_path}: {e}")

        # Calculate documentation coverage
        coverage = (documented_functions / total_functions * 100) if total_functions > 0 else 100.0

        metrics = {
            'total_functions': total_functions,
            'documented_functions': documented_functions,
            'documentation_coverage_percent': round(coverage, 2)
        }

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

    async def _analyze_file(self, file_path: str) -> tuple[List[Dict[str, Any]], int, str, Dict[str, int]]:
        """
        Analyze a single file for documentation quality.
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            lines = content.splitlines()
            line_count = len(lines)

            language = self._get_language_from_extension(file_path)

            issues = []
            doc_stats = {'total_functions': 0, 'documented_functions': 0}

            if language == 'python':
                issues, doc_stats = self._analyze_python_doc(content, file_path, lines)
            else:
                # Basic checks for other languages
                issues, doc_stats = self._analyze_generic_doc(content, file_path, lines, language)

            return issues, line_count, language, doc_stats

        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {e}")
            return [], 0, 'unknown', {'total_functions': 0, 'documented_functions': 0}

    def _get_language_from_extension(self, file_path: str) -> str:
        """
        Determine programming language from file extension.
        """
        ext = Path(file_path).suffix.lower()
        return self.supported_extensions.get(ext, 'unknown')

    def _analyze_python_doc(self, content: str, file_path: str, lines: List[str]) -> tuple[List[Dict[str, Any]], Dict[str, int]]:
        """
        Analyze Python code documentation.
        """
        import ast

        issues = []
        doc_stats = {'total_functions': 0, 'documented_functions': 0}

        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    doc_stats['total_functions'] += 1
                    if ast.get_docstring(node) is None:
                        issues.append({
                            'type': 'documentation_issue',
                            'severity': 'medium',
                            'title': 'Missing function docstring',
                            'description': f'Function "{node.name}" is missing a docstring',
                            'file_path': file_path,
                            'line_start': node.lineno,
                            'line_end': node.lineno,
                            'confidence': 0.8,
                            'recommendation': 'Add a descriptive docstring to the function'
                        })
                    else:
                        doc_stats['documented_functions'] += 1

        except SyntaxError:
            issues.append({
                'type': 'documentation_issue',
                'severity': 'high',
                'title': 'Syntax Error Prevents Documentation Analysis',
                'description': 'File contains syntax errors that prevent documentation analysis',
                'file_path': file_path,
                'line_start': 1,
                'line_end': 1,
                'confidence': 1.0,
                'recommendation': 'Fix syntax errors before analyzing documentation'
            })

        return issues, doc_stats

    def _analyze_generic_doc(self, content: str, file_path: str, lines: List[str], language: str) -> tuple[List[Dict[str, Any]], Dict[str, int]]:
        """
        Basic documentation analysis for other languages.
        """
        issues = []
        doc_stats = {'total_functions': 0, 'documented_functions': 0}

        # Simple heuristic: count /** */ or /// comments before functions
        function_pattern = re.compile(r'^\s*(function|def|class|method)\s+\w+', re.MULTILINE)
        doc_comment_pattern = re.compile(r'/\*\*.*?\*/|///.*', re.DOTALL)

        functions = function_pattern.findall(content)
        doc_comments = doc_comment_pattern.findall(content)

        doc_stats['total_functions'] = len(functions)
        doc_stats['documented_functions'] = len(doc_comments)

        if len(functions) > len(doc_comments):
            issues.append({
                'type': 'documentation_issue',
                'severity': 'medium',
                'title': 'Potential missing documentation',
                'description': 'Some functions or classes may be missing documentation comments',
                'file_path': file_path,
                'line_start': 1,
                'line_end': 1,
                'confidence': 0.6,
                'recommendation': 'Add documentation comments to functions and classes'
            })

        return issues, doc_stats
