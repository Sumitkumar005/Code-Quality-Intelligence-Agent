"""
AST-based code analyzer for parsing and analyzing code structure.
"""

import ast
import os
from typing import Dict, List, Any, Optional, Set
from pathlib import Path

from app.core.logging import get_logger

logger = get_logger(__name__)


class ASTAnalyzer:
    """
    Analyzes Python code using Abstract Syntax Tree (AST) parsing.
    """

    def __init__(self):
        self.supported_extensions = {'.py', '.pyw'}
        self.visitor = CodeVisitor()

    async def analyze(self, project_path: str, config: Any) -> Dict[str, Any]:
        """
        Analyze Python files in the project using AST.
        """
        logger.info(f"Starting AST analysis for: {project_path}")

        python_files = self._find_python_files(project_path)
        total_files = len(python_files)

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
        metrics = {
            'functions': 0,
            'classes': 0,
            'imports': 0,
            'complexity': 0,
            'max_nesting': 0
        }

        for file_path in python_files:
            try:
                issues, file_metrics, lines = await self._analyze_file(file_path)
                all_issues.extend(issues)

                # Aggregate metrics
                for key, value in file_metrics.items():
                    if key in metrics:
                        metrics[key] += value
                    else:
                        metrics[key] = value

                total_lines += lines

            except Exception as e:
                logger.error(f"Failed to analyze {file_path}: {e}")
                all_issues.append({
                    'type': 'syntax_error',
                    'severity': 'high',
                    'title': f'Syntax Error in {os.path.basename(file_path)}',
                    'description': f'Failed to parse Python file: {str(e)}',
                    'file_path': file_path,
                    'line_start': 1,
                    'line_end': 1,
                    'confidence': 1.0
                })

        # Calculate averages
        if total_files > 0:
            metrics['avg_complexity'] = round(metrics['complexity'] / total_files, 2)
            metrics['avg_functions_per_file'] = round(metrics['functions'] / total_files, 2)
            metrics['avg_classes_per_file'] = round(metrics['classes'] / total_files, 2)

        return {
            'success': True,
            'issues': all_issues,
            'metrics': metrics,
            'files_analyzed': total_files,
            'lines_analyzed': total_lines,
            'languages': ['python']
        }

    def _find_python_files(self, project_path: str) -> List[str]:
        """
        Find all Python files in the project.
        """
        python_files = []
        path = Path(project_path)

        for file_path in path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                # Skip common directories
                if not any(part.startswith('.') or part in {'__pycache__', 'venv', 'env', 'node_modules'}
                          for part in file_path.parts):
                    python_files.append(str(file_path))

        return python_files

    async def _analyze_file(self, file_path: str) -> tuple[List[Dict[str, Any]], Dict[str, Any], int]:
        """
        Analyze a single Python file.
        """
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        lines_count = len(content.splitlines())

        try:
            tree = ast.parse(content, filename=file_path)
            self.visitor.reset()

            # Visit AST nodes
            self.visitor.visit(tree)

            # Generate issues
            issues = self._generate_issues(file_path, self.visitor)

            # Calculate metrics
            metrics = self._calculate_metrics(self.visitor)

            return issues, metrics, lines_count

        except SyntaxError as e:
            return [{
                'type': 'syntax_error',
                'severity': 'critical',
                'title': 'Syntax Error',
                'description': f'Syntax error at line {e.lineno}: {e.msg}',
                'file_path': file_path,
                'line_start': e.lineno or 1,
                'line_end': e.lineno or 1,
                'confidence': 1.0
            }], {}, lines_count

    def _generate_issues(self, file_path: str, visitor: 'CodeVisitor') -> List[Dict[str, Any]]:
        """
        Generate issues based on AST analysis.
        """
        issues = []

        # Check for unused imports
        for import_name, lineno in visitor.unused_imports:
            issues.append({
                'type': 'unused_import',
                'severity': 'low',
                'title': f'Unused import: {import_name}',
                'description': f'Import "{import_name}" is imported but never used',
                'file_path': file_path,
                'line_start': lineno,
                'line_end': lineno,
                'confidence': 0.8,
                'suggestion': f'Remove unused import: {import_name}'
            })

        # Check for long functions
        for func_name, lineno, length in visitor.long_functions:
            if length > 50:  # Configurable threshold
                issues.append({
                    'type': 'long_function',
                    'severity': 'medium',
                    'title': f'Long function: {func_name}',
                    'description': f'Function "{func_name}" is {length} lines long',
                    'file_path': file_path,
                    'line_start': lineno,
                    'line_end': lineno + length,
                    'confidence': 0.9,
                    'suggestion': 'Consider breaking this function into smaller functions'
                })

        # Check for deep nesting
        for lineno, depth in visitor.deep_nesting:
            if depth > 4:  # Configurable threshold
                issues.append({
                    'type': 'deep_nesting',
                    'severity': 'medium',
                    'title': 'Deep nesting detected',
                    'description': f'Code is nested {depth} levels deep',
                    'file_path': file_path,
                    'line_start': lineno,
                    'line_end': lineno,
                    'confidence': 0.7,
                    'suggestion': 'Consider extracting nested code into separate functions'
                })

        # Check for bare except clauses
        for lineno in visitor.bare_except:
            issues.append({
                'type': 'bare_except',
                'severity': 'high',
                'title': 'Bare except clause',
                'description': 'Using bare "except:" catches all exceptions including system exits',
                'file_path': file_path,
                'line_start': lineno,
                'line_end': lineno,
                'confidence': 0.95,
                'suggestion': 'Specify exception types to catch or use "except Exception:"'
            })

        return issues

    def _calculate_metrics(self, visitor: 'CodeVisitor') -> Dict[str, Any]:
        """
        Calculate code metrics from AST visitor.
        """
        return {
            'functions': len(visitor.functions),
            'classes': len(visitor.classes),
            'imports': len(visitor.imports),
            'complexity': sum(visitor.complexity_scores.values()),
            'max_nesting': max(visitor.nesting_depths) if visitor.nesting_depths else 0,
            'total_lines': sum(visitor.function_lengths.values())
        }


class CodeVisitor(ast.NodeVisitor):
    """
    AST visitor for collecting code metrics and potential issues.
    """

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset visitor state for new file analysis."""
        self.functions = []
        self.classes = []
        self.imports = []
        self.unused_imports = []
        self.long_functions = []
        self.deep_nesting = []
        self.bare_except = []
        self.complexity_scores = {}
        self.nesting_depths = []
        self.function_lengths = {}
        self.current_nesting = 0
        self.imported_names = set()
        self.used_names = set()

    def visit_Import(self, node):
        """Visit import statements."""
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.imports.append((name, node.lineno))
            self.imported_names.add(name.split('.')[0])
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """Visit from import statements."""
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.imports.append((name, node.lineno))
            self.imported_names.add(name)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        """Visit function definitions."""
        self.functions.append((node.name, node.lineno))

        # Calculate function length
        end_lineno = getattr(node, 'end_lineno', node.lineno)
        length = end_lineno - node.lineno + 1
        self.function_lengths[node.name] = length

        if length > 30:  # Track potentially long functions
            self.long_functions.append((node.name, node.lineno, length))

        # Calculate complexity (simplified)
        complexity = self._calculate_complexity(node)
        self.complexity_scores[node.name] = complexity

        self.generic_visit(node)

    def visit_ClassDef(self, node):
        """Visit class definitions."""
        self.classes.append((node.name, node.lineno))
        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        """Visit exception handlers."""
        if node.type is None:  # Bare except
            self.bare_except.append(node.lineno)
        self.generic_visit(node)

    def visit_If(self, node):
        """Visit if statements to track nesting."""
        self.current_nesting += 1
        if self.current_nesting > 3:
            self.deep_nesting.append((node.lineno, self.current_nesting))

        self.generic_visit(node)
        self.current_nesting -= 1

    def visit_For(self, node):
        """Visit for loops to track nesting."""
        self.current_nesting += 1
        if self.current_nesting > 3:
            self.deep_nesting.append((node.lineno, self.current_nesting))

        self.generic_visit(node)
        self.current_nesting -= 1

    def visit_While(self, node):
        """Visit while loops to track nesting."""
        self.current_nesting += 1
        if self.current_nesting > 3:
            self.deep_nesting.append((node.lineno, self.current_nesting))

        self.generic_visit(node)
        self.current_nesting -= 1

    def visit_With(self, node):
        """Visit with statements to track nesting."""
        self.current_nesting += 1
        if self.current_nesting > 3:
            self.deep_nesting.append((node.lineno, self.current_nesting))

        self.generic_visit(node)
        self.current_nesting -= 1

    def visit_Name(self, node):
        """Visit name nodes to track usage."""
        if isinstance(node.ctx, (ast.Load, ast.AugLoad)):
            self.used_names.add(node.id)
        self.generic_visit(node)

    def _calculate_complexity(self, node) -> int:
        """
        Calculate cyclomatic complexity for a function (simplified).
        """
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With)):
                complexity += 1
            elif isinstance(child, ast.BoolOp) and len(child.values) > 1:
                complexity += len(child.values) - 1
            elif isinstance(child, ast.Try):
                complexity += len(child.handlers) + len(child.orelse)

        return complexity
