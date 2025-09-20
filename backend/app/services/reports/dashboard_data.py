"""
Dashboard data service for generating analytics and metrics for the frontend dashboard.
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class DashboardDataService:
    """
    Service for generating dashboard data and analytics.
    """

    def __init__(self):
        self.cache_ttl = 300  # 5 minutes cache
        self.cache = {}

    async def get_dashboard_data(
        self,
        organization_id: Optional[str] = None,
        project_id: Optional[str] = None,
        time_range: str = "7d"
    ) -> Dict[str, Any]:
        """
        Get comprehensive dashboard data.
        """
        try:
            cache_key = f"dashboard_{organization_id}_{project_id}_{time_range}"
            cached_data = self._get_from_cache(cache_key)

            if cached_data:
                return cached_data

            # Get overview metrics
            overview = await self._get_overview_metrics(organization_id, project_id, time_range)

            # Get quality trends
            quality_trends = await self._get_quality_trends(organization_id, project_id, time_range)

            # Get recent analyses
            recent_analyses = await self._get_recent_analyses(organization_id, project_id, 10)

            # Get top issues
            top_issues = await self._get_top_issues(organization_id, project_id, 10)

            # Get project statistics
            project_stats = await self._get_project_statistics(organization_id, project_id)

            # Get AI insights
            ai_insights = await self._get_ai_insights(organization_id, project_id)

            dashboard_data = {
                'overview': overview,
                'quality_trends': quality_trends,
                'recent_analyses': recent_analyses,
                'top_issues': top_issues,
                'project_stats': project_stats,
                'ai_insights': ai_insights,
                'generated_at': datetime.utcnow().isoformat(),
                'time_range': time_range
            }

            # Cache the result
            self._set_cache(cache_key, dashboard_data)
            return dashboard_data

        except Exception as e:
            logger.error(f"Dashboard data generation failed: {e}")
            return {
                'error': str(e),
                'generated_at': datetime.utcnow().isoformat()
            }

    async def _get_overview_metrics(
        self,
        organization_id: Optional[str] = None,
        project_id: Optional[str] = None,
        time_range: str = "7d"
    ) -> Dict[str, Any]:
        """
        Get overview metrics for the dashboard.
        """
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            if time_range == "24h":
                start_date = end_date - timedelta(hours=24)
            elif time_range == "7d":
                start_date = end_date - timedelta(days=7)
            elif time_range == "30d":
                start_date = end_date - timedelta(days=30)
            else:
                start_date = end_date - timedelta(days=7)

            # Mock data - in production, this would query the database
            return {
                'total_projects': 15,
                'total_analyses': 127,
                'total_issues': 342,
                'average_score': 78.5,
                'score_trend': '+2.3%',
                'high_severity_issues': 23,
                'medium_severity_issues': 89,
                'low_severity_issues': 156,
                'info_issues': 74,
                'projects_with_issues': 12,
                'improvement_rate': 15.2,
                'time_range': time_range,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            }

        except Exception as e:
            logger.error(f"Overview metrics generation failed: {e}")
            return {}

    async def _get_quality_trends(
        self,
        organization_id: Optional[str] = None,
        project_id: Optional[str] = None,
        time_range: str = "7d"
    ) -> Dict[str, Any]:
        """
        Get quality trends over time.
        """
        try:
            # Mock trend data - in production, this would query historical data
            days = 7 if time_range == "7d" else 30 if time_range == "30d" else 1

            trend_data = []
            base_score = 75

            for i in range(days):
                date = datetime.utcnow() - timedelta(days=days-1-i)
                score = base_score + (i * 0.5) + (-2 if i % 3 == 0 else 2)  # Mock variation
                score = max(0, min(100, score))

                trend_data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'score': round(score, 1),
                    'issues': max(0, 50 - i * 2),
                    'files_analyzed': 25 + i
                })

            return {
                'trend_data': trend_data,
                'current_score': trend_data[-1]['score'] if trend_data else 0,
                'previous_score': trend_data[0]['score'] if trend_data else 0,
                'score_change': (
                    trend_data[-1]['score'] - trend_data[0]['score']
                    if len(trend_data) > 1 else 0
                ),
                'trend_direction': 'up' if len(trend_data) > 1 and trend_data[-1]['score'] > trend_data[0]['score'] else 'down'
            }

        except Exception as e:
            logger.error(f"Quality trends generation failed: {e}")
            return {}

    async def _get_recent_analyses(
        self,
        organization_id: Optional[str] = None,
        project_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get recent analyses.
        """
        try:
            # Mock recent analyses data
            recent_analyses = []

            for i in range(min(limit, 8)):
                analysis_date = datetime.utcnow() - timedelta(hours=i*2)

                recent_analyses.append({
                    'id': f"analysis_{i+1}",
                    'project_name': f"Project {chr(65 + (i % 5))}",  # A, B, C, D, E
                    'project_id': f"project_{i+1}",
                    'score': round(85 - (i * 1.5), 1),
                    'grade': 'A' if i < 3 else 'B' if i < 6 else 'C',
                    'issues_count': max(0, 15 - i),
                    'high_severity': max(0, 3 - i//2),
                    'analyzed_at': analysis_date.isoformat(),
                    'duration_seconds': 45 + (i * 5),
                    'language': ['Python', 'JavaScript', 'Java', 'Go', 'TypeScript'][i % 5]
                })

            return recent_analyses

        except Exception as e:
            logger.error(f"Recent analyses generation failed: {e}")
            return []

    async def _get_top_issues(
        self,
        organization_id: Optional[str] = None,
        project_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get most common issues.
        """
        try:
            # Mock top issues data
            issue_types = [
                'Security vulnerability',
                'Code complexity',
                'Missing documentation',
                'Performance issue',
                'Code duplication',
                'Unused imports',
                'Long method',
                'Large class',
                'Missing tests',
                'Deprecated API usage'
            ]

            top_issues = []

            for i, issue_type in enumerate(issue_types[:limit]):
                top_issues.append({
                    'id': f"issue_{i+1}",
                    'type': issue_type,
                    'category': ['security', 'maintainability', 'documentation', 'performance', 'duplication'][i % 5],
                    'severity': ['high', 'medium', 'low', 'medium', 'low'][i % 5],
                    'count': max(1, 25 - i*2),
                    'affected_files': max(1, 10 - i),
                    'description': f"Description for {issue_type.lower()}",
                    'recommendation': f"Recommendation for fixing {issue_type.lower()}"
                })

            return top_issues

        except Exception as e:
            logger.error(f"Top issues generation failed: {e}")
            return []

    async def _get_project_statistics(
        self,
        organization_id: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get project statistics.
        """
        try:
            # Mock project statistics
            return {
                'total_projects': 15,
                'active_projects': 12,
                'projects_by_language': {
                    'Python': 5,
                    'JavaScript': 4,
                    'Java': 3,
                    'Go': 2,
                    'TypeScript': 1
                },
                'projects_by_status': {
                    'excellent': 3,
                    'good': 6,
                    'needs_attention': 4,
                    'critical': 2
                },
                'average_project_score': 78.5,
                'most_active_project': 'Project A',
                'least_active_project': 'Project E'
            }

        except Exception as e:
            logger.error(f"Project statistics generation failed: {e}")
            return {}

    async def _get_ai_insights(
        self,
        organization_id: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get AI-powered insights.
        """
        try:
            # Mock AI insights
            return {
                'summary': 'Overall code quality is improving with a 2.3% increase in average scores this month.',
                'key_findings': [
                    'Security vulnerabilities decreased by 15% compared to last month',
                    'Code complexity issues are the most common problem area',
                    'Documentation coverage has improved significantly',
                    'Performance optimizations show good progress'
                ],
                'recommendations': [
                    'Focus on reducing code complexity in the next sprint',
                    'Continue the good work on security improvements',
                    'Consider implementing automated documentation generation',
                    'Schedule performance reviews for critical services'
                ],
                'predictions': {
                    'next_month_score': 82.1,
                    'confidence': 0.78,
                    'risk_areas': ['code_complexity', 'error_handling']
                },
                'generated_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"AI insights generation failed: {e}")
            return {}

    async def get_project_comparison(
        self,
        project_ids: List[str],
        time_range: str = "30d"
    ) -> Dict[str, Any]:
        """
        Get comparison data between multiple projects.
        """
        try:
            comparison_data = []

            for project_id in project_ids:
                project_data = {
                    'project_id': project_id,
                    'project_name': f"Project {project_id.split('_')[-1]}",
                    'current_score': 75 + (hash(project_id) % 25),  # Mock score
                    'issues_count': max(0, 20 - (hash(project_id) % 10)),
                    'trend': 'up' if hash(project_id) % 2 == 0 else 'down',
                    'languages': ['Python', 'JavaScript'][hash(project_id) % 2],
                    'last_analysis': (datetime.utcnow() - timedelta(days=hash(project_id) % 7)).isoformat()
                }
                comparison_data.append(project_data)

            return {
                'comparison_data': comparison_data,
                'best_performer': max(comparison_data, key=lambda x: x['current_score']),
                'needs_attention': [p for p in comparison_data if p['current_score'] < 70],
                'generated_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Project comparison generation failed: {e}")
            return {}

    async def get_analysis_heatmap(
        self,
        organization_id: Optional[str] = None,
        time_range: str = "30d"
    ) -> Dict[str, Any]:
        """
        Get analysis activity heatmap data.
        """
        try:
            # Mock heatmap data
            days = 30 if time_range == "30d" else 7
            heatmap_data = []

            for day in range(days):
                for hour in range(24):
                    # Mock activity level (higher during business hours)
                    activity_level = 1 if 8 <= hour <= 18 else 0.3
                    activity_level += (hash(f"{day}_{hour}") % 100) / 100  # Add some randomness

                    heatmap_data.append({
                        'date': (datetime.utcnow() - timedelta(days=days-1-day)).strftime('%Y-%m-%d'),
                        'hour': hour,
                        'activity_level': min(1.0, activity_level),
                        'analysis_count': max(0, int(activity_level * 5))
                    })

            return {
                'heatmap_data': heatmap_data,
                'max_activity': max(d['activity_level'] for d in heatmap_data),
                'total_analyses': sum(d['analysis_count'] for d in heatmap_data),
                'time_range': time_range
            }

        except Exception as e:
            logger.error(f"Analysis heatmap generation failed: {e}")
            return {}

    def _get_from_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get data from cache if available and not expired.
        """
        try:
            if key in self.cache:
                cached_item = self.cache[key]
                if datetime.utcnow().timestamp() - cached_item['timestamp'] < self.cache_ttl:
                    return cached_item['data']
                else:
                    # Remove expired cache entry
                    del self.cache[key]
            return None
        except Exception:
            return None

    def _set_cache(self, key: str, data: Dict[str, Any]) -> None:
        """
        Store data in cache with timestamp.
        """
        try:
            self.cache[key] = {
                'data': data,
                'timestamp': datetime.utcnow().timestamp()
            }
        except Exception:
            pass  # Cache failure shouldn't break the service

    async def clear_cache(self) -> bool:
        """
        Clear all cached data.
        """
        try:
            self.cache.clear()
            logger.info("Dashboard cache cleared")
            return True
        except Exception as e:
            logger.error(f"Cache clearing failed: {e}")
            return False

    async def check_health(self) -> bool:
        """
        Check if dashboard data service is healthy.
        """
        try:
            # Test basic data generation
            test_data = await self.get_dashboard_data()
            return 'overview' in test_data and 'quality_trends' in test_data
        except Exception:
            return False
