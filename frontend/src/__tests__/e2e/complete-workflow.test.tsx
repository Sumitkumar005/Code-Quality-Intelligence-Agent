/**
 * End-to-end integration tests
 * Tests complete user workflows from start to finish
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { AnalysisProvider } from '@/contexts'
import { QualityMetrics } from '@/components/quality-metrics'
import { IssueDetection } from '@/components/issue-detection'
import { ChatInterface } from '@/components/chat-interface'
import { GitHubAnalyzer } from '@/components/advanced/github-analyzer'

// Mock all services
jest.mock('@/services', () => ({
  analysisService: {
    startAnalysis: jest.fn(),
    getAnalysisStatus: jest.fn(),
    getQualityMetrics: jest.fn(),
    getIssues: jest.fn(),
    askQuestion: jest.fn(),
    calculateMetricsFromAnalysis: jest.fn(),
  },
  githubService: {
    analyzeRepository: jest.fn(),
    validateRepoUrl: jest.fn(),
    getTrendingRepos: jest.fn(),
    formatRepoName: jest.fn(),
  },
}))

// Mock the context hook
const mockSetCurrentReportId = jest.fn()
jest.mock('@/contexts', () => ({
  ...jest.requireActual('@/contexts'),
  useAnalysis: jest.fn(() => ({
    currentAnalysis: null,
    currentReportId: null,
    isLoading: false,
    error: null,
    setCurrentReportId: mockSetCurrentReportId,
  })),
}))

describe('Complete Workflow E2E Tests', () => {
  const mockCompleteAnalysis = {
    report_id: 'e2e-test-123',
    status: 'completed' as const,
    summary: {
      quality_score: 82.5,
      total_files: 25,
      total_lines: 1500,
      total_issues: 6,
    },
    issues: [
      {
        id: 'sec-1',
        type: 'Security' as const,
        severity: 'High' as const,
        message: 'Potential SQL injection vulnerability',
        file: 'src/api/users.js',
        line: 42,
        suggestion: 'Use parameterized queries to prevent SQL injection',
      },
      {
        id: 'perf-1',
        type: 'Performance' as const,
        severity: 'Medium' as const,
        message: 'Inefficient database query in loop',
        file: 'src/services/data.js',
        line: 18,
        suggestion: 'Move query outside loop or use batch operations',
      },
    ],
    metrics: {
      test_coverage: 75.5,
      code_duplication: 8.2,
      technical_debt_hours: 3.8,
      complexity_distribution: {
        low: 70,
        medium: 25,
        high: 5,
      },
    },
  }

  beforeEach(() => {
    jest.clearAllMocks()
    
    // Setup default service mocks
    const { analysisService, githubService } = require('@/services')
    
    analysisService.getAnalysisStatus.mockResolvedValue(mockCompleteAnalysis)
    analysisService.getQualityMetrics.mockResolvedValue(mockCompleteAnalysis.metrics)
    analysisService.getIssues.mockResolvedValue(mockCompleteAnalysis.issues)
    analysisService.calculateMetricsFromAnalysis.mockReturnValue(mockCompleteAnalysis.metrics)
    
    githubService.validateRepoUrl.mockReturnValue(true)
    githubService.formatRepoName.mockReturnValue('user/repo')
  })

  describe('File Upload to Results Workflow', () => {
    it('should complete full analysis workflow', async () => {
      // Mock the analysis context to simulate completed analysis
      const { useAnalysis } = require('@/contexts')
      useAnalysis.mockReturnValue({
        currentAnalysis: mockCompleteAnalysis,
        currentReportId: 'e2e-test-123',
        isLoading: false,
        error: null,
        setCurrentReportId: mockSetCurrentReportId,
      })

      const FullWorkflowApp = () => (
        <AnalysisProvider>
          <div>
            <QualityMetrics />
            <IssueDetection />
            <ChatInterface />
          </div>
        </AnalysisProvider>
      )

      render(<FullWorkflowApp />)

      // 1. Verify Quality Metrics are displayed
      await waitFor(() => {
        expect(screen.getByText('Quality Metrics')).toBeInTheDocument()
        expect(screen.getByText('82.5/100')).toBeInTheDocument() // Quality score
        expect(screen.getByText('25')).toBeInTheDocument() // Total files
      })

      // 2. Verify Issues are displayed
      expect(screen.getByText('Issue Detection')).toBeInTheDocument()
      expect(screen.getByText('Potential SQL injection vulnerability')).toBeInTheDocument()
      expect(screen.getByText('src/api/users.js:42')).toBeInTheDocument()

      // 3. Verify Chat Interface is ready
      expect(screen.getByText('AI Assistant')).toBeInTheDocument()
      expect(screen.getByText(/I've analyzed your codebase with 25 files/)).toBeInTheDocument()

      // 4. Test issue interaction
      const securityTab = screen.getByRole('tab', { name: /security/i })
      await userEvent.click(securityTab)

      // Should show security issues
      expect(screen.getByText('Potential SQL injection vulnerability')).toBeInTheDocument()

      // 5. Test chat interaction
      const { analysisService } = require('@/services')
      analysisService.askQuestion.mockResolvedValue(
        'You have 1 high-severity security issue that requires immediate attention: a potential SQL injection vulnerability in src/api/users.js.'
      )

      const chatInput = screen.getByPlaceholderText(/ask about your code/i)
      const sendButton = screen.getByRole('button', { name: /send/i })

      await userEvent.type(chatInput, 'What security issues should I fix first?')
      await userEvent.click(sendButton)

      await waitFor(() => {
        expect(screen.getByText(/high-severity security issue/)).toBeInTheDocument()
      })
    })
  })

  describe('GitHub Analysis Workflow', () => {
    it('should complete GitHub repository analysis', async () => {
      const { githubService, analysisService } = require('@/services')
      
      // Mock GitHub analysis flow
      githubService.analyzeRepository.mockResolvedValue({
        report_id: 'github-456',
        status: 'processing',
        message: 'GitHub analysis started',
      })

      githubService.getTrendingRepos.mockResolvedValue([
        {
          name: 'awesome-project',
          url: 'https://github.com/user/awesome-project',
          language: 'JavaScript',
          stars: 1200,
          forks: 150,
        },
      ])

      // Mock progressive analysis updates
      analysisService.getAnalysisStatus
        .mockResolvedValueOnce({
          ...mockCompleteAnalysis,
          report_id: 'github-456',
          status: 'processing',
          progress: 25,
          message: 'Downloading repository...',
        })
        .mockResolvedValueOnce({
          ...mockCompleteAnalysis,
          report_id: 'github-456',
          status: 'processing',
          progress: 75,
          message: 'Analyzing code...',
        })
        .mockResolvedValueOnce({
          ...mockCompleteAnalysis,
          report_id: 'github-456',
          repository: {
            name: 'test-repo',
            url: 'https://github.com/user/test-repo',
            language: 'JavaScript',
            stars: 500,
            forks: 75,
          },
        })

      render(
        <AnalysisProvider>
          <GitHubAnalyzer />
        </AnalysisProvider>
      )

      // 1. Enter GitHub URL
      const urlInput = screen.getByPlaceholderText(/github.com\/username\/repository/)
      await userEvent.type(urlInput, 'https://github.com/user/test-repo')

      // 2. Start analysis
      const analyzeButton = screen.getByRole('button', { name: /analyze/i })
      await userEvent.click(analyzeButton)

      // 3. Verify analysis started
      expect(githubService.analyzeRepository).toHaveBeenCalledWith('https://github.com/user/test-repo')

      // 4. Check trending repos tab
      const trendingTab = screen.getByRole('tab', { name: /trending repos/i })
      await userEvent.click(trendingTab)

      await waitFor(() => {
        expect(screen.getByText('awesome-project')).toBeInTheDocument()
        expect(screen.getByText('1,200')).toBeInTheDocument() // Stars count
      })
    })
  })

  describe('Error Handling Workflow', () => {
    it('should handle and recover from errors gracefully', async () => {
      const { analysisService } = require('@/services')
      
      // Mock initial error
      analysisService.getAnalysisStatus.mockRejectedValueOnce(new Error('Network error'))
      
      // Mock successful retry
      analysisService.getAnalysisStatus.mockResolvedValueOnce(mockCompleteAnalysis)

      const ErrorRecoveryApp = () => (
        <AnalysisProvider>
          <QualityMetrics />
        </AnalysisProvider>
      )

      render(<ErrorRecoveryApp />)

      // 1. Should show error state
      await waitFor(() => {
        expect(screen.getByText(/failed to load/i)).toBeInTheDocument()
      })

      // 2. Click retry button
      const retryButton = screen.getByRole('button', { name: /try again/i })
      await userEvent.click(retryButton)

      // 3. Should recover and show data
      await waitFor(() => {
        expect(screen.getByText('Quality Metrics')).toBeInTheDocument()
        expect(screen.getByText('82.5/100')).toBeInTheDocument()
      })
    })

    it('should handle offline/online transitions', async () => {
      // Mock network status changes
      Object.defineProperty(navigator, 'onLine', {
        writable: true,
        value: false,
      })

      render(
        <AnalysisProvider>
          <QualityMetrics />
        </AnalysisProvider>
      )

      // Should show offline state
      await waitFor(() => {
        expect(screen.getByText(/no quality metrics available/i)).toBeInTheDocument()
      })

      // Simulate coming back online
      Object.defineProperty(navigator, 'onLine', {
        writable: true,
        value: true,
      })

      // Trigger online event
      fireEvent(window, new Event('online'))

      // Should attempt to reload data
      await waitFor(() => {
        // Component should try to fetch data again
        expect(screen.queryByText(/offline/i)).not.toBeInTheDocument()
      })
    })
  })

  describe('Real-time Updates Workflow', () => {
    it('should handle real-time analysis progress updates', async () => {
      const { analysisService } = require('@/services')
      
      let progressStep = 0
      analysisService.getAnalysisStatus.mockImplementation(() => {
        progressStep++
        
        if (progressStep === 1) {
          return Promise.resolve({
            ...mockCompleteAnalysis,
            status: 'processing',
            progress: 25,
            message: 'Starting analysis...',
          })
        } else if (progressStep === 2) {
          return Promise.resolve({
            ...mockCompleteAnalysis,
            status: 'processing',
            progress: 75,
            message: 'Analyzing code...',
          })
        } else {
          return Promise.resolve(mockCompleteAnalysis)
        }
      })

      // Mock context to simulate processing state
      const { useAnalysis } = require('@/contexts')
      useAnalysis.mockReturnValue({
        currentAnalysis: {
          ...mockCompleteAnalysis,
          status: 'processing',
          progress: 25,
        },
        currentReportId: 'e2e-test-123',
        isLoading: false,
        error: null,
        setCurrentReportId: mockSetCurrentReportId,
      })

      render(
        <AnalysisProvider>
          <QualityMetrics />
        </AnalysisProvider>
      )

      // Should show loading state initially
      expect(screen.getByText(/loading/i)).toBeInTheDocument()

      // Simulate analysis completion
      useAnalysis.mockReturnValue({
        currentAnalysis: mockCompleteAnalysis,
        currentReportId: 'e2e-test-123',
        isLoading: false,
        error: null,
        setCurrentReportId: mockSetCurrentReportId,
      })

      // Re-render with completed analysis
      render(
        <AnalysisProvider>
          <QualityMetrics />
        </AnalysisProvider>
      )

      await waitFor(() => {
        expect(screen.getByText('Quality Metrics')).toBeInTheDocument()
        expect(screen.getByText('82.5/100')).toBeInTheDocument()
      })
    })
  })
})