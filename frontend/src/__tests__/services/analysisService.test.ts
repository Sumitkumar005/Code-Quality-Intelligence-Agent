/**
 * Unit tests for the Analysis Service
 * Tests API integration and data transformation
 */

import { analysisService } from '@/services/analysisService'
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

describe('AnalysisService', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('startAnalysis', () => {
    it('should start analysis and return report ID', async () => {
      const mockResponse = {
        report_id: 'test-123',
        status: 'processing',
        message: 'Analysis started'
      }

      mockApiClient.post.mockResolvedValue(mockResponse)

      const request = {
        input: 'test',
        data: { files: { 'test.js': 'console.log("test")' } }
      }

      const result = await analysisService.startAnalysis(request)

      expect(mockApiClient.post).toHaveBeenCalledWith('/api/v1/analyze', request)
      expect(result).toEqual(mockResponse)
    })

    it('should handle API errors', async () => {
      mockApiClient.post.mockRejectedValue(new ApiException(500, 'Server error'))

      const request = {
        input: 'test',
        data: { files: {} }
      }

      await expect(analysisService.startAnalysis(request)).rejects.toThrow('Server error')
    })
  })

  describe('getAnalysisStatus', () => {
    it('should fetch analysis status', async () => {
      const mockAnalysis = {
        report_id: 'test-123',
        status: 'completed' as const,
        summary: {
          quality_score: 85,
          total_files: 10,
          total_lines: 1000,
          total_issues: 5
        },
        issues: []
      }

      mockApiClient.get.mockResolvedValue(mockAnalysis)

      const result = await analysisService.getAnalysisStatus('test-123')

      expect(mockApiClient.get).toHaveBeenCalledWith('/api/v1/analyze/test-123/status')
      expect(result).toEqual(mockAnalysis)
    })

    it('should handle not found errors', async () => {
      mockApiClient.get.mockRejectedValue(new ApiException(404, 'Report not found'))

      await expect(analysisService.getAnalysisStatus('invalid-id')).rejects.toThrow('Report not found')
    })
  })

  describe('getQualityMetrics', () => {
    it('should return metrics when analysis is completed', async () => {
      const mockAnalysis = {
        report_id: 'test-123',
        status: 'completed' as const,
        metrics: {
          test_coverage: 80,
          code_duplication: 15,
          technical_debt_hours: 3.5,
          complexity_distribution: {
            low: 60,
            medium: 30,
            high: 10
          }
        }
      }

      mockApiClient.get.mockResolvedValue(mockAnalysis)

      const result = await analysisService.getQualityMetrics('test-123')

      expect(result).toEqual(mockAnalysis.metrics)
    })

    it('should return null when analysis is not completed', async () => {
      const mockAnalysis = {
        report_id: 'test-123',
        status: 'processing' as const
      }

      mockApiClient.get.mockResolvedValue(mockAnalysis)

      const result = await analysisService.getQualityMetrics('test-123')

      expect(result).toBeNull()
    })

    it('should handle API errors and re-throw them', async () => {
      mockApiClient.get.mockRejectedValue(new ApiException(500, 'Server error'))

      await expect(analysisService.getQualityMetrics('test-123')).rejects.toThrow('Server error')
    })
  })

  describe('getIssues', () => {
    it('should return transformed issues when analysis is completed', async () => {
      const mockAnalysis = {
        report_id: 'test-123',
        status: 'completed' as const,
        issues: [
          {
            type: 'security',
            severity: 'High',
            message: 'SQL injection',
            file: 'db.js',
            line: 10
          }
        ]
      }

      mockApiClient.get.mockResolvedValue(mockAnalysis)

      const result = await analysisService.getIssues('test-123')

      expect(result).toHaveLength(1)
      expect(result[0]).toMatchObject({
        type: 'Security',
        severity: 'High',
        message: 'SQL injection',
        file: 'db.js',
        line: 10
      })
    })

    it('should return empty array when no issues found', async () => {
      const mockAnalysis = {
        report_id: 'test-123',
        status: 'completed' as const,
        issues: []
      }

      mockApiClient.get.mockResolvedValue(mockAnalysis)

      const result = await analysisService.getIssues('test-123')

      expect(result).toEqual([])
    })
  })

  describe('askQuestion', () => {
    it('should send question and return answer', async () => {
      const mockResponse = {
        answer: 'You have 3 security issues that need attention.',
        report_id: 'test-123'
      }

      mockApiClient.post.mockResolvedValue(mockResponse)

      const result = await analysisService.askQuestion('What security issues do I have?', 'test-123')

      expect(mockApiClient.post).toHaveBeenCalledWith('/api/v1/qa/ask', {
        question: 'What security issues do I have?',
        report_id: 'test-123'
      })
      expect(result).toBe(mockResponse.answer)
    })

    it('should handle chat service errors gracefully', async () => {
      mockApiClient.post.mockRejectedValue(new ApiException(503, 'Chat service unavailable'))

      const result = await analysisService.askQuestion('Test question', 'test-123')

      expect(result).toBe('Sorry, I could not process your question at this time.')
    })
  })

  describe('calculateMetricsFromAnalysis', () => {
    it('should calculate metrics from analysis data', () => {
      const mockAnalysis = {
        report_id: 'test-123',
        status: 'completed' as const,
        summary: {
          quality_score: 85,
          total_files: 10,
          total_lines: 1000,
          total_issues: 6
        },
        issues: [
          { severity: 'High', type: 'Security' },
          { severity: 'High', type: 'Security' },
          { severity: 'Medium', type: 'Performance' },
          { severity: 'Medium', type: 'Performance' },
          { severity: 'Low', type: 'Quality' },
          { severity: 'Low', type: 'Quality' }
        ]
      }

      const result = analysisService.calculateMetricsFromAnalysis(mockAnalysis as any)

      expect(result).toBeDefined()
      expect(result?.technical_debt_hours).toBe(5) // 2*2 + 2*1 + 2*0.5
      expect(result?.complexity_distribution.high).toBe(33) // 2/6 * 100
      expect(result?.complexity_distribution.medium).toBe(33) // 2/6 * 100
      expect(result?.complexity_distribution.low).toBe(33) // 2/6 * 100
    })

    it('should handle analysis with no issues', () => {
      const mockAnalysis = {
        report_id: 'test-123',
        status: 'completed' as const,
        summary: {
          quality_score: 95,
          total_files: 5,
          total_lines: 500,
          total_issues: 0
        },
        issues: []
      }

      const result = analysisService.calculateMetricsFromAnalysis(mockAnalysis as any)

      expect(result).toBeDefined()
      expect(result?.technical_debt_hours).toBe(0)
      expect(result?.test_coverage).toBe(85) // Default when no issues
      expect(result?.complexity_distribution.low).toBe(100)
      expect(result?.complexity_distribution.medium).toBe(0)
      expect(result?.complexity_distribution.high).toBe(0)
    })

    it('should return null for incomplete analysis', () => {
      const mockAnalysis = {
        report_id: 'test-123',
        status: 'processing' as const
      }

      const result = analysisService.calculateMetricsFromAnalysis(mockAnalysis as any)

      expect(result).toBeNull()
    })
  })

  describe('getQualityTrends', () => {
    it('should fetch quality trends for a project', async () => {
      const mockTrends = {
        project_id: 'proj-123',
        trends: [
          {
            date: '2024-01-01',
            quality_score: 80,
            issue_count: 10,
            test_coverage: 75
          },
          {
            date: '2024-01-02',
            quality_score: 85,
            issue_count: 8,
            test_coverage: 78
          }
        ]
      }

      mockApiClient.get.mockResolvedValue(mockTrends)

      const result = await analysisService.getQualityTrends('proj-123', 30)

      expect(mockApiClient.get).toHaveBeenCalledWith('/api/v1/analytics/trends/proj-123?days=30')
      expect(result).toEqual(mockTrends.trends)
    })

    it('should return empty array on error', async () => {
      mockApiClient.get.mockRejectedValue(new ApiException(404, 'Project not found'))

      const result = await analysisService.getQualityTrends('invalid-proj', 30)

      expect(result).toEqual([])
    })
  })
})