"""
HTML report generator for analysis results.
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class HTMLGenerator:
    """
    Service for generating HTML reports from analysis results.
    """

    def __init__(self):
        self.template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <style>
                {css_styles}
            </style>
        </head>
        <body>
            <div class="container">
                {content}
            </div>
        </body>
        </html>
        """

        self.css_styles = """
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .header {
                text-align: center;
                margin-bottom: 40px;
                padding-bottom: 20px;
                border-bottom: 2px solid #e0e0e0;
            }
            .header h1 {
                color: #2c3e50;
                margin-bottom: 10px;
            }
            .header .subtitle {
                color: #7f8c8d;
                font-size: 14px;
            }
            .summary-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 40px;
            }
            .summary-card {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 6px;
                border-left: 4px solid #3498db;
                text-align: center;
            }
            .summary-card.high { border-left-color: #e74c3c; }
            .summary-card.medium { border-left-color: #f39c12; }
            .summary-card.low { border-left-color: #27ae60; }
            .summary-card.info { border-left-color: #9b59b6; }
            .score-circle {
                width: 80px;
                height: 80px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 24px;
                font-weight: bold;
                margin: 0 auto 10px;
                color: white;
            }
            .score-a { background: #27ae60; }
            .score-b { background: #3498db; }
            .score-c { background: #f39c12; }
            .score-d { background: #e74c3c; }
            .score-f { background: #c0392b; }
            .files-section {
                margin-bottom: 40px;
            }
            .files-section h2 {
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
            }
            .file-item {
                background: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 15px;
                margin-bottom: 15px;
            }
            .file-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            }
            .file-name {
                font-weight: bold;
                color: #2c3e50;
            }
            .issue-count {
                background: #e74c3c;
                color: white;
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 12px;
            }
            .issue-item {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 10px;
                margin-bottom: 8px;
            }
            .issue-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 5px;
            }
            .issue-type {
                font-size: 12px;
                padding: 2px 6px;
                border-radius: 3px;
                color: white;
            }
            .severity-high { background: #e74c3c; }
            .severity-medium { background: #f39c12; }
            .severity-low { background: #27ae60; }
            .severity-info { background: #9b59b6; }
            .issue-description {
                font-size: 14px;
                color: #555;
            }
            .recommendations {
                background: #ecf0f1;
                padding: 20px;
                border-radius: 6px;
                margin-top: 30px;
            }
            .recommendations h2 {
                color: #2c3e50;
                margin-bottom: 15px;
            }
            .recommendations ul {
                list-style-type: none;
                padding: 0;
            }
            .recommendations li {
                background: white;
                padding: 10px;
                margin-bottom: 8px;
                border-radius: 4px;
                border-left: 3px solid #3498db;
            }
            .footer {
                text-align: center;
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #e0e0e0;
                color: #7f8c8d;
                font-size: 12px;
            }
        """

    async def generate_report(
        self,
        analysis_results: Dict[str, Any],
        project_info: Dict[str, Any],
        report_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate an HTML report from analysis results.
        """
        try:
            logger.info("Starting HTML report generation")

            # Build report data
            report_data = await self._build_report_data(analysis_results, project_info, report_config)

            # Generate HTML content
            html_content = await self._generate_html_content(report_data)

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
                'html_content': html_content,
                'metadata': report_metadata,
                'format': 'html'
            }

        except Exception as e:
            logger.error(f"HTML report generation failed: {e}")
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
                'title': report_config.get('title', 'Code Quality Analysis Report') if report_config else 'Code Quality Analysis Report',
                'project': {
                    'name': project_info.get('name', 'Unknown Project'),
                    'description': project_info.get('description', ''),
                    'language': project_info.get('language', 'Multiple'),
                    'repository': project_info.get('repository_url', ''),
                    'analyzed_at': analysis_results.get('analyzed_at', datetime.utcnow().isoformat())
                },
                'summary': summary,
                'files': files,
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

    async def _generate_html_content(self, report_data: Dict[str, Any]) -> str:
        """
        Generate HTML content for the report.
        """
        try:
            # Generate summary cards
            summary_html = await self._generate_summary_html(report_data['summary'])

            # Generate files section
            files_html = await self._generate_files_html(report_data['files'])

            # Generate recommendations
            recommendations_html = await self._generate_recommendations_html(report_data)

            # Combine all sections
            content = f"""
            <div class="header">
                <h1>{report_data['title']}</h1>
                <div class="subtitle">
                    Project: {report_data['project']['name']} |
                    Generated: {datetime.fromisoformat(report_data['project']['analyzed_at']).strftime('%Y-%m-%d %H:%M:%S')}
                </div>
            </div>

            {summary_html}

            {files_html}

            {recommendations_html}

            <div class="footer">
                <p>Report generated by Code Quality Intelligence Agent</p>
                <p>Generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            </div>
            """

            # Apply template
            html_content = self.template.format(
                title=report_data['title'],
                css_styles=self.css_styles,
                content=content
            )

            return html_content

        except Exception as e:
            logger.error(f"HTML content generation failed: {e}")
            raise

    async def _generate_summary_html(self, summary: Dict[str, Any]) -> str:
        """
        Generate HTML for the summary section.
        """
        try:
            score_class = f"score-{summary['grade'].lower()}"
            if summary['grade'].startswith('A'):
                score_class = 'score-a'
            elif summary['grade'].startswith('B'):
                score_class = 'score-b'
            elif summary['grade'].startswith('C'):
                score_class = 'score-c'
            elif summary['grade'].startswith('D'):
                score_class = 'score-d'
            else:
                score_class = 'score-f'

            summary_html = f"""
            <div class="summary-grid">
                <div class="summary-card">
                    <div class="score-circle {score_class}">
                        {summary['overall_score']:.0f}
                    </div>
                    <h3>Overall Score</h3>
                    <p>Grade: {summary['grade']}</p>
                </div>

                <div class="summary-card">
                    <h3>Files Analyzed</h3>
                    <p class="metric">{summary['total_files']}</p>
                </div>

                <div class="summary-card">
                    <h3>Total Issues</h3>
                    <p class="metric">{summary['total_issues']}</p>
                </div>

                <div class="summary-card high">
                    <h3>High Severity</h3>
                    <p class="metric">{summary['severity_distribution'].get('high', 0)}</p>
                </div>

                <div class="summary-card medium">
                    <h3>Medium Severity</h3>
                    <p class="metric">{summary['severity_distribution'].get('medium', 0)}</p>
                </div>

                <div class="summary-card low">
                    <h3>Low Severity</h3>
                    <p class="metric">{summary['severity_distribution'].get('low', 0)}</p>
                </div>
            </div>
            """

            return summary_html

        except Exception as e:
            logger.error(f"Summary HTML generation failed: {e}")
            return ""

    async def _generate_files_html(self, files: List[Dict[str, Any]]) -> str:
        """
        Generate HTML for the files section.
        """
        try:
            files_html = '<div class="files-section"><h2>Files Analysis</h2>'

            for file_info in files:
                files_html += f'''
                <div class="file-item">
                    <div class="file-header">
                        <span class="file-name">{file_info['path']}</span>
                        <span class="issue-count">{file_info['total_issues']} issues</span>
                    </div>
                    <div class="file-stats">
                        Language: {file_info['language']} |
                        High: {file_info['severity_counts']['high']} |
                        Medium: {file_info['severity_counts']['medium']} |
                        Low: {file_info['severity_counts']['low']}
                    </div>
                '''

                if file_info['issues']:
                    files_html += '<div class="issues-list">'
                    for issue in file_info['issues'][:10]:  # Limit to first 10 issues
                        files_html += f'''
                        <div class="issue-item">
                            <div class="issue-header">
                                <span class="issue-type severity-{issue['severity']}">{issue['severity'].upper()}</span>
                                <span class="issue-title">{issue['title']}</span>
                            </div>
                            <div class="issue-description">{issue['description']}</div>
                        </div>
                        '''
                    files_html += '</div>'

                files_html += '</div>'

            files_html += '</div>'
            return files_html

        except Exception as e:
            logger.error(f"Files HTML generation failed: {e}")
            return ""

    async def _generate_recommendations_html(self, report_data: Dict[str, Any]) -> str:
        """
        Generate HTML for the recommendations section.
        """
        try:
            recommendations_html = '''
            <div class="recommendations">
                <h2>Recommendations</h2>
                <ul>
                    <li>Focus on fixing high-severity issues first</li>
                    <li>Review files with the most issues</li>
                    <li>Consider refactoring complex code sections</li>
                    <li>Improve code documentation where needed</li>
                    <li>Run tests to ensure code quality</li>
                </ul>
            </div>
            '''

            return recommendations_html

        except Exception as e:
            logger.error(f"Recommendations HTML generation failed: {e}")
            return ""

    async def check_health(self) -> bool:
        """
        Check if HTML generator service is healthy.
        """
        try:
            # Test basic HTML generation
            test_data = {
                'title': 'Test Report',
                'project': {'name': 'Test Project'},
                'summary': {
                    'total_files': 1,
                    'total_issues': 0,
                    'overall_score': 100,
                    'grade': 'A+'
                },
                'files': []
            }
            result = await self.generate_report({}, test_data)
            return result['success']
        except Exception:
            return False
