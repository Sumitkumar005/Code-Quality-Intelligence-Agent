// GitHub service for repository analysis and integration

import { apiClient } from './api'
import {
  AnalysisResult,
  Repository,
  GitHubAnalyzeRequest,
  AnalyzeResponse,
  GitHubAnalysisResponse,
} from '@/types/api'

export class GitHubService {
  // Analyze a GitHub repository
  async analyzeRepository(repoUrl: string): Promise<AnalyzeResponse> {
    const request: GitHubAnalyzeRequest = { repo_url: repoUrl }
    return apiClient.post<AnalyzeResponse>('/api/v1/analyze/github', request)
  }

  // Get GitHub analysis results
  async getGitHubAnalysisResults(reportId: string): Promise<GitHubAnalysisResponse | null> {
    try {
      const result = await apiClient.get<GitHubAnalysisResponse>(`/api/v1/analyze/${reportId}/status`)
      
      // Ensure it's a GitHub analysis result
      if (result.repository && result.project_id) {
        return result
      }
      
      return null
    } catch (error) {
      console.error('Failed to get GitHub analysis results:', error)
      return null
    }
  }

  // Get trending repositories
  async getTrendingRepos(language: string = '', limit: number = 10): Promise<Repository[]> {
    try {
      const response = await apiClient.get<{ repositories: Repository[] }>(
        `/api/v1/github/trending?language=${encodeURIComponent(language)}&limit=${limit}`
      )
      return response.repositories || []
    } catch (error) {
      console.error('Failed to get trending repositories:', error)
      return []
    }
  }

  // Validate GitHub repository URL
  validateRepoUrl(url: string): boolean {
    const githubUrlPattern = /^https:\/\/github\.com\/[a-zA-Z0-9_.-]+\/[a-zA-Z0-9_.-]+\/?$/
    return githubUrlPattern.test(url)
  }

  // Extract owner and repo name from GitHub URL
  parseRepoUrl(url: string): { owner: string; repo: string } | null {
    const match = url.match(/github\.com\/([a-zA-Z0-9_.-]+)\/([a-zA-Z0-9_.-]+)/)
    if (match) {
      return {
        owner: match[1],
        repo: match[2].replace(/\.git$/, '') // Remove .git suffix if present
      }
    }
    return null
  }

  // Format repository display name
  formatRepoName(repository: Repository): string {
    const parsed = this.parseRepoUrl(repository.url)
    if (parsed) {
      return `${parsed.owner}/${parsed.repo}`
    }
    return repository.name
  }

  // Get repository statistics summary
  getRepoStats(repository: Repository): Array<{ label: string; value: string | number }> {
    return [
      { label: 'Language', value: repository.language || 'Unknown' },
      { label: 'Stars', value: repository.stars.toLocaleString() },
      { label: 'Forks', value: repository.forks.toLocaleString() },
    ]
  }
}

// Create singleton instance
export const githubService = new GitHubService()