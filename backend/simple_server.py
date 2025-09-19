#!/usr/bin/env python3
"""
Simple FastAPI server for CQIA - No complex dependencies
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import uuid
import asyncio
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our working services
from app.services.ast_analyzer import ASTAnalyzer
from app.services.advanced.llm_service import llm_service
from app.services.advanced.rag_service import rag_service
from app.services.advanced.github_service import github_service
from app.services.advanced.analytics_service import analytics_service

app = FastAPI(title="CQIA API", description="Code Quality Intelligence Agent")

# CORS middleware - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=False,  # Set to False when using allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global analyzer instance
analyzer = ASTAnalyzer()
active_analyses = {}

# Request/Response models
class AnalyzeRequest(BaseModel):
    input: str
    data: Optional[Dict[str, Any]] = None

class AnalyzeResponse(BaseModel):
    report_id: str
    status: str
    message: str

class QuestionRequest(BaseModel):
    question: str
    report_id: str

class QuestionResponse(BaseModel):
    answer: str
    report_id: str

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}

@app.post("/api/v1/analyze", response_model=AnalyzeResponse)
async def analyze_repository(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    """Analyze a code repository"""
    try:
        report_id = str(uuid.uuid4())
        
        # Start background analysis
        background_tasks.add_task(analyze_background, report_id, request.dict())
        
        return AnalyzeResponse(
            report_id=report_id,
            status="processing",
            message="Analysis started successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analyze/{report_id}/status")
async def get_analysis_status(report_id: str):
    """Get analysis status"""
    if report_id not in active_analyses:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return active_analyses[report_id]

@app.post("/api/v1/qa/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """Ask a question about analysis results"""
    try:
        analysis_data = active_analyses.get(request.report_id)
        if not analysis_data or analysis_data.get("status") != "completed":
            return QuestionResponse(
                answer="Analysis not found or not completed yet.",
                report_id=request.report_id
            )
        
        # Use LLM service for intelligent responses
        answer = llm_service.ask_question(request.question, analysis_data)
        
        return QuestionResponse(
            answer=answer,
            report_id=request.report_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def analyze_background(report_id: str, request_data: dict):
    """Background analysis task"""
    try:
        active_analyses[report_id] = {
            "status": "processing",
            "progress": 10,
            "message": "Starting analysis..."
        }
        
        # Get files data
        files_data = request_data.get("data", {}).get("files", {})
        
        if not files_data:
            raise ValueError("No files provided for analysis")
        
        # Update progress
        active_analyses[report_id]["progress"] = 50
        active_analyses[report_id]["message"] = "Analyzing code..."
        
        # Perform real analysis using our AST analyzer
        results = analyzer.analyze_codebase(files_data)
        
        # Update progress
        active_analyses[report_id]["progress"] = 80
        active_analyses[report_id]["message"] = "Setting up RAG index..."
        
        # Index codebase for RAG
        rag_service.index_codebase(files_data, results)
        
        # Update progress
        active_analyses[report_id]["progress"] = 100
        active_analyses[report_id]["message"] = "Analysis complete"
        
        # Store results
        active_analyses[report_id].update({
            "status": "completed",
            **results
        })
        
    except Exception as e:
        active_analyses[report_id] = {
            "status": "error",
            "message": str(e)
        }

# New advanced endpoints

@app.post("/api/v1/analyze/github")
async def analyze_github_repository(request: dict, background_tasks: BackgroundTasks):
    """Analyze a GitHub repository"""
    try:
        repo_url = request.get("repo_url")
        if not repo_url:
            raise HTTPException(status_code=400, detail="repo_url is required")
        
        report_id = str(uuid.uuid4())
        
        # Start background GitHub analysis
        background_tasks.add_task(analyze_github_background, report_id, repo_url)
        
        return AnalyzeResponse(
            report_id=report_id,
            status="processing",
            message=f"GitHub repository analysis started for {repo_url}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analytics/trends/{project_id}")
async def get_quality_trends(project_id: str, days: int = 30):
    """Get quality trends for a project"""
    try:
        trends = analytics_service.get_quality_trends(project_id, days)
        return trends
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analytics/hotspots/{project_id}")
async def get_hotspot_analysis(project_id: str):
    """Get code hotspot analysis"""
    try:
        hotspots = analytics_service.get_hotspot_analysis(project_id)
        return hotspots
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/github/trending")
async def get_trending_repositories(language: str = "", limit: int = 10):
    """Get trending GitHub repositories"""
    try:
        repos = github_service.get_trending_repos(language, limit)
        return {"repositories": repos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/analytics/compare")
async def compare_projects(request: dict):
    """Compare quality metrics across projects"""
    try:
        project_ids = request.get("project_ids", [])
        if len(project_ids) < 2:
            raise HTTPException(status_code=400, detail="At least 2 project IDs required")
        
        comparison = analytics_service.get_project_comparison(project_ids)
        return comparison
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def analyze_github_background(report_id: str, repo_url: str):
    """Background task for GitHub repository analysis"""
    try:
        active_analyses[report_id] = {
            "status": "processing",
            "progress": 10,
            "message": "Downloading repository..."
        }
        
        # Download repository
        repo_data = github_service.analyze_repository(repo_url)
        
        active_analyses[report_id]["progress"] = 40
        active_analyses[report_id]["message"] = "Analyzing code..."
        
        # Analyze code
        files_data = repo_data["files"]
        results = analyzer.analyze_codebase(files_data)
        
        active_analyses[report_id]["progress"] = 70
        active_analyses[report_id]["message"] = "Setting up RAG index..."
        
        # Setup RAG
        rag_service.index_codebase(files_data, results)
        
        active_analyses[report_id]["progress"] = 90
        active_analyses[report_id]["message"] = "Recording analytics..."
        
        # Record for analytics
        project_id = analytics_service.record_analysis(repo_url, results)
        
        # Final results
        final_result = {
            "status": "completed",
            "progress": 100,
            "message": "GitHub analysis complete",
            "project_id": project_id,
            "repository": repo_data["repository"],
            **results
        }
        
        active_analyses[report_id] = final_result
        
    except Exception as e:
        active_analyses[report_id] = {
            "status": "error",
            "message": f"GitHub analysis failed: {str(e)}"
        }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting CQIA Backend Server...")
    print("📍 API will be available at: http://localhost:8004")
    print("📖 API docs at: http://localhost:8004/docs")
    uvicorn.run(app, host="0.0.0.0", port=8004)
