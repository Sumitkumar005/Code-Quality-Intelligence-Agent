// AI Service
import { apiClient } from './api-client-working'
import { ApiResponse } from '../types/api-corrected'

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: string
  metadata?: Record<string, any>
}

export interface ChatSession {
  id: string
  title: string
  project_id?: string
  analysis_id?: string
  created_at: string
  updated_at: string
  messages: ChatMessage[]
}

export interface AIInsight {
  id: string
  type: 'suggestion' | 'warning' | 'info' | 'error'
  title: string
  description: string
  code_snippet?: string
  file_path?: string
  line_start?: number
  line_end?: number
  confidence: number
  impact: 'low' | 'medium' | 'high' | 'critical'
  category: string
  tags: string[]
}

export interface CodeExplanation {
  summary: string
  details: string
  examples: string[]
  best_practices: string[]
  common_issues: string[]
}

export interface RefactoringSuggestion {
  id: string
  title: string
  description: string
  type: 'performance' | 'security' | 'maintainability' | 'readability'
  priority: 'low' | 'medium' | 'high' | 'critical'
  effort: 'small' | 'medium' | 'large'
  code_before: string
  code_after: string
  explanation: string
  benefits: string[]
  risks: string[]
}

export interface CodeReview {
  overall_score: number
  summary: string
  strengths: string[]
  issues: {
    type: string
    severity: 'low' | 'medium' | 'high' | 'critical'
    description: string
    suggestion: string
    line?: number
    file?: string
  }[]
  suggestions: string[]
  files_reviewed: string[]
}

export class AIService {
  // Chat operations
  async createChatSession(projectId?: string, analysisId?: string): Promise<ApiResponse<ChatSession>> {
    return apiClient.post<ChatSession>('/api/v1/chat/sessions', {
      project_id: projectId,
      analysis_id: analysisId
    })
  }

  async getChatSessions(): Promise<ApiResponse<ChatSession[]>> {
    return apiClient.get<ChatSession[]>('/api/v1/chat/sessions')
  }

  async getChatSession(sessionId: string): Promise<ApiResponse<ChatSession>> {
    return apiClient.get<ChatSession>(`/api/v1/chat/sessions/${sessionId}`)
  }

  async sendMessage(sessionId: string, message: string, context?: Record<string, any>): Promise<ApiResponse<ChatMessage>> {
    return apiClient.post<ChatMessage>(`/api/v1/chat/sessions/${sessionId}/messages`, {
      content: message,
      context
    })
  }

  async getChatMessages(sessionId: string): Promise<ApiResponse<ChatMessage[]>> {
    return apiClient.get<ChatMessage[]>(`/api/v1/chat/sessions/${sessionId}/messages`)
  }

  async deleteChatSession(sessionId: string): Promise<ApiResponse<void>> {
    return apiClient.delete<void>(`/api/v1/chat/sessions/${sessionId}`)
  }

  // AI insights
  async getAIInsights(projectId: string, analysisId?: string): Promise<ApiResponse<AIInsight[]>> {
    const endpoint = analysisId
      ? `/api/v1/projects/${projectId}/insights?analysis_id=${analysisId}`
      : `/api/v1/projects/${projectId}/insights`
    return apiClient.get<AIInsight[]>(endpoint)
  }

  async getAIInsight(insightId: string): Promise<ApiResponse<AIInsight>> {
    return apiClient.get<AIInsight>(`/api/v1/insights/${insightId}`)
  }

  async applyAIInsight(insightId: string, action: 'accept' | 'reject' | 'modify'): Promise<ApiResponse<AIInsight>> {
    return apiClient.post<AIInsight>(`/api/v1/insights/${insightId}/apply`, { action })
  }

  // Code explanation
  async explainCode(code: string, language: string, context?: string): Promise<ApiResponse<CodeExplanation>> {
    return apiClient.post<CodeExplanation>('/api/v1/ai/explain', {
      code,
      language,
      context
    })
  }

  async explainIssue(issueId: string, analysisId: string): Promise<ApiResponse<CodeExplanation>> {
    return apiClient.get<CodeExplanation>(`/api/v1/analyses/${analysisId}/issues/${issueId}/explain`)
  }

  // Refactoring suggestions
  async getRefactoringSuggestions(projectId: string, filePath?: string): Promise<ApiResponse<RefactoringSuggestion[]>> {
    const endpoint = filePath
      ? `/api/v1/projects/${projectId}/refactor?file_path=${encodeURIComponent(filePath)}`
      : `/api/v1/projects/${projectId}/refactor`
    return apiClient.get<RefactoringSuggestion[]>(endpoint)
  }

  async applyRefactoring(projectId: string, suggestionId: string): Promise<ApiResponse<{
    success: boolean
    changes: string[]
    error?: string
  }>> {
    return apiClient.post<{
      success: boolean
      changes: string[]
      error?: string
    }>(`/api/v1/projects/${projectId}/refactor/${suggestionId}/apply`)
  }

  // Code review
  async requestCodeReview(projectId: string, files: string[], options?: {
    focus_areas?: string[]
    severity_threshold?: 'low' | 'medium' | 'high'
    include_suggestions?: boolean
  }): Promise<ApiResponse<CodeReview>> {
    return apiClient.post<CodeReview>('/api/v1/ai/code-review', {
      project_id: projectId,
      files,
      options
    })
  }

  async getCodeReview(reviewId: string): Promise<ApiResponse<CodeReview>> {
    return apiClient.get<CodeReview>(`/api/v1/ai/code-review/${reviewId}`)
  }

  // AI-powered search
  async searchCodebase(projectId: string, query: string, options?: {
    file_types?: string[]
    max_results?: number
    include_snippets?: boolean
  }): Promise<ApiResponse<{
    results: {
      file: string
      line: number
      content: string
      score: number
      context: string
    }[]
    total: number
  }>> {
    return apiClient.post<{
      results: {
        file: string
        line: number
        content: string
        score: number
        context: string
      }[]
      total: number
    }>('/api/v1/ai/search', {
      project_id: projectId,
      query,
      options
    })
  }

  // AI configuration
  async getAIConfig(): Promise<ApiResponse<{
    available_models: string[]
    default_model: string
    features: {
      code_explanation: boolean
      refactoring: boolean
      code_review: boolean
      chat: boolean
    }
  }>> {
    return apiClient.get<{
      available_models: string[]
      default_model: string
      features: {
        code_explanation: boolean
        refactoring: boolean
        code_review: boolean
        chat: boolean
      }
    }>('/api/v1/ai/config')
  }

  async updateAIConfig(config: Partial<{
    default_model: string
    features: Record<string, boolean>
  }>): Promise<ApiResponse<{
    available_models: string[]
    default_model: string
    features: Record<string, boolean>
  }>> {
    return apiClient.put<{
      available_models: string[]
      default_model: string
      features: Record<string, boolean>
    }>('/api/v1/ai/config', config)
  }

  // AI model management
  async listAvailableModels(): Promise<ApiResponse<{
    models: {
      id: string
      name: string
      provider: string
      capabilities: string[]
      context_window: number
      pricing: {
        input_tokens: number
        output_tokens: number
      }
    }[]
  }>> {
    return apiClient.get<{
      models: {
        id: string
        name: string
        provider: string
        capabilities: string[]
        context_window: number
        pricing: {
          input_tokens: number
          output_tokens: number
        }
      }[]
    }>('/api/v1/ai/models')
  }

  async testModel(modelId: string, testInput: string): Promise<ApiResponse<{
    success: boolean
    response: string
    latency: number
    error?: string
  }>> {
    return apiClient.post<{
      success: boolean
      response: string
      latency: number
      error?: string
    }>('/api/v1/ai/models/test', {
      model_id: modelId,
      test_input: testInput
    })
  }

  // AI usage analytics
  async getAIUsageStats(): Promise<ApiResponse<{
    total_requests: number
    total_tokens: number
    cost_estimate: number
    daily_usage: {
      date: string
      requests: number
      tokens: number
    }[]
    feature_usage: Record<string, number>
  }>> {
    return apiClient.get<{
      total_requests: number
      total_tokens: number
      cost_estimate: number
      daily_usage: {
        date: string
        requests: number
        tokens: number
      }[]
      feature_usage: Record<string, number>
    }>('/api/v1/ai/usage')
  }
}

// Create and export service instance
export const aiService = new AIService()
export default aiService
