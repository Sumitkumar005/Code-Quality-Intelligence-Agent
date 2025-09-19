"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  AlertTriangle,
  Shield,
  Zap,
  Code,
  FileText,
  TestTube,
  ChevronDown,
  ChevronRight,
  ExternalLink,
} from "lucide-react"
import { useAnalysis } from "@/contexts"
import { useIssues } from "@/hooks"
import { Issue } from "@/types/api"
import { IssueDetectionSkeleton, EmptyState, ErrorState } from "@/components/LoadingStates"

interface IssueDetectionProps {
  reportId?: string
}

interface DisplayIssue {
  id: string
  title: string
  severity: string
  file: string
  line: number
  description: string
  solution: string
  code: string
}

export function IssueDetection({ reportId }: IssueDetectionProps) {
  const [expandedIssues, setExpandedIssues] = useState<Set<string>>(new Set())
  const { currentAnalysis } = useAnalysis()
  const { issues, loading, error } = useIssues(reportId || currentAnalysis?.report_id || null)

  // Show loading state
  if (loading) {
    return <IssueDetectionSkeleton />
  }

  // Show error state
  if (error) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-3xl font-bold text-foreground mb-2">Issue Detection</h2>
          <p className="text-muted-foreground">Detailed analysis of detected issues with actionable solutions.</p>
        </div>
        <ErrorState
          title="Failed to Load Issues"
          message={`Unable to fetch issues: ${error}`}
        />
      </div>
    )
  }

  // Show empty state when no analysis or no issues
  if (!currentAnalysis && !reportId) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-3xl font-bold text-foreground mb-2">Issue Detection</h2>
          <p className="text-muted-foreground">Detailed analysis of detected issues with actionable solutions.</p>
        </div>
        <EmptyState
          title="No Analysis Available"
          message="Run a code analysis to detect and review issues in your codebase."
          action={{
            label: "Upload Files",
            onClick: () => window.location.href = "/"
          }}
        />
      </div>
    )
  }

  // Show empty state when no issues found
  if (!issues || issues.length === 0) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-3xl font-bold text-foreground mb-2">Issue Detection</h2>
          <p className="text-muted-foreground">Detailed analysis of detected issues with actionable solutions.</p>
        </div>
        <EmptyState
          title="No Issues Found"
          message="Your code analysis didn't detect any issues. Keep up the good work!"
        />
      </div>
    )
  }

  const toggleIssue = (issueId: string) => {
    const newExpanded = new Set(expandedIssues)
    if (newExpanded.has(issueId)) {
      newExpanded.delete(issueId)
    } else {
      newExpanded.add(issueId)
    }
    setExpandedIssues(newExpanded)
  }

  // Transform issues for display with enhanced code examples
  const transformIssueForDisplay = (issue: Issue): DisplayIssue => {
    const generateCodeExample = (issue: Issue): string => {
      // Generate contextual code examples based on issue type
      switch (issue.type) {
        case 'Security':
          return `// Security Issue at ${issue.file}:${issue.line}
// ${issue.message}

// Example problematic code:
// ${issue.message.includes('SQL') ? 'query = "SELECT * FROM users WHERE id = " + userId' : 
     issue.message.includes('XSS') ? 'innerHTML = userInput' :
     issue.message.includes('password') ? 'const password = "hardcoded123"' :
     '// Security vulnerability detected'}

// Recommended fix:
// ${issue.suggestion || 'Apply security best practices'}`

        case 'Performance':
          return `// Performance Issue at ${issue.file}:${issue.line}
// ${issue.message}

// Potential optimization:
// ${issue.suggestion || 'Optimize this code section for better performance'}

// Consider: caching, async operations, or algorithm improvements`

        case 'Quality':
          return `// Code Quality Issue at ${issue.file}:${issue.line}
// ${issue.message}

// Improvement suggestion:
// ${issue.suggestion || 'Refactor for better maintainability'}

// Consider: extracting methods, reducing complexity, or improving naming`

        case 'Documentation':
          return `// Documentation Issue at ${issue.file}:${issue.line}
// ${issue.message}

/**
 * Add proper documentation here
 * ${issue.suggestion || 'Describe the purpose, parameters, and return value'}
 */`

        case 'Testing':
          return `// Testing Issue at ${issue.file}:${issue.line}
// ${issue.message}

// Add test coverage:
// ${issue.suggestion || 'Write unit tests for this functionality'}

// Example test structure needed`

        default:
          return `// Issue at ${issue.file}:${issue.line}
// ${issue.message}
// ${issue.suggestion || 'Review and address this issue'}`
      }
    }

    return {
      id: issue.id,
      title: issue.message,
      severity: issue.severity,
      file: issue.file,
      line: issue.line,
      description: issue.message,
      solution: issue.suggestion || getDefaultSolution(issue.type),
      code: generateCodeExample(issue),
    }
  }

  // Get default solutions based on issue type
  const getDefaultSolution = (type: Issue['type']): string => {
    switch (type) {
      case 'Security':
        return 'Review security implications and apply appropriate security measures such as input validation, sanitization, or secure coding practices.'
      case 'Performance':
        return 'Analyze performance bottlenecks and consider optimizations such as caching, algorithm improvements, or asynchronous operations.'
      case 'Quality':
        return 'Refactor code to improve readability, maintainability, and adherence to coding standards.'
      case 'Documentation':
        return 'Add comprehensive documentation including function descriptions, parameter explanations, and usage examples.'
      case 'Testing':
        return 'Implement unit tests, integration tests, or increase test coverage for this functionality.'
      default:
        return 'Review and address this issue according to best practices.'
    }
  }

  // Group real issues by type
  const processedIssues = {
    security: issues.filter((issue: Issue) => issue.type === "Security").map(transformIssueForDisplay),
    performance: issues.filter((issue: Issue) => issue.type === "Performance").map(transformIssueForDisplay),
    quality: issues.filter((issue: Issue) => issue.type === "Quality").map(transformIssueForDisplay),
    documentation: issues.filter((issue: Issue) => issue.type === "Documentation").map(transformIssueForDisplay),
    testing: issues.filter((issue: Issue) => issue.type === "Testing").map(transformIssueForDisplay),
  }

  const getIcon = (category: string) => {
    switch (category) {
      case "security":
        return <Shield className="h-4 w-4" />
      case "performance":
        return <Zap className="h-4 w-4" />
      case "quality":
        return <Code className="h-4 w-4" />
      case "documentation":
        return <FileText className="h-4 w-4" />
      case "testing":
        return <TestTube className="h-4 w-4" />
      default:
        return <AlertTriangle className="h-4 w-4" />
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "High":
        return "destructive"
      case "Medium":
        return "default"
      case "Low":
        return "secondary"
      default:
        return "secondary"
    }
  }

  // Get issue counts for tab labels
  const getIssueCount = (category: keyof typeof processedIssues) => {
    return processedIssues[category].length
  }

  // Calculate issue statistics
  const totalIssues = issues.length
  const highSeverityCount = issues.filter(issue => issue.severity === 'High').length
  const mediumSeverityCount = issues.filter(issue => issue.severity === 'Medium').length
  const lowSeverityCount = issues.filter(issue => issue.severity === 'Low').length

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-foreground mb-2">Issue Detection</h2>
        <p className="text-muted-foreground">Detailed analysis of detected issues with actionable solutions.</p>
      </div>

      {/* Issue Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Issues</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalIssues}</div>
            <p className="text-xs text-muted-foreground">Detected in analysis</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <div className="w-2 h-2 bg-red-500 rounded-full"></div>
              High Severity
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{highSeverityCount}</div>
            <p className="text-xs text-muted-foreground">Requires immediate attention</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
              Medium Severity
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{mediumSeverityCount}</div>
            <p className="text-xs text-muted-foreground">Should be addressed</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              Low Severity
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{lowSeverityCount}</div>
            <p className="text-xs text-muted-foreground">Minor improvements</p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="security" className="w-full">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="security" className="flex items-center gap-2">
            <Shield className="h-4 w-4" />
            Security ({getIssueCount('security')})
          </TabsTrigger>
          <TabsTrigger value="performance" className="flex items-center gap-2">
            <Zap className="h-4 w-4" />
            Performance ({getIssueCount('performance')})
          </TabsTrigger>
          <TabsTrigger value="quality" className="flex items-center gap-2">
            <Code className="h-4 w-4" />
            Quality ({getIssueCount('quality')})
          </TabsTrigger>
          <TabsTrigger value="documentation" className="flex items-center gap-2">
            <FileText className="h-4 w-4" />
            Docs ({getIssueCount('documentation')})
          </TabsTrigger>
          <TabsTrigger value="testing" className="flex items-center gap-2">
            <TestTube className="h-4 w-4" />
            Testing ({getIssueCount('testing')})
          </TabsTrigger>
        </TabsList>

        {Object.entries(processedIssues).map(([category, categoryIssues]) => (
          <TabsContent key={category} value={category} className="space-y-4">
            {categoryIssues.length === 0 ? (
              <Card>
                <CardContent className="flex flex-col items-center justify-center p-6 text-center">
                  {getIcon(category)}
                  <p className="mt-2 text-muted-foreground">
                    No {category} issues found. Great job!
                  </p>
                </CardContent>
              </Card>
            ) : (
              categoryIssues.map((issue: DisplayIssue) => (
                <Card key={issue.id}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        {getIcon(category)}
                        <div>
                          <CardTitle className="text-lg">{issue.title}</CardTitle>
                          <CardDescription className="flex items-center gap-2 mt-1">
                            <span>
                              {issue.file}:{issue.line}
                            </span>
                            <Badge variant={getSeverityColor(issue.severity) as any}>{issue.severity}</Badge>
                          </CardDescription>
                        </div>
                      </div>
                      <Button variant="ghost" size="sm" onClick={() => toggleIssue(issue.id)}>
                        {expandedIssues.has(issue.id) ? (
                          <ChevronDown className="h-4 w-4" />
                        ) : (
                          <ChevronRight className="h-4 w-4" />
                        )}
                      </Button>
                    </div>
                  </CardHeader>

                  {expandedIssues.has(issue.id) && (
                    <CardContent className="space-y-4">
                      <div>
                        <h4 className="font-medium mb-2">Description</h4>
                        <p className="text-muted-foreground">{issue.description}</p>
                      </div>

                      <div>
                        <h4 className="font-medium mb-2">Recommended Solution</h4>
                        <p className="text-muted-foreground">{issue.solution}</p>
                      </div>

                      <div>
                        <h4 className="font-medium mb-2">Code Context</h4>
                        <pre className="bg-muted p-4 rounded-lg text-sm overflow-x-auto">
                          <code>{issue.code}</code>
                        </pre>
                      </div>

                      <div className="flex gap-2">
                        <Button size="sm" variant="outline">
                          <ExternalLink className="h-4 w-4 mr-2" />
                          View in File
                        </Button>
                        <Button size="sm" variant="outline">
                          Learn More
                        </Button>
                      </div>
                    </CardContent>
                  )}
                </Card>
              ))
            )}
          </TabsContent>
        ))}
      </Tabs>
    </div>
  )
}