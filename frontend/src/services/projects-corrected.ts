// Projects Service - Corrected Version
import { apiClient } from './api-client-working'
import {
  Project,
  ProjectCreate,
  ProjectUpdate,
  ProjectSettings,
  ProjectStats,
  ProjectMember,
  ProjectTemplate,
  Repository,
  RepositoryConfig
} from '../types/project-corrected'
import { PaginationParams } from '../types/common-corrected'
import { ApiResponse } from '../types/api-corrected'

export class ProjectsService {
  // Project CRUD operations
  async getProjects(params?: PaginationParams): Promise<ApiResponse<Project[]>> {
    const queryParams = new URLSearchParams()
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, String(value))
        }
      })
    }

    const endpoint = `/api/v1/projects${queryParams.toString() ? `?${queryParams.toString()}` : ''}`
    return apiClient.get<Project[]>(endpoint)
  }

  async getProject(projectId: string): Promise<ApiResponse<Project>> {
    return apiClient.get<Project>(`/api/v1/projects/${projectId}`)
  }

  async createProject(project: ProjectCreate): Promise<ApiResponse<Project>> {
    return apiClient.post<Project>('/api/v1/projects', project)
  }

  async updateProject(projectId: string, project: ProjectUpdate): Promise<ApiResponse<Project>> {
    return apiClient.put<Project>(`/api/v1/projects/${projectId}`, project)
  }

  async deleteProject(projectId: string): Promise<ApiResponse<void>> {
    return apiClient.delete<void>(`/api/v1/projects/${projectId}`)
  }

  async archiveProject(projectId: string): Promise<ApiResponse<Project>> {
    return apiClient.patch<Project>(`/api/v1/projects/${projectId}/archive`)
  }

  async unarchiveProject(projectId: string): Promise<ApiResponse<Project>> {
    return apiClient.patch<Project>(`/api/v1/projects/${projectId}/unarchive`)
  }

  // Project settings
  async getProjectSettings(projectId: string): Promise<ApiResponse<ProjectSettings>> {
    return apiClient.get<ProjectSettings>(`/api/v1/projects/${projectId}/settings`)
  }

  async updateProjectSettings(projectId: string, settings: Partial<ProjectSettings>): Promise<ApiResponse<ProjectSettings>> {
    return apiClient.put<ProjectSettings>(`/api/v1/projects/${projectId}/settings`, settings)
  }

  // Project statistics
  async getProjectStats(projectId: string): Promise<ApiResponse<ProjectStats>> {
    return apiClient.get<ProjectStats>(`/api/v1/projects/${projectId}/stats`)
  }

  async getProjectActivity(projectId: string, days: number = 30): Promise<ApiResponse<{
    date: string
    commits: number
    analyses: number
    issues: number
  }[]>> {
    return apiClient.get<{
      date: string
      commits: number
      analyses: number
      issues: number
    }[]>(`/api/v1/projects/${projectId}/activity?days=${days}`)
  }

  // Project members
  async getProjectMembers(projectId: string): Promise<ApiResponse<ProjectMember[]>> {
    return apiClient.get<ProjectMember[]>(`/api/v1/projects/${projectId}/members`)
  }

  async addProjectMember(projectId: string, member: {
    user_id: string
    role: 'owner' | 'admin' | 'developer' | 'viewer'
    permissions?: Record<string, any>
  }): Promise<ApiResponse<ProjectMember>> {
    return apiClient.post<ProjectMember>(`/api/v1/projects/${projectId}/members`, member)
  }

  async updateProjectMember(projectId: string, memberId: string, updates: {
    role?: 'owner' | 'admin' | 'developer' | 'viewer'
    permissions?: Record<string, any>
  }): Promise<ApiResponse<ProjectMember>> {
    return apiClient.put<ProjectMember>(`/api/v1/projects/${projectId}/members/${memberId}`, updates)
  }

  async removeProjectMember(projectId: string, memberId: string): Promise<ApiResponse<void>> {
    return apiClient.delete<void>(`/api/v1/projects/${projectId}/members/${memberId}`)
  }

  // Repository management
  async getProjectRepositories(projectId: string): Promise<ApiResponse<Repository[]>> {
    return apiClient.get<Repository[]>(`/api/v1/projects/${projectId}/repositories`)
  }

  async addRepository(projectId: string, config: RepositoryConfig): Promise<ApiResponse<Repository>> {
    return apiClient.post<Repository>(`/api/v1/projects/${projectId}/repositories`, config)
  }

  async updateRepository(projectId: string, repoId: string, config: Partial<RepositoryConfig>): Promise<ApiResponse<Repository>> {
    return apiClient.put<Repository>(`/api/v1/projects/${projectId}/repositories/${repoId}`, config)
  }

  async removeRepository(projectId: string, repoId: string): Promise<ApiResponse<void>> {
    return apiClient.delete<void>(`/api/v1/projects/${projectId}/repositories/${repoId}`)
  }

  async syncRepository(projectId: string, repoId: string): Promise<ApiResponse<void>> {
    return apiClient.post<void>(`/api/v1/projects/${projectId}/repositories/${repoId}/sync`)
  }

  // Project templates
  async getProjectTemplates(): Promise<ApiResponse<ProjectTemplate[]>> {
    return apiClient.get<ProjectTemplate[]>('/api/v1/projects/templates')
  }

  async createProjectFromTemplate(templateId: string, project: Omit<ProjectCreate, 'template_id'>): Promise<ApiResponse<Project>> {
    return apiClient.post<Project>('/api/v1/projects/from-template', {
      template_id: templateId,
      ...project
    })
  }

  // Project search and filtering
  async searchProjects(query: string, filters?: {
    status?: 'active' | 'archived' | 'deleted'
    owner?: string
    tags?: string[]
    created_after?: string
    created_before?: string
  }): Promise<ApiResponse<Project[]>> {
    const params = new URLSearchParams({ q: query })
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined) {
          if (Array.isArray(value)) {
            value.forEach(v => params.append(`filter_${key}`, v))
          } else {
            params.append(`filter_${key}`, String(value))
          }
        }
      })
    }
    return apiClient.get<Project[]>(`/api/v1/projects/search?${params.toString()}`)
  }

  // Project validation
  async validateProjectConfig(project: ProjectCreate | ProjectUpdate): Promise<ApiResponse<{
    valid: boolean
    errors: string[]
    warnings: string[]
  }>> {
    return apiClient.post<{
      valid: boolean
      errors: string[]
      warnings: string[]
    }>('/api/v1/projects/validate', project)
  }

  // Project transfer
  async transferProject(projectId: string, newOwnerId: string): Promise<ApiResponse<Project>> {
    return apiClient.post<Project>(`/api/v1/projects/${projectId}/transfer`, {
      new_owner_id: newOwnerId
    })
  }

  // Project favorites
  async getFavoriteProjects(): Promise<ApiResponse<Project[]>> {
    return apiClient.get<Project[]>('/api/v1/projects/favorites')
  }

  async addToFavorites(projectId: string): Promise<ApiResponse<void>> {
    return apiClient.post<void>(`/api/v1/projects/${projectId}/favorite`)
  }

  async removeFromFavorites(projectId: string): Promise<ApiResponse<void>> {
    return apiClient.delete<void>(`/api/v1/projects/${projectId}/favorite`)
  }

  // Project tags
  async getProjectTags(projectId: string): Promise<ApiResponse<string[]>> {
    return apiClient.get<string[]>(`/api/v1/projects/${projectId}/tags`)
  }

  async updateProjectTags(projectId: string, tags: string[]): Promise<ApiResponse<string[]>> {
    return apiClient.put<string[]>(`/api/v1/projects/${projectId}/tags`, { tags })
  }

  // Project export/import
  async exportProject(projectId: string, format: 'json' | 'yaml' | 'zip' = 'json'): Promise<ApiResponse<Blob>> {
    return apiClient.get<Blob>(`/api/v1/projects/${projectId}/export?format=${format}`, {
      responseType: 'blob'
    })
  }

  async importProject(projectData: any, options?: {
    overwrite?: boolean
    skip_validation?: boolean
  }): Promise<ApiResponse<Project>> {
    return apiClient.post<Project>('/api/v1/projects/import', {
      ...projectData,
      options
    })
  }
}

// Create and export service instance
export const projectsService = new ProjectsService()
export default projectsService
