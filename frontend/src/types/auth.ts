// Authentication Types
export interface User {
  id: string
  email: string
  username: string
  full_name?: string
  avatar_url?: string
  is_active: boolean
  is_superuser: boolean
  created_at: string
  updated_at: string
  last_login?: string
  organization?: Organization
}

export interface Organization {
  id: string
  name: string
  slug: string
  description?: string
  settings: Record<string, any>
  created_at: string
  updated_at: string
}

export interface OrganizationMember {
  id: string
  organization_id: string
  user_id: string
  role: 'owner' | 'admin' | 'developer' | 'viewer'
  permissions: Record<string, any>
  joined_at: string
  user?: User
  organization?: Organization
}

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
