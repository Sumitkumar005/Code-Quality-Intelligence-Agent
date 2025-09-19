"use client"

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { AnalysisResult, analysisService } from '@/services'

interface AnalysisContextType {
  currentAnalysis: AnalysisResult | null
  isLoading: boolean
  error: string | null
  currentReportId: string | null
  refreshAnalysis: () => Promise<void>
  setCurrentReportId: (reportId: string | null) => void
  clearAnalysis: () => void
  startPolling: (reportId: string) => void
  stopPolling: () => void
}

const AnalysisContext = createContext<AnalysisContextType | undefined>(undefined)

interface AnalysisProviderProps {
  children: ReactNode
}

export function AnalysisProvider({ children }: AnalysisProviderProps) {
  const [currentAnalysis, setCurrentAnalysis] = useState<AnalysisResult | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [currentReportId, setCurrentReportIdState] = useState<string | null>(null)
  const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(null)

  // Load analysis data when report ID changes
  useEffect(() => {
    if (currentReportId) {
      loadAnalysis(currentReportId)
    } else {
      setCurrentAnalysis(null)
      setError(null)
      setIsLoading(false)
    }
  }, [currentReportId])

  // Clean up polling on unmount
  useEffect(() => {
    return () => {
      if (pollingInterval) {
        clearInterval(pollingInterval)
      }
    }
  }, [pollingInterval])

  const loadAnalysis = async (reportId: string) => {
    try {
      setIsLoading(true)
      setError(null)
      
      const analysis = await analysisService.getAnalysisStatus(reportId)
      setCurrentAnalysis(analysis)
      
      // If analysis is still processing, start polling
      if (analysis.status === 'processing') {
        startPolling(reportId)
      } else {
        stopPolling()
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load analysis'
      setError(errorMessage)
      setCurrentAnalysis(null)
    } finally {
      setIsLoading(false)
    }
  }

  const refreshAnalysis = async () => {
    if (currentReportId) {
      await loadAnalysis(currentReportId)
    }
  }

  const setCurrentReportId = (reportId: string | null) => {
    // Stop any existing polling when changing report ID
    stopPolling()
    setCurrentReportIdState(reportId)
  }

  const clearAnalysis = () => {
    stopPolling()
    setCurrentAnalysis(null)
    setCurrentReportIdState(null)
    setError(null)
    setIsLoading(false)
  }

  const startPolling = (reportId: string) => {
    // Clear existing polling
    if (pollingInterval) {
      clearInterval(pollingInterval)
    }

    // Start new polling every 3 seconds
    const interval = setInterval(async () => {
      try {
        const analysis = await analysisService.getAnalysisStatus(reportId)
        setCurrentAnalysis(analysis)
        
        // Stop polling if analysis is complete or failed
        if (analysis.status === 'completed' || analysis.status === 'error') {
          stopPolling()
        }
      } catch (err) {
        console.error('Polling error:', err)
        // Continue polling on error, but don't update state
      }
    }, 3000)

    setPollingInterval(interval)
  }

  const stopPolling = () => {
    if (pollingInterval) {
      clearInterval(pollingInterval)
      setPollingInterval(null)
    }
  }

  const contextValue: AnalysisContextType = {
    currentAnalysis,
    isLoading,
    error,
    currentReportId,
    refreshAnalysis,
    setCurrentReportId,
    clearAnalysis,
    startPolling,
    stopPolling,
  }

  return (
    <AnalysisContext.Provider value={contextValue}>
      {children}
    </AnalysisContext.Provider>
  )
}

export function useAnalysis(): AnalysisContextType {
  const context = useContext(AnalysisContext)
  if (context === undefined) {
    throw new Error('useAnalysis must be used within an AnalysisProvider')
  }
  return context
}