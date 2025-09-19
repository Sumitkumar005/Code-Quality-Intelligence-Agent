import { render, screen } from '@testing-library/react'
import { QualityMetrics } from '../quality-metrics'
import { AnalysisProvider } from '@/contexts'

// Mock the services
jest.mock('@/services', () => ({
  analysisService: {
    calculateMetricsFromAnalysis: jest.fn(() => ({
      test_coverage: 85,
      code_duplication: 12,
      technical_debt_hours: 2.5,
      complexity_distribution: {
        low: 60,
        medium: 30,
        high: 10
      }
    }))
  }
}))

// Mock the hooks
jest.mock('@/hooks', () => ({
  useQualityMetrics: jest.fn(() => ({
    metrics: null,
    loading: false,
    error: null
  })),
  useIssues: jest.fn(() => ({
    issues: [
      {
        id: '1',
        type: 'Security',
        severity: 'High',
        message: 'Test issue',
        file: 'test.js',
        line: 10
      }
    ],
    loading: false,
    error: null
  })),
  useQualityTrends: jest.fn(() => ({
    trends: [],
    loading: false,
    error: null
  }))
}))

// Mock the context
jest.mock('@/contexts', () => ({
  useAnalysis: jest.fn(() => ({
    currentAnalysis: {
      report_id: 'test-123',
      status: 'completed',
      summary: {
        quality_score: 85,
        total_files: 10,
        total_lines: 1000,
        total_issues: 5
      },
      issues: []
    },
    currentReportId: 'test-123',
    isLoading: false,
    error: null
  }))
}))

describe('QualityMetrics', () => {
  it('renders quality metrics with real data', () => {
    render(
      <AnalysisProvider>
        <QualityMetrics />
      </AnalysisProvider>
    )

    expect(screen.getByText('Quality Metrics')).toBeInTheDocument()
    expect(screen.getByText('Real-time metrics and visualizations from your code quality analysis.')).toBeInTheDocument()
  })

  it('shows empty state when no analysis available', () => {
    const { useAnalysis } = require('@/contexts')
    useAnalysis.mockReturnValue({
      currentAnalysis: null,
      currentReportId: null,
      isLoading: false,
      error: null
    })

    render(
      <AnalysisProvider>
        <QualityMetrics />
      </AnalysisProvider>
    )

    expect(screen.getByText('No Quality Metrics Available')).toBeInTheDocument()
  })
})