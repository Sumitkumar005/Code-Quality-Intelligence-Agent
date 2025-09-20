// Analysis Types
export interface Analysis extends BaseEntity {
  project_id: string
  status: Status
  analysis_type: 'full' | 'incremental' | 'security' | 'performance' | 'custom'
  progress: number
  results: AnalysisResults
  metadata: Record<string, any>
  started_at: string
  completed_at?: string
  duration?: number
  project?: Project
}

export interface AnalysisResults {
  summary: AnalysisSummary
  issues: Issue[]
  metrics: QualityMetrics
  files: FileAnalysis[]
  dependencies: DependencyAnalysis
  security: SecurityAnalysis
  performance: PerformanceAnalysis
  complexity: ComplexityAnalysis
  duplication: DuplicationAnalysis
  documentation: DocumentationAnalysis
  tests: TestAnalysis
}

export interface AnalysisSummary {
  total_files: number
  analyzed_files: number
  total_lines: number
  code_lines: number
  comment_lines: number
  blank_lines: number
  complexity_score: number
  maintainability_index: number
  quality_score: number
  issues_count: number
  critical_issues: number
  high_issues: number
  medium_issues: number
  low_issues: number
  info_issues: number
}

export interface Issue {
  id: string
  type: IssueType
  category: IssueCategory
  severity: Severity
  priority: Priority
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
  created_at: string
  analysis_id: string
}

export interface QualityMetrics {
  maintainability: number
  reliability: number
  security: number
  performance: number
  overall: number
  trends: MetricTrend[]
}

export interface FileAnalysis {
  file_path: string
  language: string
  lines_of_code: number
  complexity: number
  maintainability_index: number
  issues_count: number
  issues: Issue[]
  coverage?: number
  last_modified: string
}

export interface DependencyAnalysis {
  total_dependencies: number
  outdated_dependencies: number
  vulnerable_dependencies: number
  dependencies: Dependency[]
  recommendations: string[]
}

export interface SecurityAnalysis {
  vulnerabilities: Vulnerability[]
  security_score: number
  risk_level: 'low' | 'medium' | 'high' | 'critical'
  recommendations: string[]
}

export interface PerformanceAnalysis {
  performance_score: number
  bottlenecks: PerformanceIssue[]
  recommendations: string[]
  metrics: PerformanceMetrics
}

export interface ComplexityAnalysis {
  complexity_score: number
  complex_functions: ComplexFunction[]
  recommendations: string[]
}

export interface DuplicationAnalysis {
  duplication_rate: number
  duplicated_blocks: DuplicatedBlock[]
  recommendations: string[]
}

export interface DocumentationAnalysis {
  documentation_score: number
  coverage: number
  missing_docs: string[]
  recommendations: string[]
}

export interface TestAnalysis {
  test_coverage: number
  test_count: number
  test_types: Record<string, number>
  recommendations: string[]
}

// Supporting Types
export interface Dependency {
  name: string
  version: string
  latest_version: string
  is_outdated: boolean
  is_vulnerable: boolean
  vulnerabilities?: Vulnerability[]
  license?: string
  description?: string
}

export interface Vulnerability {
  id: string
  severity: Severity
  title: string
  description: string
  cve?: string
  cvss_score?: number
  affected_versions: string[]
  fixed_versions: string[]
  references: string[]
}

export interface PerformanceIssue {
  type: string
  severity: Severity
  file_path: string
  line_number: number
  description: string
  impact: string
  suggestion: string
}

export interface PerformanceMetrics {
  execution_time: number
  memory_usage: number
  cpu_usage: number
  network_requests: number
}

export interface ComplexFunction {
  name: string
  file_path: string
  complexity: number
  lines_of_code: number
  parameters: number
  cyclomatic_complexity: number
}

export interface DuplicatedBlock {
  file_path: string
  start_line: number
  end_line: number
  duplicated_in: string[]
  content: string
}

export interface MetricTrend {
  metric: string
  date: string
  value: number
  change: number
  change_percent: number
}

// Enums
export type IssueType =
  | 'bug'
  | 'vulnerability'
  | 'code_smell'
  | 'duplication'
  | 'documentation'
  | 'performance'
  | 'security'
  | 'maintainability'
  | 'reliability'
  | 'test'

export type IssueCategory =
  | 'syntax'
  | 'logic'
  | 'performance'
  | 'security'
  | 'maintainability'
  | 'documentation'
  | 'testing'
  | 'dependency'
  | 'configuration'
  | 'architecture'

// Import types from common
import { BaseEntity, Status, Severity, Priority } from './common'
import { Project } from './project'
