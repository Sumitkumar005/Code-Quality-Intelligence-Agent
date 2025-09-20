// Projects Service
import { apiClient } from './api-client-working'
import {
  Project,
  CreateProjectRequest,
  UpdateProjectRequest,
  ProjectListResponse,
  ProjectStats,
  ProjectSettings,
  Repository,
  ProjectMember,
  ProjectActivity
} from '../types/project'
import { PaginationParams, Status } from '../types/common-corrected'
import { ApiResponse } from '../types/api-corrected'

export class ProjectsService {
  // Project CRUD operations
  async getProjects(params?: PaginationParams): Promise<ApiResponse<ProjectListResponse>> {
    const queryParams = new URLSearchParams()
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, String(value))
        }
      })
    }

    const endpoint = `/api/v1/projects${queryParams.toString() ? `?${queryParams.toString()}` : ''}`
    return apiClient.get<ProjectListResponse>(endpoint)
  }

  async getProject(projectId: string): Promise<ApiResponse<Project>> {
    return apiClient.get<Project>(`/api/v1/projects/${projectId}`)
  }

  async createProject(data: CreateProjectRequest): Promise<ApiResponse<Project>> {
    return apiClient.post<Project>('/api/v1/projects', data)
  }

  async updateProject(projectId: string, data: UpdateProjectRequest): Promise<ApiResponse<Project>> {
    return apiClient.put<Project>(`/api/v1/projects/${projectId}`, data)
  }

  async deleteProject(projectId: string): Promise<ApiResponse<void>> {
    return apiClient.delete<void>(`/api/v1/projects/${projectId}`)
  }

  async archiveProject(projectId: string): Promise<ApiResponse<Project>> {
    return apiClient.post<Project>(`/api/v1/projects/${projectId}/archive`)
  }

  async unarchiveProject(projectId: string): Promise<ApiResponse<Project>> {
    return apiClient.post<Project>(`/api/v1/projects/${projectId}/unarchive`)
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

  async getProjectActivity(projectId: string, days: number = 30): Promise<ApiResponse<ProjectActivity[]>> {
    return apiClient.get<ProjectActivity[]>(`/api/v1/projects/${projectId}/activity?days=${days}`)
  }

  // Repository operations
  async syncRepository(projectId: string): Promise<ApiResponse<Repository>> {
    return apiClient.post<Repository>(`/api/v1/projects/${projectId}/sync`)
  }

  async getRepositoryInfo(projectId: string): Promise<ApiResponse<Repository>> {
    return apiClient.get<Repository>(`/api/v1/projects/${projectId}/repository`)
  }

  async updateRepositorySettings(projectId: string, settings: Partial<Repository>): Promise<ApiResponse<Repository>> {
    return apiClient.put<Repository>(`/api/v1/projects/${projectId}/repository`, settings)
  }

  // Project members
  async getProjectMembers(projectId: string): Promise<ApiResponse<ProjectMember[]>> {
    return apiClient.get<ProjectMember[]>(`/api/v1/projects/${projectId}/members`)
  }

  async addProjectMember(projectId: string, userId: string, role: string): Promise<ApiResponse<ProjectMember>> {
    return apiClient.post<ProjectMember>(`/api/v1/projects/${projectId}/members`, { user_id: userId, role })
  }

  async updateProjectMember(projectId: string, userId: string, role: string): Promise<ApiResponse<ProjectMember>> {
    return apiClient.put<ProjectMember>(`/api/v1/projects/${projectId}/members/${userId}`, { role })
  }

  async removeProjectMember(projectId: string, userId: string): Promise<ApiResponse<void>> {
    return apiClient.delete<void>(`/api/v1/projects/${projectId}/members/${userId}`)
  }

  // Project search and filtering
  async searchProjects(query: string, filters?: Record<string, any>): Promise<ApiResponse<ProjectListResponse>> {
    const params = new URLSearchParams({ q: query })
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        params.append(`filter_${key}`, String(value))
      })
    }
    return apiClient.get<ProjectListResponse>(`/api/v1/projects/search?${params.toString()}`)
  }

  // Project templates
  async getProjectTemplates(): Promise<ApiResponse<Project[]>> {
    return apiClient.get<Project[]>('/api/v1/projects/templates')
  }

  async createProjectFromTemplate(templateId: string, data: CreateProjectRequest): Promise<ApiResponse<Project>> {
    return apiClient.post<Project>(`/api/v1/projects/templates/${templateId}`, data)
  }

  // Project validation
  async validateProjectConfig(projectId: string): Promise<ApiResponse<{ valid: boolean; issues: string[] }>> {
    return apiClient.post<{ valid: boolean; issues: string[] }>(`/api/v1/projects/${projectId}/validate`)
  }

  // Project export/import
  async exportProject(projectId: string, format: 'json' | 'yaml' = 'json'): Promise<ApiResponse<Blob>> {
    return apiClient.get<Blob>(`/api/v1/projects/${projectId}/export?format=${format}`, {
      responseType: 'blob'
    })
  }

  async importProject(data: FormData): Promise<ApiResponse<Project>> {
    return apiClient.post<Project>('/api/v1/projects/import', data, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  }

  // Project health checks
  async getProjectHealth(projectId: string): Promise<ApiResponse<{
    status: Status
    last_analysis?: string
    issues_count: number
    health_score: number
  }>> {
    return apiClient.get<{
      status: Status
      last_analysis?: string
      issues_count: number
      health_score: number
    }>(`/api/v1/projects/${projectId}/health`)
  }

  // Bulk operations
  async bulkUpdateProjects(projectIds: string[], updates: Partial<Project>): Promise<ApiResponse<{ updated: number; failed: number }>> {
    return apiClient.post<{ updated: number; failed: number }>('/api/v1/projects/bulk-update', {
      project_ids: projectIds,
      updates
    })
  }

  async bulkDeleteProjects(projectIds: string[]): Promise<ApiResponse<{ deleted: number; failed: number }>> {
    return apiClient.post<{ deleted: number; failed: number }>('/api/v1/projects/bulk-delete', {
      project_ids: projectIds
    })
  }
}

// Create and export service instance
export const projectsService = new ProjectsService()
export default projectsService
