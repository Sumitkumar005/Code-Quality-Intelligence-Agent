"""
Analytics Service - Track quality trends and insights
"""
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import hashlib

class AnalyticsService:
    """Service for tracking quality trends and analytics"""
    
    def __init__(self, db_path: str = "analytics.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize analytics database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Analysis history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                project_name TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                quality_score INTEGER,
                total_files INTEGER,
                total_lines INTEGER,
                languages TEXT,
                issues_high INTEGER DEFAULT 0,
                issues_medium INTEGER DEFAULT 0,
                issues_low INTEGER DEFAULT 0,
                analysis_data TEXT
            )
        ''')
        
        # Quality trends table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quality_trends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                date DATE,
                quality_score INTEGER,
                technical_debt_hours REAL,
                security_issues INTEGER,
                performance_issues INTEGER,
                maintainability_score INTEGER
            )
        ''')
        
        # Developer insights table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS developer_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                file_path TEXT,
                change_frequency INTEGER DEFAULT 1,
                issue_density REAL DEFAULT 0.0,
                complexity_score REAL DEFAULT 0.0,
                last_analyzed DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def record_analysis(self, project_identifier: str, analysis_results: Dict[str, Any]) -> str:
        """Record analysis results for trend tracking"""
        
        # Generate project ID from identifier (repo URL, folder path, etc.)
        project_id = hashlib.md5(project_identifier.encode()).hexdigest()[:12]
        
        # Extract metrics from analysis results
        summary = analysis_results.get("summary", {})
        issues = analysis_results.get("issues", [])
        
        # Count issues by severity
        issue_counts = {"High": 0, "Medium": 0, "Low": 0}
        for issue in issues:
            severity = issue.get("severity", "Low")
            issue_counts[severity] = issue_counts.get(severity, 0) + 1
        
        # Store analysis
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO analysis_history 
            (project_id, project_name, quality_score, total_files, total_lines, 
             languages, issues_high, issues_medium, issues_low, analysis_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            project_id,
            project_identifier.split('/')[-1],  # Use last part as project name
            summary.get("quality_score", 0),
            summary.get("total_files", 0),
            summary.get("total_lines", 0),
            json.dumps(summary.get("languages", [])),
            issue_counts["High"],
            issue_counts["Medium"], 
            issue_counts["Low"],
            json.dumps(analysis_results)
        ))
        
        conn.commit()
        conn.close()
        
        return project_id
    
    def get_quality_trends(self, project_id: str, days: int = 30) -> Dict[str, Any]:
        """Get quality trends for a project"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get historical data
        cursor.execute('''
            SELECT timestamp, quality_score, issues_high, issues_medium, issues_low,
                   total_files, total_lines
            FROM analysis_history 
            WHERE project_id = ? 
            AND timestamp >= datetime('now', '-{} days')
            ORDER BY timestamp ASC
        '''.format(days), (project_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return {"message": "No historical data available"}
        
        # Process trends
        trends = {
            "dates": [],
            "quality_scores": [],
            "total_issues": [],
            "high_severity_issues": [],
            "codebase_growth": []
        }
        
        for row in rows:
            timestamp, quality_score, high, medium, low, files, lines = row
            
            trends["dates"].append(timestamp.split()[0])  # Date only
            trends["quality_scores"].append(quality_score)
            trends["total_issues"].append(high + medium + low)
            trends["high_severity_issues"].append(high)
            trends["codebase_growth"].append(lines)
        
        # Calculate insights
        insights = self._calculate_insights(trends)
        
        return {
            "trends": trends,
            "insights": insights,
            "summary": {
                "total_analyses": len(rows),
                "date_range": f"{trends['dates'][0]} to {trends['dates'][-1]}",
                "current_quality": trends["quality_scores"][-1] if trends["quality_scores"] else 0,
                "quality_change": self._calculate_change(trends["quality_scores"]),
                "issue_trend": self._calculate_change(trends["total_issues"], reverse=True)
            }
        }
    
    def _calculate_insights(self, trends: Dict[str, List]) -> List[str]:
        """Generate insights from trend data"""
        insights = []
        
        quality_scores = trends["quality_scores"]
        total_issues = trends["total_issues"]
        
        if len(quality_scores) >= 2:
            # Quality trend
            if quality_scores[-1] > quality_scores[0]:
                insights.append("📈 Quality is improving over time")
            elif quality_scores[-1] < quality_scores[0]:
                insights.append("📉 Quality is declining - attention needed")
            else:
                insights.append("📊 Quality remains stable")
        
        if len(total_issues) >= 2:
            # Issue trend
            if total_issues[-1] < total_issues[0]:
                insights.append("✅ Issue count is decreasing")
            elif total_issues[-1] > total_issues[0]:
                insights.append("⚠️ Issue count is increasing")
        
        # Codebase growth vs quality
        if len(trends["codebase_growth"]) >= 2:
            growth_rate = (trends["codebase_growth"][-1] - trends["codebase_growth"][0]) / trends["codebase_growth"][0]
            if growth_rate > 0.2:  # 20% growth
                insights.append("🚀 Codebase is growing rapidly - monitor quality closely")
        
        return insights
    
    def _calculate_change(self, values: List[float], reverse: bool = False) -> str:
        """Calculate percentage change between first and last values"""
        if len(values) < 2:
            return "No change"
        
        first, last = values[0], values[-1]
        if first == 0:
            return "New baseline"
        
        change = ((last - first) / first) * 100
        if reverse:
            change = -change
        
        if change > 5:
            return f"↗️ +{change:.1f}%"
        elif change < -5:
            return f"↘️ {change:.1f}%"
        else:
            return "→ Stable"
    
    def get_hotspot_analysis(self, project_id: str) -> Dict[str, Any]:
        """Identify code hotspots (files that change often and have issues)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get recent analysis data
        cursor.execute('''
            SELECT analysis_data FROM analysis_history 
            WHERE project_id = ? 
            ORDER BY timestamp DESC LIMIT 1
        ''', (project_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return {"hotspots": [], "message": "No data available"}
        
        analysis_data = json.loads(row[0])
        issues = analysis_data.get("issues", [])
        
        # Group issues by file
        file_issues = {}
        for issue in issues:
            file_path = issue.get("file", "unknown")
            if file_path not in file_issues:
                file_issues[file_path] = []
            file_issues[file_path].append(issue)
        
        # Calculate hotspot scores
        hotspots = []
        for file_path, file_issue_list in file_issues.items():
            high_issues = len([i for i in file_issue_list if i.get("severity") == "High"])
            total_issues = len(file_issue_list)
            
            # Simple hotspot score (can be enhanced with change frequency data)
            hotspot_score = (high_issues * 3) + (total_issues * 1)
            
            if hotspot_score > 0:
                hotspots.append({
                    "file": file_path,
                    "total_issues": total_issues,
                    "high_severity_issues": high_issues,
                    "hotspot_score": hotspot_score,
                    "risk_level": "High" if hotspot_score >= 5 else "Medium" if hotspot_score >= 2 else "Low"
                })
        
        # Sort by hotspot score
        hotspots.sort(key=lambda x: x["hotspot_score"], reverse=True)
        
        return {
            "hotspots": hotspots[:10],  # Top 10 hotspots
            "summary": {
                "total_hotspots": len(hotspots),
                "high_risk_files": len([h for h in hotspots if h["risk_level"] == "High"]),
                "recommendation": "Focus on high-risk files first for maximum impact"
            }
        }
    
    def get_project_comparison(self, project_ids: List[str]) -> Dict[str, Any]:
        """Compare quality metrics across multiple projects"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        comparisons = []
        
        for project_id in project_ids:
            cursor.execute('''
                SELECT project_name, quality_score, total_files, total_lines,
                       issues_high, issues_medium, issues_low
                FROM analysis_history 
                WHERE project_id = ? 
                ORDER BY timestamp DESC LIMIT 1
            ''', (project_id,))
            
            row = cursor.fetchone()
            if row:
                name, quality, files, lines, high, medium, low = row
                comparisons.append({
                    "project_id": project_id,
                    "project_name": name,
                    "quality_score": quality,
                    "total_files": files,
                    "total_lines": lines,
                    "total_issues": high + medium + low,
                    "high_severity_issues": high,
                    "issues_per_kloc": round((high + medium + low) / max(lines / 1000, 1), 2)
                })
        
        conn.close()
        
        # Add rankings
        if comparisons:
            # Sort by quality score for ranking
            sorted_by_quality = sorted(comparisons, key=lambda x: x["quality_score"], reverse=True)
            for i, project in enumerate(sorted_by_quality):
                project["quality_rank"] = i + 1
        
        return {
            "projects": comparisons,
            "insights": self._generate_comparison_insights(comparisons)
        }
    
    def _generate_comparison_insights(self, projects: List[Dict]) -> List[str]:
        """Generate insights from project comparison"""
        if len(projects) < 2:
            return ["Need at least 2 projects for comparison"]
        
        insights = []
        
        # Best and worst quality
        best = max(projects, key=lambda x: x["quality_score"])
        worst = min(projects, key=lambda x: x["quality_score"])
        
        insights.append(f"🏆 Best quality: {best['project_name']} ({best['quality_score']}/100)")
        insights.append(f"⚠️ Needs attention: {worst['project_name']} ({worst['quality_score']}/100)")
        
        # Average metrics
        avg_quality = sum(p["quality_score"] for p in projects) / len(projects)
        insights.append(f"📊 Average quality score: {avg_quality:.1f}/100")
        
        return insights

# Global analytics service
analytics_service = AnalyticsService()