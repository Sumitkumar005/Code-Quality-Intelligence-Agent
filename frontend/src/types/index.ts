// Export all types from this module
export * from './api'
export * from './auth'
export * from './common'
export * from './project'
export * from './analysis'
export * from './report'
export * from './ui'

// Re-export commonly used types for convenience
export type {
  User,
  Organization,
  Project,
  Analysis,
  Report,
  Issue,
  QualityMetrics,
  ApiResponse,
  ApiError,
  NavItem,
  TableProps,
  ModalProps,
  FormProps,
  ButtonProps,
  InputProps,
  SelectProps,
} from './common'

export type {
  LoginCredentials,
  RegisterData,
  AuthTokens,
  AuthState,
} from './auth'

export type {
  CreateProjectData,
  UpdateProjectData,
  ProjectSettings,
  ProjectStats,
} from './project'

export type {
  AnalysisResults,
  AnalysisSummary,
  Issue as AnalysisIssue,
  QualityMetrics as AnalysisQualityMetrics,
  FileAnalysis,
  DependencyAnalysis,
  SecurityAnalysis,
  PerformanceAnalysis,
  ComplexityAnalysis,
  DuplicationAnalysis,
  DocumentationAnalysis,
  TestAnalysis,
} from './analysis'

export type {
  ReportTemplate,
  ReportGenerationRequest,
  ReportExportOptions,
  ReportData,
  ReportSummary,
  ReportSectionData,
  ChartData,
  TableData,
} from './report'
