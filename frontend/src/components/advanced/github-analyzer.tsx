"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card"
import { Button } from "../ui/button"
import { Input } from "../ui/input"
import { Badge } from "../ui/badge"
import { Progress } from "../ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../ui/tabs"
import {
  GitBranch,
  Star,
  GitFork,
  TrendingUp,
  Search,
  ExternalLink,
  Zap,
  AlertCircle,
  CheckCircle,
  Clock
} from "lucide-react"
import { useAnalysis } from "@/contexts"
import { githubService, analysisService } from "@/services"
import { Repository } from "@/types/api"
import { LoadingSpinner, ErrorState, EmptyState } from "@/components/LoadingStates"

interface GitHubAnalyzerProps {
  onAnalysisComplete?: (data: any) => void
}

export function GitHubAnalyzer({ onAnalysisComplete }: GitHubAnalyzerProps) {
  const { setCurrentReportId } = useAnalysis()

  const [repoUrl, setRepoUrl] = useState("")
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [progress, setProgress] = useState(0)
  const [currentStep, setCurrentStep] = useState("")
  const [analysisError, setAnalysisError] = useState<string | null>(null)

  const [trendingRepos, setTrendingRepos] = useState<Repository[]>([])
  const [trendingLoading, setTrendingLoading] = useState(false)
  const [trendingError, setTrendingError] = useState<string | null>(null)
  const [selectedLanguage, setSelectedLanguage] = useState("")

  const analyzeRepository = async () => {
    if (!repoUrl.trim()) return

    // Validate GitHub URL
    if (!githubService.validateRepoUrl(repoUrl)) {
      setAnalysisError("Please enter a valid GitHub repository URL")
      return
    }

    setIsAnalyzing(true)
    setProgress(0)
    setCurrentStep("Starting GitHub repository analysis...")
    setAnalysisError(null)

    try {
      // Start GitHub analysis using service
      const response = await githubService.analyzeRepository(repoUrl)
      const reportId = response.report_id

      // Poll for progress
      const pollProgress = async () => {
        try {
          const statusData = await analysisService.getAnalysisStatus(reportId)

          setProgress(statusData.progress || 0)
          setCurrentStep(statusData.message || "Processing...")

          if (statusData.status === 'completed') {
            // Set the current analysis in context
            setCurrentReportId(reportId)

            // Call completion callback if provided
            if (onAnalysisComplete) {
              onAnalysisComplete(statusData)
            }

            setIsAnalyzing(false)
            setCurrentStep("Analysis completed successfully!")
          } else if (statusData.status === 'error') {
            throw new Error(statusData.message || 'Analysis failed')
          } else {
            // Continue polling
            setTimeout(pollProgress, 2000)
          }
        } catch (pollError) {
          console.error('Polling error:', pollError)
          // Continue polling on temporary errors
          setTimeout(pollProgress, 3000)
        }
      }

      pollProgress()

    } catch (error) {
      console.error('GitHub analysis error:', error)
      setIsAnalyzing(false)
      setAnalysisError(error instanceof Error ? error.message : 'Analysis failed')
      setCurrentStep("Analysis failed")
    }
  }

  const loadTrendingRepos = async (language = "") => {
    setTrendingLoading(true)
    setTrendingError(null)

    try {
      const repos = await githubService.getTrendingRepos(language, 10)
      setTrendingRepos(repos)
    } catch (error) {
      console.error('Failed to load trending repos:', error)
      setTrendingError(error instanceof Error ? error.message : 'Failed to load trending repositories')
    } finally {
      setTrendingLoading(false)
    }
  }

  const analyzeFromTrending = (repo: Repository) => {
    setRepoUrl(repo.url)
  }

  // Load trending repos on component mount
  useEffect(() => {
    loadTrendingRepos()
  }, [])

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-foreground mb-2 flex items-center gap-2">
          <GitBranch className="h-8 w-8" />
          GitHub Repository Analysis
        </h2>
        <p className="text-muted-foreground">
          Analyze any public GitHub repository with AI-powered insights and quality metrics.
        </p>
      </div>

      <Tabs defaultValue="analyze" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="analyze">Analyze Repository</TabsTrigger>
          <TabsTrigger value="trending" onClick={() => loadTrendingRepos()}>
            Trending Repos
          </TabsTrigger>
        </TabsList>

        <TabsContent value="analyze" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Search className="h-5 w-5" />
                Repository URL
              </CardTitle>
              <CardDescription>
                Enter a GitHub repository URL to analyze its code quality
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-2">
                <Input
                  placeholder="https://github.com/username/repository"
                  value={repoUrl}
                  onChange={(e) => setRepoUrl(e.target.value)}
                  disabled={isAnalyzing}
                />
                <Button
                  onClick={analyzeRepository}
                  disabled={!repoUrl.trim() || isAnalyzing}
                  className="min-w-[120px]"
                >
                  {isAnalyzing ? (
                    <>
                      <Zap className="h-4 w-4 mr-2 animate-spin" />
                      Analyzing
                    </>
                  ) : (
                    <>
                      <GitBranch className="h-4 w-4 mr-2" />
                      Analyze
                    </>
                  )}
                </Button>
              </div>

              {isAnalyzing && (
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground flex items-center gap-2">
                      <Clock className="h-4 w-4" />
                      {currentStep}
                    </span>
                    <span className="font-medium">{progress}%</span>
                  </div>
                  <Progress value={progress} className="w-full" />
                </div>
              )}

              {analysisError && (
                <div className="flex items-center gap-2 p-3 bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-800 rounded-lg">
                  <AlertCircle className="h-4 w-4 text-red-600" />
                  <span className="text-sm text-red-600">{analysisError}</span>
                </div>
              )}

              {!isAnalyzing && currentStep.includes("completed") && (
                <div className="flex items-center gap-2 p-3 bg-green-50 dark:bg-green-950/20 border border-green-200 dark:border-green-800 rounded-lg">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span className="text-sm text-green-600">{currentStep}</span>
                </div>
              )}

              <div className="text-sm text-muted-foreground">
                <p className="mb-2">✨ What we analyze:</p>
                <ul className="space-y-1 text-xs">
                  <li>• Security vulnerabilities and best practices</li>
                  <li>• Performance bottlenecks and optimization opportunities</li>
                  <li>• Code quality metrics and maintainability</li>
                  <li>• Documentation coverage and completeness</li>
                  <li>• Architecture patterns and dependencies</li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="trending" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Trending Repositories
              </CardTitle>
              <CardDescription>
                Discover and analyze popular repositories
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex gap-2 mb-4">
                <select
                  className="px-3 py-2 border rounded-md"
                  value={selectedLanguage}
                  onChange={(e) => {
                    setSelectedLanguage(e.target.value)
                    loadTrendingRepos(e.target.value)
                  }}
                  disabled={trendingLoading}
                >
                  <option value="">All Languages</option>
                  <option value="javascript">JavaScript</option>
                  <option value="python">Python</option>
                  <option value="typescript">TypeScript</option>
                  <option value="java">Java</option>
                  <option value="go">Go</option>
                  <option value="rust">Rust</option>
                  <option value="cpp">C++</option>
                  <option value="csharp">C#</option>
                </select>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => loadTrendingRepos(selectedLanguage)}
                  disabled={trendingLoading}
                >
                  {trendingLoading ? <LoadingSpinner size="sm" /> : "Refresh"}
                </Button>
              </div>

              {trendingLoading ? (
                <div className="flex items-center justify-center py-8">
                  <LoadingSpinner />
                  <span className="ml-2 text-muted-foreground">Loading trending repositories...</span>
                </div>
              ) : trendingError ? (
                <ErrorState
                  title="Failed to Load Trending Repositories"
                  message={trendingError}
                  onRetry={() => loadTrendingRepos(selectedLanguage)}
                />
              ) : trendingRepos.length === 0 ? (
                <EmptyState
                  title="No Trending Repositories"
                  message="No trending repositories found for the selected language."
                />
              ) : (
                <div className="grid gap-3 max-h-96 overflow-y-auto">
                  {trendingRepos.map((repo, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50 transition-colors"
                    >
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="font-medium truncate">
                            {githubService.formatRepoName(repo)}
                          </h4>
                          <Badge variant="secondary" className="text-xs">
                            {repo.language || 'Unknown'}
                          </Badge>
                        </div>
                        <div className="flex items-center gap-4 text-xs text-muted-foreground mb-2">
                          <span className="flex items-center gap-1">
                            <Star className="h-3 w-3" />
                            {repo.stars?.toLocaleString() || 0}
                          </span>
                          <span className="flex items-center gap-1">
                            <GitFork className="h-3 w-3" />
                            {repo.forks?.toLocaleString() || 0}
                          </span>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => window.open(repo.url, '_blank')}
                        >
                          <ExternalLink className="h-3 w-3" />
                        </Button>
                        <Button
                          size="sm"
                          onClick={() => analyzeFromTrending(repo)}
                          disabled={isAnalyzing}
                        >
                          Analyze
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}