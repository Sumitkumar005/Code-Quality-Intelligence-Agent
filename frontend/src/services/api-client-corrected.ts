// Corrected API Client with proper types
import { ApiResponse, ApiError, RequestOptions } from '../types/api-corrected'

class ApiClient {
  private baseURL: string
  private defaultTimeout: number
  private defaultRetries: number

  constructor(baseURL: string = '/api/v1', timeout: number = 10000, retries: number = 3) {
    this.baseURL = baseURL
    this.defaultTimeout = timeout
    this.defaultRetries = retries
  }

  private async request<T>(
    endpoint: string,
    options: RequestOptions = {}
  ): Promise<ApiResponse<T>> {
    const {
      method = 'GET',
      headers = {},
      params,
      timeout = this.defaultTimeout,
      retries = this.defaultRetries,
      body
    } = options

    const url = new URL(endpoint, this.baseURL)

    // Add query parameters
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        url.searchParams.append(key, String(value))
      })
    }

    // Set up headers
    const requestHeaders: Record<string, string> = {
      'Content-Type': 'application/json',
      ...headers
    }

    // Remove Content-Type for FormData
    if (headers['Content-Type'] === 'multipart/form-data') {
      delete requestHeaders['Content-Type']
    }

    const requestOptions: RequestInit = {
      method,
      headers: requestHeaders,
      signal: AbortSignal.timeout(timeout)
    }

    // Add body for non-GET requests
    if (method !== 'GET' && body) {
      requestOptions.body = JSON.stringify(body)
    }

    let lastError: Error | null = null

    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        const response = await fetch(url.toString(), requestOptions)
        const data = await response.json()

        if (!response.ok) {
          const error: ApiError = {
            success: false,
            error: {
              code: data.code || `HTTP_${response.status}`,
              message: data.message || `HTTP ${response.status}`,
              details: data,
              timestamp: new Date().toISOString(),
              request_id: crypto.randomUUID()
            },
            message: data.message || `HTTP ${response.status}`,
            status: response.status,
            code: data.code,
            details: data
          }
          throw error
        }

        return {
          success: true,
          data,
          status: response.status,
          message: 'Success'
        }
      } catch (error) {
        lastError = error as Error

        if (attempt === retries) {
          break
        }

        // Exponential backoff
        const delay = Math.min(1000 * Math.pow(2, attempt), 10000)
        await new Promise(resolve => setTimeout(resolve, delay))
      }
    }

    return {
      success: false,
      data: null as T,
      status: 0,
      message: lastError?.message || 'Network error',
      error: lastError as ApiError
    }
  }

  async get<T>(endpoint: string, options: Omit<RequestOptions, 'method' | 'body'> = {}): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'GET' })
  }

  async post<T>(endpoint: string, body?: any, options: Omit<RequestOptions, 'method'> = {}): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'POST', body })
  }

  async put<T>(endpoint: string, body?: any, options: Omit<RequestOptions, 'method'> = {}): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'PUT', body })
  }

  async patch<T>(endpoint: string, body?: any, options: Omit<RequestOptions, 'method'> = {}): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'PATCH', body })
  }

  async delete<T>(endpoint: string, options: Omit<RequestOptions, 'method' | 'body'> = {}): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'DELETE' })
  }
}

// Create and export API client instance
export const apiClient = new ApiClient()
export default apiClient
