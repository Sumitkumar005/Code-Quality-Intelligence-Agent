// Base API client with error handling and request/response interceptors

import { ApiException } from '@/types/api'

export class ApiClient {
  private baseURL: string
  private defaultHeaders: Record<string, string>

  constructor(baseURL: string = 'http://localhost:8000') {
    this.baseURL = baseURL
    this.defaultHeaders = {
      'Content-Type': 'application/json',
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`
    
    const config: RequestInit = {
      ...options,
      headers: {
        ...this.defaultHeaders,
        ...options.headers,
      },
    }

    try {
      const response = await fetch(url, config)
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new ApiException(
          response.status,
          errorData.detail || errorData.message || `HTTP ${response.status}`,
          errorData.code
        )
      }

      const data = await response.json()
      return data as T
    } catch (error) {
      if (error instanceof ApiException) {
        throw error
      }
      
      // Network or other errors
      throw new ApiException(
        0,
        error instanceof Error ? error.message : 'Network error occurred'
      )
    }
  }

  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' })
  }

  async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  async put<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' })
  }

  // Health check method
  async healthCheck(): Promise<{ status: string; version: string }> {
    return this.get('/health')
  }
}

// Create singleton instance
export const apiClient = new ApiClient()
