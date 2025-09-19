/**
 * Unit tests for the GitHub Service
 * Tests GitHub integration and repository analysis
 */

import { githubService } from '@/services/githubService'
import { apiClient } from '@/services/api'
import { ApiException } from '@/types/api'

// Mock the API client
jest.mock('@/services/api', () => ({
  apiClient: {
    get: jest.fn(),
    post: jest.fn()
  }
}))

const mockApiClient = apiClient as jest.Mocked<typeof apiClient>

describe('GitHubService', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('validateRepoUrl', () => {
    it('should validate correct GitHub URLs', () => {
      const validUrls = [
        'https://github.com/user/repo',
        'https://github.com/user-name/repo-name',
        'https://github.com/user123/repo_name',
        'https://github.com/user/repo/'
      ]

      validUrls.forEach(url => {
        expect(githubService.validateRepoUrl(url)).toBe(true)
      })
    })

    it('should reject invalid URLs', () => {
      const invalidUrls = [
        'https://gitlab.com/user/repo',
        'https://github.com/user',
        'https://github.com/',
        'not-a-url',
        'https://github.com/user/repo/issues',
        'http://github.com/user/repo' // http instead of https
      ]

      invalidUrls.forEach(url => {
        expect(githubService.validateRepoUrl(url)).toBe(false)
      })
    })
  })

  describe('parseRepoUrl', () => {
    it('should parse GitHub URLs correctly', () => {
      const testCases = [
        {
          url: 'https://github.com/facebook/react',
          expected: { owner: 'facebook', repo: 'react' }
        },
        {
          url: 'https://github.com/microsoft/vscode.git',
          expected: { owner: 'microsoft', repo: 'vscode' }
        },
        {
          url: 'https://github.com/user-name/repo_name/',
          expected: { owner: 'user-name', repo: 'repo_name' }
        }
      ]

      testCases.forEach(({ url, expected }) => {
        const result = githubService.parseRepoUrl(url)
        expect(result).toEqual(expected)
      })
    })

    it('should return null for invalid URLs', () => {
      const invalidUrls = [
        'https://gitlab.com/user/repo',
        'not-a-url',
        'https://github.com/user'
      ]

      invalidUrls.forEach(url => {
        expect(githubService.parseRepoUrl(url)).toBeNull()
      })
    })
  })

  describe('analyzeRepository', () => {
    it('should start GitHub repository analysis', async () => {
      const mockResponse = {
        report_id: 'github-123',
        status: 'processing',
        message: 'GitHub analysis started'
      }

      mockApiClient.post.mockResolvedValue(mockResponse)

      const result = await githubService.analyzeRepository('https://github.com/user/repo')

      expect(mockApiClient.post).toHaveBeenCalledWith('/api/v1/analyze/github', {
        repo_url: 'https://github.com/user/repo'
      })
      expect(result).toEqual(mockResponse)
    })

    it('should handle API errors', async () => {
      mockApiClient.post.mockRejectedValue(new ApiException(400, 'Invalid repository'))

      await expect(
        githubService.analyzeRepository('https://github.com/invalid/repo')
      ).rejects.toThrow('Invalid repository')
    })
  })

  describe('getGitHubAnalysisResults', () => {
    it('should fetch GitHub analysis results', async () => {
      const mockResult = {
        report_id: 'github-123',
        status: 'completed' as const,
        repository: {
          name: 'test-repo',
          url: 'https://github.com/user/test-repo',
          language: 'JavaScript',
          stars: 100,
          forks: 25
        },
        project_id: 'proj-456',
        summary: {
          quality_score: 88,
          total_files: 50,
          total_lines: 3000,
          total_issues: 12
        }
      }

      mockApiClient.get.mockResolvedValue(mockResult)

      const result = await githubService.getGitHubAnalysisResults('github-123')

      expect(mockApiClient.get).toHaveBeenCalledWith('/api/v1/analyze/github-123/status')
      expect(result).toEqual(mockResult)
    })

    it('should return null for non-GitHub analysis', async () => {
      const mockResult = {
        report_id: 'regular-123',
        status: 'completed' as const,
        // Missing repository and project_id
      }

      mockApiClient.get.mockResolvedValue(mockResult)

      const result = await githubService.getGitHubAnalysisResults('regular-123')

      expect(result).toBeNull()
    })

    it('should handle API errors', async () => {
      mockApiClient.get.mockRejectedValue(new ApiException(404, 'Analysis not found'))

      const result = await githubService.getGitHubAnalysisResults('invalid-id')

      expect(result).toBeNull()
    })
  })

  describe('getTrendingRepos', () => {
    it('should fetch trending repositories', async () => {
      const mockRepos = {
        repositories: [
          {
            name: 'awesome-project',
            url: 'https://github.com/user/awesome-project',
            language: 'JavaScript',
            stars: 1500,
            forks: 200
          },
          {
            name: 'cool-library',
            url: 'https://github.com/dev/cool-library',
            language: 'TypeScript',
            stars: 800,
            forks: 100
          }
        ]
      }

      mockApiClient.get.mockResolvedValue(mockRepos)

      const result = await githubService.getTrendingRepos('javascript', 10)

      expect(mockApiClient.get).toHaveBeenCalledWith(
        '/api/v1/github/trending?language=javascript&limit=10'
      )
      expect(result).toEqual(mockRepos.repositories)
    })

    it('should handle empty language parameter', async () => {
      const mockRepos = { repositories: [] }
      mockApiClient.get.mockResolvedValue(mockRepos)

      await githubService.getTrendingRepos('', 5)

      expect(mockApiClient.get).toHaveBeenCalledWith(
        '/api/v1/github/trending?language=&limit=5'
      )
    })

    it('should return empty array on error', async () => {
      mockApiClient.get.mockRejectedValue(new ApiException(503, 'Service unavailable'))

      const result = await githubService.getTrendingRepos('python', 10)

      expect(result).toEqual([])
    })
  })

  describe('formatRepoName', () => {
    it('should format repository names correctly', () => {
      const testCases = [
        {
          repository: {
            name: 'react',
            url: 'https://github.com/facebook/react',
            language: 'JavaScript',
            stars: 1000,
            forks: 500
          },
          expected: 'facebook/react'
        },
        {
          repository: {
            name: 'invalid-name',
            url: 'https://invalid-url',
            language: 'JavaScript',
            stars: 0,
            forks: 0
          },
          expected: 'invalid-name'
        }
      ]

      testCases.forEach(({ repository, expected }) => {
        const result = githubService.formatRepoName(repository)
        expect(result).toBe(expected)
      })
    })
  })

  describe('getRepoStats', () => {
    it('should return formatted repository statistics', () => {
      const repository = {
        name: 'test-repo',
        url: 'https://github.com/user/test-repo',
        language: 'TypeScript',
        stars: 1500,
        forks: 250
      }

      const result = githubService.getRepoStats(repository)

      expect(result).toEqual([
        { label: 'Language', value: 'TypeScript' },
        { label: 'Stars', value: '1,500' },
        { label: 'Forks', value: '250' }
      ])
    })

    it('should handle missing language', () => {
      const repository = {
        name: 'test-repo',
        url: 'https://github.com/user/test-repo',
        language: '',
        stars: 100,
        forks: 20
      }

      const result = githubService.getRepoStats(repository)

      expect(result[0]).toEqual({ label: 'Language', value: 'Unknown' })
    })
  })
})