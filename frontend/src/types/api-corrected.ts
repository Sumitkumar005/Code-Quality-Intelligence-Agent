// API Response Types
export interface ApiResponse<T> {
  success: boolean
  data: T
  error?: ApiError
  meta?: {
    pagination?: PaginationMeta
    timestamp: string
    request_id: string
  }
}

export interface ApiError {
  success: false
  error: {
    code: string
    message: string
    details?: any
    timestamp: string
    request_id: string
  }
}

export interface PaginationMeta {
  page: number
  per_page: number
  total: number
  total_pages: number
  has_next: boolean
  has_prev: boolean
}

// Base API Client Configuration
export interface ApiConfig {
  baseURL: string
  timeout: number
  retries: number
}

// Request/Response Types
export interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'
  headers?: Record<string, string>
  params?: Record<string, any>
  timeout?: number
}

export interface PaginatedResponse<T> {
  data: T[]
  pagination: PaginationMeta
}
