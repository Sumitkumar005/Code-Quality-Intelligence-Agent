// Export all services for easy importing

export { apiClient, ApiClient } from './api'
export { analysisService, AnalysisService } from './analysisService'
export { githubService, GitHubService } from './githubService'

// Re-export types for convenience
export type {
  AnalysisResult,
  Issue,
  QualityMetrics,
  TrendData,
  Repository,
  ComparisonData,
  ApiError,
  AnalyzeRequest,
  AnalyzeResponse,
} from '@/types/api'