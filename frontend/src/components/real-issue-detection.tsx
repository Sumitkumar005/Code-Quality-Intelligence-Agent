"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card"
import { Badge } from "./ui/badge"
import { Button } from "./ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "./ui/collapsible"
import { 
  AlertTriangle, 
  Shield, 
  Zap, 
  Code, 
  FileText, 
  TestTube,
  ChevronDown,
  ChevronRight,
  ExternalLink
} from "lucide-react"

interface RealIssueDetectionProps {
  data: any
}

export function RealIssueDetection({ data }: RealIssueDetectionProps) {
  const [expandedIssues, setExpandedIssues] = useState<Set<string>>(new Set())

  if (!data || !data.issues || data.issues.length === 0) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-3xl font-bold text-foreground mb-2">Issue Detection</h2>
          <p className="text-muted-foreground">No issues detected! Your code quality is excellent. 🎉</p>
        </div>
        <Card>
          <CardContent className="flex items-center justify-center h-64">
            <div className="text-center">
              <Shield className="h-12 w-12 mx-auto mb-4 text-green-500" />
              <p className="text-lg font-semibold text-green-600">All Clear!</p>
              <p className="text-muted-foreground">No quality issues found in your codebase</p>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  // Process real issues from analysis
  const realIssues = data.issues || []
  
  // Group issues by type
  const groupedIssues = {
    security: realIssues.filter((issue: any) => issue.type === "Security"),
    performance: realIssues.filter((issue: any) => issue.type === "Performance"),
    quality: realIssues.filter((issue: any) => issue.type === "Code Quality"),
    documentation: realIssues.filter((issue: any) => issue.type === "Documentation"),
    testing: realIssues.filter((issue: any) => issue.type === "Testing")
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

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "High": return "destructive"
      case "Medium": return "secondary" 
      case "Low": return "outline"
      default: return "outline"
    }
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case "High": return <AlertTriangle className="h-4 w-4 text-red-500" />
      case "Medium": return <AlertTriangle className="h-4 w-4 text-yellow-500" />
      case "Low": return <AlertTriangle className="h-4 w-4 text-blue-500" />
      default: return <AlertTriangle className="h-4 w-4 text-gray-500" />
    }
  }

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case "security": return <Shield className="h-5 w-5" />
      case "performance": return <Zap className="h-5 w-5" />
      case "quality": return <Code className="h-5 w-5" />
      case "documentation": return <FileText className="h-5 w-5" />
      case "testing": return <TestTube className="h-5 w-5" />
      default: return <AlertTriangle className="h-5 w-5" />
    }
  }

  const totalIssues = realIssues.length
  const highSeverityCount = realIssues.filter((issue: any) => issue.severity === "High").length
  const mediumSeverityCount = realIssues.filter((issue: any) => issue.severity === "Medium").length
  const lowSeverityCount = realIssues.filter((issue: any) => issue.severity === "Low").length

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-foreground mb-2">Issue Detection</h2>
        <p className="text-muted-foreground">
          Detailed analysis of detected issues with actionable solutions from real code analysis.
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Issues</p>
                <p className="text-2xl font-bold">{totalIssues}</p>
              </div>
              <AlertTriangle className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">High Severity</p>
                <p className="text-2xl font-bold text-red-600">{highSeverityCount}</p>
              </div>
              <AlertTriangle className="h-8 w-8 text-red-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Medium Severity</p>
                <p className="text-2xl font-bold text-yellow-600">{mediumSeverityCount}</p>
              </div>
              <AlertTriangle className="h-8 w-8 text-yellow-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Low Severity</p>
                <p className="text-2xl font-bold text-blue-600">{lowSeverityCount}</p>
              </div>
              <AlertTriangle className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Issues by Category */}
      <Card>
        <CardHeader>
          <CardTitle>Issues by Category</CardTitle>
          <CardDescription>
            Browse issues organized by type with detailed explanations and solutions
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="all" className="w-full">
            <TabsList className="grid w-full grid-cols-6">
              <TabsTrigger value="all">All ({totalIssues})</TabsTrigger>
              <TabsTrigger value="security">Security ({groupedIssues.security.length})</TabsTrigger>
              <TabsTrigger value="performance">Performance ({groupedIssues.performance.length})</TabsTrigger>
              <TabsTrigger value="quality">Quality ({groupedIssues.quality.length})</TabsTrigger>
              <TabsTrigger value="documentation">Docs ({groupedIssues.documentation.length})</TabsTrigger>
              <TabsTrigger value="testing">Testing ({groupedIssues.testing.length})</TabsTrigger>
            </TabsList>

            <TabsContent value="all" className="space-y-4">
              <div className="space-y-3">
                {realIssues.map((issue: any, index: number) => (
                  <Card key={index} className="border-l-4 border-l-red-500">
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            {getSeverityIcon(issue.severity)}
                            <h4 className="font-semibold">{issue.message || "Code Issue"}</h4>
                            <Badge variant={getSeverityColor(issue.severity)}>
                              {issue.severity || "Unknown"}
                            </Badge>
                            <Badge variant="outline">{issue.type || "Unknown"}</Badge>
                          </div>
                          
                          <div className="text-sm text-muted-foreground mb-2">
                            <span className="font-medium">File:</span> {issue.file || "Unknown"}
                            {issue.line && <span className="ml-4"><span className="font-medium">Line:</span> {issue.line}</span>}
                          </div>
                          
                          <p className="text-sm mb-3">{issue.message || "Issue detected in code"}</p>
                          
                          {issue.suggestion && (
                            <div className="bg-green-50 dark:bg-green-950/20 p-3 rounded-lg border border-green-200 dark:border-green-800">
                              <p className="text-sm text-green-800 dark:text-green-200">
                                <strong>💡 Suggestion:</strong> {issue.suggestion}
                              </p>
                            </div>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </TabsContent>

            {Object.entries(groupedIssues).map(([category, issues]) => (
              <TabsContent key={category} value={category} className="space-y-4">
                {issues.length > 0 ? (
                  <div className="space-y-3">
                    {issues.map((issue: any, index: number) => (
                      <Card key={index} className="border-l-4 border-l-blue-500">
                        <CardContent className="p-4">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-2">
                                {getCategoryIcon(category)}
                                <h4 className="font-semibold">{issue.message || `${category} Issue`}</h4>
                                <Badge variant={getSeverityColor(issue.severity)}>
                                  {issue.severity || "Unknown"}
                                </Badge>
                              </div>
                              
                              <div className="text-sm text-muted-foreground mb-2">
                                <span className="font-medium">File:</span> {issue.file || "Unknown"}
                                {issue.line && <span className="ml-4"><span className="font-medium">Line:</span> {issue.line}</span>}
                              </div>
                              
                              <p className="text-sm mb-3">{issue.message || "Issue detected"}</p>
                              
                              {issue.suggestion && (
                                <div className="bg-blue-50 dark:bg-blue-950/20 p-3 rounded-lg border border-blue-200 dark:border-blue-800">
                                  <p className="text-sm text-blue-800 dark:text-blue-200">
                                    <strong>💡 Solution:</strong> {issue.suggestion}
                                  </p>
                                </div>
                              )}
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <div className="text-green-500 mb-4">
                      {getCategoryIcon(category)}
                    </div>
                    <p className="text-muted-foreground">No {category} issues detected</p>
                  </div>
                )}
              </TabsContent>
            ))}
          </Tabs>
        </CardContent>
      </Card>
    </div>
  )
}