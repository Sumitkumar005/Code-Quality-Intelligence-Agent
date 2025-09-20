// WebSocket Service
import { ApiResponse } from '../types/api-corrected'

export interface WebSocketMessage {
  type: string
  payload: any
  timestamp: string
  id: string
}

export interface WebSocketEvent {
  type: 'analysis_progress' | 'analysis_complete' | 'analysis_error' | 'project_update' | 'notification' | 'chat_message'
  data: any
  timestamp: string
}

export interface AnalysisProgressData {
  analysis_id: string
  progress: number
  current_step: string
  estimated_time_remaining: number
  logs: string[]
  status: 'pending' | 'running' | 'paused' | 'completed' | 'failed'
}

export interface AnalysisCompleteData {
  analysis_id: string
  result: {
    total_issues: number
    quality_score: number
    metrics: Record<string, any>
  }
  report_url?: string
}

export interface AnalysisErrorData {
  analysis_id: string
  error: string
  error_code: string
  details?: Record<string, any>
}

export interface ProjectUpdateData {
  project_id: string
  type: 'created' | 'updated' | 'deleted' | 'archived'
  changes: Record<string, any>
}

export interface NotificationData {
  id: string
  type: 'info' | 'warning' | 'error' | 'success'
  title: string
  message: string
  actions?: {
    label: string
    action: string
    url?: string
  }[]
}

export interface ChatMessageData {
  session_id: string
  message: {
    id: string
    role: 'user' | 'assistant'
    content: string
    timestamp: string
  }
}

export type WebSocketEventHandler = (event: WebSocketEvent) => void

export class WebSocketService {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000
  private eventHandlers: Map<string, WebSocketEventHandler[]> = new Map()
  private isConnecting = false
  private shouldReconnect = true

  // Connection management
  async connect(token?: string): Promise<void> {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return
    }

    if (this.isConnecting) {
      return
    }

    this.isConnecting = true

    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const wsUrl = `${protocol}//${window.location.host}/ws`

      const url = token ? `${wsUrl}?token=${token}` : wsUrl

      this.ws = new WebSocket(url)

      return new Promise((resolve, reject) => {
        if (!this.ws) {
          reject(new Error('WebSocket not initialized'))
          return
        }

        this.ws.onopen = () => {
          console.log('WebSocket connected')
          this.reconnectAttempts = 0
          this.isConnecting = false
          this.emit('connected', { timestamp: new Date().toISOString() })
          resolve()
        }

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data)
            this.handleMessage(message)
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error)
          }
        }

        this.ws.onclose = (event) => {
          console.log('WebSocket disconnected:', event.code, event.reason)
          this.isConnecting = false
          this.emit('disconnected', {
            code: event.code,
            reason: event.reason,
            timestamp: new Date().toISOString()
          })

          if (this.shouldReconnect && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.attemptReconnect()
          }
        }

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error)
          this.isConnecting = false
          reject(error)
        }
      })
    } catch (error) {
      this.isConnecting = false
      throw error
    }
  }

  disconnect(): void {
    this.shouldReconnect = false
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect')
      this.ws = null
    }
  }

  private attemptReconnect(): void {
    this.reconnectAttempts++
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1)

    console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`)

    setTimeout(() => {
      if (this.shouldReconnect) {
        this.connect().catch(error => {
          console.error('Reconnection failed:', error)
        })
      }
    }, delay)
  }

  // Message handling
  private handleMessage(message: WebSocketMessage): void {
    const event: WebSocketEvent = {
      type: message.type,
      data: message.payload,
      timestamp: message.timestamp
    }

    this.emit(message.type, event)
    this.emit('message', event)
  }

  // Event subscription
  on(eventType: string, handler: WebSocketEventHandler): void {
    if (!this.eventHandlers.has(eventType)) {
      this.eventHandlers.set(eventType, [])
    }
    this.eventHandlers.get(eventType)!.push(handler)
  }

  off(eventType: string, handler: WebSocketEventHandler): void {
    const handlers = this.eventHandlers.get(eventType)
    if (handlers) {
      const index = handlers.indexOf(handler)
      if (index > -1) {
        handlers.splice(index, 1)
      }
    }
  }

  private emit(eventType: string, event: WebSocketEvent): void {
    const handlers = this.eventHandlers.get(eventType)
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(event)
        } catch (error) {
          console.error('Error in WebSocket event handler:', error)
        }
      })
    }
  }

  // Specific event handlers
  onAnalysisProgress(handler: (data: AnalysisProgressData) => void): void {
    this.on('analysis_progress', (event) => {
      handler(event.data as AnalysisProgressData)
    })
  }

  onAnalysisComplete(handler: (data: AnalysisCompleteData) => void): void {
    this.on('analysis_complete', (event) => {
      handler(event.data as AnalysisCompleteData)
    })
  }

  onAnalysisError(handler: (data: AnalysisErrorData) => void): void {
    this.on('analysis_error', (event) => {
      handler(event.data as AnalysisErrorData)
    })
  }

  onProjectUpdate(handler: (data: ProjectUpdateData) => void): void {
    this.on('project_update', (event) => {
      handler(event.data as ProjectUpdateData)
    })
  }

  onNotification(handler: (data: NotificationData) => void): void {
    this.on('notification', (event) => {
      handler(event.data as NotificationData)
    })
  }

  onChatMessage(handler: (data: ChatMessageData) => void): void {
    this.on('chat_message', (event) => {
      handler(event.data as ChatMessageData)
    })
  }

  // Connection status
  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }

  get isConnecting(): boolean {
    return this.ws?.readyState === WebSocket.CONNECTING
  }

  get connectionState(): 'connected' | 'connecting' | 'disconnected' {
    if (this.ws?.readyState === WebSocket.OPEN) return 'connected'
    if (this.ws?.readyState === WebSocket.CONNECTING) return 'connecting'
    return 'disconnected'
  }

  // Send messages
  send(type: string, payload: any): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      const message: WebSocketMessage = {
        type,
        payload,
        timestamp: new Date().toISOString(),
        id: crypto.randomUUID()
      }
      this.ws.send(JSON.stringify(message))
    } else {
      console.warn('WebSocket not connected, cannot send message')
    }
  }

  // Subscribe to specific analysis
  subscribeToAnalysis(analysisId: string): void {
    this.send('subscribe_analysis', { analysis_id: analysisId })
  }

  unsubscribeFromAnalysis(analysisId: string): void {
    this.send('unsubscribe_analysis', { analysis_id: analysisId })
  }

  // Subscribe to project updates
  subscribeToProject(projectId: string): void {
    this.send('subscribe_project', { project_id: projectId })
  }

  unsubscribeFromProject(projectId: string): void {
    this.send('unsubscribe_project', { project_id: projectId })
  }

  // Chat subscription
  subscribeToChat(sessionId: string): void {
    this.send('subscribe_chat', { session_id: sessionId })
  }

  unsubscribeFromChat(sessionId: string): void {
    this.send('unsubscribe_chat', { session_id: sessionId })
  }

  // Health check
  ping(): void {
    this.send('ping', { timestamp: new Date().toISOString() })
  }

  // Connection management
  enableReconnect(): void {
    this.shouldReconnect = true
  }

  disableReconnect(): void {
    this.shouldReconnect = false
  }
}

// Create and export service instance
export const websocketService = new WebSocketService()
export default websocketService
