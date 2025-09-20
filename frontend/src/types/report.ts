// Report Types
export interface Report extends BaseEntity {
  project_id: string
  analysis_id?: string
  title: string
  description?: string
  report_type: ReportType
  format: ReportFormat
  status: Status
  file_path?: string
  file_url?: string
  file_size?: number
  metadata: Record<string, any>
  generated_at?: string
  expires_at?: string
  project?: Project
  analysis?: Analysis
  created_by?: User
}

export interface ReportTemplate {
  id: string
  name: string
  description: string
  type: ReportType
  format: ReportFormat
  sections: ReportSection[]
  settings: Record<string, any>
  is_default: boolean
  created_at: string
  updated_at: string
}

export interface ReportSection {
  id: string
  type: SectionType
  title: string
  description?: string
  order: number
  enabled: boolean
  settings: Record<string, any>
  data?: any
}

export interface ReportGenerationRequest {
  project_id: string
  analysis_id?: string
  template_id?: string
  title: string
  description?: string
  report_type: ReportType
  format: ReportFormat
  sections?: string[]
  include_charts: boolean
  include_raw_data: boolean
  filters?: Record<string, any>
  custom_settings?: Record<string, any>
}

export interface ReportExportOptions {
  format: ReportFormat
  include_charts: boolean
  include_raw_data: boolean
  sections: string[]
  filters?: Record<string, any>
  custom_settings?: Record<string, any>
}

export interface ReportData {
  summary: ReportSummary
  sections: ReportSectionData[]
  charts: ChartData[]
  metadata: Record<string, any>
}

export interface ReportSummary {
  title: string
  description?: string
  generated_at: string
  project: {
    name: string
    description?: string
  }
  analysis: {
    id: string
    type: string
    completed_at: string
  }
  metrics: {
    total_issues: number
    critical_issues: number
    quality_score: number
    coverage: number
  }
}

export interface ReportSectionData {
  id: string
  type: SectionType
  title: string
  content: any
  charts?: ChartData[]
  tables?: TableData[]
  metadata?: Record<string, any>
}

export interface ChartData {
  id: string
  type: ChartType
  title: string
  data: any[]
  config: Record<string, any>
  width?: number
  height?: number
}

export interface TableData {
  id: string
  title: string
  headers: string[]
  rows: any[][]
  pagination?: {
    page: number
    per_page: number
    total: number
  }
}

// Enums and Types
export type ReportType =
  | 'comprehensive'
  | 'security'
  | 'performance'
  | 'quality'
  | 'compliance'
  | 'custom'

export type ReportFormat =
  | 'pdf'
  | 'html'
  | 'json'
  | 'xml'
  | 'csv'
  | 'excel'

export type SectionType =
  | 'summary'
  | 'issues'
  | 'metrics'
  | 'charts'
  | 'files'
  | 'dependencies'
  | 'security'
  | 'performance'
  | 'complexity'
  | 'duplication'
  | 'documentation'
  | 'tests'
  | 'recommendations'
  | 'custom'

export type ChartType =
  | 'bar'
  | 'line'
  | 'pie'
  | 'doughnut'
  | 'area'
  | 'scatter'
  | 'heatmap'
  | 'treemap'
  | 'gauge'

// Import types from other modules
import { BaseEntity, Status } from './common'
import { Project } from './project'
import { Analysis } from './analysis'
import { User } from './common'
