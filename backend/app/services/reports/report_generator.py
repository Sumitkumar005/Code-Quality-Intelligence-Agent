"""
Report generator service for creating analysis reports.
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import os

from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class ReportGenerator:
    """
    Service for generating comprehensive code quality reports.
    """

    def __init__(self):
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict[str, str]:
        """
        Load report templates.
        """
        return {
            'summary': self._get_summary_template(),
            'detailed': self._get_detailed_template(),
            'executive': self._get_executive_template()
        }

    async def generate_report(
        self,
        analysis_results: Dict[str, Any],
        report_type: str = "detailed",
        format_type: str = "json"
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive report from analysis results.
        """
        try:
            logger.info(f"Generating {report_type} report in {format_type} format")

            # Aggregate analysis data
            aggregated_data = self._aggregate_analysis_data(analysis_results)

            # Generate report content
            report_content = self._generate_report_content(aggregated_data, report_type)

            # Format report
            if format_type == "json":
                formatted_report = self._format_json_report(report_content)
            elif format_type == "html":
                formatted_report = self._format_html_report(report_content)
            else:
                formatted_report = report_content

            # Calculate overall scores
            overall_scores = self._calculate_overall_scores(aggregated_data)

            report = {
                'success': True,
                'report_type': report_type,
                'format_type': format_type,
                'generated_at': datetime.utcnow().isoformat(),
                'overall_scores': overall_scores,
                'content': formatted_report,
                'metadata': {
                    'analysis_types': list(analysis_results.keys()),
                    'total_issues': sum(len(result.get('issues', [])) for result in analysis_results.values()),
                    'files_analyzed': aggregated_data.get('total_files', 0)
                }
            }

            return report

        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'report_type': report_type,
                'format_type': format_type
            }

    def _aggregate_analysis_data(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aggregate data from multiple analysis types.
        """
        aggregated = {
            'total_files': 0,
            'total_lines': 0,
            'languages': set(),
            'all_issues': [],
            'metrics': {},
            'analysis_types': list(analysis_results.keys())
        }

        for analysis_type, result in analysis_results.items():
            if not result.get('success', False):
                continue

            # Aggregate basic metrics
            aggregated['total_files'] = max(aggregated['total_files'], result.get('files_analyzed', 0))
            aggregated['total_lines'] += result.get('lines_analyzed', 0)

            # Aggregate languages
            languages = result.get('languages', [])
            aggregated['languages'].update(languages)

            # Aggregate issues
            issues = result.get('issues', [])
            for issue in issues:
                issue['analysis_type'] = analysis_type
                aggregated['all_issues'].append(issue)

            # Aggregate metrics
            metrics = result.get('metrics', {})
            aggregated['metrics'][analysis_type] = metrics

        aggregated['languages'] = list(aggregated['languages'])
        return aggregated

    def _generate_report_content(self, data: Dict[str, Any], report_type: str) -> Dict[str, Any]:
        """
        Generate report content based on type.
        """
        if report_type == "summary":
            return self._generate_summary_report(data)
        elif report_type == "detailed":
            return self._generate_detailed_report(data)
        elif report_type == "executive":
            return self._generate_executive_report(data)
        else:
            return self._generate_detailed_report(data)

    def _generate_summary_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a summary report.
        """
        issues = data['all_issues']

        # Group issues by severity
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for issue in issues:
            severity = issue.get('severity', 'low')
            severity_counts[severity] += 1

        # Get top issues
        top_issues = sorted(issues, key=lambda x: self._get_severity_weight(x.get('severity', 'low')), reverse=True)[:10]

        return {
            'summary': {
                'total_files': data['total_files'],
                'total_lines': data['total_lines'],
                'total_issues': len(issues),
                'languages': data['languages'],
                'severity_breakdown': severity_counts
            },
            'top_issues': top_issues,
            'metrics_overview': data['metrics']
        }

    def _generate_detailed_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a detailed report.
        """
        summary = self._generate_summary_report(data)

        # Group issues by file
        issues_by_file = {}
        for issue in data['all_issues']:
            file_path = issue.get('file_path', 'unknown')
            if file_path not in issues_by_file:
                issues_by_file[file_path] = []
            issues_by_file[file_path].append(issue)

        # Group issues by type
        issues_by_type = {}
        for issue in data['all_issues']:
            issue_type = issue.get('type', 'unknown')
            if issue_type not in issues_by_type:
                issues_by_type[issue_type] = []
            issues_by_type[issue_type].append(issue)

        return {
            **summary,
            'issues_by_file': issues_by_file,
            'issues_by_type': issues_by_type,
            'detailed_metrics': data['metrics'],
            'analysis_types': data['analysis_types']
        }

    def _generate_executive_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate an executive summary report.
        """
        summary = self._generate_summary_report(data)

        # Calculate risk levels
        risk_level = self._calculate_risk_level(data['all_issues'])

        # Key recommendations
        recommendations = self._generate_recommendations(data)

        return {
            'executive_summary': {
                'overall_health': self._get_overall_health_score(data),
                'risk_level': risk_level,
                'key_findings': self._get_key_findings(data),
                'recommendations': recommendations
            },
            **summary
        }

    def _calculate_overall_scores(self, data: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate overall quality scores.
        """
        issues = data['all_issues']

        if not issues:
            return {'overall_score': 100.0, 'quality_score': 100.0}

        # Weight issues by severity
        total_weight = 0
        for issue in issues:
            severity = issue.get('severity', 'low')
            weight = self._get_severity_weight(severity)
            total_weight += weight

        # Calculate scores (higher is better)
        max_possible_weight = len(issues) * self._get_severity_weight('critical')
        overall_score = max(0, 100 - (total_weight / max(max_possible_weight, 1)) * 100)

        return {
            'overall_score': round(overall_score, 1),
            'quality_score': round(overall_score, 1),
            'issues_count': len(issues)
        }

    def _get_severity_weight(self, severity: str) -> int:
        """
        Get weight for severity level.
        """
        weights = {'critical': 10, 'high': 7, 'medium': 4, 'low': 1}
        return weights.get(severity, 1)

    def _calculate_risk_level(self, issues: List[Dict[str, Any]]) -> str:
        """
        Calculate overall risk level.
        """
        if not issues:
            return 'low'

        critical_count = sum(1 for issue in issues if issue.get('severity') == 'critical')
        high_count = sum(1 for issue in issues if issue.get('severity') == 'high')

        if critical_count > 0 or high_count > 5:
            return 'high'
        elif high_count > 0 or len(issues) > 20:
            return 'medium'
        else:
            return 'low'

    def _get_overall_health_score(self, data: Dict[str, Any]) -> float:
        """
        Calculate overall health score.
        """
        scores = self._calculate_overall_scores(data)
        return scores['overall_score']

    def _get_key_findings(self, data: Dict[str, Any]) -> List[str]:
        """
        Extract key findings from the analysis.
        """
        findings = []

        issues = data['all_issues']
        if not issues:
            return ['No issues found - code appears to be in good condition']

        # Most common issue types
        issue_types = {}
        for issue in issues:
            issue_type = issue.get('type', 'unknown')
            issue_types[issue_type] = issue_types.get(issue_type, 0) + 1

        top_types = sorted(issue_types.items(), key=lambda x: x[1], reverse=True)[:3]
        for issue_type, count in top_types:
            findings.append(f"Found {count} {issue_type.replace('_', ' ')} issues")

        return findings

    def _generate_recommendations(self, data: Dict[str, Any]) -> List[str]:
        """
        Generate recommendations based on analysis.
        """
        recommendations = []

        issues = data['all_issues']
        if not issues:
            return ['Continue maintaining high code quality standards']

        # Check for specific patterns
        security_issues = [i for i in issues if 'security' in i.get('type', '')]
        if security_issues:
            recommendations.append('Address security vulnerabilities immediately')

        complexity_issues = [i for i in issues if 'complexity' in i.get('type', '')]
        if complexity_issues:
            recommendations.append('Refactor complex functions to improve maintainability')

        test_issues = [i for i in issues if 'test' in i.get('type', '')]
        if test_issues:
            recommendations.append('Improve test coverage and quality')

        if len(issues) > 50:
            recommendations.append('Consider a comprehensive code refactoring effort')

        return recommendations

    def _format_json_report(self, content: Dict[str, Any]) -> str:
        """
        Format report as JSON string.
        """
        return json.dumps(content, indent=2, default=str)

    def _format_html_report(self, content: Dict[str, Any]) -> str:
        """
        Format report as HTML (simplified).
        """
        html = f"""
        <html>
        <head><title>Code Quality Report</title></head>
        <body>
        <h1>Code Quality Analysis Report</h1>
        <p>Generated at: {datetime.utcnow().isoformat()}</p>

        <h2>Summary</h2>
        <ul>
        <li>Total Files: {content.get('summary', {}).get('total_files', 0)}</li>
        <li>Total Issues: {content.get('summary', {}).get('total_issues', 0)}</li>
        <li>Languages: {', '.join(content.get('summary', {}).get('languages', []))}</li>
        </ul>

        <h2>Issues by Severity</h2>
        <ul>
        """

        severity_breakdown = content.get('summary', {}).get('severity_breakdown', {})
        for severity, count in severity_breakdown.items():
            html += f"<li>{severity.title()}: {count}</li>"

        html += """
        </ul>
        </body>
        </html>
        """

        return html

    def _get_summary_template(self) -> str:
        """Get summary report template."""
        return "Summary template"

    def _get_detailed_template(self) -> str:
        """Get detailed report template."""
        return "Detailed template"

    def _get_executive_template(self) -> str:
        """Get executive report template."""
        return "Executive template"
