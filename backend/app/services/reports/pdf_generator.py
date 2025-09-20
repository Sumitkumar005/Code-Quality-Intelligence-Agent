"""
PDF report generator for analysis results.
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class PDFGenerator:
    """
    Service for generating PDF reports from analysis results.
    """

    def __init__(self):
        self.title = "Code Quality Analysis Report"
        self.company_name = "Code Quality Intelligence Agent"

    async def generate_report(
        self,
        analysis_results: Dict[str, Any],
        project_info: Dict[str, Any],
        report_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a PDF report from analysis results.
        """
        try:
            logger.info("Starting PDF report generation")

            # Build report structure
            report_data = await self._build_report_data(analysis_results, project_info, report_config)

            # Generate PDF content (in production, this would use ReportLab or similar)
            pdf_content = await self._generate_pdf_content(report_data)

            # Save report metadata
            report_metadata = {
                'title': report_data['title'],
                'generated_at': datetime.utcnow().isoformat(),
                'project_name': project_info.get('name', 'Unknown Project'),
                'analysis_date': analysis_results.get('analyzed_at', datetime.utcnow().isoformat()),
                'total_issues': report_data['summary']['total_issues'],
                'overall_score': report_data['summary']['overall_score'],
                'file_count': len(report_data['files'])
            }

            return {
                'success': True,
                'report_data': report_data,
                'pdf_content': pdf_content,
                'metadata': report_metadata,
                'format': 'pdf'
            }

        except Exception as e:
            logger.error(f"PDF report generation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def _build_report_data(
        self,
        analysis_results: Dict[str, Any],
        project_info: Dict[str, Any],
        report_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Build structured report data.
        """
        try:
            # Calculate summary statistics
            summary = await self._calculate_summary(analysis_results)

            # Process file analysis results
            files = await self._process_file_results(analysis_results)

            # Build report structure
            report_data = {
                'title': report_config.get('title', self.title) if report_config else self.title,
                'company': report_config.get('company', self.company_name) if report_config else self.company_name,
                'project': {
                    'name': project_info.get('name', 'Unknown Project'),
                    'description': project_info.get('description', ''),
                    'language': project_info.get('language', 'Multiple'),
                    'repository': project_info.get('repository_url', ''),
                    'analyzed_at': analysis_results.get('analyzed_at', datetime.utcnow().isoformat())
                },
                'summary': summary,
                'files': files,
                'sections': await self._build_report_sections(analysis_results, report_config),
                'config': report_config or {}
            }

            return report_data

        except Exception as e:
            logger.error(f"Report data building failed: {e}")
            raise

    async def _calculate_summary(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate summary statistics for the report.
        """
        try:
            total_issues = 0
            severity_counts = {'high': 0, 'medium': 0, 'low': 0, 'info': 0}
            category_counts = {}

            # Process analysis results
            for file_path, file_result in analysis_results.get('files', {}).items():
                for issue_type, issues in file_result.get('issues', {}).items():
                    total_issues += len(issues)
                    category_counts[issue_type] = category_counts.get(issue_type, 0) + len(issues)

                    for issue in issues:
                        severity = issue.get('severity', 'medium')
                        if severity in severity_counts:
                            severity_counts[severity] += 1

            # Calculate overall score (0-100)
            if total_issues == 0:
                overall_score = 100
            else:
                # Simple scoring algorithm
                score_deduction = (
                    severity_counts['high'] * 10 +
                    severity_counts['medium'] * 5 +
                    severity_counts['low'] * 2 +
                    severity_counts['info'] * 1
                )
                overall_score = max(0, 100 - score_deduction)

            return {
                'total_files': len(analysis_results.get('files', {})),
                'total_issues': total_issues,
                'overall_score': overall_score,
                'severity_distribution': severity_counts,
                'category_distribution': category_counts,
                'grade': self._calculate_grade(overall_score)
            }

        except Exception as e:
            logger.error(f"Summary calculation failed: {e}")
            return {
                'total_files': 0,
                'total_issues': 0,
                'overall_score': 0,
                'severity_distribution': {},
                'category_distribution': {},
                'grade': 'Unknown'
            }

    def _calculate_grade(self, score: float) -> str:
        """
        Calculate letter grade from score.
        """
        if score >= 90:
            return 'A+'
        elif score >= 85:
            return 'A'
        elif score >= 80:
            return 'A-'
        elif score >= 75:
            return 'B+'
        elif score >= 70:
            return 'B'
        elif score >= 65:
            return 'B-'
        elif score >= 60:
            return 'C+'
        elif score >= 55:
            return 'C'
        elif score >= 50:
            return 'C-'
        elif score >= 40:
            return 'D'
        else:
            return 'F'

    async def _process_file_results(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process file analysis results for the report.
        """
        try:
            files = []

            for file_path, file_result in analysis_results.get('files', {}).items():
                file_summary = {
                    'path': file_path,
                    'language': file_result.get('language', 'unknown'),
                    'total_issues': sum(len(issues) for issues in file_result.get('issues', {}).values()),
                    'severity_counts': {'high': 0, 'medium': 0, 'low': 0, 'info': 0},
                    'issues': []
                }

                # Process issues for this file
                for issue_type, issues in file_result.get('issues', {}).items():
                    for issue in issues:
                        severity = issue.get('severity', 'medium')
                        if severity in file_summary['severity_counts']:
                            file_summary['severity_counts'][severity] += 1

                        file_summary['issues'].append({
                            'type': issue_type,
                            'severity': severity,
                            'title': issue.get('title', ''),
                            'description': issue.get('description', ''),
                            'line': issue.get('line', 0),
                            'column': issue.get('column', 0),
                            'suggestion': issue.get('suggestion', '')
                        })

                files.append(file_summary)

            # Sort files by issue count (descending)
            files.sort(key=lambda x: x['total_issues'], reverse=True)
            return files

        except Exception as e:
            logger.error(f"File results processing failed: {e}")
            return []

    async def _build_report_sections(
        self,
        analysis_results: Dict[str, Any],
        report_config: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Build report sections based on analysis results.
        """
        try:
            sections = [
                {
                    'title': 'Executive Summary',
                    'type': 'summary',
                    'content': 'This report provides a comprehensive analysis of code quality issues found in the project.'
                },
                {
                    'title': 'Analysis Overview',
                    'type': 'overview',
                    'content': 'Overview of the analysis methodology and tools used.'
                }
            ]

            # Add sections based on analysis types
            analysis_types = analysis_results.get('analysis_types', [])
            for analysis_type in analysis_types:
                sections.append({
                    'title': f'{analysis_type.title()} Analysis',
                    'type': analysis_type.lower(),
                    'content': f'Results from {analysis_type} analysis.'
                })

            # Add recommendations section
            sections.append({
                'title': 'Recommendations',
                'type': 'recommendations',
                'content': 'Suggested improvements and best practices.'
            })

            return sections

        except Exception as e:
            logger.error(f"Report sections building failed: {e}")
            return []

    async def _generate_pdf_content(self, report_data: Dict[str, Any]) -> bytes:
        """
        Generate actual PDF content.
        In production, this would use ReportLab, WeasyPrint, or similar.
        """
        try:
            # For now, return mock PDF content
            # In production, this would generate actual PDF bytes
            pdf_content = b'%PDF-1.4\n%Mock PDF Content\n'

            return pdf_content

        except Exception as e:
            logger.error(f"PDF content generation failed: {e}")
            raise

    async def generate_comparison_report(
        self,
        analysis_results1: Dict[str, Any],
        analysis_results2: Dict[str, Any],
        project_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a comparison report between two analysis results.
        """
        try:
            logger.info("Starting comparison report generation")

            # Calculate comparison metrics
            comparison_data = await self._calculate_comparison(analysis_results1, analysis_results2)

            # Build comparison report
            report_data = {
                'title': 'Code Quality Comparison Report',
                'type': 'comparison',
                'project': project_info,
                'comparison': comparison_data,
                'baseline': analysis_results1.get('metadata', {}),
                'current': analysis_results2.get('metadata', {}),
                'generated_at': datetime.utcnow().isoformat()
            }

            pdf_content = await self._generate_pdf_content(report_data)

            return {
                'success': True,
                'report_data': report_data,
                'pdf_content': pdf_content,
                'format': 'pdf'
            }

        except Exception as e:
            logger.error(f"Comparison report generation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def _calculate_comparison(
        self,
        analysis1: Dict[str, Any],
        analysis2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate comparison metrics between two analysis results.
        """
        try:
            summary1 = await self._calculate_summary(analysis1)
            summary2 = await self._calculate_summary(analysis2)

            return {
                'score_change': summary2['overall_score'] - summary1['overall_score'],
                'issues_change': summary2['total_issues'] - summary1['total_issues'],
                'files_change': summary2['total_files'] - summary1['total_files'],
                'severity_changes': {
                    severity: summary2['severity_distribution'].get(severity, 0) -
                             summary1['severity_distribution'].get(severity, 0)
                    for severity in ['high', 'medium', 'low', 'info']
                },
                'trend': 'improving' if summary2['overall_score'] > summary1['overall_score'] else 'degrading',
                'improvement_percentage': (
                    (summary2['overall_score'] - summary1['overall_score']) / max(summary1['overall_score'], 1)
                ) * 100
            }

        except Exception as e:
            logger.error(f"Comparison calculation failed: {e}")
            return {}

    async def check_health(self) -> bool:
        """
        Check if PDF generator service is healthy.
        """
        try:
            # Test basic report generation
            test_data = {
                'files': {},
                'analysis_types': ['test'],
                'metadata': {'test': True}
            }
            result = await self.generate_report(test_data, {'name': 'Test Project'})
            return result['success']
        except Exception:
            return False
