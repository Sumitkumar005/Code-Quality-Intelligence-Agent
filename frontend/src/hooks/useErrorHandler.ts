"use client"

import { useState, useCallback } from 'react'
import { ApiException } from '@/types/api'

interface ErrorState {
  error: string | null
  isError: boolean
  errorType: 'network' | 'timeout' | 'auth' | 'notFound' | 'server' | 'client' | 'unknown'
}

export function useErrorHandler() {
  const [errorState, setErrorState] = useState<ErrorState>({
    error: null,
    isError: false,
    errorType: 'unknown'
  })

  const handleError = useCallback((error: unknown) => {
    console.error('Error handled:', error)

    let errorMessage = 'An unexpected error occurred'
    let errorType: ErrorState['errorType'] = 'unknown'

    if (error instanceof ApiException) {
      errorMessage = error.message
      
      // Determine error type based on status code
      if (error.status === 0) {
        errorType = 'network'
        errorMessage = 'Network connection failed. Please check your internet connection.'
      } else if (error.status === 401 || error.status === 403) {
        errorType = 'auth'
        errorMessage = 'Authentication failed. Please check your permissions.'
      } else if (error.status === 404) {
        errorType = 'notFound'
        errorMessage = 'The requested resource was not found.'
      } else if (error.status === 408) {
        errorType = 'timeout'
        errorMessage = 'Request timed out. Please try again.'
      } else if (error.status >= 500) {
        errorType = 'server'
        errorMessage = 'Server error occurred. Please try again later.'
      } else if (error.status >= 400) {
        errorType = 'client'
      }
    } else if (error instanceof Error) {
      errorMessage = error.message
      
      // Check for common error patterns
      if (error.message.toLowerCase().includes('network')) {
        errorType = 'network'
      } else if (error.message.toLowerCase().includes('timeout')) {
        errorType = 'timeout'
      }
    } else if (typeof error === 'string') {
      errorMessage = error
    }

    setErrorState({
      error: errorMessage,
      isError: true,
      errorType
    })
  }, [])

  const clearError = useCallback(() => {
    setErrorState({
      error: null,
      isError: false,
      errorType: 'unknown'
    })
  }, [])

  const retryWithErrorHandling = useCallback(async (
    operation: () => Promise<any>,
    onSuccess?: (result: any) => void
  ) => {
    try {
      clearError()
      const result = await operation()
      if (onSuccess) {
        onSuccess(result)
      }
      return result
    } catch (error) {
      handleError(error)
      throw error
    }
  }, [handleError, clearError])

  return {
    ...errorState,
    handleError,
    clearError,
    retryWithErrorHandling
  }
}

// Hook for handling async operations with loading and error states
export function useAsyncOperation<T>() {
  const [loading, setLoading] = useState(false)
  const { error, isError, errorType, handleError, clearError } = useErrorHandler()

  const execute = useCallback(async (
    operation: () => Promise<T>,
    onSuccess?: (result: T) => void,
    onError?: (error: unknown) => void
  ): Promise<T | null> => {
    try {
      setLoading(true)
      clearError()
      
      const result = await operation()
      
      if (onSuccess) {
        onSuccess(result)
      }
      
      return result
    } catch (err) {
      handleError(err)
      if (onError) {
        onError(err)
      }
      return null
    } finally {
      setLoading(false)
    }
  }, [handleError, clearError])

  const retry = useCallback((
    operation: () => Promise<T>,
    onSuccess?: (result: T) => void
  ) => {
    return execute(operation, onSuccess)
  }, [execute])

  return {
    loading,
    error,
    isError,
    errorType,
    execute,
    retry,
    clearError
  }
}

// Hook for handling form submissions with error handling
export function useFormSubmission<T>() {
  const [submitting, setSubmitting] = useState(false)
  const [submitted, setSubmitted] = useState(false)
  const { error, isError, errorType, handleError, clearError } = useErrorHandler()

  const submit = useCallback(async (
    submitFn: () => Promise<T>,
    onSuccess?: (result: T) => void,
    onError?: (error: unknown) => void
  ): Promise<boolean> => {
    try {
      setSubmitting(true)
      setSubmitted(false)
      clearError()
      
      const result = await submitFn()
      
      setSubmitted(true)
      if (onSuccess) {
        onSuccess(result)
      }
      
      return true
    } catch (err) {
      handleError(err)
      if (onError) {
        onError(err)
      }
      return false
    } finally {
      setSubmitting(false)
    }
  }, [handleError, clearError])

  const reset = useCallback(() => {
    setSubmitted(false)
    clearError()
  }, [clearError])

  return {
    submitting,
    submitted,
    error,
    isError,
    errorType,
    submit,
    reset,
    clearError
  }
}