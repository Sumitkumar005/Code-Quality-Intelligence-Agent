"""
Analysis orchestrator for coordinating code analysis services.
"""

import asyncio
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import os
import tempfile

from app.core.logging import get_logger
from app.core.config import settings
from app.models.analysis import Analysis
from app.schemas.analysis import AnalysisResult, AnalysisConfig
from .ast_analyzer import ASTAnalyzer
from .security_scanner import SecurityScanner
from .performance_analyzer import PerformanceAnalyzer
from .complexity_analyzer import ComplexityAnalyzer
from .duplication_detector import DuplicationDetector
from .documentation_analyzer import DocumentationAnalyzer
from .test_analyzer import TestAnalyzer
from .dependency_analyzer import DependencyAnalyzer

logger = get_logger(__name__)


class AnalysisOrchestrator:
    """
    Orchestrates various code analysis services to provide comprehensive analysis.
    """

    def __init__(self):
        self.analyzers = {
            'ast': ASTAnalyzer(),
            'security': SecurityScanner(),
            'performance': PerformanceAnalyzer(),
            'complexity': ComplexityAnalyzer(),
            'duplication': DuplicationDetector(),
            'documentation': DocumentationAnalyzer(),
            'test': TestAnalyzer(),
            'dependency': DependencyAnalyzer()
        }

    async def run_analysis(
        self,
        project_path: str,
        config: AnalysisConfig,
        analysis_id: str
    ) -> AnalysisResult:
        """
        Run comprehensive code analysis on a project.
        """
        logger.info(f"Starting analysis {analysis_id} for project: {project_path}")

        # Create temporary directory if needed
        temp_dir = None
        if not os.path.exists(project_path):
            # Assume it's a git URL or archive
            temp_dir = await self._prepare_project(project_path)
            project_path = temp_dir

        try:
            # Run analyzers concurrently
            results = await self._run_analyzers_concurrently(project_path, config)

            # Aggregate results
            final_result = self._aggregate_results(results, config)

            logger.info(f"Analysis {analysis_id} completed successfully")
            return final_result

        finally:
            # Cleanup temporary directory
            if temp_dir and os.path.exists(temp_dir):
                await self._cleanup_temp_dir(temp_dir)

    async def _prepare_project(self, source: str) -> str:
        """
        Prepare project for analysis (clone repo, extract archive, etc.).
        """
        temp_dir = tempfile.mkdtemp(prefix="cqia_analysis_")

        # For now, assume it's a local path
        # In production, this would handle git URLs, archives, etc.
        if os.path.exists(source):
            # Copy to temp directory
            import shutil
            shutil.copytree(source, temp_dir, dirs_exist_ok=True)

        return temp_dir

    async def _run_analyzers_concurrently(
        self,
        project_path: str,
        config: AnalysisConfig
    ) -> Dict[str, Any]:
        """
        Run all enabled analyzers concurrently.
        """
        enabled_analyzers = self._get_enabled_analyzers(config)

        # Create tasks for concurrent execution
        tasks = []
        for analyzer_name, analyzer in enabled_analyzers.items():
            task = asyncio.create_task(
                self._run_analyzer_safe(analyzer_name, analyzer, project_path, config)
            )
            tasks.append(task)

        # Wait for all analyzers to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        final_results = {}
        for i, (analyzer_name, _) in enumerate(enabled_analyzers.items()):
            result = results[i]
            if isinstance(result, Exception):
                logger.error(f"Analyzer {analyzer_name} failed: {result}")
                final_results[analyzer_name] = {
                    'success': False,
                    'error': str(result),
                    'issues': [],
                    'metrics': {}
                }
            else:
                final_results[analyzer_name] = result

        return final_results

    def _get_enabled_analyzers(self, config: AnalysisConfig) -> Dict[str, Any]:
        """
        Get analyzers that are enabled in the configuration.
        """
        enabled = {}
        for name, analyzer in self.analyzers.items():
            if getattr(config, f'enable_{name}_analysis', True):
                enabled[name] = analyzer
        return enabled

    async def _run_analyzer_safe(
        self,
        name: str,
        analyzer: Any,
        project_path: str,
        config: AnalysisConfig
    ) -> Dict[str, Any]:
        """
        Run an analyzer with error handling.
        """
        try:
            logger.debug(f"Running analyzer: {name}")
            result = await analyzer.analyze(project_path, config)
            logger.debug(f"Analyzer {name} completed successfully")
            return result
        except Exception as e:
            logger.error(f"Analyzer {name} failed: {e}")
            raise

    def _aggregate_results(self, results: Dict[str, Any], config: AnalysisConfig) -> AnalysisResult:
        """
        Aggregate results from all analyzers into a final analysis result.
        """
        all_issues = []
        all_metrics = {}
        summary = {
            'total_files': 0,
            'total_lines': 0,
            'languages': set(),
            'severity_counts': {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0}
        }

        for analyzer_name, result in results.items():
            if result.get('success', False):
                # Aggregate issues
                issues = result.get('issues', [])
                all_issues.extend(issues)

                # Count severity
                for issue in issues:
                    severity = issue.get('severity', 'info')
                    summary['severity_counts'][severity] += 1

                # Aggregate metrics
                metrics = result.get('metrics', {})
                all_metrics.update(metrics)

                # Update summary
                summary['total_files'] += result.get('files_analyzed', 0)
                summary['total_lines'] += result.get('lines_analyzed', 0)
                summary['languages'].update(result.get('languages', []))

        # Convert languages set to list
        summary['languages'] = list(summary['languages'])

        # Calculate overall score
        overall_score = self._calculate_overall_score(summary['severity_counts'])

        return AnalysisResult(
            summary=summary,
            issues=all_issues,
            metrics=all_metrics,
            overall_score=overall_score,
            recommendations=self._generate_recommendations(summary, all_issues)
        )

    def _calculate_overall_score(self, severity_counts: Dict[str, int]) -> float:
        """
        Calculate overall code quality score based on issue severity.
        """
        total_issues = sum(severity_counts.values())
        if total_issues == 0:
            return 100.0

        # Weighted scoring
        weights = {'critical': 10, 'high': 5, 'medium': 2, 'low': 1, 'info': 0.5}
        weighted_sum = sum(severity_counts[sev] * weights.get(sev, 0) for sev in severity_counts)

        # Base score of 100, reduce based on weighted issues
        score = max(0, 100 - (weighted_sum / max(total_issues, 1)) * 10)
        return round(score, 1)

    def _generate_recommendations(self, summary: Dict[str, Any], issues: List[Dict[str, Any]]) -> List[str]:
        """
        Generate recommendations based on analysis results.
        """
        recommendations = []

        severity_counts = summary['severity_counts']

        if severity_counts['critical'] > 0:
            recommendations.append("Address critical security issues immediately")
        if severity_counts['high'] > 0:
            recommendations.append("Fix high-priority issues to improve code quality")
        if severity_counts['medium'] > 10:
            recommendations.append("Consider refactoring to reduce technical debt")

        # Language-specific recommendations
        languages = summary['languages']
        if 'python' in languages:
            recommendations.append("Ensure Python code follows PEP 8 standards")
        if 'javascript' in languages:
            recommendations.append("Consider using ESLint and Prettier for JavaScript code")

        # General recommendations
        if summary['total_files'] > 100:
            recommendations.append("Consider breaking large codebase into smaller modules")
        if not any(issue.get('type') == 'test' for issue in issues):
            recommendations.append("Add comprehensive unit and integration tests")

        return recommendations[:5]  # Limit to top 5 recommendations

    async def _cleanup_temp_dir(self, temp_dir: str):
        """
        Clean up temporary directory.
        """
        try:
            import shutil
            shutil.rmtree(temp_dir)
            logger.debug(f"Cleaned up temporary directory: {temp_dir}")
        except Exception as e:
            logger.error(f"Failed to cleanup temp directory {temp_dir}: {e}")

    async def get_analysis_progress(self, analysis_id: str) -> Dict[str, Any]:
        """
        Get current progress of an analysis.
        """
        # In a real implementation, this would track progress in a database/cache
        return {
            'analysis_id': analysis_id,
            'status': 'running',
            'progress': 75,
            'current_step': 'Running security analysis',
            'estimated_time_remaining': 30
        }
