"""
Background Report Generation Tasks

This module contains Celery tasks for generating various types of reports
in the background, including PDF reports, HTML reports, and dashboard data.
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
from ..models.analysis import Analysis
from ..models.project import Project
from ..models.report import Report
from ..services.reports.report_generator import ReportGenerator
from ..services.reports.pdf_generator import PDFGenerator
from ..services.reports.html_generator import HTMLGenerator
from ..services.reports.dashboard_data import DashboardDataService
from ..services.storage.file_storage import FileStorageService

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def generate_comprehensive_report(
    self,
    report_id: str,
    project_id: str,
    analysis_ids: List[str],
    report_config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate a comprehensive analysis report.

    Args:
        report_id: Report identifier
        project_id: Project identifier
        analysis_ids: List of analysis session IDs to include
        report_config: Report generation configuration

    Returns:
        Dictionary containing report generation results
    """
    logger.info(f"Starting comprehensive report generation for report {report_id}")

    try:
        db = SessionLocal()
        report_generator = ReportGenerator()
        file_storage = FileStorageService()

        try:
            # Get project information
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                raise ValueError(f"Project {project_id} not found")

            # Get analysis data
            analyses = db.query(Analysis).filter(
                Analysis.id.in_(analysis_ids)
            ).all()

            if not analyses:
                raise ValueError(f"No analyses found for IDs: {analysis_ids}")

            # Generate report data
            report_data = asyncio.run(report_generator.generate_comprehensive_report(
                project=project,
                analyses=analyses,
                config=report_config
            ))

            # Generate output file based on format
            output_format = report_config.get('output_format', 'pdf')
            file_path = f"reports/{report_id}/comprehensive_report.{output_format}"

            if output_format == 'pdf':
                pdf_generator = PDFGenerator()
                file_content = asyncio.run(pdf_generator.generate_pdf(report_data))
            elif output_format == 'html':
                html_generator = HTMLGenerator()
                file_content = asyncio.run(html_generator.generate_html(report_data))
            else:
                # JSON format
                import json
                file_content = json.dumps(report_data, indent=2, default=str).encode()

            # Store the report file
            file_storage.write_file(project_id, file_path, file_content)

            # Update report record
            _update_report_status(
                report_id, "completed", file_path, report_data, db
            )

            logger.info(f"Completed comprehensive report generation for report {report_id}")
            return {
                "report_id": report_id,
                "status": "completed",
                "file_path": file_path,
                "report_data": report_data
            }

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error in comprehensive report generation {report_id}: {e}")
        _update_report_status(report_id, "failed", error=str(e), db=None)
        raise self.retry(countdown=60, exc=e)


@celery_app.task(bind=True, max_retries=3)
def generate_security_report(
    self,
    report_id: str,
    project_id: str,
    analysis_ids: List[str],
    report_config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate a security-focused report.

    Args:
        report_id: Report identifier
        project_id: Project identifier
        analysis_ids: List of analysis session IDs to include
        report_config: Report generation configuration

    Returns:
        Dictionary containing report generation results
    """
    logger.info(f"Starting security report generation for report {report_id}")

    try:
        db = SessionLocal()
        report_generator = ReportGenerator()

        try:
            # Get project and analysis data
            project = db.query(Project).filter(Project.id == project_id).first()
            analyses = db.query(Analysis).filter(
                Analysis.id.in_(analysis_ids)
            ).all()

            # Generate security-focused report
            report_data = asyncio.run(report_generator.generate_security_report(
                project=project,
                analyses=analyses,
                config=report_config
            ))

            # Generate output file
            output_format = report_config.get('output_format', 'pdf')
            file_path = f"reports/{report_id}/security_report.{output_format}"

            if output_format == 'pdf':
                pdf_generator = PDFGenerator()
                file_content = asyncio.run(pdf_generator.generate_pdf(report_data))
            elif output_format == 'html':
                html_generator = HTMLGenerator()
                file_content = asyncio.run(html_generator.generate_html(report_data))
            else:
                import json
                file_content = json.dumps(report_data, indent=2, default=str).encode()

            # Store the report file
            file_storage = FileStorageService()
            file_storage.write_file(project_id, file_path, file_content)

            # Update report record
            _update_report_status(
                report_id, "completed", file_path, report_data, db
            )

            logger.info(f"Completed security report generation for report {report_id}")
            return {
                "report_id": report_id,
                "status": "completed",
                "file_path": file_path,
                "report_data": report_data
            }

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error in security report generation {report_id}: {e}")
        _update_report_status(report_id, "failed", error=str(e), db=None)
        raise self.retry(countdown=60, exc=e)


@celery_app.task(bind=True, max_retries=3)
def generate_performance_report(
    self,
    report_id: str,
    project_id: str,
    analysis_ids: List[str],
    report_config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate a performance-focused report.

    Args:
        report_id: Report identifier
        project_id: Project identifier
        analysis_ids: List of analysis session IDs to include
        report_config: Report generation configuration

    Returns:
        Dictionary containing report generation results
    """
    logger.info(f"Starting performance report generation for report {report_id}")

    try:
        db = SessionLocal()
        report_generator = ReportGenerator()

        try:
            # Get project and analysis data
            project = db.query(Project).filter(Project.id == project_id).first()
            analyses = db.query(Analysis).filter(
                Analysis.id.in_(analysis_ids)
            ).all()

            # Generate performance-focused report
            report_data = asyncio.run(report_generator.generate_performance_report(
                project=project,
                analyses=analyses,
                config=report_config
            ))

            # Generate output file
            output_format = report_config.get('output_format', 'pdf')
            file_path = f"reports/{report_id}/performance_report.{output_format}"

            if output_format == 'pdf':
                pdf_generator = PDFGenerator()
                file_content = asyncio.run(pdf_generator.generate_pdf(report_data))
            elif output_format == 'html':
                html_generator = HTMLGenerator()
                file_content = asyncio.run(html_generator.generate_html(report_data))
            else:
                import json
                file_content = json.dumps(report_data, indent=2, default=str).encode()

            # Store the report file
            file_storage = FileStorageService()
            file_storage.write_file(project_id, file_path, file_content)

            # Update report record
            _update_report_status(
                report_id, "completed", file_path, report_data, db
            )

            logger.info(f"Completed performance report generation for report {report_id}")
            return {
                "report_id": report_id,
                "status": "completed",
                "file_path": file_path,
                "report_data": report_data
            }

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error in performance report generation {report_id}: {e}")
        _update_report_status(report_id, "failed", error=str(e), db=None)
        raise self.retry(countdown=60, exc=e)


@celery_app.task
def generate_dashboard_data(
    project_id: str,
    time_range_days: int = 30
) -> Dict[str, Any]:
    """
    Generate dashboard data for a project.

    Args:
        project_id: Project identifier
        time_range_days: Number of days to include in dashboard data

    Returns:
        Dictionary containing dashboard data
    """
    logger.info(f"Starting dashboard data generation for project {project_id}")

    try:
        db = SessionLocal()
        dashboard_service = DashboardDataService()

        try:
            # Generate dashboard data
            dashboard_data = asyncio.run(dashboard_service.generate_dashboard_data(
                project_id=project_id,
                time_range_days=time_range_days
            ))

            logger.info(f"Completed dashboard data generation for project {project_id}")
            return {
                "project_id": project_id,
                "status": "completed",
                "dashboard_data": dashboard_data,
                "generated_at": datetime.now().isoformat()
            }

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error in dashboard data generation {project_id}: {e}")
        return {
            "project_id": project_id,
            "status": "failed",
            "error": str(e)
        }


@celery_app.task
def generate_project_summary_report(
    project_id: str,
    include_trends: bool = True,
    include_recommendations: bool = True
) -> Dict[str, Any]:
    """
    Generate a project summary report.

    Args:
        project_id: Project identifier
        include_trends: Whether to include trend analysis
        include_recommendations: Whether to include AI recommendations

    Returns:
        Dictionary containing project summary data
    """
    logger.info(f"Starting project summary report generation for project {project_id}")

    try:
        db = SessionLocal()
        report_generator = ReportGenerator()

        try:
            # Get project information
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                raise ValueError(f"Project {project_id} not found")

            # Get recent analyses
            cutoff_date = datetime.now() - timedelta(days=90)
            recent_analyses = db.query(Analysis).filter(
                Analysis.project_id == project_id,
                Analysis.created_at >= cutoff_date
            ).order_by(Analysis.created_at.desc()).limit(10).all()

            # Generate summary report
            summary_data = asyncio.run(report_generator.generate_project_summary(
                project=project,
                recent_analyses=recent_analyses,
                include_trends=include_trends,
                include_recommendations=include_recommendations
            ))

            logger.info(f"Completed project summary report generation for project {project_id}")
            return {
                "project_id": project_id,
                "status": "completed",
                "summary_data": summary_data,
                "generated_at": datetime.now().isoformat()
            }

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error in project summary report generation {project_id}: {e}")
        return {
            "project_id": project_id,
            "status": "failed",
            "error": str(e)
        }


@celery_app.task
def export_analysis_data(
    analysis_ids: List[str],
    export_format: str = "json",
    include_raw_data: bool = False
) -> Dict[str, Any]:
    """
    Export analysis data in various formats.

    Args:
        analysis_ids: List of analysis session IDs to export
        export_format: Export format (json, csv, xml)
        include_raw_data: Whether to include raw analysis data

    Returns:
        Dictionary containing export results
    """
    logger.info(f"Starting analysis data export for {len(analysis_ids)} analyses")

    try:
        db = SessionLocal()

        try:
            # Get analysis data
            analyses = db.query(Analysis).filter(
                Analysis.id.in_(analysis_ids)
            ).all()

            if not analyses:
                raise ValueError(f"No analyses found for IDs: {analysis_ids}")

            # Export data based on format
            if export_format == "json":
                export_data = _export_as_json(analyses, include_raw_data)
            elif export_format == "csv":
                export_data = _export_as_csv(analyses, include_raw_data)
            elif export_format == "xml":
                export_data = _export_as_xml(analyses, include_raw_data)
            else:
                raise ValueError(f"Unsupported export format: {export_format}")

            logger.info(f"Completed analysis data export for {len(analysis_ids)} analyses")
            return {
                "analysis_ids": analysis_ids,
                "status": "completed",
                "export_format": export_format,
                "export_data": export_data,
                "exported_at": datetime.now().isoformat()
            }

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error in analysis data export: {e}")
        return {
            "analysis_ids": analysis_ids,
            "status": "failed",
            "error": str(e)
        }


@celery_app.task
def cleanup_old_reports(days_old: int = 90) -> Dict[str, Any]:
    """
    Clean up old report files and records.

    Args:
        days_old: Number of days old reports to clean up

    Returns:
        Dictionary containing cleanup statistics
    """
    logger.info(f"Starting cleanup task for reports older than {days_old} days")

    try:
        db = SessionLocal()
        file_storage = FileStorageService()

        cutoff_date = datetime.now() - timedelta(days=days_old)

        try:
            # Get old reports
            old_reports = db.query(Report).filter(
                Report.created_at < cutoff_date
            ).all()

            deleted_count = 0
            for report in old_reports:
                try:
                    # Delete report files
                    if report.file_path:
                        try:
                            file_storage.delete_file(
                                str(report.project_id), report.file_path
                            )
                        except Exception as e:
                            logger.warning(f"Could not delete file {report.file_path}: {e}")

                    # Delete the report record
                    db.delete(report)
                    deleted_count += 1

                except Exception as e:
                    logger.error(f"Error deleting report {report.id}: {e}")
                    continue

            db.commit()

            logger.info(f"Completed report cleanup task. Deleted {deleted_count} old reports")
            return {
                "status": "completed",
                "deleted_reports": deleted_count,
                "cutoff_date": cutoff_date.isoformat()
            }

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error in report cleanup task: {e}")
        return {
            "status": "failed",
            "error": str(e)
        }


# Helper functions

def _update_report_status(
    report_id: str,
    status: str,
    file_path: Optional[str] = None,
    report_data: Optional[Dict] = None,
    db: Optional[Session] = None
) -> None:
    """Update report status in database."""
    if db is None:
        db = SessionLocal()

    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        if report:
            report.status = status
            report.updated_at = datetime.now()
            if file_path:
                report.file_path = file_path
            if report_data:
                report.report_data = report_data
            db.commit()
    finally:
        if db:
            db.close()


def _export_as_json(analyses: List[Analysis], include_raw_data: bool) -> str:
    """Export analyses as JSON."""
    import json

    export_data = []
    for analysis in analyses:
        data = {
            "id": str(analysis.id),
            "project_id": str(analysis.project_id),
            "status": analysis.status,
            "analysis_type": analysis.analysis_type,
            "created_at": analysis.created_at.isoformat(),
            "completed_at": analysis.completed_at.isoformat() if analysis.completed_at else None,
        }

        if include_raw_data:
            # Include raw analysis data if requested
            data["config"] = analysis.config
            data["metadata"] = analysis.metadata

        export_data.append(data)

    return json.dumps(export_data, indent=2, default=str)


def _export_as_csv(analyses: List[Analysis], include_raw_data: bool) -> str:
    """Export analyses as CSV."""
    import csv
    import io

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        "id", "project_id", "status", "analysis_type",
        "created_at", "completed_at"
    ])

    writer.writeheader()
    for analysis in analyses:
        writer.writerow({
            "id": str(analysis.id),
            "project_id": str(analysis.project_id),
            "status": analysis.status,
            "analysis_type": analysis.analysis_type,
            "created_at": analysis.created_at.isoformat(),
            "completed_at": analysis.completed_at.isoformat() if analysis.completed_at else None,
        })

    return output.getvalue()


def _export_as_xml(analyses: List[Analysis], include_raw_data: bool) -> str:
    """Export analyses as XML."""
    import xml.etree.ElementTree as ET
    from xml.dom import minidom

    root = ET.Element("analyses")

    for analysis in analyses:
        analysis_elem = ET.SubElement(root, "analysis")

        ET.SubElement(analysis_elem, "id").text = str(analysis.id)
        ET.SubElement(analysis_elem, "project_id").text = str(analysis.project_id)
        ET.SubElement(analysis_elem, "status").text = analysis.status
        ET.SubElement(analysis_elem, "analysis_type").text = analysis.analysis_type
        ET.SubElement(analysis_elem, "created_at").text = analysis.created_at.isoformat()
        if analysis.completed_at:
            ET.SubElement(analysis_elem, "completed_at").text = analysis.completed_at.isoformat()

    # Pretty print XML
    rough_string = ET.tostring(root, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")
