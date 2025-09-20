// AI Service - Working Version
import { apiClient } from './api-client-working'
import { PaginationParams } from '../types/common-corrected'
import { ApiResponse } from '../types/api-corrected'

export class AIService {
  // Chat sessions
  async startChatSession(projectId?: string): Promise<ApiResponse<{
    session_id: string
    project_id?: string
    created_at: string
    messages: Array<{
      id: string
      role: 'user' | 'assistant' | 'system'
      content: string
      created_at: string
    }>
  }>> {
    return apiClient.post<{
      session_id: string
      project_id?: string
      created_at: string
      messages: Array<{
        id: string
        role: 'user' | 'assistant' | 'system'
        content: string
        created_at: string
      }>
    }>('/api/v1/ai/chat', { project_id: projectId })
  }

  async sendChatMessage(sessionId: string, message: string, options?: {
    context?: Record<string, any>
    temperature?: number
    max_tokens?: number
  }): Promise<ApiResponse<{
    message_id: string
    session_id: string
    role: 'assistant'
    content: string
    created_at: string
    metadata?: Record<string, any>
  }>> {
    return apiClient.post<{
      message_id: string
      session_id: string
      role: 'assistant'
      content: string
      created_at: string
      metadata?: Record<string, any>
    }>(`/api/v1/ai/chat/${sessionId}/messages`, {
      message,
      ...options
    })
  }

  async getChatSession(sessionId: string): Promise<ApiResponse<{
    session_id: string
    project_id?: string
    created_at: string
    updated_at: string
    messages: Array<{
      id: string
      role: 'user' | 'assistant' | 'system'
      content: string
      created_at: string
    }>
  }>> {
    return apiClient.get<{
      session_id: string
      project_id?: string
      created_at: string
      updated_at: string
      messages: Array<{
        id: string
        role: 'user' | 'assistant' | 'system'
        content: string
        created_at: string
      }>
    }>(`/api/v1/ai/chat/${sessionId}`)
  }

  async getChatSessions(params?: PaginationParams & {
    project_id?: string
    created_after?: string
    created_before?: string
  }): Promise<ApiResponse<Array<{
    session_id: string
    project_id?: string
    created_at: string
    updated_at: string
    message_count: number
    last_message?: string
  }>>> {
    const queryParams = new URLSearchParams()
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, String(value))
        }
      })
    }

    const endpoint = `/api/v1/ai/chat/sessions${queryParams.toString() ? `?${queryParams.toString()}` : ''}`
    return apiClient.get<Array<{
      session_id: string
      project_id?: string
      created_at: string
      updated_at: string
      message_count: number
      last_message?: string
    }>>(endpoint)
  }

  async deleteChatSession(sessionId: string): Promise<ApiResponse<void>> {
    return apiClient.delete<void>(`/api/v1/ai/chat/${sessionId}`)
  }

  // Code analysis and insights
  async analyzeCode(code: string, language: string, options?: {
    analysis_type?: 'explain' | 'review' | 'refactor' | 'optimize' | 'debug'
    context?: Record<string, any>
  }): Promise<ApiResponse<{
    analysis_id: string
    code: string
    language: string
    analysis_type: 'explain' | 'review' | 'refactor' | 'optimize' | 'debug'
    result: {
      explanation?: string
      issues?: Array<{
        type: string
        severity: 'low' | 'medium' | 'high' | 'critical'
        message: string
        line?: number
        suggestion?: string
      }>
      suggestions?: Array<{
        type: string
        description: string
        code?: string
        explanation?: string
      }>
      optimized_code?: string
      debug_info?: Record<string, any>
    }
    created_at: string
  }>> {
    return apiClient.post<{
      analysis_id: string
      code: string
      language: string
      analysis_type: 'explain' | 'review' | 'refactor' | 'optimize' | 'debug'
      result: {
        explanation?: string
        issues?: Array<{
          type: string
          severity: 'low' | 'medium' | 'high' | 'critical'
          message: string
          line?: number
          suggestion?: string
        }>
        suggestions?: Array<{
          type: string
          description: string
          code?: string
          explanation?: string
        }>
        optimized_code?: string
        debug_info?: Record<string, any>
      }
      created_at: string
    }>('/api/v1/ai/analyze', {
      code,
      language,
      ...options
    })
  }

  async explainCode(code: string, language: string): Promise<ApiResponse<{
    explanation: string
    complexity: 'low' | 'medium' | 'high'
    concepts: string[]
    examples?: Array<{
      concept: string
      example: string
      explanation: string
    }>
  }>> {
    return apiClient.post<{
      explanation: string
      complexity: 'low' | 'medium' | 'high'
      concepts: string[]
      examples?: Array<{
        concept: string
        example: string
        explanation: string
      }>
    }>('/api/v1/ai/explain', { code, language })
  }

  async reviewCode(code: string, language: string, options?: {
    style_guide?: string
    security_focus?: boolean
    performance_focus?: boolean
  }): Promise<ApiResponse<{
    review: {
      overall_score: number
      issues: Array<{
        type: string
        severity: 'low' | 'medium' | 'high' | 'critical'
        message: string
        line?: number
        suggestion: string
      }>
      suggestions: Array<{
        type: string
        description: string
        code?: string
        explanation: string
      }>
      best_practices: string[]
    }
    summary: string
  }>> {
    return apiClient.post<{
      review: {
        overall_score: number
        issues: Array<{
          type: string
          severity: 'low' | 'medium' | 'high' | 'critical'
          message: string
          line?: number
          suggestion: string
        }>
        suggestions: Array<{
          type: string
          description: string
          code?: string
          explanation: string
        }>
        best_practices: string[]
      }
      summary: string
    }>('/api/v1/ai/review', {
      code,
      language,
      ...options
    })
  }

  async refactorCode(code: string, language: string, options?: {
    target_style?: string
    improve_performance?: boolean
    add_comments?: boolean
    simplify?: boolean
  }): Promise<ApiResponse<{
    refactored_code: string
    changes: Array<{
      type: string
      description: string
      before: string
      after: string
    }>
    explanation: string
    benefits: string[]
  }>> {
    return apiClient.post<{
      refactored_code: string
      changes: Array<{
        type: string
        description: string
        before: string
        after: string
      }>
      explanation: string
      benefits: string[]
    }>('/api/v1/ai/refactor', {
      code,
      language,
      ...options
    })
  }

  async optimizeCode(code: string, language: string, options?: {
    focus?: 'performance' | 'memory' | 'readability'
    target_environment?: string
  }): Promise<ApiResponse<{
    optimized_code: string
    optimizations: Array<{
      type: string
      description: string
      impact: 'low' | 'medium' | 'high'
      before: string
      after: string
    }>
    performance_improvement: {
      time_complexity?: string
      space_complexity?: string
      estimated_speedup?: number
    }
    explanation: string
  }>> {
    return apiClient.post<{
      optimized_code: string
      optimizations: Array<{
        type: string
        description: string
        impact: 'low' | 'medium' | 'high'
        before: string
        after: string
      }>
      performance_improvement: {
        time_complexity?: string
        space_complexity?: string
        estimated_speedup?: number
      }
      explanation: string
    }>('/api/v1/ai/optimize', {
      code,
      language,
      ...options
    })
  }

  async debugCode(code: string, language: string, error?: string): Promise<ApiResponse<{
    debug_info: {
      potential_issues: Array<{
        type: string
        description: string
        line?: number
        confidence: number
      }>
      suggestions: Array<{
        type: string
        description: string
        code?: string
        explanation: string
      }>
      fixed_code?: string
    }
    explanation: string
  }>> {
    return apiClient.post<{
      debug_info: {
        potential_issues: Array<{
          type: string
          description: string
          line?: number
          confidence: number
        }>
        suggestions: Array<{
          type: string
          description: string
          code?: string
          explanation: string
        }>
        fixed_code?: string
      }
      explanation: string
    }>('/api/v1/ai/debug', {
      code,
      language,
      error
    })
  }

  // AI search
  async searchCodebase(query: string, options?: {
    project_id?: string
    file_types?: string[]
    max_results?: number
    context?: Record<string, any>
  }): Promise<ApiResponse<{
    results: Array<{
      file: string
      line: number
      content: string
      relevance_score: number
      explanation: string
      suggestions?: string[]
    }>
    summary: string
    total_matches: number
  }>> {
    return apiClient.post<{
      results: Array<{
        file: string
        line: number
        content: string
        relevance_score: number
        explanation: string
        suggestions?: string[]
      }>
      summary: string
      total_matches: number
    }>('/api/v1/ai/search', {
      query,
      ...options
    })
  }

  // AI models and settings
  async getAvailableModels(): Promise<ApiResponse<Array<{
    id: string
    name: string
    provider: string
    capabilities: string[]
    context_window: number
    pricing: {
      input_tokens: number
      output_tokens: number
    }
    is_default: boolean
  }>>> {
    return apiClient.get<Array<{
      id: string
      name: string
      provider: string
      capabilities: string[]
      context_window: number
      pricing: {
        input_tokens: number
        output_tokens: number
      }
      is_default: boolean
    }>>('/api/v1/ai/models')
  }

  async getCurrentModel(): Promise<ApiResponse<{
    id: string
    name: string
    provider: string
    capabilities: string[]
    context_window: number
  }>> {
    return apiClient.get<{
      id: string
      name: string
      provider: string
      capabilities: string[]
      context_window: number
    }>('/api/v1/ai/models/current')
  }

  async setCurrentModel(modelId: string): Promise<ApiResponse<{
    id: string
    name: string
    provider: string
    capabilities: string[]
    context_window: number
  }>> {
    return apiClient.put<{
      id: string
      name: string
      provider: string
      capabilities: string[]
      context_window: number
    }>('/api/v1/ai/models/current', { model_id: modelId })
  }

  // AI usage analytics
  async getAIUsageAnalytics(period?: 'day' | 'week' | 'month' | 'year'): Promise<ApiResponse<{
    total_requests: number
    total_tokens: number
    total_cost: number
    usage_by_type: Record<string, number>
    usage_trends: Array<{
      date: string
      requests: number
      tokens: number
      cost: number
    }>
    popular_features: Array<{
      feature: string
      usage_count: number
      percentage: number
    }>
  }>> {
    const params = period ? `?period=${period}` : ''
    return apiClient.get<{
      total_requests: number
      total_tokens: number
      total_cost: number
      usage_by_type: Record<string, number>
      usage_trends: Array<{
        date: string
        requests: number
        tokens: number
        cost: number
      }>
      popular_features: Array<{
        feature: string
        usage_count: number
        percentage: number
      }>
    }>(`/api/v1/ai/analytics${params}`)
  }

  // AI settings
  async getAISettings(): Promise<ApiResponse<{
    default_model: string
    temperature: number
    max_tokens: number
    enable_streaming: boolean
    features: Record<string, boolean>
    rate_limits: {
      requests_per_minute: number
      tokens_per_minute: number
    }
  }>> {
    return apiClient.get<{
      default_model: string
      temperature: number
      max_tokens: number
      enable_streaming: boolean
      features: Record<string, boolean>
      rate_limits: {
        requests_per_minute: number
        tokens_per_minute: number
      }
    }>('/api/v1/ai/settings')
  }

  async updateAISettings(settings: {
    default_model?: string
    temperature?: number
    max_tokens?: number
    enable_streaming?: boolean
    features?: Record<string, boolean>
    rate_limits?: {
      requests_per_minute?: number
      tokens_per_minute?: number
    }
  }): Promise<ApiResponse<{
    default_model: string
    temperature: number
    max_tokens: number
    enable_streaming: boolean
    features: Record<string, boolean>
    rate_limits: {
      requests_per_minute: number
      tokens_per_minute: number
    }
  }>> {
    return apiClient.put<{
      default_model: string
      temperature: number
      max_tokens: number
      enable_streaming: boolean
      features: Record<string, boolean>
      rate_limits: {
        requests_per_minute: number
        tokens_per_minute: number
      }
    }>('/api/v1/ai/settings', settings)
  }
}

// Create and export service instance
export const aiService = new AIService()
export default aiService
