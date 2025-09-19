"""
Code complexity analyzer for measuring code maintainability.
"""

import ast
import re
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

from app.core.logging import get_logger

logger = get_logger(__name__)


class ComplexityAnalyzer:
    """
    Analyzes code complexity metrics like cyclomatic complexity, nesting depth, etc.
    """

    def __init__(self):
        self.supported_extensions = {'.py': 'python', '.js': 'javascript', '.ts': 'typescript', '.java': 'java'}

    async def analyze(self, project_path: str, config: Any) -> Dict[str, Any]:
        """
        Analyze project for code complexity metrics.
        """
        logger.info(f"Starting complexity analysis for: {project_path}")

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
        complexity_data = []

        for file_path in source_files:
            try:
                issues, lines, language, file_complexity = await self._analyze_file(file_path)
                all_issues.extend(issues)
                total_lines += lines
                languages_found.add(language)
                complexity_data.append(file_complexity)

            except Exception as e:
                logger.error(f"Failed to analyze {file_path}: {e}")

        # Calculate aggregate complexity metrics
        metrics = self._calculate_complexity_metrics(complexity_data, total_files)

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

    async def _analyze_file(self, file_path: str) -> tuple[List[Dict[str, Any]], int, str, Dict[str, Any]]:
        """
        Analyze a single file for complexity metrics.
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            lines = content.splitlines()
            line_count = len(lines)

            # Determine language
            language = self._get_language_from_extension(file_path)

            # Analyze complexity based on language
            if language == 'python':
                issues, complexity_data = self._analyze_python_complexity(content, file_path, lines)
            else:
                # Basic analysis for other languages
                issues, complexity_data = self._analyze_generic_complexity(content, file_path, lines, language)

            return issues, line_count, language, complexity_data

        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {e}")
            return [], 0, 'unknown', {}

    def _get_language_from_extension(self, file_path: str) -> str:
        """
        Determine programming language from file extension.
        """
        ext = Path(file_path).suffix.lower()
        return self.supported_extensions.get(ext, 'unknown')

    def _analyze_python_complexity(self, content: str, file_path: str, lines: List[str]) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Analyze Python code complexity using AST.
        """
        issues = []

        try:
            tree = ast.parse(content)
            analyzer = PythonComplexityVisitor()
            analyzer.visit(tree)

            # Generate issues based on complexity thresholds
            issues.extend(self._generate_complexity_issues(analyzer.functions, file_path, 'python'))

            # Calculate file-level metrics
            complexity_data = {
                'functions': len(analyzer.functions),
                'classes': len(analyzer.classes),
                'avg_cyclomatic_complexity': analyzer.get_average_complexity(),
                'max_cyclomatic_complexity': analyzer.get_max_complexity(),
                'total_lines': len(lines),
                'code_lines': analyzer.get_code_lines(),
                'max_nesting_depth': analyzer.get_max_nesting_depth(),
                'maintainability_index': analyzer.calculate_maintainability_index(len(lines))
            }

        except SyntaxError:
            issues.append({
                'type': 'complexity_issue',
                'severity': 'high',
                'title': 'Syntax Error Prevents Complexity Analysis',
                'description': 'File contains syntax errors that prevent complexity analysis',
                'file_path': file_path,
                'line_start': 1,
                'line_end': 1,
                'confidence': 1.0,
                'recommendation': 'Fix syntax errors before analyzing complexity'
            })
            complexity_data = {}

        return issues, complexity_data

    def _analyze_generic_complexity(self, content: str, file_path: str, lines: List[str], language: str) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Analyze complexity for languages without AST support.
        """
        issues = []

        # Basic line-based analysis
        code_lines = self._count_code_lines(lines, language)
        functions = self._estimate_functions(content, language)
        classes = self._estimate_classes(content, language)

        # Estimate complexity based on patterns
        estimated_complexity = self._estimate_complexity(content, language)

        complexity_data = {
            'functions': len(functions),
            'classes': len(classes),
            'estimated_complexity': estimated_complexity,
            'total_lines': len(lines),
            'code_lines': code_lines,
            'max_nesting_depth': self._estimate_nesting_depth(content, language)
        }

        # Generate issues for high complexity
        if estimated_complexity > 50:
            issues.append({
                'type': 'complexity_issue',
                'severity': 'medium',
                'title': 'High Estimated Complexity',
                'description': f'File has high estimated complexity score: {estimated_complexity}',
                'file_path': file_path,
                'line_start': 1,
                'line_end': len(lines),
                'confidence': 0.7,
                'recommendation': 'Consider refactoring to reduce complexity'
            })

        return issues, complexity_data

    def _generate_complexity_issues(self, functions: List[Dict[str, Any]], file_path: str, language: str) -> List[Dict[str, Any]]:
        """
        Generate issues based on complexity analysis.
        """
        issues = []

        for func in functions:
            complexity = func.get('complexity', 0)
            name = func.get('name', 'unknown')
            lineno = func.get('lineno', 1)

            # Cyclomatic complexity thresholds
            if complexity > 10:
                severity = 'high'
                title = f'Very High Cyclomatic Complexity: {name}'
            elif complexity > 5:
                severity = 'medium'
                title = f'High Cyclomatic Complexity: {name}'
            else:
                continue  # Not an issue

            issues.append({
                'type': 'complexity_issue',
                'severity': severity,
                'title': title,
                'description': f'Function {name} has cyclomatic complexity of {complexity}',
                'file_path': file_path,
                'line_start': lineno,
                'line_end': lineno,
                'confidence': 0.9,
                'complexity_score': complexity,
                'recommendation': 'Consider breaking this function into smaller, more focused functions'
            })

        return issues

    def _count_code_lines(self, lines: List[str], language: str) -> int:
        """
        Count actual code lines (excluding comments and blank lines).
        """
        code_lines = 0

        if language == 'python':
            comment_pattern = re.compile(r'^\s*#')
        elif language in ['javascript', 'typescript']:
            comment_pattern = re.compile(r'^\s*//|^\s*/\*|\*/\s*$')
        else:
            comment_pattern = re.compile(r'^\s*//|^\s*#|^\s*/\*')

        for line in lines:
            stripped = line.strip()
            if stripped and not comment_pattern.match(line):
                code_lines += 1

        return code_lines

    def _estimate_functions(self, content: str, language: str) -> List[str]:
        """
        Estimate number of functions in the file.
        """
        if language == 'python':
            pattern = r'^\s*def\s+\w+\s*\('
        elif language in ['javascript', 'typescript']:
            pattern = r'^\s*(function\s+\w+|const\s+\w+\s*=\s*\(|let\s+\w+\s*=\s*\()'
        elif language == 'java':
            pattern = r'^\s*(public|private|protected)?\s*\w+\s+\w+\s*\('
        else:
            return []

        matches = re.findall(pattern, content, re.MULTILINE)
        return matches

    def _estimate_classes(self, content: str, language: str) -> List[str]:
        """
        Estimate number of classes in the file.
        """
        if language == 'python':
            pattern = r'^\s*class\s+\w+'
        elif language in ['javascript', 'typescript']:
            pattern = r'^\s*class\s+\w+'
        elif language == 'java':
            pattern = r'^\s*(public\s+)?class\s+\w+'
        else:
            return []

        matches = re.findall(pattern, content, re.MULTILINE)
        return matches

    def _estimate_complexity(self, content: str, language: str) -> int:
        """
        Estimate complexity based on code patterns.
        """
        complexity = 1  # Base complexity

        # Count decision points
        decision_patterns = [
            r'\bif\b', r'\belif\b', r'\belse\b',
            r'\bfor\b', r'\bwhile\b', r'\bcase\b',
            r'\bcatch\b', r'\band\b', r'\bor\b'
        ]

        for pattern in decision_patterns:
            matches = len(re.findall(pattern, content, re.IGNORECASE))
            complexity += matches

        # Count function calls (potential complexity)
        func_call_pattern = r'\w+\s*\('
        func_calls = len(re.findall(func_call_pattern, content))
        complexity += min(func_calls // 10, 10)  # Cap at 10 additional points

        return complexity

    def _estimate_nesting_depth(self, content: str, language: str) -> int:
        """
        Estimate maximum nesting depth.
        """
        max_depth = 0
        current_depth = 0

        lines = content.splitlines()

        for line in lines:
            stripped = line.strip()

            # Increase depth
            if any(keyword in stripped for keyword in ['if ', 'for ', 'while ', 'with ', 'try:', 'def ', 'class ']):
                current_depth += 1
                max_depth = max(max_depth, current_depth)

            # Decrease depth (simplified)
            elif stripped.startswith(('return', 'break', 'continue', 'pass')) or stripped.endswith(':'):
                current_depth = max(0, current_depth - 1)

        return max_depth

    def _calculate_complexity_metrics(self, complexity_data: List[Dict[str, Any]], total_files: int) -> Dict[str, Any]:
        """
        Calculate aggregate complexity metrics.
        """
        if not complexity_data:
            return {}

        # Aggregate metrics
        total_functions = sum(data.get('functions', 0) for data in complexity_data)
        total_classes = sum(data.get('classes', 0) for data in complexity_data)
        total_lines = sum(data.get('total_lines', 0) for data in complexity_data)
        total_code_lines = sum(data.get('code_lines', 0) for data in complexity_data)

        # Calculate averages
        avg_complexity = sum(data.get('avg_cyclomatic_complexity', 0) for data in complexity_data) / len(complexity_data) if complexity_data else 0
        max_complexity = max((data.get('max_cyclomatic_complexity', 0) for data in complexity_data), default=0)
        max_nesting = max((data.get('max_nesting_depth', 0) for data in complexity_data), default=0)

        # Calculate maintainability index (simplified)
        if total_lines > 0:
            maintainability_index = max(0, 171 - 5.2 * (total_lines / total_files) - 0.23 * avg_complexity - 16.2 * (total_functions / total_files))
        else:
            maintainability_index = 100

        return {
            'total_functions': total_functions,
            'total_classes': total_classes,
            'total_lines': total_lines,
            'total_code_lines': total_code_lines,
            'avg_cyclomatic_complexity': round(avg_complexity, 2),
            'max_cyclomatic_complexity': max_complexity,
            'max_nesting_depth': max_nesting,
            'maintainability_index': round(maintainability_index, 1),
            'functions_per_file': round(total_functions / total_files, 2) if total_files > 0 else 0,
            'classes_per_file': round(total_classes / total_files, 2) if total_files > 0 else 0,
            'code_to_comment_ratio': round(total_code_lines / total_lines, 2) if total_lines > 0 else 0
        }


class PythonComplexityVisitor(ast.NodeVisitor):
    """
    AST visitor for calculating Python code complexity metrics.
    """

    def __init__(self):
        self.functions = []
        self.classes = []
        self.current_class = None
        self.nesting_depth = 0
        self.max_nesting_depth = 0

    def visit_FunctionDef(self, node):
        """Visit function definitions."""
        complexity = self._calculate_cyclomatic_complexity(node)

        self.functions.append({
            'name': node.name,
            'lineno': node.lineno,
            'complexity': complexity,
            'class': self.current_class
        })

        # Track nesting
        self.nesting_depth += 1
        self.max_nesting_depth = max(self.max_nesting_depth, self.nesting_depth)

        self.generic_visit(node)
        self.nesting_depth -= 1

    def visit_ClassDef(self, node):
        """Visit class definitions."""
        self.classes.append({
            'name': node.name,
            'lineno': node.lineno
        })

        old_class = self.current_class
        self.current_class = node.name

        self.nesting_depth += 1
        self.max_nesting_depth = max(self.max_nesting_depth, self.nesting_depth)

        self.generic_visit(node)

        self.current_class = old_class
        self.nesting_depth -= 1

    def visit_If(self, node):
        """Track nesting depth."""
        self.nesting_depth += 1
        self.max_nesting_depth = max(self.max_nesting_depth, self.nesting_depth)
        self.generic_visit(node)
        self.nesting_depth -= 1

    def visit_For(self, node):
        """Track nesting depth."""
        self.nesting_depth += 1
        self.max_nesting_depth = max(self.max_nesting_depth, self.nesting_depth)
        self.generic_visit(node)
        self.nesting_depth -= 1

    def visit_While(self, node):
        """Track nesting depth."""
        self.nesting_depth += 1
        self.max_nesting_depth = max(self.max_nesting_depth, self.nesting_depth)
        self.generic_visit(node)
        self.nesting_depth -= 1

    def visit_With(self, node):
        """Track nesting depth."""
        self.nesting_depth += 1
        self.max_nesting_depth = max(self.max_nesting_depth, self.nesting_depth)
        self.generic_visit(node)
        self.nesting_depth -= 1

    def visit_Try(self, node):
        """Track nesting depth."""
        self.nesting_depth += 1
        self.max_nesting_depth = max(self.max_nesting_depth, self.nesting_depth)
        self.generic_visit(node)
        self.nesting_depth -= 1

    def _calculate_cyclomatic_complexity(self, node) -> int:
        """
        Calculate cyclomatic complexity for a function.
        """
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With)):
                complexity += 1
            elif isinstance(child, ast.BoolOp) and len(child.values) > 1:
                complexity += len(child.values) - 1
            elif isinstance(child, ast.Try):
                complexity += len(child.handlers) + len(child.orelse)
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1

        return complexity

    def get_average_complexity(self) -> float:
        """
        Get average cyclomatic complexity.
        """
        if not self.functions:
            return 0
        return sum(f['complexity'] for f in self.functions) / len(self.functions)

    def get_max_complexity(self) -> int:
        """
        Get maximum cyclomatic complexity.
        """
        if not self.functions:
            return 0
        return max(f['complexity'] for f in self.functions)

    def get_max_nesting_depth(self) -> int:
        """
        Get maximum nesting depth.
        """
        return self.max_nesting_depth

    def get_code_lines(self) -> int:
        """
        Estimate code lines (simplified).
        """
        # This is a rough estimate - in practice, you'd need source code access
        return sum(f.get('complexity', 1) * 5 for f in self.functions)

    def calculate_maintainability_index(self, total_lines: int) -> float:
        """
        Calculate maintainability index (simplified version).
        """
        if not self.functions:
            return 100

        avg_complexity = self.get_average_complexity()
        num_functions = len(self.functions)

        # Simplified maintainability index formula
        mi = max(0, 171 - 5.2 * (total_lines / max(num_functions, 1)) - 0.23 * avg_complexity - 16.2 * num_functions)
        return round(mi, 1)
