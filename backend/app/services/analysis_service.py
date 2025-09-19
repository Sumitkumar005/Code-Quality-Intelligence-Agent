"""
Analysis service for code quality assessment
"""

from typing import Dict, List, Any, Optional
import asyncio
import structlog
from pathlib import Path
import json

from .ast_analyzer import ASTAnalyzer
# from .agent_service import CodeQualityAgent, CodeQualityRAG  # Disabled for now

logger = structlog.get_logger(__name__)

class AnalysisService:
    """Service for analyzing code repositories"""
    
    def __init__(self):
        self.active_analyses = {}
        self.ast_analyzer = ASTAnalyzer()
        # self.agent = CodeQualityAgent()  # Disabled for now
        # self.rag_system = CodeQualityRAG()  # Disabled for now
    
    async def analyze_repository_background(self, report_id: str, request_data: dict):
        """Background task for repository analysis"""
        try:
            self.active_analyses[report_id] = {
                "status": "processing",
                "progress": 10,
                "message": "Starting analysis..."
            }
            
            # Extract files data from request
            files_data = request_data.get("data", {}).get("files", {})
            
            if not files_data:
                raise ValueError("No files provided for analysis")
            
            # Update progress
            self.active_analyses[report_id]["progress"] = 30
            self.active_analyses[report_id]["message"] = "Analyzing code structure..."
            
            # Perform AST-based analysis
            analysis_results = self.ast_analyzer.analyze_codebase(files_data)
            
            # Update progress
            self.active_analyses[report_id]["progress"] = 60
            self.active_analyses[report_id]["message"] = "Setting up intelligent Q&A..."
            
            # Setup RAG for intelligent Q&A (disabled for now)
            # self.agent.setup_rag(analysis_results)
            # self.rag_system.index_codebase(files_data)
            
            # Update progress
            self.active_analyses[report_id]["progress"] = 90
            self.active_analyses[report_id]["message"] = "Finalizing report..."
            
            # Enhance results with agent insights
            try:
                enhanced_results = await self._enhance_with_agent_insights(analysis_results)
            except Exception as e:
                logger.error(f"Enhancement failed for {report_id}: {e}", exc_info=True)
                enhanced_results = analysis_results
            
            # Final result
            final_result = {
                "status": "completed",
                "progress": 100,
                "message": "Analysis complete",
                **enhanced_results
            }
            
            self.active_analyses[report_id] = final_result
            logger.info(f"Analysis completed for {report_id}")
            
        except Exception as e:
            logger.error(f"Analysis failed for {report_id}: {e}", exc_info=True)
            self.active_analyses[report_id] = {
                "status": "error",
                "progress": 0,
                "message": str(e)
            }
    
    async def _enhance_with_agent_insights(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance analysis results with agent-generated insights"""
        try:
            # Generate additional insights using the agent
            issues = analysis_results.get("issues", [])
            
            # Prioritize issues using agent intelligence
            prioritized_issues = self._prioritize_issues(issues)
            
            # Generate contextual recommendations
            contextual_recommendations = self._generate_contextual_recommendations(analysis_results)
            
            # Add severity scoring
            severity_scores = self._calculate_severity_scores(issues)
            
            enhanced_results = analysis_results.copy()
            enhanced_results.update({
                "issues": prioritized_issues,
                "recommendations": contextual_recommendations,
                "severity_analysis": severity_scores,
                "agent_insights": {
                    "critical_areas": self._identify_critical_areas(analysis_results),
                    "improvement_priority": self._suggest_improvement_priority(issues),
                    "technical_debt_estimate": self._estimate_technical_debt(issues)
                }
            })
            
            return enhanced_results
            
        except Exception as e:
            logger.error(f"Failed to enhance with agent insights: {e}")
            return analysis_results
    
    def _prioritize_issues(self, issues: List[Dict]) -> List[Dict]:
        """Prioritize issues based on severity and impact"""
        severity_order = {"High": 3, "Medium": 2, "Low": 1}
        
        # Sort by severity first, then by type importance
        type_importance = {
            "Security": 4,
            "Performance": 3,
            "Code Quality": 2,
            "Documentation": 1
        }
        
        def priority_key(issue):
            severity_score = severity_order.get(issue.get("severity", "Low"), 1)
            type_score = type_importance.get(issue.get("type", "Documentation"), 1)
            return (severity_score * 10) + type_score
        
        return sorted(issues, key=priority_key, reverse=True)
    
    def _generate_contextual_recommendations(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Generate contextual recommendations based on analysis"""
        recommendations = analysis_results.get("recommendations", [])
        issues = analysis_results.get("issues", [])
        summary = analysis_results.get("summary", {})
        
        # Add context-specific recommendations
        contextual_recs = recommendations.copy()
        
        # Security-focused recommendations
        security_issues = [i for i in issues if i.get("type") == "Security"]
        if len(security_issues) > 2:
            contextual_recs.insert(0, "🚨 URGENT: Multiple security vulnerabilities detected. Conduct immediate security audit")
        
        # Performance recommendations
        performance_issues = [i for i in issues if i.get("type") == "Performance"]
        if len(performance_issues) > 3:
            contextual_recs.append("⚡ Consider performance profiling to identify bottlenecks")
        
        # Code quality recommendations based on size
        total_lines = summary.get("total_lines", 0)
        if total_lines > 10000:
            contextual_recs.append("📊 Large codebase detected - consider implementing automated quality gates")
        
        return contextual_recs[:8]  # Limit to top 8 recommendations
    
    def _calculate_severity_scores(self, issues: List[Dict]) -> Dict[str, Any]:
        """Calculate severity distribution and scores"""
        severity_counts = {"High": 0, "Medium": 0, "Low": 0}
        type_counts = {}
        
        for issue in issues:
            severity = issue.get("severity", "Low")
            issue_type = issue.get("type", "Unknown")
            
            severity_counts[severity] += 1
            type_counts[issue_type] = type_counts.get(issue_type, 0) + 1
        
        # Calculate risk score (0-100)
        risk_score = min(100, (severity_counts["High"] * 20) + 
                        (severity_counts["Medium"] * 10) + 
                        (severity_counts["Low"] * 3))
        
        return {
            "severity_distribution": severity_counts,
            "type_distribution": type_counts,
            "risk_score": risk_score,
            "total_issues": sum(severity_counts.values())
        }
    
    def _identify_critical_areas(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Identify critical areas that need immediate attention"""
        issues = analysis_results.get("issues", [])
        critical_areas = []
        
        # Group issues by file
        file_issues = {}
        for issue in issues:
            file_path = issue.get("file", "unknown")
            if file_path not in file_issues:
                file_issues[file_path] = []
            file_issues[file_path].append(issue)
        
        # Find files with multiple high-severity issues
        for file_path, file_issue_list in file_issues.items():
            high_severity = [i for i in file_issue_list if i.get("severity") == "High"]
            if len(high_severity) >= 2:
                critical_areas.append(f"📁 {file_path} - Multiple high-severity issues")
        
        # Add general critical areas
        security_issues = [i for i in issues if i.get("type") == "Security"]
        if len(security_issues) > 0:
            critical_areas.append("🔒 Security vulnerabilities require immediate attention")
        
        return critical_areas[:5]  # Top 5 critical areas
    
    def _suggest_improvement_priority(self, issues: List[Dict]) -> List[str]:
        """Suggest improvement priority order"""
        priorities = []
        
        # Count issues by type and severity
        high_security = len([i for i in issues if i.get("type") == "Security" and i.get("severity") == "High"])
        high_performance = len([i for i in issues if i.get("type") == "Performance" and i.get("severity") == "High"])
        
        if high_security > 0:
            priorities.append("1. Fix security vulnerabilities immediately")
        
        if high_performance > 0:
            priorities.append("2. Address performance bottlenecks")
        
        priorities.extend([
            "3. Improve code documentation",
            "4. Refactor complex functions",
            "5. Add comprehensive tests"
        ])
        
        return priorities[:5]
    
    def _estimate_technical_debt(self, issues: List[Dict]) -> Dict[str, Any]:
        """Estimate technical debt in hours"""
        # Simple estimation based on issue types and severity
        debt_hours = 0
        
        for issue in issues:
            severity = issue.get("severity", "Low")
            issue_type = issue.get("type", "Documentation")
            
            # Base hours by severity
            base_hours = {"High": 4, "Medium": 2, "Low": 0.5}
            
            # Multiplier by type
            type_multiplier = {
                "Security": 2.0,
                "Performance": 1.5,
                "Code Quality": 1.0,
                "Documentation": 0.5
            }
            
            hours = base_hours.get(severity, 0.5) * type_multiplier.get(issue_type, 1.0)
            debt_hours += hours
        
        return {
            "estimated_hours": round(debt_hours, 1),
            "estimated_days": round(debt_hours / 8, 1),
            "priority_hours": round(sum(4 for i in issues if i.get("severity") == "High"), 1)
        }
    
    async def ask_question(self, report_id: str, question: str) -> str:
        """Ask a question about the analysis results"""
        try:
            analysis_data = self.active_analyses.get(report_id)
            if not analysis_data or analysis_data.get("status") != "completed":
                return "Analysis not found or not completed yet."
            
            # Simple Q&A fallback (agent disabled for now)
            return self._simple_qa_response(question, analysis_data)
            
        except Exception as e:
            logger.error(f"Failed to answer question: {e}")
            return "I'm sorry, I couldn't process your question at the moment."
    
    async def get_analysis_status(self, report_id: str) -> Optional[dict]:
        """Get analysis status by report ID"""
        return self.active_analyses.get(report_id)
    
    async def cancel_analysis(self, report_id: str) -> bool:
        """Cancel ongoing analysis"""
        if report_id in self.active_analyses:
            self.active_analyses[report_id]["status"] = "cancelled"
            return True
        return False
    
    def _simple_qa_response(self, question: str, context: Optional[Dict] = None) -> str:
        """Simple Q&A fallback when agent is not available"""
        question_lower = question.lower()
        
        responses = {
            "security": "Based on the analysis, focus on addressing high-severity security issues first. Look for hardcoded credentials, input validation gaps, and unsafe function usage.",
            "performance": "The main performance issues identified include inefficient loops, string concatenation in loops, and potential memory leaks. Consider optimizing algorithms and using appropriate data structures.",
            "quality": "Code quality can be improved by reducing function complexity, adding proper documentation, following consistent naming conventions, and breaking large files into smaller modules.",
            "test": "Improve test coverage by adding unit tests for critical functions, integration tests for key workflows, and edge case testing.",
            "complexity": "High complexity areas should be refactored into smaller, more manageable functions. Consider using design patterns and extracting common functionality.",
            "documentation": "Add docstrings to functions and classes, create README files for modules, and include inline comments for complex logic."
        }
        
        # Find matching response
        for keyword, response in responses.items():
            if keyword in question_lower:
                return response
        
        # Default response with context
        if context and "summary" in context:
            summary = context["summary"]
            return f"""Based on your codebase analysis:
            
- You have {summary.get('total_files', 0)} files with {summary.get('total_lines', 0):,} lines of code
- Quality score: {summary.get('quality_score', 0)}/100
- Languages: {', '.join(summary.get('languages', []))}

I can help you understand specific aspects of your code quality. Try asking about security, performance, testing, or code complexity issues."""
        
        return "I can help you understand your code analysis results. Try asking about security issues, performance problems, code quality improvements, or testing recommendations."