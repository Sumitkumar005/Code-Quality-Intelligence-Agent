// Project Types
export interface Project {
  id: string
  organization_id: string
  name: string
  description?: string
  repository_url?: string
  repository_type: 'git' | 'github' | 'gitlab' | 'bitbucket'
  default_branch: string
  languages: string[]
  settings: Record<string, any>
  created_by: string
  created_at: string
  updated_at: string
  organization?: Organization
  creator?: User
  analyses?: Analysis[]
  reports?: Report[]
}

export interface CreateProjectData {
  name: string
  description?: string
  repository_url?: string
  repository_type?: 'git' | 'github' | 'gitlab' | 'bitbucket'
  default_branch?: string
  languages?: string[]
  settings?: Record<string, any>
}

export interface UpdateProjectData {
  name?: string
  description?: string
  repository_url?: string
  repository_type?: 'git' | 'github' | 'gitlab' | 'bitbucket'
  default_branch?: string
  languages?: string[]
  settings?: Record<string, any>
}

export interface ProjectSettings {
  analysis_config: {
    enabled_analyzers: string[]
    excluded_paths: string[]
    custom_rules: Record<string, any>
  }
  notifications: {
    email_enabled: boolean
    slack_webhook?: string
    report_format: 'pdf' | 'html' | 'json'
  }
  integrations: {
    github?: GitHubIntegration
    gitlab?: GitLabIntegration
    jira?: JiraIntegration
  }
}

export interface GitHubIntegration {
  repository: string
  webhook_secret: string
  auto_analyze_prs: boolean
  require_reviews: boolean
}

export interface GitLabIntegration {
  project_id: string
  webhook_secret: string
  auto_analyze_mrs: boolean
}

export interface JiraIntegration {
  project_key: string
  api_token: string
  auto_create_issues: boolean
}

export interface ProjectStats {
  total_analyses: number
  total_issues: number
  critical_issues: number
  last_analysis?: string
  quality_score: number
  trend: 'up' | 'down' | 'stable'
}
