"""
AST-based code analysis for multiple programming languages
"""

import ast
import os
import re
from typing import Dict, List, Any, Optional
from pathlib import Path
import json

class ASTAnalyzer:
    """Advanced AST-based code analyzer"""
    
    def __init__(self):
        self.supported_languages = {
            '.py': self._analyze_python,
            '.js': self._analyze_javascript,
            '.jsx': self._analyze_javascript,
            '.ts': self._analyze_typescript,
            '.tsx': self._analyze_typescript,
        }
    
    def analyze_codebase(self, files_data: Dict[str, str]) -> Dict[str, Any]:
        """Analyze entire codebase and return comprehensive results"""
        
        results = {
            "summary": {
                "total_files": len(files_data),
                "total_lines": sum(len(content.splitlines()) for content in files_data.values()),
                "languages": self._detect_languages(files_data),
                "quality_score": 0
            },
            "issues": [],
            "metrics": {
                "complexity": {},
                "duplication": {},
                "security": {},
                "performance": {}
            },
            "dependencies": {},
            "recommendations": []
        }
        
        all_issues = []
        complexity_scores = []
        
        for file_path, content in files_data.items():
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext in self.supported_languages:
                file_analysis = self.supported_languages[file_ext](file_path, content)
                all_issues.extend(file_analysis.get("issues", []))
                
                if "complexity" in file_analysis:
                    complexity_scores.append(file_analysis["complexity"])
                    results["metrics"]["complexity"][file_path] = file_analysis["complexity"]
        
        # Calculate overall quality score
        results["issues"] = all_issues
        results["summary"]["quality_score"] = self._calculate_quality_score(all_issues, complexity_scores)
        results["recommendations"] = self._generate_recommendations(all_issues)
        
        return results
    
    def _analyze_python(self, file_path: str, content: str) -> Dict[str, Any]:
        """Analyze Python code using AST"""
        issues = []
        
        try:
            tree = ast.parse(content)
            
            # Security analysis
            issues.extend(self._check_python_security(tree, file_path))
            
            # Complexity analysis
            complexity = self._calculate_python_complexity(tree)
            
            # Performance analysis
            issues.extend(self._check_python_performance(tree, file_path))
            
            # Code quality analysis
            issues.extend(self._check_python_quality(tree, file_path, content))
            
            return {
                "issues": issues,
                "complexity": complexity,
                "functions": self._extract_python_functions(tree),
                "classes": self._extract_python_classes(tree)
            }
            
        except SyntaxError as e:
            issues.append({
                "file": file_path,
                "type": "Syntax Error",
                "severity": "High",
                "line": e.lineno or 1,
                "message": f"Syntax error: {e.msg}",
                "suggestion": "Fix syntax errors before analysis"
            })
            
        return {"issues": issues, "complexity": 1}
    
    def _check_python_security(self, tree: ast.AST, file_path: str) -> List[Dict]:
        """Check for Python security issues"""
        issues = []
        
        for node in ast.walk(tree):
            # Check for eval/exec usage
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in ['eval', 'exec']:
                    issues.append({
                        "file": file_path,
                        "type": "Security",
                        "severity": "High",
                        "line": node.lineno,
                        "message": f"Dangerous function '{node.func.id}' detected",
                        "suggestion": "Avoid using eval/exec. Use safer alternatives like ast.literal_eval"
                    })
            
            # Check for hardcoded secrets
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id.lower()
                        if any(keyword in var_name for keyword in ['password', 'secret', 'key', 'token']):
                            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                                issues.append({
                                    "file": file_path,
                                    "type": "Security",
                                    "severity": "High",
                                    "line": node.lineno,
                                    "message": f"Hardcoded credential in variable '{target.id}'",
                                    "suggestion": "Move credentials to environment variables or secure config"
                                })
        
        return issues
    
    def _check_python_performance(self, tree: ast.AST, file_path: str) -> List[Dict]:
        """Check for Python performance issues"""
        issues = []
        
        for node in ast.walk(tree):
            # Check for inefficient loops
            if isinstance(node, ast.For):
                # Check for nested loops
                nested_loops = [n for n in ast.walk(node) if isinstance(n, (ast.For, ast.While)) and n != node]
                if len(nested_loops) >= 2:
                    issues.append({
                        "file": file_path,
                        "type": "Performance",
                        "severity": "Medium",
                        "line": node.lineno,
                        "message": "Deeply nested loops detected",
                        "suggestion": "Consider optimizing algorithm complexity or using vectorized operations"
                    })
            
            # Check for string concatenation in loops
            if isinstance(node, ast.For):
                for child in ast.walk(node):
                    if isinstance(child, ast.AugAssign) and isinstance(child.op, ast.Add):
                        if isinstance(child.target, ast.Name):
                            issues.append({
                                "file": file_path,
                                "type": "Performance",
                                "severity": "Medium",
                                "line": child.lineno,
                                "message": "String concatenation in loop",
                                "suggestion": "Use join() or f-strings for better performance"
                            })
        
        return issues
    
    def _check_python_quality(self, tree: ast.AST, file_path: str, content: str) -> List[Dict]:
        """Check Python code quality issues"""
        issues = []
        lines = content.splitlines()
        
        # Check function length
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_lines = self._count_function_lines(node, lines)
                if func_lines > 50:
                    issues.append({
                        "file": file_path,
                        "type": "Code Quality",
                        "severity": "Low",
                        "line": node.lineno,
                        "message": f"Function '{node.name}' is too long ({func_lines} lines)",
                        "suggestion": "Break large functions into smaller, focused functions"
                    })
                
                # Check for too many parameters
                if len(node.args.args) > 5:
                    issues.append({
                        "file": file_path,
                        "type": "Code Quality",
                        "severity": "Medium",
                        "line": node.lineno,
                        "message": f"Function '{node.name}' has too many parameters ({len(node.args.args)})",
                        "suggestion": "Consider using a configuration object or breaking the function"
                    })
        
        # Check for missing docstrings
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                if not ast.get_docstring(node):
                    issues.append({
                        "file": file_path,
                        "type": "Documentation",
                        "severity": "Low",
                        "line": node.lineno,
                        "message": f"{type(node).__name__[:-3]} '{node.name}' missing docstring",
                        "suggestion": "Add docstring to document purpose and usage"
                    })
        
        return issues
    
    def _analyze_javascript(self, file_path: str, content: str) -> Dict[str, Any]:
        """Analyze JavaScript/JSX code using regex patterns"""
        issues = []
        lines = content.splitlines()
        
        # Security checks
        security_patterns = [
            (r'eval\s*\(', "Use of eval() detected", "Avoid eval() - use safer alternatives"),
            (r'innerHTML\s*=', "innerHTML usage detected", "Use textContent or sanitize HTML"),
            (r'document\.write\s*\(', "document.write usage", "Use modern DOM manipulation methods"),
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, message, suggestion in security_patterns:
                if re.search(pattern, line):
                    issues.append({
                        "file": file_path,
                        "type": "Security",
                        "severity": "High",
                        "line": i,
                        "message": message,
                        "suggestion": suggestion
                    })
        
        # Performance checks
        performance_patterns = [
            (r'for\s*\(.*in.*\)', "for...in loop detected", "Consider for...of or forEach for arrays"),
            (r'\.length.*for\s*\(', "Length in loop condition", "Cache array length outside loop"),
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, message, suggestion in performance_patterns:
                if re.search(pattern, line):
                    issues.append({
                        "file": file_path,
                        "type": "Performance",
                        "severity": "Medium",
                        "line": i,
                        "message": message,
                        "suggestion": suggestion
                    })
        
        # Calculate basic complexity
        complexity = self._calculate_js_complexity(content)
        
        return {
            "issues": issues,
            "complexity": complexity
        }
    
    def _analyze_typescript(self, file_path: str, content: str) -> Dict[str, Any]:
        """Analyze TypeScript code"""
        # Use JavaScript analyzer as base, add TypeScript-specific checks
        result = self._analyze_javascript(file_path, content)
        
        lines = content.splitlines()
        
        # TypeScript-specific checks
        for i, line in enumerate(lines, 1):
            # Check for 'any' type usage
            if re.search(r':\s*any\b', line):
                result["issues"].append({
                    "file": file_path,
                    "type": "Type Safety",
                    "severity": "Medium",
                    "line": i,
                    "message": "Usage of 'any' type detected",
                    "suggestion": "Use specific types instead of 'any' for better type safety"
                })
        
        return result
    
    def _calculate_python_complexity(self, tree: ast.AST) -> float:
        """Calculate cyclomatic complexity for Python code"""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        
        return complexity
    
    def _calculate_js_complexity(self, content: str) -> float:
        """Calculate basic complexity for JavaScript code"""
        complexity = 1
        
        # Count control flow statements
        patterns = [r'\bif\b', r'\bwhile\b', r'\bfor\b', r'\bcatch\b', r'\bswitch\b']
        
        for pattern in patterns:
            complexity += len(re.findall(pattern, content))
        
        return complexity
    
    def _calculate_quality_score(self, issues: List[Dict], complexity_scores: List[float]) -> int:
        """Calculate overall quality score"""
        base_score = 100
        
        # Deduct points for issues
        for issue in issues:
            severity = issue.get("severity", "Low")
            if severity == "High":
                base_score -= 15
            elif severity == "Medium":
                base_score -= 8
            else:
                base_score -= 3
        
        # Deduct points for high complexity
        if complexity_scores:
            avg_complexity = sum(complexity_scores) / len(complexity_scores)
            if avg_complexity > 10:
                base_score -= 10
            elif avg_complexity > 5:
                base_score -= 5
        
        return max(0, min(100, base_score))
    
    def _generate_recommendations(self, issues: List[Dict]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Count issues by type
        issue_types = {}
        for issue in issues:
            issue_type = issue.get("type", "Unknown")
            issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
        
        # Generate recommendations based on most common issues
        if issue_types.get("Security", 0) > 0:
            recommendations.append("🔒 Address security vulnerabilities immediately - they pose the highest risk")
        
        if issue_types.get("Performance", 0) > 2:
            recommendations.append("⚡ Focus on performance optimizations to improve user experience")
        
        if issue_types.get("Code Quality", 0) > 5:
            recommendations.append("🧹 Refactor code to improve maintainability and readability")
        
        if issue_types.get("Documentation", 0) > 3:
            recommendations.append("📚 Add documentation to improve code understanding and maintenance")
        
        if not recommendations:
            recommendations.append("✨ Great job! Your code quality is excellent")
        
        return recommendations
    
    def _detect_languages(self, files_data: Dict[str, str]) -> List[str]:
        """Detect programming languages from file extensions"""
        lang_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.jsx': 'JavaScript',
            '.ts': 'TypeScript',
            '.tsx': 'TypeScript',
            '.java': 'Java',
            '.go': 'Go',
            '.rs': 'Rust',
            '.cs': 'C#'
        }
        
        languages = set()
        for file_path in files_data.keys():
            ext = Path(file_path).suffix.lower()
            if ext in lang_map:
                languages.add(lang_map[ext])
        
        return list(languages)
    
    def _extract_python_functions(self, tree: ast.AST) -> List[Dict]:
        """Extract function information from Python AST"""
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    "name": node.name,
                    "line": node.lineno,
                    "args": len(node.args.args),
                    "docstring": ast.get_docstring(node) is not None
                })
        
        return functions
    
    def _extract_python_classes(self, tree: ast.AST) -> List[Dict]:
        """Extract class information from Python AST"""
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                classes.append({
                    "name": node.name,
                    "line": node.lineno,
                    "methods": len(methods),
                    "docstring": ast.get_docstring(node) is not None
                })
        
        return classes
    
    def _count_function_lines(self, func_node: ast.FunctionDef, lines: List[str]) -> int:
        """Count lines in a function"""
        start_line = func_node.lineno - 1
        end_line = start_line
        
        # Find the end of the function
        for i in range(start_line + 1, len(lines)):
            if lines[i].strip() and not lines[i].startswith(' ') and not lines[i].startswith('\t'):
                end_line = i
                break
        else:
            end_line = len(lines)
        
        return end_line - start_line