// Common/Base Types
export interface BaseEntity {
  id: string
  created_at: string
  updated_at: string
}

export interface User extends BaseEntity {
  email: string
  username: string
  full_name?: string
  avatar_url?: string
  is_active: boolean
  is_superuser: boolean
  last_login?: string
  organization?: Organization
}

export interface Organization extends BaseEntity {
  name: string
  slug: string
  description?: string
  settings: Record<string, any>
  members?: OrganizationMember[]
}

export interface OrganizationMember extends BaseEntity {
  organization_id: string
  user_id: string
  role: 'owner' | 'admin' | 'developer' | 'viewer'
  permissions: Record<string, any>
  user?: User
  organization?: Organization
}

// Status and State Types
export type Status = 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled'
export type Priority = 'low' | 'medium' | 'high' | 'critical'
export type Severity = 'info' | 'warning' | 'error' | 'critical'

// Pagination Types
export interface PaginationParams {
  page?: number
  per_page?: number
  sort_by?: string
  sort_order?: 'asc' | 'desc'
  search?: string
  filters?: Record<string, any>
}

// Filter and Sort Types
export interface FilterOption {
  key: string
  label: string
  type: 'text' | 'select' | 'date' | 'boolean'
  options?: { value: string; label: string }[]
}

export interface SortOption {
  key: string
  label: string
  direction: 'asc' | 'desc'
}

// UI State Types
export interface LoadingState {
  isLoading: boolean
  error: string | null
  message?: string
}

export interface TableState {
  pagination: PaginationParams
  sorting: SortOption[]
  filters: Record<string, any>
  selectedRows: string[]
}

// Form Types
export interface FormField {
  name: string
  label: string
  type: 'text' | 'email' | 'password' | 'select' | 'textarea' | 'checkbox' | 'radio'
  required?: boolean
  placeholder?: string
  options?: { value: string; label: string }[]
  validation?: Record<string, any>
}

export interface FormState {
  isSubmitting: boolean
  isDirty: boolean
  errors: Record<string, string>
  values: Record<string, any>
}
