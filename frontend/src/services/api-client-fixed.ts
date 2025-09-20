// API Client Service
import { ApiConfig, ApiResponse, ApiError, RequestOptions } from '../types/api'

class ApiClient {
  private baseURL: string
  private defaultTimeout: number
  private defaultRetries: number

  constructor(config: ApiConfig) {
    this.baseURL = config.baseURL
    this.defaultTimeout = config.timeout
    this.defaultRetries = config.retries
  }

  private async request<T>(
    endpoint: string,
    options: RequestOptions = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseURL}${endpoint}`
    const timeout = options.timeout || this.defaultTimeout

    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), timeout)

      const response = await fetch(url, {
        method: options.method || 'GET',
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        body: options.method !== 'GET' && options.method !== 'DELETE'
          ? JSON.stringify(options.params)
          : undefined,
      })

      clearTimeout(timeoutId)

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        const apiError: ApiError = {
          success: false,
          error: {
            code: 'HTTP_ERROR',
            message: errorData.message || `HTTP ${response.status}`,
            details: errorData,
            timestamp: new Date().toISOString(),
            request_id: response.headers.get('x-request-id') || '',
          },
        }
        return apiError as any
      }

      const data = await response.json()
      return {
        success: true,
        data,
        meta: {
          timestamp: new Date().toISOString(),
          request_id: response.headers.get('x-request-id') || '',
        },
      }
    } catch (error) {
      const apiError: ApiError = {
        success: false,
        error: {
          code: 'NETWORK_ERROR',
          message: error instanceof Error ? error.message : 'Unknown error',
          timestamp: new Date().toISOString(),
          request_id: '',
        },
      }
      return apiError as any
    }
  }

  async get<T>(endpoint: string, options: RequestOptions = {}): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'GET' })
  }

  async post<T>(
    endpoint: string,
    data?: any,
    options: RequestOptions = {}
  ): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'POST',
      params: data,
    })
  }

  async put<T>(
    endpoint: string,
    data?: any,
    options: RequestOptions = {}
  ): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'PUT',
      params: data,
    })
  }

  async patch<T>(
    endpoint: string,
    data?: any,
    options: RequestOptions = {}
  ): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'PATCH',
      params: data,
    })
  }

  async delete<T>(endpoint: string, options: RequestOptions = {}): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'DELETE' })
  }
}

// Create and export API client instance
const apiConfig: ApiConfig = {
  baseURL: 'http://localhost:8000/api/v1',
  timeout: 10000,
  retries: 3,
}

export const apiClient = new ApiClient(apiConfig)
export default apiClient
