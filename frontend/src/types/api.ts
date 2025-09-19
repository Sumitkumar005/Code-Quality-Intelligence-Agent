// Core API types and interfaces for CQIA frontend

export interface AnalysisResult {
  report_id: string
  status: 'processing' | 'completed' | 'error'
  progress?: number
  message?: string
  summary?: AnalysisSummary
  issues?: Issue[]
  metrics?: QualityMetrics
  trends?: TrendData[]
  project_id?: string
  repository?: Repository
}

export interface AnalysisSummary {
  quality_score: number
  total_files: number
  total_lines: number
  total_issues: number
}

export interface Issue {
  id: string
  type: 'Security' | 'Performance' | 'Quality' | 'Documentation' | 'Testing'
  severity: 'High' | 'Medium' | 'Low'
  message: string
  file: string
  line: number
  suggestion?: string
}

export interface QualityMetrics {
  test_coverage: number
  code_duplication: number
  technical_debt_hours: number
  complexity_distribution: {
    low: number
    medium: number
    high: number
  }
}

export interface TrendData {
  date: string
  quality_score: number
  issue_count: number
  test_coverage: number
}

export interface Repository {
  name: string
  url: string
  language: string
  stars: number
  forks: number
}

export interface ComparisonData {
  projects: Array<{
    project_id: string
    name: string
    quality_score: number
    issue_count: number
    last_analysis: string
  }>
  comparison_metrics: {
    avg_quality_score: number
    total_issues: number
    best_project: string
    worst_project: string
  }
}

// API Request types
export interface AnalyzeRequest {
  input: string
  data?: {
    files?: Record<string, string>
  }
}

export interface QuestionRequest {
  question: string
  report_id: string
}

export interface GitHubAnalyzeRequest {
  repo_url: string
}

export interface ProjectComparisonRequest {
  project_ids: string[]
}

// API Response types
export interface AnalyzeResponse {
  report_id: string
  status: string
  message: string
}

export interface QuestionResponse {
  answer: string
  report_id: string
}

export interface QualityTrendsResponse {
  project_id: string
  trends: TrendData[]
}

export interface GitHubAnalysisResponse extends AnalysisResult {
  repository: Repository
  project_id: string
}

// Error types
export interface ApiError {
  message: string
  status: number
  code?: string
}

export class ApiException extends Error {
  constructor(
    public status: number,
    public message: string,
    public code?: string
  ) {
    super(message)
    this.name = 'ApiException'
  }
}