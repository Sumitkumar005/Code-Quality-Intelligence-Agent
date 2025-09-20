// Analysis Service
import { apiClient } from './api-client-working'
import {
  AnalysisResult,
  AnalysisRequest,
  AnalysisResponse,
  AnalysisStatus,
  AnalysisConfig,
  AnalysisMetrics,
  Issue,
  CodeMetrics,
  QualityReport,
  ComparisonData,
  TrendData
} from '../types/analysis'
import { PaginationParams } from '../types/common-corrected'
import { ApiResponse } from '../types/api-corrected'

export class AnalysisService {
  // Analysis operations
  async startAnalysis(projectId: string, request: AnalysisRequest): Promise<ApiResponse<AnalysisResponse>> {
    return apiClient.post<AnalysisResponse>(`/api/v1/projects/${projectId}/analyze`, request)
  }

  async getAnalysis(analysisId: string): Promise<ApiResponse<AnalysisResult>> {
    return apiClient.get<AnalysisResult>(`/api/v1/analyses/${analysisId}`)
  }

  async getAnalysisStatus(analysisId: string): Promise<ApiResponse<AnalysisStatus>> {
    return apiClient.get<AnalysisStatus>(`/api/v1/analyses/${analysisId}/status`)
  }

  async getAnalysisResults(analysisId: string): Promise<ApiResponse<AnalysisResult>> {
    return apiClient.get<AnalysisResult>(`/api/v1/analyses/${analysisId}/results`)
  }

  async getAnalysisIssues(analysisId: string, params?: PaginationParams): Promise<ApiResponse<Issue[]>> {
    const queryParams = new URLSearchParams()
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, String(value))
        }
      })
    }

    const endpoint = `/api/v1/analyses/${analysisId}/issues${queryParams.toString() ? `?${queryParams.toString()}` : ''}`
    return apiClient.get<Issue[]>(endpoint)
  }

  async getAnalysisMetrics(analysisId: string): Promise<ApiResponse<AnalysisMetrics>> {
    return apiClient.get<AnalysisMetrics>(`/api/v1/analyses/${analysisId}/metrics`)
  }

  async getCodeMetrics(analysisId: string): Promise<ApiResponse<CodeMetrics>> {
    return apiClient.get<CodeMetrics>(`/api/v1/analyses/${analysisId}/code-metrics`)
  }

  // Analysis configuration
  async getAnalysisConfig(projectId: string): Promise<ApiResponse<AnalysisConfig>> {
    return apiClient.get<AnalysisConfig>(`/api/v1/projects/${projectId}/analysis-config`)
  }

  async updateAnalysisConfig(projectId: string, config: Partial<AnalysisConfig>): Promise<ApiResponse<AnalysisConfig>> {
    return apiClient.put<AnalysisConfig>(`/api/v1/projects/${projectId}/analysis-config`, config)
  }

  // Analysis history
  async getProjectAnalyses(projectId: string, params?: PaginationParams): Promise<ApiResponse<AnalysisResult[]>> {
    const queryParams = new URLSearchParams()
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, String(value))
        }
      })
    }

    const endpoint = `/api/v1/projects/${projectId}/analyses${queryParams.toString() ? `?${queryParams.toString()}` : ''}`
    return apiClient.get<AnalysisResult[]>(endpoint)
  }

  async getLatestAnalysis(projectId: string): Promise<ApiResponse<AnalysisResult>> {
    return apiClient.get<AnalysisResult>(`/api/v1/projects/${projectId}/analyses/latest`)
  }

  // Analysis comparison
  async compareAnalyses(analysisIds: string[]): Promise<ApiResponse<ComparisonData>> {
    return apiClient.post<ComparisonData>('/api/v1/analyses/compare', { analysis_ids: analysisIds })
  }

  async getAnalysisDiff(analysisId1: string, analysisId2: string): Promise<ApiResponse<{
    new_issues: Issue[]
    resolved_issues: Issue[]
    changed_issues: Issue[]
    metrics_diff: Record<string, number>
  }>> {
    return apiClient.get<{
      new_issues: Issue[]
      resolved_issues: Issue[]
      changed_issues: Issue[]
      metrics_diff: Record<string, number>
    }>(`/api/v1/analyses/${analysisId1}/diff/${analysisId2}`)
  }

  // Quality trends
  async getQualityTrends(projectId: string, days: number = 90): Promise<ApiResponse<TrendData[]>> {
    return apiClient.get<TrendData[]>(`/api/v1/projects/${projectId}/quality-trends?days=${days}`)
  }

  async getQualityScore(projectId: string): Promise<ApiResponse<{
    current_score: number
    previous_score: number
    trend: 'up' | 'down' | 'stable'
    last_updated: string
  }>> {
    return apiClient.get<{
      current_score: number
      previous_score: number
      trend: 'up' | 'down' | 'stable'
      last_updated: string
    }>(`/api/v1/projects/${projectId}/quality-score`)
  }

  // Issue management
  async updateIssueStatus(analysisId: string, issueId: string, status: 'open' | 'resolved' | 'ignored'): Promise<ApiResponse<Issue>> {
    return apiClient.patch<Issue>(`/api/v1/analyses/${analysisId}/issues/${issueId}`, { status })
  }

  async bulkUpdateIssues(analysisId: string, issueIds: string[], updates: Partial<Issue>): Promise<ApiResponse<{ updated: number; failed: number }>> {
    return apiClient.patch<{ updated: number; failed: number }>(`/api/v1/analyses/${analysisId}/issues/bulk`, {
      issue_ids: issueIds,
      updates
    })
  }

  async exportIssues(analysisId: string, format: 'json' | 'csv' | 'xml' = 'json'): Promise<ApiResponse<Blob>> {
    return apiClient.get<Blob>(`/api/v1/analyses/${analysisId}/issues/export?format=${format}`, {
      responseType: 'blob'
    })
  }

  // Analysis reports
  async generateQualityReport(analysisId: string, config?: Partial<QualityReport>): Promise<ApiResponse<QualityReport>> {
    return apiClient.post<QualityReport>(`/api/v1/analyses/${analysisId}/report`, config || {})
  }

  async getQualityReport(analysisId: string): Promise<ApiResponse<QualityReport>> {
    return apiClient.get<QualityReport>(`/api/v1/analyses/${analysisId}/report`)
  }

  // Analysis cancellation
  async cancelAnalysis(analysisId: string): Promise<ApiResponse<void>> {
    return apiClient.post<void>(`/api/v1/analyses/${analysisId}/cancel`)
  }

  async pauseAnalysis(analysisId: string): Promise<ApiResponse<void>> {
    return apiClient.post<void>(`/api/v1/analyses/${analysisId}/pause`)
  }

  async resumeAnalysis(analysisId: string): Promise<ApiResponse<void>> {
    return apiClient.post<void>(`/api/v1/analyses/${analysisId}/resume`)
  }

  // Analysis validation
  async validateAnalysisConfig(config: Partial<AnalysisConfig>): Promise<ApiResponse<{
    valid: boolean
    errors: string[]
    warnings: string[]
  }>> {
    return apiClient.post<{
      valid: boolean
      errors: string[]
      warnings: string[]
    }>('/api/v1/analyses/validate-config', config)
  }

  // Real-time updates
  async getAnalysisProgress(analysisId: string): Promise<ApiResponse<{
    progress: number
    current_step: string
    estimated_time_remaining: number
    logs: string[]
  }>> {
    return apiClient.get<{
      progress: number
      current_step: string
      estimated_time_remaining: number
      logs: string[]
    }>(`/api/v1/analyses/${analysisId}/progress`)
  }

  // Analysis templates
  async getAnalysisTemplates(): Promise<ApiResponse<AnalysisConfig[]>> {
    return apiClient.get<AnalysisConfig[]>('/api/v1/analyses/templates')
  }

  async saveAnalysisTemplate(projectId: string, name: string, config: AnalysisConfig): Promise<ApiResponse<AnalysisConfig>> {
    return apiClient.post<AnalysisConfig>('/api/v1/analyses/templates', {
      project_id: projectId,
      name,
      config
    })
  }
}

// Create and export service instance
export const analysisService = new AnalysisService()
export default analysisService
