"""
Dependency analyzer for assessing code dependencies and potential issues.
"""

import os
from typing import Dict, List, Any, Optional
from pathlib import Path
import re
import subprocess

from app.core.logging import get_logger

logger = get_logger(__name__)


class DependencyAnalyzer:
    """
    Analyzes code dependencies, imports, and potential issues.
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
        Analyze project dependencies.
        """
        logger.info(f"Starting dependency analysis for: {project_path}")

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
        dependency_data = {}

        for file_path in source_files:
            try:
                issues, lines, language, deps = await self._analyze_file(file_path)
                all_issues.extend(issues)
                total_lines += lines
                languages_found.add(language)

                # Aggregate dependency data
                for dep, count in deps.items():
                    dependency_data[dep] = dependency_data.get(dep, 0) + count

            except Exception as e:
                logger.error(f"Failed to analyze {file_path}: {e}")

        # Analyze dependency issues
        dep_issues = self._analyze_dependency_issues(dependency_data, project_path)
        all_issues.extend(dep_issues)

        # Calculate dependency metrics
        metrics = self._calculate_dependency_metrics(dependency_data, total_files)

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
        Analyze a single file for dependencies.
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            lines = content.splitlines()
            line_count = len(lines)
            language = self._get_language_from_extension(file_path)

            issues = []
            dependencies = {}

            if language == 'python':
                issues, dependencies = self._analyze_python_dependencies(content, file_path, lines)
            elif language in ['javascript', 'typescript']:
                issues, dependencies = self._analyze_js_dependencies(content, file_path, lines)
            else:
                # Basic analysis for other languages
                dependencies = self._extract_basic_imports(content, language)

            return issues, line_count, language, dependencies

        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {e}")
            return [], 0, 'unknown', {}

    def _get_language_from_extension(self, file_path: str) -> str:
        """
        Determine programming language from file extension.
        """
        ext = Path(file_path).suffix.lower()
        return self.supported_extensions.get(ext, 'unknown')

    def _analyze_python_dependencies(self, content: str, file_path: str, lines: List[str]) -> tuple[List[Dict[str, Any]], Dict[str, int]]:
        """
        Analyze Python import dependencies.
        """
        issues = []
        dependencies = {}

        # Extract imports
        import_patterns = [
            r'^import\s+(\w+)',  # import module
            r'^from\s+(\w+)\s+import',  # from module import
        ]

        for pattern in import_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            for match in matches:
                dependencies[match] = dependencies.get(match, 0) + 1

        # Check for problematic imports
        problematic_imports = {
            'os.system': 'Use subprocess instead of os.system for security',
            'pickle': 'Pickle can be unsafe, consider safer alternatives',
            'eval': 'Eval is dangerous and should be avoided',
            'exec': 'Exec is dangerous and should be avoided'
        }

        for problematic, message in problematic_imports.items():
            if re.search(r'\b' + re.escape(problematic) + r'\b', content):
                line_number = self._find_line_with_pattern(content, problematic)
                issues.append({
                    'type': 'dependency_issue',
                    'severity': 'high' if problematic in ['eval', 'exec'] else 'medium',
                    'title': f'Problematic import: {problematic}',
                    'description': message,
                    'file_path': file_path,
                    'line_start': line_number,
                    'line_end': line_number,
                    'confidence': 0.9,
                    'recommendation': f'Avoid using {problematic} or use safer alternatives'
                })

        return issues, dependencies

    def _analyze_js_dependencies(self, content: str, file_path: str, lines: List[str]) -> tuple[List[Dict[str, Any]], Dict[str, int]]:
        """
        Analyze JavaScript/TypeScript import dependencies.
        """
        issues = []
        dependencies = {}

        # Extract imports
        import_patterns = [
            r'import\s+.*?\s+from\s+["\']([^"\']+)["\']',  # ES6 imports
            r'const\s+\w+\s*=\s*require\s*\(\s*["\']([^"\']+)["\']',  # CommonJS require
        ]

        for pattern in import_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                # Extract module name (remove path components)
                module_name = match.split('/')[0] if '/' in match else match
                dependencies[module_name] = dependencies.get(module_name, 0) + 1

        # Check for problematic patterns
        problematic_patterns = [
            r'eval\s*\(',
            r'new\s+Function\s*\(',
            r'document\.write\s*\(',
            r'innerHTML\s*=',
        ]

        for pattern in problematic_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                line_number = self._get_line_number(content, match.start())
                issues.append({
                    'type': 'dependency_issue',
                    'severity': 'high',
                    'title': 'Potentially unsafe operation',
                    'description': 'Code contains potentially unsafe operations',
                    'file_path': file_path,
                    'line_start': line_number,
                    'line_end': line_number,
                    'confidence': 0.8,
                    'recommendation': 'Review and sanitize user inputs, avoid direct DOM manipulation'
                })

        return issues, dependencies

    def _extract_basic_imports(self, content: str, language: str) -> Dict[str, int]:
        """
        Basic import extraction for other languages.
        """
        dependencies = {}

        # Generic import patterns
        if language == 'java':
            matches = re.findall(r'^import\s+([^;]+);', content, re.MULTILINE)
        elif language == 'go':
            matches = re.findall(r'^import\s+["\']([^"\']+)["\']', content, re.MULTILINE)
        else:
            matches = []

        for match in matches:
            module_name = match.split('.')[0] if '.' in match else match
            dependencies[module_name] = dependencies.get(module_name, 0) + 1

        return dependencies

    def _analyze_dependency_issues(self, dependencies: Dict[str, int], project_path: str) -> List[Dict[str, Any]]:
        """
        Analyze dependency-related issues.
        """
        issues = []

        # Check for dependency management files
        has_requirements = os.path.exists(os.path.join(project_path, 'requirements.txt'))
        has_package_json = os.path.exists(os.path.join(project_path, 'package.json'))
        has_go_mod = os.path.exists(os.path.join(project_path, 'go.mod'))

        if not (has_requirements or has_package_json or has_go_mod):
            issues.append({
                'type': 'dependency_issue',
                'severity': 'medium',
                'title': 'Missing dependency management file',
                'description': 'Project does not have a dependency management file (requirements.txt, package.json, go.mod, etc.)',
                'file_path': project_path,
                'line_start': 1,
                'line_end': 1,
                'confidence': 1.0,
                'recommendation': 'Add a dependency management file to track project dependencies'
            })

        # Check for potentially unused dependencies
        # This is a simple heuristic - in practice, you'd need more sophisticated analysis
        if len(dependencies) > 20:
            issues.append({
                'type': 'dependency_issue',
                'severity': 'low',
                'title': 'Many dependencies detected',
                'description': f'Project has {len(dependencies)} unique dependencies',
                'file_path': project_path,
                'line_start': 1,
                'line_end': 1,
                'confidence': 0.6,
                'recommendation': 'Review dependencies and remove unused ones to reduce bundle size and security surface'
            })

        return issues

    def _calculate_dependency_metrics(self, dependencies: Dict[str, int], total_files: int) -> Dict[str, Any]:
        """
        Calculate dependency-related metrics.
        """
        total_imports = sum(dependencies.values())
        unique_dependencies = len(dependencies)

        # Calculate dependency density
        density = total_imports / total_files if total_files > 0 else 0

        # Find most used dependencies
        most_used = sorted(dependencies.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            'total_imports': total_imports,
            'unique_dependencies': unique_dependencies,
            'imports_per_file': round(density, 2),
            'most_used_dependencies': most_used
        }

    def _find_line_with_pattern(self, content: str, pattern: str) -> int:
        """
        Find the line number containing a specific pattern.
        """
        lines = content.splitlines()
        for i, line in enumerate(lines, 1):
            if pattern in line:
                return i
        return 1

    def _get_line_number(self, content: str, position: int) -> int:
        """
        Get line number from character position in content.
        """
        return content[:position].count('\n') + 1
