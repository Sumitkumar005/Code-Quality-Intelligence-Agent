// Analysis service for managing code analysis data and API calls

import { apiClient } from './api'
import {
  AnalysisResult,
  QualityMetrics,
  Issue,
  TrendData,
  ComparisonData,
  AnalyzeRequest,
  AnalyzeResponse,
  QuestionRequest,
  QuestionResponse,
  QualityTrendsResponse,
  ProjectComparisonRequest,
} from '@/types/api'

export class AnalysisService {
  // Start a new analysis
  async startAnalysis(request: AnalyzeRequest): Promise<AnalyzeResponse> {
    return apiClient.post<AnalyzeResponse>('/api/v1/analyze', request)
  }

  // Get analysis status and results
  async getAnalysisStatus(reportId: string): Promise<AnalysisResult> {
    return apiClient.get<AnalysisResult>(`/api/v1/analyze/${reportId}/status`)
  }

  // Get quality metrics from analysis
  async getQualityMetrics(reportId: string): Promise<QualityMetrics | null> {
    try {
      const analysis = await this.getAnalysisStatus(reportId)
      if (analysis.status === 'completed' && analysis.metrics) {
        return analysis.metrics
      }
      return null
    } catch (error) {
      console.error('Failed to get quality metrics:', error)
      
      // Re-throw ApiException to preserve error details
      if (error instanceof ApiException) {
        throw error
      }
      
      // Wrap other errors in ApiException
      throw new ApiException(0, 'Failed to fetch quality metrics')
    }
  }

  // Get issues from analysis
  async getIssues(reportId: string): Promise<Issue[]> {
    try {
      const analysis = await this.getAnalysisStatus(reportId)
      if (analysis.status === 'completed' && analysis.issues) {
        return this.transformIssues(analysis.issues)
      }
      return []
    } catch (error) {
      console.error('Failed to get issues:', error)
      
      // Re-throw ApiException to preserve error details
      if (error instanceof ApiException) {
        throw error
      }
      
      // Wrap other errors in ApiException
      throw new ApiException(0, 'Failed to fetch issues')
    }
  }

  // Get quality trends for a project
  async getQualityTrends(projectId: string, days: number = 30): Promise<TrendData[]> {
    try {
      const response = await apiClient.get<QualityTrendsResponse>(
        `/api/v1/analytics/trends/${projectId}?days=${days}`
      )
      return response.trends || []
    } catch (error) {
      console.error('Failed to get quality trends:', error)
      return []
    }
  }

  // Get project comparison data
  async getProjectComparison(projectIds: string[]): Promise<ComparisonData | null> {
    try {
      const request: ProjectComparisonRequest = { project_ids: projectIds }
      return apiClient.post<ComparisonData>('/api/v1/analytics/compare', request)
    } catch (error) {
      console.error('Failed to get project comparison:', error)
      return null
    }
  }

  // Ask a question about analysis results
  async askQuestion(question: string, reportId: string): Promise<string> {
    try {
      const request: QuestionRequest = { question, report_id: reportId }
      const response = await apiClient.post<QuestionResponse>('/api/v1/qa/ask', request)
      return response.answer
    } catch (error) {
      console.error('Failed to ask question:', error)
      return 'Sorry, I could not process your question at this time.'
    }
  }

  // Get hotspot analysis for a project
  async getHotspotAnalysis(projectId: string): Promise<any> {
    try {
      return apiClient.get(`/api/v1/analytics/hotspots/${projectId}`)
    } catch (error) {
      console.error('Failed to get hotspot analysis:', error)
      return null
    }
  }

  // Transform backend issues to frontend format
  private transformIssues(backendIssues: any[]): Issue[] {
    return backendIssues.map((issue, index) => ({
      id: issue.id || `issue-${index}`,
      type: this.mapIssueType(issue.type),
      severity: issue.severity || 'Medium',
      message: issue.message || 'Issue detected',
      file: issue.file || 'Unknown file',
      line: issue.line || 0,
      suggestion: issue.suggestion || 'Review and fix this issue'
    }))
  }

  // Map backend issue types to frontend types
  private mapIssueType(backendType: string): Issue['type'] {
    const typeMap: Record<string, Issue['type']> = {
      'security': 'Security',
      'performance': 'Performance',
      'quality': 'Quality',
      'documentation': 'Documentation',
      'testing': 'Testing',
      'Security': 'Security',
      'Performance': 'Performance',
      'Quality': 'Quality',
      'Documentation': 'Documentation',
      'Testing': 'Testing'
    }
    
    return typeMap[backendType] || 'Quality'
  }

  // Calculate quality metrics from analysis data
  calculateMetricsFromAnalysis(analysis: AnalysisResult): QualityMetrics | null {
    if (!analysis.issues || !analysis.summary) {
      return null
    }

    const issues = analysis.issues
    const totalIssues = issues.length

    if (totalIssues === 0) {
      return {
        test_coverage: 85, // Default when no issues
        code_duplication: 5,
        technical_debt_hours: 0,
        complexity_distribution: {
          low: 100,
          medium: 0,
          high: 0
        }
      }
    }

    const highSeverity = issues.filter(issue => issue.severity === 'High').length
    const mediumSeverity = issues.filter(issue => issue.severity === 'Medium').length
    const lowSeverity = issues.filter(issue => issue.severity === 'Low').length

    return {
      test_coverage: Math.max(20, 90 - (totalIssues * 2)), // Decrease coverage based on issues
      code_duplication: Math.min(50, totalIssues * 1.5), // Increase duplication based on issues
      technical_debt_hours: (highSeverity * 2) + (mediumSeverity * 1) + (lowSeverity * 0.5),
      complexity_distribution: {
        low: Math.round((lowSeverity / totalIssues) * 100),
        medium: Math.round((mediumSeverity / totalIssues) * 100),
        high: Math.round((highSeverity / totalIssues) * 100)
      }
    }
  }
}

// Create singleton instance
export const analysisService = new AnalysisService()