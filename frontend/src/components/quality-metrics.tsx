"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
} from "recharts"
import { useAnalysis } from '@/contexts'
import { useQualityMetrics, useIssues, useQualityTrends } from '@/hooks'
import { QualityMetricsSkeleton, ErrorState, EmptyState } from '@/components/LoadingStates'
import { analysisService } from '@/services'

interface QualityMetricsProps {
  reportId?: string
}

export function QualityMetrics({ reportId }: QualityMetricsProps) {
  const { currentAnalysis, currentReportId } = useAnalysis()
  const activeReportId = reportId || currentReportId
  
  const { issues, loading: issuesLoading, error: issuesError } = useIssues(activeReportId)
  const { metrics, loading: metricsLoading, error: metricsError } = useQualityMetrics(activeReportId)
  const { trends } = useQualityTrends(currentAnalysis?.project_id || null)

  // Show loading state
  if (metricsLoading || issuesLoading) {
    return <QualityMetricsSkeleton />
  }

  // Show error state
  if (metricsError || issuesError) {
    return (
      <ErrorState 
        title="Failed to load quality metrics"
        message={metricsError || issuesError || "Unable to fetch quality data"}
      />
    )
  }

  // Show empty state if no analysis available
  if (!activeReportId || !currentAnalysis) {
    return (
      <EmptyState
        title="No Quality Metrics Available"
        message="Run an analysis to see detailed quality metrics and visualizations."
        action={{
          label: "Upload Files",
          onClick: () => window.location.href = "/"
        }}
      />
    )
  }

  // Calculate real metrics from analysis data
  const calculatedMetrics = metrics || analysisService.calculateMetricsFromAnalysis(currentAnalysis)
  
  if (!calculatedMetrics) {
    return (
      <EmptyState
        title="No Metrics Data"
        message="Analysis completed but no metrics data is available."
      />
    )
  }

  // Calculate complexity distribution from real issues
  const totalIssues = issues.length
  const highSeverityIssues = issues.filter(issue => issue.severity === "High").length
  const mediumSeverityIssues = issues.filter(issue => issue.severity === "Medium").length
  const lowSeverityIssues = issues.filter(issue => issue.severity === "Low").length
  
  const complexityData = totalIssues > 0 ? [
    { 
      name: "Low", 
      value: Math.round((lowSeverityIssues / totalIssues) * 100), 
      color: "#22c55e",
      count: lowSeverityIssues
    },
    { 
      name: "Medium", 
      value: Math.round((mediumSeverityIssues / totalIssues) * 100), 
      color: "#f59e0b",
      count: mediumSeverityIssues
    },
    { 
      name: "High", 
      value: Math.round((highSeverityIssues / totalIssues) * 100), 
      color: "#ef4444",
      count: highSeverityIssues
    },
  ] : [
    { name: "No Issues", value: 100, color: "#22c55e", count: 0 }
  ]

  // Group real issues by type for chart
  const issuesByType = issues.reduce((acc: any[], issue) => {
    const existingType = acc.find(item => item.name === issue.type)
    if (existingType) {
      existingType.count += 1
    } else {
      acc.push({
        name: issue.type,
        count: 1,
        severity: issue.severity
      })
    }
    return acc
  }, [])

  // Generate trend data for test coverage (mock for now, will be real when historical data available)
  const testCoverageData = trends.length > 0 ? trends.map(trend => ({
    name: new Date(trend.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    coverage: trend.test_coverage
  })) : [
    { name: "Current", coverage: calculatedMetrics.test_coverage }
  ]

  // Calculate detailed metrics from real analysis data
  const detailedMetrics = [
    { 
      metric: "Quality Score", 
      value: currentAnalysis.summary?.quality_score?.toFixed(1) || "N/A", 
      target: "> 80", 
      status: (currentAnalysis.summary?.quality_score || 0) > 80 ? "good" : "warning" 
    },
    { 
      metric: "Total Files", 
      value: currentAnalysis.summary?.total_files?.toString() || "0", 
      target: "N/A", 
      status: "good" 
    },
    { 
      metric: "Total Lines", 
      value: currentAnalysis.summary?.total_lines?.toLocaleString() || "0", 
      target: "N/A", 
      status: "good" 
    },
    { 
      metric: "Total Issues", 
      value: totalIssues.toString(), 
      target: "< 10", 
      status: totalIssues < 10 ? "good" : "warning" 
    },
    { 
      metric: "High Severity Issues", 
      value: highSeverityIssues.toString(), 
      target: "0", 
      status: highSeverityIssues === 0 ? "good" : "warning" 
    },
    { 
      metric: "Technical Debt", 
      value: `${calculatedMetrics.technical_debt_hours.toFixed(1)}h`, 
      target: "< 5h", 
      status: calculatedMetrics.technical_debt_hours < 5 ? "good" : "warning" 
    },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-foreground mb-2">Quality Metrics</h2>
        <p className="text-muted-foreground">
          Real-time metrics and visualizations from your code quality analysis.
        </p>
      </div>

      {/* Key Metrics - Now using REAL data */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Test Coverage</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground mb-2">
              {calculatedMetrics.test_coverage.toFixed(1)}%
            </div>
            <Progress value={calculatedMetrics.test_coverage} className="mb-2" />
            <p className="text-xs text-muted-foreground">
              Based on analysis results
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Code Duplication</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground mb-2">
              {calculatedMetrics.code_duplication.toFixed(1)}%
            </div>
            <Progress value={calculatedMetrics.code_duplication} className="mb-2" />
            <p className="text-xs text-muted-foreground">
              Calculated from detected issues
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Technical Debt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground mb-2">
              {calculatedMetrics.technical_debt_hours.toFixed(1)}h
            </div>
            <Progress 
              value={Math.min(calculatedMetrics.technical_debt_hours * 10, 100)} 
              className="mb-2" 
            />
            <p className="text-xs text-muted-foreground">
              Estimated fix time
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts - Now using REAL data */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Issue Severity Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Issue Severity Distribution</CardTitle>
            <CardDescription>
              Distribution of issues by severity level ({totalIssues} total issues)
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={complexityData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, count }) => `${name}: ${count || 0}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {complexityData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(val, name) => [`${val}%`, name]} />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Test Coverage Trend */}
        <Card>
          <CardHeader>
            <CardTitle>Quality Trend</CardTitle>
            <CardDescription>
              {trends.length > 0 
                ? `Quality metrics over time (${trends.length} data points)`
                : "Current analysis snapshot"
              }
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={testCoverageData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis domain={[0, 100]} />
                <Tooltip formatter={(val) => [`${val}%`, 'Test Coverage']} />
                <Line 
                  type="monotone" 
                  dataKey="coverage" 
                  stroke="#3b82f6" 
                  strokeWidth={2}
                  dot={{ fill: '#3b82f6' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Issues by Type - Now using REAL data */}
      {issuesByType.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Issues by Category</CardTitle>
            <CardDescription>
              Breakdown of {totalIssues} detected issues by type
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={issuesByType}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {/* Detailed Metrics Table - Now using REAL data */}
      <Card>
        <CardHeader>
          <CardTitle>Detailed Analysis Metrics</CardTitle>
          <CardDescription>
            Comprehensive breakdown of real analysis results
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {detailedMetrics.map((item, index) => (
              <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                <div>
                  <h4 className="font-medium text-foreground">{item.metric}</h4>
                  <p className="text-sm text-muted-foreground">
                    {item.target !== "N/A" ? `Target: ${item.target}` : "From analysis"}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-lg font-semibold">{item.value}</span>
                  <Badge variant={item.status === "good" ? "default" : "secondary"}>
                    {item.status === "good" ? "Good" : "Warning"}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
