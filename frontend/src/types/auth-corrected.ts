// Authentication Types
export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  email: string
  username: string
  password: string
  full_name?: string
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface JWTPayload {
  user_id: string
  username: string
  org_id?: string
  permissions: string[]
  exp: number
  iat: number
  jti: string
}

export interface AuthState {
  user: User | null
  organization: Organization | null
  tokens: AuthTokens | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}

export interface Permission {
  resource: string
  action: 'read' | 'write' | 'delete' | 'admin'
}

export interface RolePermissions {
  owner: Permission[]
  admin: Permission[]
  developer: Permission[]
  viewer: Permission[]
}

// Import types from common
import { User, Organization } from './common-corrected'
