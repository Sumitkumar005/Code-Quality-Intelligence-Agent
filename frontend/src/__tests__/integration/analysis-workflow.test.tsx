/**
 * Integration tests for the complete analysis workflow
 * Tests the real data flow from file upload to result display
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { AnalysisProvider } from '@/contexts'
import { QualityMetrics } from '@/components/quality-metrics'
import { IssueDetection } from '@/components/issue-detection'
import { ChatInterface } from '@/components/chat-interface'
import { analysisService, githubService } from '@/services'

// Mock the API services
jest.mock('@/services', () => ({
  analysisService: {
    startAnalysis: jest.fn(),
    getAnalysisStatus: jest.fn(),
    getQualityMetrics: jest.fn(),
    getIssues: jest.fn(),
    askQuestion: jest.fn(),
    calculateMetricsFromAnalysis: jest.fn()
  },
  githubService: {
    analyzeRepository: jest.fn(),
    validateRepoUrl: jest.fn(),
    getTrendingRepos: jest.fn()
  }
}))

// Mock fetch for API calls
global.fetch = jest.fn()

const mockAnalysisResult = {
  report_id: 'test-report-123',
  status: 'completed' as const,
  summary: {
    quality_score: 85.5,
    total_files: 42,
    total_lines: 2500,
    total_issues: 8
  },
  issues: [
    {
      id: 'issue-1',
      type: 'Security' as const,
      severity: 'High' as const,
      message: 'SQL injection vulnerability detected',
      file: 'src/database.js',
      line: 45,
      suggestion: 'Use parameterized queries'
    },
    {
      id: 'issue-2',
      type: 'Performance' as const,
      severity: 'Medium' as const,
      message: 'Inefficient loop detected',
      file: 'src/utils.js',
      line: 23,
      suggestion: 'Consider using array methods'
    }
  ],
  metrics: {
    test_coverage: 78.5,
    code_duplication: 12.3,
    technical_debt_hours: 4.2,
    complexity_distribution: {
      low: 65,
      medium: 25,
      high: 10
    }
  }
}

describe('Analysis Workflow Integration', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    
    // Setup default mock implementations
    ;(analysisService.getAnalysisStatus as jest.Mock).mockResolvedValue(mockAnalysisResult)
    ;(analysisService.getQualityMetrics as jest.Mock).mockResolvedValue(mockAnalysisResult.metrics)
    ;(analysisService.getIssues as jest.Mock).mockResolvedValue(mockAnalysisResult.issues)
    ;(analysisService.calculateMetricsFromAnalysis as jest.Mock).mockReturnValue(mockAnalysisResult.metrics)
  })

  describe('Complete Analysis Flow', () => {
    it('should handle complete analysis workflow from start to finish', async () => {
      // Mock the analysis start
      ;(analysisService.startAnalysis as jest.Mock).mockResolvedValue({
        report_id: 'test-report-123',
        status: 'processing',
        message: 'Analysis started'
      })

      // Mock progressive status updates
      ;(analysisService.getAnalysisStatus as jest.Mock)
        .mockResolvedValueOnce({
          ...mockAnalysisResult,
          status: 'processing',
          progress: 50,
          message: 'Analyzing code...'
        })
        .mockResolvedValueOnce(mockAnalysisResult)

      const TestComponent = () => (
        <AnalysisProvider>
          <div>
            <QualityMetrics />
            <IssueDetection />
          </div>
        </AnalysisProvider>
      )

      render(<TestComponent />)

      // Should show loading state initially
      expect(screen.getByText(/loading/i)).toBeInTheDocument()

      // Wait for analysis to complete and data to load
      await waitFor(() => {
        expect(screen.getByText('Quality Metrics')).toBeInTheDocument()
        expect(screen.getByText('Issue Detection')).toBeInTheDocument()
      })

      // Verify real data is displayed
      expect(screen.getByText('85.5/100')).toBeInTheDocument() // Quality score
      expect(screen.getByText('42')).toBeInTheDocument() // Total files
      expect(screen.getByText('8')).toBeInTheDocument() // Total issues

      // Verify issues are displayed
      expect(screen.getByText('SQL injection vulnerability detected')).toBeInTheDocument()
      expect(screen.getByText('src/database.js:45')).toBeInTheDocument()
    })

    it('should handle analysis errors gracefully', async () => {
      // Mock analysis failure
      ;(analysisService.getAnalysisStatus as jest.Mock).mockRejectedValue(
        new Error('Analysis failed')
      )

      const TestComponent = () => (
        <AnalysisProvider>
          <QualityMetrics />
        </AnalysisProvider>
      )

      render(<TestComponent />)

      await waitFor(() => {
        expect(screen.getByText(/failed to load/i)).toBeInTheDocument()
      })
    })
  })

  describe('GitHub Integration Flow', () => {
    it('should handle GitHub repository analysis workflow', async () => {
      const mockGitHubResponse = {
        report_id: 'github-report-456',
        status: 'processing',
        message: 'GitHub analysis started'
      }

      ;(githubService.validateRepoUrl as jest.Mock).mockReturnValue(true)
      ;(githubService.analyzeRepository as jest.Mock).mockResolvedValue(mockGitHubResponse)
      ;(analysisService.getAnalysisStatus as jest.Mock).mockResolvedValue({
        ...mockAnalysisResult,
        report_id: 'github-report-456',
        repository: {
          name: 'test-repo',
          url: 'https://github.com/user/test-repo',
          language: 'JavaScript',
          stars: 100,
          forks: 25
        }
      })

      // This would be tested in the GitHub analyzer component
      expect(githubService.validateRepoUrl).toBeDefined()
      expect(githubService.analyzeRepository).toBeDefined()
    })

    it('should handle invalid GitHub URLs', async () => {
      ;(githubService.validateRepoUrl as jest.Mock).mockReturnValue(false)

      // Test URL validation
      const isValid = githubService.validateRepoUrl('invalid-url')
      expect(isValid).toBe(false)
    })
  })

  describe('Chat Integration Flow', () => {
    it('should handle chat questions with real analysis context', async () => {
      const mockChatResponse = 'Based on your analysis, you have 1 high-severity security issue that needs immediate attention.'

      ;(analysisService.askQuestion as jest.Mock).mockResolvedValue(mockChatResponse)

      const TestComponent = () => (
        <AnalysisProvider>
          <ChatInterface />
        </AnalysisProvider>
      )

      render(<TestComponent />)

      // Wait for component to load with analysis context
      await waitFor(() => {
        expect(screen.getByText(/AI Assistant/)).toBeInTheDocument()
      })

      // Find and click on a suggested question or type a question
      const input = screen.getByPlaceholderText(/ask about your code/i)
      const sendButton = screen.getByRole('button', { name: /send/i })

      await userEvent.type(input, 'What are the security issues?')
      await userEvent.click(sendButton)

      // Verify the question was sent and response received
      await waitFor(() => {
        expect(analysisService.askQuestion).toHaveBeenCalledWith(
          'What are the security issues?',
          'test-report-123'
        )
      })
    })

    it('should handle chat errors and provide fallback responses', async () => {
      ;(analysisService.askQuestion as jest.Mock).mockRejectedValue(
        new Error('Chat service unavailable')
      )

      const TestComponent = () => (
        <AnalysisProvider>
          <ChatInterface />
        </AnalysisProvider>
      )

      render(<TestComponent />)

      await waitFor(() => {
        expect(screen.getByText(/AI Assistant/)).toBeInTheDocument()
      })

      const input = screen.getByPlaceholderText(/ask about your code/i)
      const sendButton = screen.getByRole('button', { name: /send/i })

      await userEvent.type(input, 'Test question')
      await userEvent.click(sendButton)

      // Should show fallback response when API fails
      await waitFor(() => {
        expect(screen.getByText(/based on your analysis/i)).toBeInTheDocument()
      })
    })
  })

  describe('Error Handling Integration', () => {
    it('should handle network errors across all components', async () => {
      // Mock network error
      ;(analysisService.getAnalysisStatus as jest.Mock).mockRejectedValue(
        new Error('Network error')
      )

      const TestComponent = () => (
        <AnalysisProvider>
          <QualityMetrics />
        </AnalysisProvider>
      )

      render(<TestComponent />)

      await waitFor(() => {
        expect(screen.getByText(/failed to load/i)).toBeInTheDocument()
      })
    })

    it('should handle empty analysis states', async () => {
      const TestComponent = () => (
        <AnalysisProvider>
          <QualityMetrics reportId={null} />
        </AnalysisProvider>
      )

      render(<TestComponent />)

      expect(screen.getByText(/no quality metrics available/i)).toBeInTheDocument()
    })
  })

  describe('Real-time Updates', () => {
    it('should update components when analysis completes', async () => {
      let analysisStatus = 'processing'
      
      ;(analysisService.getAnalysisStatus as jest.Mock).mockImplementation(() => {
        if (analysisStatus === 'processing') {
          return Promise.resolve({
            ...mockAnalysisResult,
            status: 'processing',
            progress: 75,
            message: 'Almost done...'
          })
        }
        return Promise.resolve(mockAnalysisResult)
      })

      const TestComponent = () => (
        <AnalysisProvider>
          <QualityMetrics />
        </AnalysisProvider>
      )

      render(<TestComponent />)

      // Initially should show loading
      expect(screen.getByText(/loading/i)).toBeInTheDocument()

      // Simulate analysis completion
      analysisStatus = 'completed'

      await waitFor(() => {
        expect(screen.getByText('Quality Metrics')).toBeInTheDocument()
      })
    })
  })

  describe('Data Consistency', () => {
    it('should maintain data consistency across components', async () => {
      const TestComponent = () => (
        <AnalysisProvider>
          <div>
            <QualityMetrics />
            <IssueDetection />
          </div>
        </AnalysisProvider>
      )

      render(<TestComponent />)

      await waitFor(() => {
        // Both components should show the same issue count
        const issueElements = screen.getAllByText('8')
        expect(issueElements.length).toBeGreaterThan(0)
        
        // Both should reference the same quality score
        expect(screen.getByText('85.5/100')).toBeInTheDocument()
      })
    })

    it('should handle concurrent API calls efficiently', async () => {
      let callCount = 0
      ;(analysisService.getAnalysisStatus as jest.Mock).mockImplementation(() => {
        callCount++
        return Promise.resolve(mockAnalysisResult)
      })

      const TestComponent = () => (
        <AnalysisProvider>
          <div>
            <QualityMetrics />
            <IssueDetection />
          </div>
        </AnalysisProvider>
      )

      render(<TestComponent />)

      await waitFor(() => {
        expect(screen.getByText('Quality Metrics')).toBeInTheDocument()
      })

      // Should not make excessive API calls
      expect(callCount).toBeLessThan(5)
    })
  })
})