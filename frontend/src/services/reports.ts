// Reports Service
import { apiClient } from './api-client-working'
import {
  Report,
  ReportTemplate,
  ReportConfig,
  ReportData,
  ReportExport,
  DashboardData,
  AnalyticsData,
  ReportSchedule,
  ReportFilter
} from '../types/report'
import { PaginationParams } from '../types/common-corrected'
import { ApiResponse } from '../types/api-corrected'

export class ReportsService {
  // Report CRUD operations
  async getReports(params?: PaginationParams): Promise<ApiResponse<Report[]>> {
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

  async getReport(reportId: string): Promise<ApiResponse<Report>> {
    return apiClient.get<Report>(`/api/v1/reports/${reportId}`)
  }

  async createReport(config: ReportConfig): Promise<ApiResponse<Report>> {
    return apiClient.post<Report>('/api/v1/reports', config)
  }

  async updateReport(reportId: string, config: Partial<ReportConfig>): Promise<ApiResponse<Report>> {
    return apiClient.put<Report>(`/api/v1/reports/${reportId}`, config)
  }

  async deleteReport(reportId: string): Promise<ApiResponse<void>> {
    return apiClient.delete<void>(`/api/v1/reports/${reportId}`)
  }

  // Report generation
  async generateReport(config: ReportConfig): Promise<ApiResponse<Report>> {
    return apiClient.post<Report>('/api/v1/reports/generate', config)
  }

  async generateProjectReport(projectId: string, config?: Partial<ReportConfig>): Promise<ApiResponse<Report>> {
    return apiClient.post<Report>(`/api/v1/projects/${projectId}/reports`, config || {})
  }

  async generateAnalysisReport(analysisId: string, config?: Partial<ReportConfig>): Promise<ApiResponse<Report>> {
    return apiClient.post<Report>(`/api/v1/analyses/${analysisId}/reports`, config || {})
  }

  // Report templates
  async getReportTemplates(): Promise<ApiResponse<ReportTemplate[]>> {
    return apiClient.get<ReportTemplate[]>('/api/v1/reports/templates')
  }

  async getReportTemplate(templateId: string): Promise<ApiResponse<ReportTemplate>> {
    return apiClient.get<ReportTemplate>(`/api/v1/reports/templates/${templateId}`)
  }

  async createReportTemplate(template: Omit<ReportTemplate, 'id' | 'created_at' | 'updated_at'>): Promise<ApiResponse<ReportTemplate>> {
    return apiClient.post<ReportTemplate>('/api/v1/reports/templates', template)
  }

  async updateReportTemplate(templateId: string, template: Partial<ReportTemplate>): Promise<ApiResponse<ReportTemplate>> {
    return apiClient.put<ReportTemplate>(`/api/v1/reports/templates/${templateId}`, template)
  }

  async deleteReportTemplate(templateId: string): Promise<ApiResponse<void>> {
    return apiClient.delete<void>(`/api/v1/reports/templates/${templateId}`)
  }

  // Report data and content
  async getReportData(reportId: string): Promise<ApiResponse<ReportData>> {
    return apiClient.get<ReportData>(`/api/v1/reports/${reportId}/data`)
  }

  async getReportContent(reportId: string, format: 'html' | 'pdf' | 'json' = 'html'): Promise<ApiResponse<Blob>> {
    return apiClient.get<Blob>(`/api/v1/reports/${reportId}/content?format=${format}`, {
      responseType: 'blob'
    })
  }

  async downloadReport(reportId: string, format: 'pdf' | 'html' | 'json' | 'csv' | 'xml' = 'pdf'): Promise<ApiResponse<Blob>> {
    return apiClient.get<Blob>(`/api/v1/reports/${reportId}/download?format=${format}`, {
      responseType: 'blob'
    })
  }

  // Report export
  async exportReport(reportId: string, config: ReportExport): Promise<ApiResponse<Blob>> {
    return apiClient.post<Blob>('/api/v1/reports/export', { report_id: reportId, ...config }, {
      responseType: 'blob'
    })
  }

  async bulkExportReports(reportIds: string[], format: string): Promise<ApiResponse<Blob>> {
    return apiClient.post<Blob>('/api/v1/reports/bulk-export', { report_ids: reportIds, format }, {
      responseType: 'blob'
    })
  }

  // Report scheduling
  async getReportSchedules(): Promise<ApiResponse<ReportSchedule[]>> {
    return apiClient.get<ReportSchedule[]>('/api/v1/reports/schedules')
  }

  async createReportSchedule(schedule: Omit<ReportSchedule, 'id' | 'created_at'>): Promise<ApiResponse<ReportSchedule>> {
    return apiClient.post<ReportSchedule>('/api/v1/reports/schedules', schedule)
  }

  async updateReportSchedule(scheduleId: string, schedule: Partial<ReportSchedule>): Promise<ApiResponse<ReportSchedule>> {
    return apiClient.put<ReportSchedule>(`/api/v1/reports/schedules/${scheduleId}`, schedule)
  }

  async deleteReportSchedule(scheduleId: string): Promise<ApiResponse<void>> {
    return apiClient.delete<void>(`/api/v1/reports/schedules/${scheduleId}`)
  }

  async toggleReportSchedule(scheduleId: string, enabled: boolean): Promise<ApiResponse<ReportSchedule>> {
    return apiClient.patch<ReportSchedule>(`/api/v1/reports/schedules/${scheduleId}/toggle`, { enabled })
  }

  // Dashboard and analytics
  async getDashboardData(projectId?: string): Promise<ApiResponse<DashboardData>> {
    const endpoint = projectId
      ? `/api/v1/analytics/dashboard?project_id=${projectId}`
      : '/api/v1/analytics/dashboard'
    return apiClient.get<DashboardData>(endpoint)
  }

  async getAnalyticsData(filters?: ReportFilter): Promise<ApiResponse<AnalyticsData>> {
    const queryParams = new URLSearchParams()
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, String(value))
        }
      })
    }

    const endpoint = `/api/v1/analytics/data${queryParams.toString() ? `?${queryParams.toString()}` : ''}`
    return apiClient.get<AnalyticsData>(endpoint)
  }

  async getQualityTrends(projectId: string, days: number = 90): Promise<ApiResponse<{
    date: string
    score: number
    issues: number
    coverage: number
  }[]>> {
    return apiClient.get<{
      date: string
      score: number
      issues: number
      coverage: number
    }[]>(`/api/v1/analytics/trends?project_id=${projectId}&days=${days}`)
  }

  async getProjectMetrics(projectId: string): Promise<ApiResponse<{
    total_analyses: number
    total_issues: number
    avg_quality_score: number
    trend_direction: 'up' | 'down' | 'stable'
    last_analysis_date: string
  }>> {
    return apiClient.get<{
      total_analyses: number
      total_issues: number
      avg_quality_score: number
      trend_direction: 'up' | 'down' | 'stable'
      last_analysis_date: string
    }>(`/api/v1/analytics/project-metrics?project_id=${projectId}`)
  }

  // Report sharing
  async shareReport(reportId: string, emails: string[], message?: string): Promise<ApiResponse<void>> {
    return apiClient.post<void>('/api/v1/reports/share', {
      report_id: reportId,
      emails,
      message
    })
  }

  async getSharedReports(): Promise<ApiResponse<Report[]>> {
    return apiClient.get<Report[]>('/api/v1/reports/shared')
  }

  async revokeReportAccess(reportId: string, userId: string): Promise<ApiResponse<void>> {
    return apiClient.post<void>(`/api/v1/reports/${reportId}/revoke`, { user_id: userId })
  }

  // Report filters and search
  async searchReports(query: string, filters?: ReportFilter): Promise<ApiResponse<Report[]>> {
    const params = new URLSearchParams({ q: query })
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        params.append(`filter_${key}`, String(value))
      })
    }
    return apiClient.get<Report[]>(`/api/v1/reports/search?${params.toString()}`)
  }

  // Report validation
  async validateReportConfig(config: ReportConfig): Promise<ApiResponse<{
    valid: boolean
    errors: string[]
    warnings: string[]
  }>> {
    return apiClient.post<{
      valid: boolean
      errors: string[]
      warnings: string[]
    }>('/api/v1/reports/validate', config)
  }

  // Report statistics
  async getReportStats(): Promise<ApiResponse<{
    total_reports: number
    reports_this_month: number
    most_used_templates: string[]
    avg_generation_time: number
  }>> {
    return apiClient.get<{
      total_reports: number
      reports_this_month: number
      most_used_templates: string[]
      avg_generation_time: number
    }>('/api/v1/reports/stats')
  }
}

// Create and export service instance
export const reportsService = new ReportsService()
export default reportsService
