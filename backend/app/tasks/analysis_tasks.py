"""
Background Analysis Tasks

This module contains Celery tasks for running code analysis in the background.
These tasks handle the heavy lifting of code analysis, security scanning,
performance analysis, and other time-intensive operations.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path

from celery import Celery
from sqlalchemy.orm import Session

from ..core.celery_app import celery_app
from ..core.database import SessionLocal
from ..models.analysis import Analysis, AnalysisStatus
from ..models.project import Project
from ..models.issue import Issue
from ..models.analysis_result import AnalysisResult
from ..services.analysis.orchestrator import AnalysisOrchestrator
from ..services.analysis.ast_analyzer import ASTAnalyzer
from ..services.analysis.security_scanner import SecurityScanner
from ..services.analysis.performance_analyzer import PerformanceAnalyzer
from ..services.analysis.complexity_analyzer import ComplexityAnalyzer
from ..services.analysis.duplication_detector import DuplicationDetector
from ..services.analysis.documentation_analyzer import DocumentationAnalyzer
from ..services.analysis.test_analyzer import TestAnalyzer
from ..services.analysis.dependency_analyzer import DependencyAnalyzer
from ..services.storage.file_storage import FileStorageService
from ..services.git.git_service import GitService

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def run_full_analysis(
    self,
    analysis_id: str,
    project_id: str,
    file_paths: List[str],
    analysis_config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Run a complete code analysis in the background.

    Args:
        analysis_id: Analysis session identifier
        project_id: Project identifier
        file_paths: List of files to analyze
        analysis_config: Analysis configuration options

    Returns:
        Dictionary containing analysis results
    """
    logger.info(f"Starting full analysis task for analysis {analysis_id}")

    try:
        # Update analysis status to running
        _update_analysis_status(analysis_id, AnalysisStatus.RUNNING)

        # Initialize services
        orchestrator = AnalysisOrchestrator()
        file_storage = FileStorageService()
        git_service = GitService()

        # Get project information
        db = SessionLocal()
        try:
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                raise ValueError(f"Project {project_id} not found")

            # Get file contents
            files_content = {}
            for file_path in file_paths:
                try:
                    content = file_storage.read_file(project_id, file_path)
                    files_content[file_path] = content
                except Exception as e:
                    logger.error(f"Error reading file {file_path}: {e}")
                    continue

            if not files_content:
                raise ValueError("No files could be read for analysis")

            # Run analysis
            analysis_results = asyncio.run(orchestrator.analyze_files(
                files_content=files_content,
                language=analysis_config.get('language', 'python'),
                analysis_types=analysis_config.get('analysis_types', [
                    'ast', 'security', 'performance', 'complexity',
                    'duplication', 'documentation', 'test', 'dependency'
                ])
            ))

            # Store results
            _store_analysis_results(analysis_id, analysis_results, db)

            # Update analysis status to completed
            _update_analysis_status(analysis_id, AnalysisStatus.COMPLETED)

            logger.info(f"Completed full analysis task for analysis {analysis_id}")
            return {
                "analysis_id": analysis_id,
                "status": "completed",
                "results": analysis_results,
                "files_analyzed": len(files_content)
            }

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error in full analysis task {analysis_id}: {e}")
        _update_analysis_status(analysis_id, AnalysisStatus.FAILED)
        raise self.retry(countdown=60, exc=e)


@celery_app.task(bind=True, max_retries=3)
def run_security_scan(
    self,
    analysis_id: str,
    project_id: str,
    file_paths: List[str],
    scan_config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Run security vulnerability scan.

    Args:
        analysis_id: Analysis session identifier
        project_id: Project identifier
        file_paths: List of files to scan
        scan_config: Security scan configuration

    Returns:
        Dictionary containing security scan results
    """
    logger.info(f"Starting security scan task for analysis {analysis_id}")

    try:
        _update_analysis_status(analysis_id, AnalysisStatus.RUNNING)

        db = SessionLocal()
        file_storage = FileStorageService()

        try:
            # Get file contents
            files_content = {}
            for file_path in file_paths:
                try:
                    content = file_storage.read_file(project_id, file_path)
                    files_content[file_path] = content
                except Exception as e:
                    logger.error(f"Error reading file {file_path}: {e}")
                    continue

            # Run security analysis
            security_scanner = SecurityScanner()
            security_results = asyncio.run(security_scanner.analyze_files(
                files_content=files_content,
                language=scan_config.get('language', 'python'),
                severity_threshold=scan_config.get('severity_threshold', 'medium')
            ))

            # Store security issues
            _store_security_issues(analysis_id, security_results, db)

            _update_analysis_status(analysis_id, AnalysisStatus.COMPLETED)

            logger.info(f"Completed security scan task for analysis {analysis_id}")
            return {
                "analysis_id": analysis_id,
                "status": "completed",
                "security_issues": security_results,
                "files_scanned": len(files_content)
            }

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error in security scan task {analysis_id}: {e}")
        _update_analysis_status(analysis_id, AnalysisStatus.FAILED)
        raise self.retry(countdown=60, exc=e)


@celery_app.task(bind=True, max_retries=3)
def run_performance_analysis(
    self,
    analysis_id: str,
    project_id: str,
    file_paths: List[str],
    perf_config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Run performance analysis.

    Args:
        analysis_id: Analysis session identifier
        project_id: Project identifier
        file_paths: List of files to analyze
        perf_config: Performance analysis configuration

    Returns:
        Dictionary containing performance analysis results
    """
    logger.info(f"Starting performance analysis task for analysis {analysis_id}")

    try:
        _update_analysis_status(analysis_id, AnalysisStatus.RUNNING)

        db = SessionLocal()
        file_storage = FileStorageService()

        try:
            # Get file contents
            files_content = {}
            for file_path in file_paths:
                try:
                    content = file_storage.read_file(project_id, file_path)
                    files_content[file_path] = content
                except Exception as e:
                    logger.error(f"Error reading file {file_path}: {e}")
                    continue

            # Run performance analysis
            perf_analyzer = PerformanceAnalyzer()
            perf_results = asyncio.run(perf_analyzer.analyze_files(
                files_content=files_content,
                language=perf_config.get('language', 'python'),
                include_memory_analysis=perf_config.get('include_memory_analysis', True),
                include_cpu_analysis=perf_config.get('include_cpu_analysis', True)
            ))

            # Store performance metrics
            _store_performance_metrics(analysis_id, perf_results, db)

            _update_analysis_status(analysis_id, AnalysisStatus.COMPLETED)

            logger.info(f"Completed performance analysis task for analysis {analysis_id}")
            return {
                "analysis_id": analysis_id,
                "status": "completed",
                "performance_metrics": perf_results,
                "files_analyzed": len(files_content)
            }

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error in performance analysis task {analysis_id}: {e}")
        _update_analysis_status(analysis_id, AnalysisStatus.FAILED)
        raise self.retry(countdown=60, exc=e)


@celery_app.task(bind=True, max_retries=3)
def run_dependency_analysis(
    self,
    analysis_id: str,
    project_id: str,
    file_paths: List[str],
    dep_config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Run dependency analysis.

    Args:
        analysis_id: Analysis session identifier
        project_id: Project identifier
        file_paths: List of files to analyze
        dep_config: Dependency analysis configuration

    Returns:
        Dictionary containing dependency analysis results
    """
    logger.info(f"Starting dependency analysis task for analysis {analysis_id}")

    try:
        _update_analysis_status(analysis_id, AnalysisStatus.RUNNING)

        db = SessionLocal()
        file_storage = FileStorageService()

        try:
            # Get file contents
            files_content = {}
            for file_path in file_paths:
                try:
                    content = file_storage.read_file(project_id, file_path)
                    files_content[file_path] = content
                except Exception as e:
                    logger.error(f"Error reading file {file_path}: {e}")
                    continue

            # Run dependency analysis
            dep_analyzer = DependencyAnalyzer()
            dep_results = asyncio.run(dep_analyzer.analyze_files(
                files_content=files_content,
                language=dep_config.get('language', 'python'),
                check_vulnerabilities=dep_config.get('check_vulnerabilities', True),
                check_outdated=dep_config.get('check_outdated', True)
            ))

            # Store dependency issues
            _store_dependency_issues(analysis_id, dep_results, db)

            _update_analysis_status(analysis_id, AnalysisStatus.COMPLETED)

            logger.info(f"Completed dependency analysis task for analysis {analysis_id}")
            return {
                "analysis_id": analysis_id,
                "status": "completed",
                "dependency_issues": dep_results,
                "files_analyzed": len(files_content)
            }

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error in dependency analysis task {analysis_id}: {e}")
        _update_analysis_status(analysis_id, AnalysisStatus.FAILED)
        raise self.retry(countdown=60, exc=e)


@celery_app.task
def cleanup_old_analyses(days_old: int = 30) -> Dict[str, Any]:
    """
    Clean up old analysis records and associated data.

    Args:
        days_old: Number of days old analyses to clean up

    Returns:
        Dictionary containing cleanup statistics
    """
    logger.info(f"Starting cleanup task for analyses older than {days_old} days")

    try:
        db = SessionLocal()
        cutoff_date = datetime.now() - timedelta(days=days_old)

        try:
            # Get old analyses
            old_analyses = db.query(Analysis).filter(
                Analysis.created_at < cutoff_date
            ).all()

            deleted_count = 0
            for analysis in old_analyses:
                try:
                    # Delete associated issues
                    db.query(Issue).filter(Issue.analysis_id == analysis.id).delete()

                    # Delete associated results
                    db.query(AnalysisResult).filter(
                        AnalysisResult.analysis_id == analysis.id
                    ).delete()

                    # Delete the analysis
                    db.delete(analysis)
                    deleted_count += 1

                except Exception as e:
                    logger.error(f"Error deleting analysis {analysis.id}: {e}")
                    continue

            db.commit()

            logger.info(f"Completed cleanup task. Deleted {deleted_count} old analyses")
            return {
                "status": "completed",
                "deleted_analyses": deleted_count,
                "cutoff_date": cutoff_date.isoformat()
            }

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error in cleanup task: {e}")
        return {
            "status": "failed",
            "error": str(e)
        }


@celery_app.task
def generate_analysis_report(
    analysis_id: str,
    report_type: str = "comprehensive",
    output_format: str = "json"
) -> Dict[str, Any]:
    """
    Generate a comprehensive analysis report.

    Args:
        analysis_id: Analysis session identifier
        report_type: Type of report to generate
        output_format: Output format (json, pdf, html)

    Returns:
        Dictionary containing report generation results
    """
    logger.info(f"Starting report generation task for analysis {analysis_id}")

    try:
        db = SessionLocal()

        try:
            # Get analysis with related data
            analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
            if not analysis:
                raise ValueError(f"Analysis {analysis_id} not found")

            # Get associated issues and results
            issues = db.query(Issue).filter(Issue.analysis_id == analysis_id).all()
            results = db.query(AnalysisResult).filter(
                AnalysisResult.analysis_id == analysis_id
            ).all()

            # Generate report data
            report_data = {
                "analysis_id": analysis_id,
                "project_id": str(analysis.project_id),
                "created_at": analysis.created_at.isoformat(),
                "status": analysis.status,
                "total_issues": len(issues),
                "issues_by_severity": _group_issues_by_severity(issues),
                "issues_by_type": _group_issues_by_type(issues),
                "analysis_results": [result.to_dict() for result in results],
                "report_type": report_type,
                "generated_at": datetime.now().isoformat()
            }

            # Store report
            _store_analysis_report(analysis_id, report_data, db)

            logger.info(f"Completed report generation task for analysis {analysis_id}")
            return {
                "analysis_id": analysis_id,
                "status": "completed",
                "report_data": report_data
            }

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error in report generation task {analysis_id}: {e}")
        return {
            "analysis_id": analysis_id,
            "status": "failed",
            "error": str(e)
        }


# Helper functions

def _update_analysis_status(analysis_id: str, status: AnalysisStatus) -> None:
    """Update analysis status in database."""
    db = SessionLocal()
    try:
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if analysis:
            analysis.status = status
            analysis.updated_at = datetime.now()
            db.commit()
    finally:
        db.close()


def _store_analysis_results(
    analysis_id: str,
    results: Dict[str, Any],
    db: Session
) -> None:
    """Store analysis results in database."""
    for result_type, result_data in results.items():
        result = AnalysisResult(
            analysis_id=analysis_id,
            result_type=result_type,
            result_data=result_data,
            created_at=datetime.now()
        )
        db.add(result)
    db.commit()


def _store_security_issues(
    analysis_id: str,
    security_results: Dict[str, Any],
    db: Session
) -> None:
    """Store security issues in database."""
    for file_path, issues in security_results.items():
        for issue in issues:
            db_issue = Issue(
                analysis_id=analysis_id,
                type="security",
                severity=issue.get("severity", "medium"),
                category="security",
                title=issue.get("title", "Security Issue"),
                description=issue.get("description", ""),
                file_path=file_path,
                line_start=issue.get("line_start"),
                line_end=issue.get("line_end"),
                code_snippet=issue.get("code_snippet"),
                suggestion=issue.get("suggestion"),
                created_at=datetime.now()
            )
            db.add(db_issue)
    db.commit()


def _store_performance_metrics(
    analysis_id: str,
    perf_results: Dict[str, Any],
    db: Session
) -> None:
    """Store performance metrics in database."""
    for file_path, metrics in perf_results.items():
        for metric_name, metric_value in metrics.items():
            result = AnalysisResult(
                analysis_id=analysis_id,
                result_type="performance_metric",
                result_data={
                    "file_path": file_path,
                    "metric_name": metric_name,
                    "metric_value": metric_value
                },
                created_at=datetime.now()
            )
            db.add(result)
    db.commit()


def _store_dependency_issues(
    analysis_id: str,
    dep_results: Dict[str, Any],
    db: Session
) -> None:
    """Store dependency issues in database."""
    for file_path, issues in dep_results.items():
        for issue in issues:
            db_issue = Issue(
                analysis_id=analysis_id,
                type="dependency",
                severity=issue.get("severity", "info"),
                category="dependency",
                title=issue.get("title", "Dependency Issue"),
                description=issue.get("description", ""),
                file_path=file_path,
                line_start=issue.get("line_start"),
                line_end=issue.get("line_end"),
                code_snippet=issue.get("code_snippet"),
                suggestion=issue.get("suggestion"),
                created_at=datetime.now()
            )
            db.add(db_issue)
    db.commit()


def _group_issues_by_severity(issues: List[Issue]) -> Dict[str, int]:
    """Group issues by severity level."""
    severity_counts = {}
    for issue in issues:
        severity = issue.severity or "unknown"
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    return severity_counts


def _group_issues_by_type(issues: List[Issue]) -> Dict[str, int]:
    """Group issues by type."""
    type_counts = {}
    for issue in issues:
        issue_type = issue.type or "unknown"
        type_counts[issue_type] = type_counts.get(issue_type, 0) + 1
    return type_counts


def _store_analysis_report(
    analysis_id: str,
    report_data: Dict[str, Any],
    db: Session
) -> None:
    """Store analysis report in database."""
    result = AnalysisResult(
        analysis_id=analysis_id,
        result_type="report",
        result_data=report_data,
        created_at=datetime.now()
    )
    db.add(result)
    db.commit()
