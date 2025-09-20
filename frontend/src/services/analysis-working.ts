// Analysis Service - Working Version
import { apiClient } from './api-client-working'
import { Analysis, AnalysisResults } from '../types/analysis'
import { PaginationParams } from '../types/common-corrected'
import { ApiResponse } from '../types/api-corrected'

// Analysis configuration type
export interface AnalysisConfig {
  enabled_analyzers: string[]
  excluded_paths: string[]
  custom_rules: Record<string, any>
  analysis_type?: 'full' | 'incremental' | 'security' | 'performance' | 'custom'
  timeout?: number
  max_file_size?: number
  skip_tests?: boolean
}

export class AnalysisService {
  // Analysis execution
  async startAnalysis(projectId: string, config?: Partial<AnalysisConfig>): Promise<ApiResponse<Analysis>> {
    return apiClient.post<Analysis>('/api/v1/analyses', {
      project_id: projectId,
      config
    })
  }

  async getAnalysis(analysisId: string): Promise<ApiResponse<Analysis>> {
    return apiClient.get<Analysis>(`/api/v1/analyses/${analysisId}`)
  }

  async getAnalyses(params?: PaginationParams & {
    project_id?: string
    status?: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
    created_after?: string
    created_before?: string
  }): Promise<ApiResponse<Analysis[]>> {
    const queryParams = new URLSearchParams()
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, String(value))
        }
      })
    }

    const endpoint = `/api/v1/analyses${queryParams.toString() ? `?${queryParams.toString()}` : ''}`
    return apiClient.get<Analysis[]>(endpoint)
  }

  async cancelAnalysis(analysisId: string): Promise<ApiResponse<void>> {
    return apiClient.post<void>(`/api/v1/analyses/${analysisId}/cancel`)
  }

  async deleteAnalysis(analysisId: string): Promise<ApiResponse<void>> {
    return apiClient.delete<void>(`/api/v1/analyses/${analysisId}`)
  }

  // Analysis results
  async getAnalysisResults(analysisId: string): Promise<ApiResponse<AnalysisResults>> {
    return apiClient.get<AnalysisResults>(`/api/v1/analyses/${analysisId}/results`)
  }

  async getAnalysisMetrics(analysisId: string): Promise<ApiResponse<{
    total_issues: number
    critical_issues: number
    high_issues: number
    medium_issues: number
    low_issues: number
    quality_score: number
    coverage: number
    complexity: number
    maintainability: number
    security_score: number
    performance_score: number
  }>> {
    return apiClient.get<{
      total_issues: number
      critical_issues: number
      high_issues: number
      medium_issues: number
      low_issues: number
      quality_score: number
      coverage: number
      complexity: number
      maintainability: number
      security_score: number
      performance_score: number
    }>(`/api/v1/analyses/${analysisId}/metrics`)
  }

  async getAnalysisIssues(analysisId: string, params?: {
    severity?: 'critical' | 'high' | 'medium' | 'low' | 'info'
    category?: string
    file?: string
    page?: number
    per_page?: number
  }): Promise<ApiResponse<{
    issues: Array<{
      id: string
      type: string
      severity: 'critical' | 'high' | 'medium' | 'low' | 'info'
      category: string
      title: string
      description: string
      file_path: string
      line_number: number
      column_start?: number
      column_end?: number
      code_snippet?: string
      rule_id: string
      rule_name: string
      tags: string[]
      suggestions: string[]
    }>
    pagination: {
      page: number
      per_page: number
      total: number
      total_pages: number
    }
  }>> {
    const queryParams = new URLSearchParams()
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, String(value))
        }
      })
    }

    const endpoint = `/api/v1/analyses/${analysisId}/issues${queryParams.toString() ? `?${queryParams.toString()}` : ''}`
    return apiClient.get<{
      issues: Array<{
        id: string
        type: string
        severity: 'critical' | 'high' | 'medium' | 'low' | 'info'
        category: string
        title: string
        description: string
        file_path: string
        line_number: number
        column_start?: number
        column_end?: number
        code_snippet?: string
        rule_id: string
        rule_name: string
        tags: string[]
        suggestions: string[]
      }>
      pagination: {
        page: number
        per_page: number
        total: number
        total_pages: number
      }
    }>(endpoint)
  }

  // Analysis comparison
  async compareAnalyses(baseAnalysisId: string, compareAnalysisId: string): Promise<ApiResponse<{
    base_analysis: Analysis
    compare_analysis: Analysis
    differences: {
      new_issues: number
      fixed_issues: number
      worsened_issues: number
      improved_issues: number
      quality_score_change: number
      metrics_comparison: Record<string, {
        base: number
        compare: number
        change: number
        change_percent: number
      }>
    }
  }>> {
    return apiClient.get<{
      base_analysis: Analysis
      compare_analysis: Analysis
      differences: {
        new_issues: number
        fixed_issues: number
        worsened_issues: number
        improved_issues: number
        quality_score_change: number
        metrics_comparison: Record<string, {
          base: number
          compare: number
          change: number
          change_percent: number
        }>
      }
    }>(`/api/v1/analyses/${baseAnalysisId}/compare/${compareAnalysisId}`)
  }

  // Analysis scheduling
  async scheduleAnalysis(projectId: string, schedule: {
    cron_expression: string
    config?: Partial<AnalysisConfig>
    enabled: boolean
    timezone?: string
  }): Promise<ApiResponse<{
    id: string
    project_id: string
    cron_expression: string
    config?: Partial<AnalysisConfig>
    enabled: boolean
    timezone?: string
    next_run?: string
    created_at: string
    updated_at: string
  }>> {
    return apiClient.post<{
      id: string
      project_id: string
      cron_expression: string
      config?: Partial<AnalysisConfig>
      enabled: boolean
      timezone?: string
      next_run?: string
      created_at: string
      updated_at: string
    }>('/api/v1/analyses/schedules', {
      project_id: projectId,
      ...schedule
    })
  }

  async getAnalysisSchedules(projectId?: string): Promise<ApiResponse<Array<{
    id: string
    project_id: string
    cron_expression: string
    config?: Partial<AnalysisConfig>
    enabled: boolean
    timezone?: string
    next_run?: string
    created_at: string
    updated_at: string
  }>>> {
    const endpoint = projectId
      ? `/api/v1/analyses/schedules?project_id=${projectId}`
      : '/api/v1/analyses/schedules'
    return apiClient.get<Array<{
      id: string
      project_id: string
      cron_expression: string
      config?: Partial<AnalysisConfig>
      enabled: boolean
      timezone?: string
      next_run?: string
      created_at: string
      updated_at: string
    }>>(endpoint)
  }

  async updateAnalysisSchedule(scheduleId: string, updates: {
    cron_expression?: string
    config?: Partial<AnalysisConfig>
    enabled?: boolean
    timezone?: string
  }): Promise<ApiResponse<{
    id: string
    project_id: string
    cron_expression: string
    config?: Partial<AnalysisConfig>
    enabled: boolean
    timezone?: string
    next_run?: string
    created_at: string
    updated_at: string
  }>> {
    return apiClient.put<{
      id: string
      project_id: string
      cron_expression: string
      config?: Partial<AnalysisConfig>
      enabled: boolean
      timezone?: string
      next_run?: string
      created_at: string
      updated_at: string
    }>(`/api/v1/analyses/schedules/${scheduleId}`, updates)
  }

  async deleteAnalysisSchedule(scheduleId: string): Promise<ApiResponse<void>> {
    return apiClient.delete<void>(`/api/v1/analyses/schedules/${scheduleId}`)
  }

  // Analysis templates
  async getAnalysisTemplates(): Promise<ApiResponse<Array<{
    id: string
    name: string
    description: string
    config: AnalysisConfig
    category: string
    tags: string[]
    created_by: string
    created_at: string
  }>>> {
    return apiClient.get<Array<{
      id: string
      name: string
      description: string
      config: AnalysisConfig
      category: string
      tags: string[]
      created_by: string
      created_at: string
    }>>('/api/v1/analyses/templates')
  }

  async createAnalysisTemplate(template: {
    name: string
    description: string
    config: AnalysisConfig
    category: string
    tags?: string[]
  }): Promise<ApiResponse<{
    id: string
    name: string
    description: string
    config: AnalysisConfig
    category: string
    tags: string[]
    created_by: string
    created_at: string
  }>> {
    return apiClient.post<{
      id: string
      name: string
      description: string
      config: AnalysisConfig
      category: string
      tags: string[]
      created_by: string
      created_at: string
    }>('/api/v1/analyses/templates', template)
  }

  // Analysis statistics
  async getAnalysisStats(projectId?: string, period?: 'day' | 'week' | 'month' | 'year'): Promise<ApiResponse<{
    total_analyses: number
    successful_analyses: number
    failed_analyses: number
    average_duration: number
    quality_trend: Array<{
      date: string
      average_score: number
      total_issues: number
    }>
    top_issues: Array<{
      type: string
      count: number
      severity: 'critical' | 'high' | 'medium' | 'low' | 'info'
    }>
  }>> {
    const params = new URLSearchParams()
    if (projectId) params.append('project_id', projectId)
    if (period) params.append('period', period)

    const endpoint = `/api/v1/analyses/stats${params.toString() ? `?${params.toString()}` : ''}`
    return apiClient.get<{
      total_analyses: number
      successful_analyses: number
      failed_analyses: number
      average_duration: number
      quality_trend: Array<{
        date: string
        average_score: number
        total_issues: number
      }>
      top_issues: Array<{
        type: string
        count: number
        severity: 'critical' | 'high' | 'medium' | 'low' | 'info'
      }>
    }>(endpoint)
  }

  // Analysis export
  async exportAnalysisResults(analysisId: string, format: 'json' | 'csv' | 'pdf' | 'html' = 'json'): Promise<ApiResponse<Blob>> {
    return apiClient.get<Blob>(`/api/v1/analyses/${analysisId}/export?format=${format}`)
  }

  async exportAnalysisReport(analysisId: string, format: 'pdf' | 'html' = 'pdf'): Promise<ApiResponse<Blob>> {
    return apiClient.get<Blob>(`/api/v1/analyses/${analysisId}/report?format=${format}`)
  }
}

// Create and export service instance
export const analysisService = new AnalysisService()
export default analysisService
