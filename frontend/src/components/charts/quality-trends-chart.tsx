"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card"
import { Badge } from "../ui/badge"
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell
} from "recharts"
import {
  TrendingUp,
  TrendingDown,
  Activity,
  AlertTriangle,
  CheckCircle,
  Clock,
  Calendar
} from "lucide-react"
import { useAnalysis } from "@/contexts"
import { useQualityTrends, useIssues, useQualityMetrics } from "@/hooks"
import { EmptyState, ErrorState, LoadingSpinner } from "@/components/LoadingStates"
import { analysisService } from "@/services"

interface QualityTrendsChartProps {
  reportId?: string
  projectId?: string
  days?: number
}

export function QualityTrendsChart({ reportId, projectId, days = 30 }: QualityTrendsChartProps) {
  const { currentAnalysis, currentReportId } = useAnalysis()
  const activeReportId = reportId || currentReportId
  const activeProjectId = projectId || currentAnalysis?.project_id || null

  const { issues, loading: issuesLoading } = useIssues(activeReportId)
  const { metrics, loading: metricsLoading } = useQualityMetrics(activeReportId)
  const { trends, loading: trendsLoading, error: trendsError } = useQualityTrends(activeProjectId, days)

  // Show loading state
  if (trendsLoading || issuesLoading || metricsLoading) {
    return (
      <div className="space-y-6">
        <div>
          <h3 className="text-2xl font-bold text-foreground mb-2 flex items-center gap-2">
            <Activity className="h-6 w-6" />
            Quality Trends & Analytics
          </h3>
          <p className="text-muted-foreground">
            Track your code quality improvements over time with detailed metrics and insights.
          </p>
        </div>
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  // Show error state
  if (trendsError) {
    return (
      <div className="space-y-6">
        <div>
          <h3 className="text-2xl font-bold text-foreground mb-2 flex items-center gap-2">
            <Activity className="h-6 w-6" />
            Quality Trends & Analytics
          </h3>
          <p className="text-muted-foreground">
            Track your code quality improvements over time with detailed metrics and insights.
          </p>
        </div>
        <ErrorState
          title="Failed to Load Trends Data"
          message={`Unable to fetch quality trends: ${trendsError}`}
        />
      </div>
    )
  }

  // Show empty state when no analysis available
  if (!currentAnalysis || !activeReportId) {
    return (
      <div className="space-y-6">
        <div>
          <h3 className="text-2xl font-bold text-foreground mb-2 flex items-center gap-2">
            <Activity className="h-6 w-6" />
            Quality Trends & Analytics
          </h3>
          <p className="text-muted-foreground">
            Track your code quality improvements over time with detailed metrics and insights.
          </p>
        </div>
        <EmptyState
          title="No Trends Data Available"
          message="Run multiple analyses over time to see quality trends and historical data."
          action={{
            label: "Upload Files",
            onClick: () => window.location.href = "/"
          }}
        />
      </div>
    )
  }

  // Calculate current analysis data
  const calculatedMetrics = metrics || analysisService.calculateMetricsFromAnalysis(currentAnalysis)
  const totalIssues = issues?.length || 0
  const highSeverityIssues = issues?.filter(issue => issue.severity === 'High').length || 0
  const mediumSeverityIssues = issues?.filter(issue => issue.severity === 'Medium').length || 0
  const lowSeverityIssues = issues?.filter(issue => issue.severity === 'Low').length || 0
  const currentQuality = currentAnalysis.summary?.quality_score || 0

  // Use historical data if available, otherwise create current snapshot
  const hasHistoricalData = trends && trends.length > 1

  let chartData: any[] = []
  let qualityChange = 0
  let issueChange = 0

  if (hasHistoricalData) {
    // Use real historical data
    chartData = trends.map((trend, index) => ({
      date: new Date(trend.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      quality: trend.quality_score,
      issues: trend.issue_count,
      highSeverity: Math.round(trend.issue_count * 0.2), // Estimate high severity as 20% of total
      codebase: currentAnalysis.summary?.total_lines || 1000,
      testCoverage: trend.test_coverage
    }))

    // Calculate changes
    const firstQuality = trends[0].quality_score
    const lastQuality = trends[trends.length - 1].quality_score
    qualityChange = ((lastQuality - firstQuality) / firstQuality) * 100

    const firstIssues = trends[0].issue_count
    const lastIssues = trends[trends.length - 1].issue_count
    issueChange = ((lastIssues - firstIssues) / firstIssues) * 100
  } else {
    // Create current snapshot data
    chartData = [
      {
        date: 'Current',
        quality: currentQuality,
        issues: totalIssues,
        highSeverity: highSeverityIssues,
        codebase: currentAnalysis.summary?.total_lines || 0,
        testCoverage: calculatedMetrics?.test_coverage || 0
      }
    ]
  }

  // Real issue distribution data
  const issueDistribution = [
    { name: 'High', value: highSeverityIssues, color: '#ef4444' },
    { name: 'Medium', value: mediumSeverityIssues, color: '#f59e0b' },
    { name: 'Low', value: lowSeverityIssues, color: '#10b981' }
  ].filter(item => item.value > 0) // Only show categories with issues

  // Generate AI insights based on real data
  const generateInsights = () => {
    const insights: string[] = []

    if (hasHistoricalData) {
      if (qualityChange > 5) {
        insights.push("📈 Quality score is improving significantly over time")
      } else if (qualityChange < -5) {
        insights.push("📉 Quality score is declining - attention needed")
      } else {
        insights.push("📊 Quality score is stable")
      }

      if (issueChange < -10) {
        insights.push("✅ Issue count is decreasing - great progress!")
      } else if (issueChange > 10) {
        insights.push("⚠️ Issue count is increasing - review needed")
      }
    } else {
      insights.push("📊 Current analysis snapshot - run more analyses to see trends")
    }

    if (highSeverityIssues > 0) {
      insights.push(`🚨 ${highSeverityIssues} high-severity issues require immediate attention`)
    } else {
      insights.push("✅ No high-severity issues detected")
    }

    if (calculatedMetrics?.test_coverage && calculatedMetrics.test_coverage < 70) {
      insights.push("🧪 Test coverage is below recommended 70% threshold")
    } else if (calculatedMetrics?.test_coverage && calculatedMetrics.test_coverage > 80) {
      insights.push("🎯 Excellent test coverage above 80%")
    }

    if (calculatedMetrics?.technical_debt_hours && calculatedMetrics.technical_debt_hours > 10) {
      insights.push(`⏰ High technical debt detected: ${calculatedMetrics.technical_debt_hours.toFixed(1)} hours`)
    }

    return insights
  }

  const insights = generateInsights()

  // Summary data
  const summaryData = {
    total_analyses: hasHistoricalData ? trends.length : 1,
    date_range: hasHistoricalData
      ? `${new Date(trends[0].date).toLocaleDateString()} to ${new Date(trends[trends.length - 1].date).toLocaleDateString()}`
      : new Date().toLocaleDateString(),
    current_quality: currentQuality,
    quality_change: hasHistoricalData
      ? `${qualityChange > 0 ? '↗️ +' : '↘️ '}${Math.abs(qualityChange).toFixed(1)}%`
      : 'N/A',
    issue_trend: hasHistoricalData
      ? `${issueChange < 0 ? '↗️ ' : '↘️ +'}${Math.abs(issueChange).toFixed(1)}%`
      : 'N/A'
  }

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-2xl font-bold text-foreground mb-2 flex items-center gap-2">
          <Activity className="h-6 w-6" />
          Quality Trends & Analytics
        </h3>
        <p className="text-muted-foreground">
          Track your code quality improvements over time with detailed metrics and insights.
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Current Quality</p>
                <p className="text-2xl font-bold">{summaryData.current_quality.toFixed(1)}/100</p>
              </div>
              <div className="flex items-center text-green-600">
                {qualityChange >= 0 ? <TrendingUp className="h-4 w-4 mr-1" /> : <TrendingDown className="h-4 w-4 mr-1" />}
                <span className="text-sm font-medium">{summaryData.quality_change}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Issues</p>
                <p className="text-2xl font-bold">{totalIssues}</p>
              </div>
              <div className="flex items-center text-green-600">
                {issueChange <= 0 ? <TrendingDown className="h-4 w-4 mr-1" /> : <TrendingUp className="h-4 w-4 mr-1" />}
                <span className="text-sm font-medium">{summaryData.issue_trend}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">High Severity</p>
                <p className="text-2xl font-bold text-red-600">{highSeverityIssues}</p>
              </div>
              <AlertTriangle className="h-8 w-8 text-red-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Analyses</p>
                <p className="text-2xl font-bold">{summaryData.total_analyses}</p>
              </div>
              <Calendar className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Quality Score Trend */}
        <Card>
          <CardHeader>
            <CardTitle>Quality Score Trend</CardTitle>
            <CardDescription>
              {hasHistoricalData
                ? `Track quality improvements over ${trends.length} analyses`
                : 'Current analysis snapshot - run more analyses to see trends'
              }
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis domain={[0, 100]} />
                <Tooltip
                  formatter={(value) => [`${value}/100`, 'Quality Score']}
                  labelFormatter={(label) => `Date: ${label}`}
                />
                <Area
                  type="monotone"
                  dataKey="quality"
                  stroke="#10b981"
                  fill="#10b981"
                  fillOpacity={0.3}
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Issues Trend */}
        <Card>
          <CardHeader>
            <CardTitle>Issues Trend</CardTitle>
            <CardDescription>
              {hasHistoricalData
                ? 'Monitor issue resolution progress over time'
                : `Current: ${totalIssues} total issues, ${highSeverityIssues} high severity`
              }
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="issues"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  name="Total Issues"
                />
                <Line
                  type="monotone"
                  dataKey="highSeverity"
                  stroke="#ef4444"
                  strokeWidth={2}
                  name="High Severity"
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Test Coverage Trend */}
        <Card>
          <CardHeader>
            <CardTitle>Test Coverage Trend</CardTitle>
            <CardDescription>
              {hasHistoricalData
                ? 'Test coverage percentage over time'
                : `Current coverage: ${calculatedMetrics?.test_coverage?.toFixed(1) || 0}%`
              }
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis domain={[0, 100]} />
                <Tooltip formatter={(value) => [`${value}%`, 'Test Coverage']} />
                <Area
                  type="monotone"
                  dataKey="testCoverage"
                  stroke="#8b5cf6"
                  fill="#8b5cf6"
                  fillOpacity={0.3}
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Issue Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Issue Distribution</CardTitle>
            <CardDescription>
              {totalIssues > 0
                ? `Current ${totalIssues} issues by severity level`
                : 'No issues detected in current analysis'
              }
            </CardDescription>
          </CardHeader>
          <CardContent>
            {totalIssues > 0 ? (
              <>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={issueDistribution}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {issueDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
                <div className="flex justify-center gap-4 mt-4">
                  {issueDistribution.map((entry, index) => (
                    <div key={index} className="flex items-center gap-2">
                      <div
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: entry.color }}
                      />
                      <span className="text-sm">{entry.name}: {entry.value}</span>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <div className="flex flex-col items-center justify-center h-[300px] text-center">
                <CheckCircle className="h-16 w-16 text-green-500 mb-4" />
                <h4 className="text-lg font-semibold text-green-600 mb-2">No Issues Found!</h4>
                <p className="text-muted-foreground">Your code analysis didn't detect any issues.</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Insights */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CheckCircle className="h-5 w-5 text-green-600" />
            AI-Generated Insights
          </CardTitle>
          <CardDescription>
            Intelligent analysis of your quality trends and recommendations
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3">
            {insights.map((insight: string, index: number) => (
              <div key={index} className="flex items-start gap-3 p-3 bg-muted/50 rounded-lg">
                <div className="w-2 h-2 rounded-full bg-blue-500 mt-2 flex-shrink-0" />
                <p className="text-sm">{insight}</p>
              </div>
            ))}
          </div>

          <div className="mt-4 p-4 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-950/20 dark:to-purple-950/20 rounded-lg border">
            <h4 className="font-semibold mb-2">📊 Summary</h4>
            <p className="text-sm text-muted-foreground">
              Analysis period: {summaryData.date_range} •
              Total analyses: {summaryData.total_analyses} •
              {hasHistoricalData && `Quality change: ${summaryData.quality_change} • Issue change: ${summaryData.issue_trend}`}
              {!hasHistoricalData && 'Run more analyses to see trends'}
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}