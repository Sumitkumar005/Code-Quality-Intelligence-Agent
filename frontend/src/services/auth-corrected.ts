// Authentication Service - Corrected Version
import { apiClient } from './api-client-working'
import {
  LoginCredentials,
  RegisterData,
  AuthTokens,
  User,
  AuthState,
  JWTPayload,
  Permission
} from '../types/auth-corrected'
import { RolePermissions } from '../types/common-corrected'
import { ApiResponse } from '../types/api-corrected'

export class AuthService {
  // Authentication endpoints
  async login(credentials: LoginCredentials): Promise<ApiResponse<AuthTokens>> {
    return apiClient.post('/auth/login', credentials)
  }

  async register(userData: RegisterData): Promise<ApiResponse<AuthTokens>> {
    return apiClient.post('/auth/register', userData)
  }

  async refreshToken(): Promise<ApiResponse<AuthTokens>> {
    return apiClient.post('/auth/refresh')
  }

  async logout(): Promise<ApiResponse<void>> {
    return apiClient.post('/auth/logout')
  }

  async getCurrentUser(): Promise<ApiResponse<User>> {
    return apiClient.get('/auth/me')
  }

  async updateProfile(userData: Partial<User>): Promise<ApiResponse<User>> {
    return apiClient.put('/auth/profile', userData)
  }

  async changePassword(data: {
    current_password: string
    new_password: string
  }): Promise<ApiResponse<void>> {
    return apiClient.post('/auth/change-password', data)
  }

  // OAuth endpoints
  async oauthLogin(provider: string, code: string): Promise<ApiResponse<AuthTokens>> {
    return apiClient.post(`/auth/oauth/${provider}`, { code })
  }

  async oauthCallback(provider: string, state: string): Promise<ApiResponse<AuthTokens>> {
    return apiClient.get(`/auth/oauth/${provider}/callback`, {
      params: { state }
    })
  }

  // Token validation
  async validateToken(token: string): Promise<ApiResponse<JWTPayload>> {
    return apiClient.post('/auth/validate', { token })
  }

  async revokeToken(token: string): Promise<ApiResponse<void>> {
    return apiClient.post('/auth/revoke', { token })
  }

  // Permission helpers
  hasPermission(user: User | null, resource: string, action: Permission['action']): boolean {
    if (!user || !user.permissions) return false

    return user.permissions.some((perm: Permission) =>
      perm.resource === resource && perm.action === action
    )
  }

  hasRole(user: User | null, requiredRole: string): boolean {
    if (!user || !user.role) return false
    return user.role === requiredRole
  }

  getRolePermissions(role: string): Permission[] {
    return RolePermissions[role] || []
  }

  // Local storage helpers
  saveTokens(tokens: AuthTokens): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', tokens.access_token)
      localStorage.setItem('refresh_token', tokens.refresh_token)
      localStorage.setItem('token_type', tokens.token_type)
    }
  }

  getStoredTokens(): AuthTokens | null {
    if (typeof window === 'undefined') return null

    const accessToken = localStorage.getItem('access_token')
    const refreshToken = localStorage.getItem('refresh_token')
    const tokenType = localStorage.getItem('token_type')

    if (!accessToken || !refreshToken || !tokenType) return null

    return {
      access_token: accessToken,
      refresh_token: refreshToken,
      token_type: tokenType,
      expires_in: 0 // We don't store this locally
    }
  }

  clearTokens(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('token_type')
    }
  }

  // Auth state management
  isAuthenticated(): boolean {
    const tokens = this.getStoredTokens()
    return tokens !== null && tokens.access_token.length > 0
  }

  getAuthHeaders(): Record<string, string> {
    const tokens = this.getStoredTokens()
    if (!tokens) return {}

    return {
      'Authorization': `${tokens.token_type} ${tokens.access_token}`
    }
  }
}

// Create and export service instance
export const authService = new AuthService()
export default authService
