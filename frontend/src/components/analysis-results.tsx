"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { FileText, Code, Languages, TrendingUp, CheckCircle, AlertCircle, XCircle } from "lucide-react"

interface AnalysisResultsProps {
  data: any
}

export function AnalysisResults({ data }: AnalysisResultsProps) {
  if (!data) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-3xl font-bold text-foreground mb-2">Analysis Results</h2>
          <p className="text-muted-foreground">No analysis data available. Please upload code files first.</p>
        </div>

        <Card>
          <CardContent className="flex items-center justify-center h-64">
            <div className="text-center">
              <FileText className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
              <p className="text-muted-foreground">Upload code to see analysis results</p>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-600"
    if (score >= 60) return "text-yellow-600"
    return "text-red-600"
  }

  const getScoreIcon = (score: number) => {
    if (score >= 80) return <CheckCircle className="h-5 w-5 text-green-600" />
    if (score >= 60) return <AlertCircle className="h-5 w-5 text-yellow-600" />
    return <XCircle className="h-5 w-5 text-red-600" />
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-foreground mb-2">Analysis Results</h2>
        <p className="text-muted-foreground">Comprehensive code quality analysis and insights for your codebase.</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Files</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.summary.totalFiles}</div>
            <p className="text-xs text-muted-foreground">Analyzed files</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Lines of Code</CardTitle>
            <Code className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.summary.linesOfCode.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">Total LOC</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Languages</CardTitle>
            <Languages className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.summary.languages.length}</div>
            <p className="text-xs text-muted-foreground">Programming languages</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Quality Score</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold flex items-center gap-2 ${getScoreColor(data.summary.qualityScore)}`}>
              {getScoreIcon(data.summary.qualityScore)}
              {data.summary.qualityScore}/100
            </div>
            <Progress value={data.summary.qualityScore} className="mt-2" />
          </CardContent>
        </Card>
      </div>

      {/* Languages Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle>Language Distribution</CardTitle>
          <CardDescription>Programming languages detected in your codebase</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {data.summary.languages.map((lang: string, index: number) => (
              <Badge key={index} variant="secondary">
                {lang}
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Issues Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Issues Overview</CardTitle>
          <CardDescription>Summary of detected issues by category and severity</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {data.issues.map((issue: any, index: number) => (
              <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="font-medium">{issue.type}</h4>
                    <Badge
                      variant={
                        issue.severity === "High"
                          ? "destructive"
                          : issue.severity === "Medium"
                            ? "default"
                            : "secondary"
                      }
                    >
                      {issue.severity}
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground">{issue.description}</p>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-foreground">{issue.count}</div>
                  <div className="text-xs text-muted-foreground">issues</div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
