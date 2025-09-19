/**
 * Unit tests for analysis data hooks
 * Tests custom hooks for data fetching and state management
 */

import { renderHook, waitFor } from '@testing-library/react'
import { useAnalysisData, useQualityMetrics, useIssues, useAnalysisChat } from '@/hooks/useAnalysisData'
import { analysisService } from '@/services'

// Mock the analysis service
jest.mock('@/services', () => ({
  analysisService: {
    getAnalysisStatus: jest.fn(),
    getQualityMetrics: jest.fn(),
    getIssues: jest.fn(),
    askQuestion: jest.fn()
  }
}))

const mockAnalysisService = analysisService as jest.Mocked<typeof analysisService>

describe('Analysis Data Hooks', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('useAnalysisData', () => {
    it('should fetch analysis data successfully', async () => {
      const mockAnalysis = {
        report_id: 'test-123',
        status: 'completed' as const,
        summary: {
          quality_score: 85,
          total_files: 10,
          total_lines: 1000,
          total_issues: 5
        }
      }

      mockAnalysisService.getAnalysisStatus.mockResolvedValue(mockAnalysis)

      const { result } = renderHook(() => useAnalysisData('test-123'))

      expect(result.current.loading).toBe(true)
      expect(result.current.data).toBeNull()

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
        expect(result.current.data).toEqual(mockAnalysis)
        expect(result.current.error).toBeNull()
      })
    })

    it('should handle null report ID', () => {
      const { result } = renderHook(() => useAnalysisData(null))

      expect(result.current.loading).toBe(false)
      expect(result.current.data).toBeNull()
      expect(result.current.error).toBeNull()
    })

    it('should handle API errors', async () => {
      mockAnalysisService.getAnalysisStatus.mockRejectedValue(new Error('API Error'))

      const { result } = renderHook(() => useAnalysisData('test-123'))

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
        expect(result.current.data).toBeNull()
        expect(result.current.error).toBe('API Error')
      })
    })

    it('should update when report ID changes', async () => {
      const mockAnalysis1 = { report_id: 'test-1', status: 'completed' as const }
      const mockAnalysis2 = { report_id: 'test-2', status: 'completed' as const }

      mockAnalysisService.getAnalysisStatus
        .mockResolvedValueOnce(mockAnalysis1)
        .mockResolvedValueOnce(mockAnalysis2)

      const { result, rerender } = renderHook(
        ({ reportId }) => useAnalysisData(reportId),
        { initialProps: { reportId: 'test-1' } }
      )

      await waitFor(() => {
        expect(result.current.data).toEqual(mockAnalysis1)
      })

      rerender({ reportId: 'test-2' })

      await waitFor(() => {
        expect(result.current.data).toEqual(mockAnalysis2)
      })

      expect(mockAnalysisService.getAnalysisStatus).toHaveBeenCalledTimes(2)
    })
  })

  describe('useQualityMetrics', () => {
    it('should fetch quality metrics successfully', async () => {
      const mockMetrics = {
        test_coverage: 80,
        code_duplication: 15,
        technical_debt_hours: 3.5,
        complexity_distribution: {
          low: 60,
          medium: 30,
          high: 10
        }
      }

      mockAnalysisService.getQualityMetrics.mockResolvedValue(mockMetrics)

      const { result } = renderHook(() => useQualityMetrics('test-123'))

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
        expect(result.current.metrics).toEqual(mockMetrics)
        expect(result.current.error).toBeNull()
      })
    })

    it('should handle null metrics', async () => {
      mockAnalysisService.getQualityMetrics.mockResolvedValue(null)

      const { result } = renderHook(() => useQualityMetrics('test-123'))

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
        expect(result.current.metrics).toBeNull()
        expect(result.current.error).toBeNull()
      })
    })
  })

  describe('useIssues', () => {
    it('should fetch issues successfully', async () => {
      const mockIssues = [
        {
          id: 'issue-1',
          type: 'Security' as const,
          severity: 'High' as const,
          message: 'SQL injection',
          file: 'db.js',
          line: 10
        },
        {
          id: 'issue-2',
          type: 'Performance' as const,
          severity: 'Medium' as const,
          message: 'Slow query',
          file: 'api.js',
          line: 25
        }
      ]

      mockAnalysisService.getIssues.mockResolvedValue(mockIssues)

      const { result } = renderHook(() => useIssues('test-123'))

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
        expect(result.current.issues).toEqual(mockIssues)
        expect(result.current.error).toBeNull()
      })
    })

    it('should handle empty issues array', async () => {
      mockAnalysisService.getIssues.mockResolvedValue([])

      const { result } = renderHook(() => useIssues('test-123'))

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
        expect(result.current.issues).toEqual([])
        expect(result.current.error).toBeNull()
      })
    })

    it('should handle issues fetch error', async () => {
      mockAnalysisService.getIssues.mockRejectedValue(new Error('Failed to fetch issues'))

      const { result } = renderHook(() => useIssues('test-123'))

      await waitFor(() => {
        expect(result.current.loading).toBe(false)
        expect(result.current.issues).toEqual([])
        expect(result.current.error).toBe('Failed to fetch issues')
      })
    })
  })

  describe('useAnalysisChat', () => {
    it('should ask questions successfully', async () => {
      const mockAnswer = 'You have 2 security issues that need attention.'
      mockAnalysisService.askQuestion.mockResolvedValue(mockAnswer)

      const { result } = renderHook(() => useAnalysisChat('test-123'))

      expect(result.current.loading).toBe(false)
      expect(result.current.error).toBeNull()

      const answer = await result.current.askQuestion('What security issues do I have?')

      expect(answer).toBe(mockAnswer)
      expect(mockAnalysisService.askQuestion).toHaveBeenCalledWith(
        'What security issues do I have?',
        'test-123'
      )
    })

    it('should handle null report ID', async () => {
      const { result } = renderHook(() => useAnalysisChat(null))

      const answer = await result.current.askQuestion('Test question')

      expect(answer).toBe('No analysis available. Please run an analysis first.')
      expect(mockAnalysisService.askQuestion).not.toHaveBeenCalled()
    })

    it('should handle chat errors', async () => {
      mockAnalysisService.askQuestion.mockRejectedValue(new Error('Chat service error'))

      const { result } = renderHook(() => useAnalysisChat('test-123'))

      const answer = await result.current.askQuestion('Test question')

      expect(answer).toBe('Sorry, I could not process your question at this time.')
      expect(result.current.error).toBe('Chat service error')
    })

    it('should track loading state during question', async () => {
      let resolvePromise: (value: string) => void
      const promise = new Promise<string>((resolve) => {
        resolvePromise = resolve
      })

      mockAnalysisService.askQuestion.mockReturnValue(promise)

      const { result } = renderHook(() => useAnalysisChat('test-123'))

      // Start asking question
      const questionPromise = result.current.askQuestion('Test question')

      // Should be loading
      expect(result.current.loading).toBe(true)

      // Resolve the promise
      resolvePromise!('Test answer')
      await questionPromise

      // Should no longer be loading
      await waitFor(() => {
        expect(result.current.loading).toBe(false)
      })
    })
  })
})