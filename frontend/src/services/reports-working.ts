// Reports Service - Working Version
import { apiClient } from './api-client-working'
import { Report } from '../types/report'
import { PaginationParams } from '../types/common-corrected'
import { ApiResponse } from '../types/api-corrected'

export class ReportsService {
  // Report generation
  async generateReport(projectId: string, options?: {
    analysis_id?: string
    report_type?: 'summary' | 'detailed' | 'security' | 'performance' | 'compliance'
    format?: 'pdf' | 'html' | 'json' | 'xml'
    include_charts?: boolean
    include_raw_data?: boolean
    sections?: string[]
    filters?: Record<string, any>
  }): Promise<ApiResponse<Report>> {
    return apiClient.post<Report>('/api/v1/reports', {
      project_id: projectId,
      ...options
    })
  }

  async getReport(reportId: string): Promise<ApiResponse<Report>> {
    return apiClient.get<Report>(`/api/v1/reports/${reportId}`)
  }

  async getReports(params?: PaginationParams & {
    project_id?: string
    status?: 'pending' | 'generating' | 'completed' | 'failed'
    report_type?: 'summary' | 'detailed' | 'security' | 'performance' | 'compliance'
    created_after?: string
    created_before?: string
  }): Promise<ApiResponse<Report[]>> {
    const queryParams = new URLSearchParams()
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, String(value))
        }
      })
    }

    const endpoint = `/api/v1/reports${queryParams.toString() ? `?${queryParams.toString()}` : ''}`
    return apiClient.get<Report[]>(endpoint)
  }

  async deleteReport(reportId: string): Promise<ApiResponse<void>> {
    return apiClient.delete<void>(`/api/v1/reports/${reportId}`)
  }

  // Report download
  async downloadReport(reportId: string, format?: 'pdf' | 'html' | 'json' | 'xml'): Promise<ApiResponse<Blob>> {
    const endpoint = format
      ? `/api/v1/reports/${reportId}/download?format=${format}`
      : `/api/v1/reports/${reportId}/download`
    return apiClient.get<Blob>(endpoint)
  }

  // Report templates
  async getReportTemplates(): Promise<ApiResponse<Array<{
    id: string
    name: string
    description: string
    report_type: 'summary' | 'detailed' | 'security' | 'performance' | 'compliance'
    format: 'pdf' | 'html' | 'json' | 'xml'
    config: Record<string, any>
    created_by: string
    created_at: string
  }>>> {
    return apiClient.get<Array<{
      id: string
      name: string
      description: string
      report_type: 'summary' | 'detailed' | 'security' | 'performance' | 'compliance'
      format: 'pdf' | 'html' | 'json' | 'xml'
      config: Record<string, any>
      created_by: string
      created_at: string
    }>>('/api/v1/reports/templates')
  }

  async createReportTemplate(template: {
    name: string
    description: string
    report_type: 'summary' | 'detailed' | 'security' | 'performance' | 'compliance'
    format: 'pdf' | 'html' | 'json' | 'xml'
    config: Record<string, any>
  }): Promise<ApiResponse<{
    id: string
    name: string
    description: string
    report_type: 'summary' | 'detailed' | 'security' | 'performance' | 'compliance'
    format: 'pdf' | 'html' | 'json' | 'xml'
    config: Record<string, any>
    created_by: string
    created_at: string
  }>> {
    return apiClient.post<{
      id: string
      name: string
      description: string
      report_type: 'summary' | 'detailed' | 'security' | 'performance' | 'compliance'
      format: 'pdf' | 'html' | 'json' | 'xml'
      config: Record<string, any>
      created_by: string
      created_at: string
    }>('/api/v1/reports/templates', template)
  }

  async updateReportTemplate(templateId: string, updates: {
    name?: string
    description?: string
    config?: Record<string, any>
  }): Promise<ApiResponse<{
    id: string
    name: string
    description: string
    report_type: 'summary' | 'detailed' | 'security' | 'performance' | 'compliance'
    format: 'pdf' | 'html' | 'json' | 'xml'
    config: Record<string, any>
    created_by: string
    created_at: string
  }>> {
    return apiClient.put<{
      id: string
      name: string
      description: string
      report_type: 'summary' | 'detailed' | 'security' | 'performance' | 'compliance'
      format: 'pdf' | 'html' | 'json' | 'xml'
      config: Record<string, any>
      created_by: string
      created_at: string
    }>(`/api/v1/reports/templates/${templateId}`, updates)
  }

  async deleteReportTemplate(templateId: string): Promise<ApiResponse<void>> {
    return apiClient.delete<void>(`/api/v1/reports/templates/${templateId}`)
  }

  // Report scheduling
  async scheduleReport(projectId: string, schedule: {
    report_type: 'summary' | 'detailed' | 'security' | 'performance' | 'compliance'
    format: 'pdf' | 'html' | 'json' | 'xml'
    cron_expression: string
    recipients?: string[]
    config?: Record<string, any>
    enabled: boolean
    timezone?: string
  }): Promise<ApiResponse<{
    id: string
    project_id: string
    report_type: 'summary' | 'detailed' | 'security' | 'performance' | 'compliance'
    format: 'pdf' | 'html' | 'json' | 'xml'
    cron_expression: string
    recipients?: string[]
    config?: Record<string, any>
    enabled: boolean
    timezone?: string
    next_run?: string
    created_at: string
    updated_at: string
  }>> {
    return apiClient.post<{
      id: string
      project_id: string
      report_type: 'summary' | 'detailed' | 'security' | 'performance' | 'compliance'
      format: 'pdf' | 'html' | 'json' | 'xml'
      cron_expression: string
      recipients?: string[]
      config?: Record<string, any>
      enabled: boolean
      timezone?: string
      next_run?: string
      created_at: string
      updated_at: string
    }>('/api/v1/reports/schedules', {
      project_id: projectId,
      ...schedule
    })
  }

  async getReportSchedules(projectId?: string): Promise<ApiResponse<Array<{
    id: string
    project_id: string
    report_type: 'summary' | 'detailed' | 'security' | 'performance' | 'compliance'
    format: 'pdf' | 'html' | 'json' | 'xml'
    cron_expression: string
    recipients?: string[]
    config?: Record<string, any>
    enabled: boolean
    timezone?: string
    next_run?: string
    created_at: string
    updated_at: string
  }>>> {
    const endpoint = projectId
      ? `/api/v1/reports/schedules?project_id=${projectId}`
      : '/api/v1/reports/schedules'
    return apiClient.get<Array<{
      id: string
      project_id: string
      report_type: 'summary' | 'detailed' | 'security' | 'performance' | 'compliance'
      format: 'pdf' | 'html' | 'json' | 'xml'
      cron_expression: string
      recipients?: string[]
      config?: Record<string, any>
      enabled: boolean
      timezone?: string
      next_run?: string
      created_at: string
      updated_at: string
    }>>(endpoint)
  }

  async updateReportSchedule(scheduleId: string, updates: {
    report_type?: 'summary' | 'detailed' | 'security' | 'performance' | 'compliance'
    format?: 'pdf' | 'html' | 'json' | 'xml'
    cron_expression?: string
    recipients?: string[]
    config?: Record<string, any>
    enabled?: boolean
    timezone?: string
  }): Promise<ApiResponse<{
    id: string
    project_id: string
    report_type: 'summary' | 'detailed' | 'security' | 'performance' | 'compliance'
    format: 'pdf' | 'html' | 'json' | 'xml'
    cron_expression: string
    recipients?: string[]
    config?: Record<string, any>
    enabled: boolean
    timezone?: string
    next_run?: string
    created_at: string
    updated_at: string
  }>> {
    return apiClient.put<{
      id: string
      project_id: string
      report_type: 'summary' | 'detailed' | 'security' | 'performance' | 'compliance'
      format: 'pdf' | 'html' | 'json' | 'xml'
      cron_expression: string
      recipients?: string[]
      config?: Record<string, any>
      enabled: boolean
      timezone?: string
      next_run?: string
      created_at: string
      updated_at: string
    }>(`/api/v1/reports/schedules/${scheduleId}`, updates)
  }

  async deleteReportSchedule(scheduleId: string): Promise<ApiResponse<void>> {
    return apiClient.delete<void>(`/api/v1/reports/schedules/${scheduleId}`)
  }

  // Report analytics
  async getReportAnalytics(projectId?: string, period?: 'day' | 'week' | 'month' | 'year'): Promise<ApiResponse<{
    total_reports: number
    reports_by_type: Record<string, number>
    reports_by_format: Record<string, number>
    average_generation_time: number
    success_rate: number
    popular_templates: Array<{
      template_id: string
      name: string
      usage_count: number
    }>
    generation_trends: Array<{
      date: string
      count: number
      average_time: number
    }>
  }>> {
    const params = new URLSearchParams()
    if (projectId) params.append('project_id', projectId)
    if (period) params.append('period', period)

    const endpoint = `/api/v1/reports/analytics${params.toString() ? `?${params.toString()}` : ''}`
    return apiClient.get<{
      total_reports: number
      reports_by_type: Record<string, number>
      reports_by_format: Record<string, number>
      average_generation_time: number
      success_rate: number
      popular_templates: Array<{
        template_id: string
        name: string
        usage_count: number
      }>
      generation_trends: Array<{
        date: string
        count: number
        average_time: number
      }>
    }>(endpoint)
  }

  // Report sharing
  async shareReport(reportId: string, recipients: string[], options?: {
    message?: string
    expires_in?: number // hours
    allow_download?: boolean
  }): Promise<ApiResponse<{
    share_id: string
    share_url: string
    expires_at: string
    recipients: string[]
  }>> {
    return apiClient.post<{
      share_id: string
      share_url: string
      expires_at: string
      recipients: string[]
    }>(`/api/v1/reports/${reportId}/share`, {
      recipients,
      ...options
    })
  }

  async getSharedReport(shareId: string): Promise<ApiResponse<Report>> {
    return apiClient.get<Report>(`/api/v1/reports/shared/${shareId}`)
  }

  // Report export
  async exportReportData(reportId: string, format: 'csv' | 'json' | 'xml' = 'json'): Promise<ApiResponse<Blob>> {
    return apiClient.get<Blob>(`/api/v1/reports/${reportId}/export?format=${format}`)
  }

  // Report preview
  async previewReport(projectId: string, options?: {
    report_type?: 'summary' | 'detailed' | 'security' | 'performance' | 'compliance'
    format?: 'html'
    sections?: string[]
  }): Promise<ApiResponse<{
    preview_url: string
    expires_in: number
    generated_at: string
  }>> {
    return apiClient.post<{
      preview_url: string
      expires_in: number
      generated_at: string
    }>('/api/v1/reports/preview', {
      project_id: projectId,
      ...options
    })
  }

  // Report validation
  async validateReportConfig(config: {
    report_type: 'summary' | 'detailed' | 'security' | 'performance' | 'compliance'
    format: 'pdf' | 'html' | 'json' | 'xml'
    sections?: string[]
    filters?: Record<string, any>
  }): Promise<ApiResponse<{
    valid: boolean
    errors: string[]
    warnings: string[]
    estimated_size: number
    estimated_time: number
  }>> {
    return apiClient.post<{
      valid: boolean
      errors: string[]
      warnings: string[]
      estimated_size: number
      estimated_time: number
    }>('/api/v1/reports/validate', config)
  }
}

// Create and export service instance
export const reportsService = new ReportsService()
export default reportsService
