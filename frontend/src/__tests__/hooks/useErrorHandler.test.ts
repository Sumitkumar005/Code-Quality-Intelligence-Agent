/**
 * Unit tests for error handling hooks
 * Tests error classification and handling logic
 */

import { renderHook, act } from '@testing-library/react'
import { useErrorHandler, useAsyncOperation, useFormSubmission } from '@/hooks/useErrorHandler'
import { ApiException } from '@/types/api'

describe('Error Handling Hooks', () => {
  describe('useErrorHandler', () => {
    it('should handle ApiException errors correctly', () => {
      const { result } = renderHook(() => useErrorHandler())

      act(() => {
        result.current.handleError(new ApiException(404, 'Not found'))
      })

      expect(result.current.isError).toBe(true)
      expect(result.current.error).toBe('Not found')
      expect(result.current.errorType).toBe('notFound')
    })

    it('should classify network errors', () => {
      const { result } = renderHook(() => useErrorHandler())

      act(() => {
        result.current.handleError(new ApiException(0, 'Network error'))
      })

      expect(result.current.errorType).toBe('network')
      expect(result.current.error).toBe('Network connection failed. Please check your internet connection.')
    })

    it('should classify authentication errors', () => {
      const { result } = renderHook(() => useErrorHandler())

      act(() => {
        result.current.handleError(new ApiException(401, 'Unauthorized'))
      })

      expect(result.current.errorType).toBe('auth')
      expect(result.current.error).toBe('Authentication failed. Please check your permissions.')
    })

    it('should classify server errors', () => {
      const { result } = renderHook(() => useErrorHandler())

      act(() => {
        result.current.handleError(new ApiException(500, 'Internal server error'))
      })

      expect(result.current.errorType).toBe('server')
      expect(result.current.error).toBe('Server error occurred. Please try again later.')
    })

    it('should handle regular Error objects', () => {
      const { result } = renderHook(() => useErrorHandler())

      act(() => {
        result.current.handleError(new Error('Something went wrong'))
      })

      expect(result.current.isError).toBe(true)
      expect(result.current.error).toBe('Something went wrong')
      expect(result.current.errorType).toBe('unknown')
    })

    it('should handle string errors', () => {
      const { result } = renderHook(() => useErrorHandler())

      act(() => {
        result.current.handleError('String error message')
      })

      expect(result.current.isError).toBe(true)
      expect(result.current.error).toBe('String error message')
      expect(result.current.errorType).toBe('unknown')
    })

    it('should clear errors', () => {
      const { result } = renderHook(() => useErrorHandler())

      act(() => {
        result.current.handleError(new Error('Test error'))
      })

      expect(result.current.isError).toBe(true)

      act(() => {
        result.current.clearError()
      })

      expect(result.current.isError).toBe(false)
      expect(result.current.error).toBeNull()
      expect(result.current.errorType).toBe('unknown')
    })

    it('should retry operations with error handling', async () => {
      const { result } = renderHook(() => useErrorHandler())
      const mockOperation = jest.fn().mockResolvedValue('success')
      const mockOnSuccess = jest.fn()

      await act(async () => {
        const operationResult = await result.current.retryWithErrorHandling(mockOperation, mockOnSuccess)
        expect(operationResult).toBe('success')
      })

      expect(mockOperation).toHaveBeenCalled()
      expect(mockOnSuccess).toHaveBeenCalledWith('success')
      expect(result.current.isError).toBe(false)
    })

    it('should handle retry operation failures', async () => {
      const { result } = renderHook(() => useErrorHandler())
      const mockError = new Error('Operation failed')
      const mockOperation = jest.fn().mockRejectedValue(mockError)

      await act(async () => {
        try {
          await result.current.retryWithErrorHandling(mockOperation)
        } catch (error) {
          expect(error).toBe(mockError)
        }
      })

      expect(result.current.isError).toBe(true)
      expect(result.current.error).toBe('Operation failed')
    })
  })

  describe('useAsyncOperation', () => {
    it('should execute async operations successfully', async () => {
      const { result } = renderHook(() => useAsyncOperation())
      const mockOperation = jest.fn().mockResolvedValue('success')
      const mockOnSuccess = jest.fn()

      expect(result.current.loading).toBe(false)

      await act(async () => {
        const operationResult = await result.current.execute(mockOperation, mockOnSuccess)
        expect(operationResult).toBe('success')
      })

      expect(mockOperation).toHaveBeenCalled()
      expect(mockOnSuccess).toHaveBeenCalledWith('success')
      expect(result.current.loading).toBe(false)
      expect(result.current.isError).toBe(false)
    })

    it('should handle loading states correctly', async () => {
      const { result } = renderHook(() => useAsyncOperation())
      let resolveOperation: (value: string) => void
      const mockOperation = jest.fn(() => new Promise<string>((resolve) => {
        resolveOperation = resolve
      }))

      // Start operation
      act(() => {
        result.current.execute(mockOperation)
      })

      // Should be loading
      expect(result.current.loading).toBe(true)

      // Complete operation
      await act(async () => {
        resolveOperation!('success')
      })

      // Should no longer be loading
      expect(result.current.loading).toBe(false)
    })

    it('should handle operation errors', async () => {
      const { result } = renderHook(() => useAsyncOperation())
      const mockError = new Error('Operation failed')
      const mockOperation = jest.fn().mockRejectedValue(mockError)
      const mockOnError = jest.fn()

      await act(async () => {
        const operationResult = await result.current.execute(mockOperation, undefined, mockOnError)
        expect(operationResult).toBeNull()
      })

      expect(result.current.isError).toBe(true)
      expect(result.current.error).toBe('Operation failed')
      expect(result.current.loading).toBe(false)
      expect(mockOnError).toHaveBeenCalledWith(mockError)
    })

    it('should retry operations', async () => {
      const { result } = renderHook(() => useAsyncOperation())
      const mockOperation = jest.fn().mockResolvedValue('retry success')
      const mockOnSuccess = jest.fn()

      await act(async () => {
        const retryResult = await result.current.retry(mockOperation, mockOnSuccess)
        expect(retryResult).toBe('retry success')
      })

      expect(mockOperation).toHaveBeenCalled()
      expect(mockOnSuccess).toHaveBeenCalledWith('retry success')
    })
  })

  describe('useFormSubmission', () => {
    it('should handle form submissions successfully', async () => {
      const { result } = renderHook(() => useFormSubmission())
      const mockSubmitFn = jest.fn().mockResolvedValue('submitted')
      const mockOnSuccess = jest.fn()

      expect(result.current.submitting).toBe(false)
      expect(result.current.submitted).toBe(false)

      await act(async () => {
        const success = await result.current.submit(mockSubmitFn, mockOnSuccess)
        expect(success).toBe(true)
      })

      expect(mockSubmitFn).toHaveBeenCalled()
      expect(mockOnSuccess).toHaveBeenCalledWith('submitted')
      expect(result.current.submitting).toBe(false)
      expect(result.current.submitted).toBe(true)
      expect(result.current.isError).toBe(false)
    })

    it('should handle submission loading states', async () => {
      const { result } = renderHook(() => useFormSubmission())
      let resolveSubmit: (value: string) => void
      const mockSubmitFn = jest.fn(() => new Promise<string>((resolve) => {
        resolveSubmit = resolve
      }))

      // Start submission
      act(() => {
        result.current.submit(mockSubmitFn)
      })

      // Should be submitting
      expect(result.current.submitting).toBe(true)
      expect(result.current.submitted).toBe(false)

      // Complete submission
      await act(async () => {
        resolveSubmit!('success')
      })

      // Should no longer be submitting
      expect(result.current.submitting).toBe(false)
      expect(result.current.submitted).toBe(true)
    })

    it('should handle submission errors', async () => {
      const { result } = renderHook(() => useFormSubmission())
      const mockError = new Error('Submission failed')
      const mockSubmitFn = jest.fn().mockRejectedValue(mockError)
      const mockOnError = jest.fn()

      await act(async () => {
        const success = await result.current.submit(mockSubmitFn, undefined, mockOnError)
        expect(success).toBe(false)
      })

      expect(result.current.isError).toBe(true)
      expect(result.current.error).toBe('Submission failed')
      expect(result.current.submitting).toBe(false)
      expect(result.current.submitted).toBe(false)
      expect(mockOnError).toHaveBeenCalledWith(mockError)
    })

    it('should reset form state', () => {
      const { result } = renderHook(() => useFormSubmission())

      // Set some state
      act(() => {
        result.current.submit(jest.fn().mockRejectedValue(new Error('Test error')))
      })

      // Reset
      act(() => {
        result.current.reset()
      })

      expect(result.current.submitted).toBe(false)
      expect(result.current.isError).toBe(false)
      expect(result.current.error).toBeNull()
    })
  })
})