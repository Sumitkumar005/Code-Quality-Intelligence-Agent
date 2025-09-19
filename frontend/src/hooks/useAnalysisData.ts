"use client"

import { useState, useEffect } from 'react'
import { AnalysisResult, QualityMetrics, Issue, analysisService } from '@/services'

// Custom hook for fetching analysis data with loading and error states
export function useAnalysisData(reportId: string | null) {
  const [data, setData] = useState<AnalysisResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!reportId) {
      setData(null)
      setLoading(false)
      setError(null)
      return
    }

    const fetchData = async () => {
      try {
        setLoading(true)
        setError(null)
        const analysis = await analysisService.getAnalysisStatus(reportId)
        setData(analysis)
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to fetch analysis data'
        setError(errorMessage)
        setData(null)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [reportId])

  return { data, loading, error, refetch: () => reportId && useAnalysisData(reportId) }
}

// Custom hook for fetching quality metrics
export function useQualityMetrics(reportId: string | null) {
  const [metrics, setMetrics] = useState<QualityMetrics | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!reportId) {
      setMetrics(null)
      setLoading(false)
      setError(null)
      return
    }

    const fetchMetrics = async () => {
      try {
        setLoading(true)
        setError(null)
        const metricsData = await analysisService.getQualityMetrics(reportId)
        setMetrics(metricsData)
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to fetch quality metrics'
        setError(errorMessage)
        setMetrics(null)
      } finally {
        setLoading(false)
      }
    }

    fetchMetrics()
  }, [reportId])

  return { metrics, loading, error }
}

// Custom hook for fetching issues
export function useIssues(reportId: string | null) {
  const [issues, setIssues] = useState<Issue[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!reportId) {
      setIssues([])
      setLoading(false)
      setError(null)
      return
    }

    const fetchIssues = async () => {
      try {
        setLoading(true)
        setError(null)
        const issuesData = await analysisService.getIssues(reportId)
        setIssues(issuesData)
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to fetch issues'
        setError(errorMessage)
        setIssues([])
      } finally {
        setLoading(false)
      }
    }

    fetchIssues()
  }, [reportId])

  return { issues, loading, error }
}

// Custom hook for fetching quality trends
export function useQualityTrends(projectId: string | null, days: number = 30) {
  const [trends, setTrends] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!projectId) {
      setTrends([])
      setLoading(false)
      setError(null)
      return
    }

    const fetchTrends = async () => {
      try {
        setLoading(true)
        setError(null)
        const trendsData = await analysisService.getQualityTrends(projectId, days)
        setTrends(trendsData)
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to fetch quality trends'
        setError(errorMessage)
        setTrends([])
      } finally {
        setLoading(false)
      }
    }

    fetchTrends()
  }, [projectId, days])

  return { trends, loading, error }
}

// Custom hook for asking questions about analysis
export function useAnalysisChat(reportId: string | null) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const askQuestion = async (question: string): Promise<string> => {
    if (!reportId) {
      return 'No analysis available. Please run an analysis first.'
    }

    try {
      setLoading(true)
      setError(null)
      const answer = await analysisService.askQuestion(question, reportId)
      return answer
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to get answer'
      setError(errorMessage)
      return 'Sorry, I could not process your question at this time.'
    } finally {
      setLoading(false)
    }
  }

  return { askQuestion, loading, error }
}