"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"
import { MessageSquare, Send, Bot, User, Lightbulb, TrendingUp, AlertCircle, FileText } from "lucide-react"
import { useAnalysis } from "@/contexts"
import { useAnalysisChat, useIssues } from "@/hooks"
import { analysisService } from "@/services"
import { EmptyState } from "@/components/LoadingStates"

interface ChatInterfaceProps {
  reportId?: string
}

interface Message {
  id: string
  type: "user" | "assistant"
  content: string
  timestamp: Date
}

export function ChatInterface({ reportId }: ChatInterfaceProps) {
  const { currentAnalysis, currentReportId } = useAnalysis()
  const activeReportId = reportId || currentReportId
  
  const { issues } = useIssues(activeReportId)
  const { askQuestion, loading: chatLoading, error: chatError } = useAnalysisChat(activeReportId)
  
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [isInitialized, setIsInitialized] = useState(false)

  // Initialize chat with context-aware welcome message
  useEffect(() => {
    if (!isInitialized) {
      const welcomeMessage = getWelcomeMessage()
      setMessages([{
        id: "welcome",
        type: "assistant",
        content: welcomeMessage,
        timestamp: new Date(),
      }])
      setIsInitialized(true)
    }
  }, [currentAnalysis, isInitialized])

  const getWelcomeMessage = (): string => {
    if (!currentAnalysis || !activeReportId) {
      return "Hello! I'm your Code Quality AI Assistant. Please run a code analysis first, and I'll be able to help you understand your results, explain issues, and provide recommendations about your codebase."
    }

    const totalIssues = issues?.length || 0
    const qualityScore = currentAnalysis.summary?.quality_score || 0
    const totalFiles = currentAnalysis.summary?.total_files || 0

    return `Hello! I'm your Code Quality AI Assistant. I've analyzed your codebase with ${totalFiles} files and found ${totalIssues} issues. Your current quality score is ${qualityScore.toFixed(1)}/100. I can help you understand these results, explain specific issues, and provide recommendations. What would you like to know?`
  }

  // Generate context-aware suggested questions
  const getSuggestedQuestions = (): string[] => {
    if (!currentAnalysis || !issues) {
      return [
        "How do I get started with code analysis?",
        "What types of issues can you detect?",
        "How is the quality score calculated?",
      ]
    }

    const securityIssues = issues.filter(issue => issue.type === 'Security').length
    const performanceIssues = issues.filter(issue => issue.type === 'Performance').length
    const qualityIssues = issues.filter(issue => issue.type === 'Quality').length
    const testingIssues = issues.filter(issue => issue.type === 'Testing').length
    const highSeverityIssues = issues.filter(issue => issue.severity === 'High').length

    const questions: string[] = []

    if (highSeverityIssues > 0) {
      questions.push("What are the most critical issues I should fix first?")
    }

    if (securityIssues > 0) {
      questions.push(`Explain the ${securityIssues} security issues found`)
    }

    if (performanceIssues > 0) {
      questions.push("What performance optimizations do you recommend?")
    }

    if (qualityIssues > 0) {
      questions.push("How can I improve my code quality?")
    }

    if (testingIssues > 0) {
      questions.push("How can I improve my test coverage?")
    }

    // Add general questions
    questions.push("How does my code quality compare to industry standards?")
    questions.push("What are the main causes of technical debt in my code?")

    return questions.slice(0, 6) // Limit to 6 questions
  }

  const suggestedQuestions = getSuggestedQuestions()

  const handleSendMessage = async () => {
    if (!input.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: input,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    const currentInput = input
    setInput("")

    try {
      // Use the analysis chat hook which handles the API call
      const answer = await askQuestion(currentInput)

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "assistant",
        content: answer,
        timestamp: new Date(),
      }

      setMessages((prev) => [...prev, assistantMessage])

    } catch (error) {
      console.error('Chat error:', error)
      
      // Enhanced fallback responses based on real analysis data
      let response = generateFallbackResponse(currentInput)

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "assistant",
        content: response,
        timestamp: new Date(),
      }

      setMessages((prev) => [...prev, assistantMessage])
    }
  }

  const generateFallbackResponse = (question: string): string => {
    const lowerQuestion = question.toLowerCase()

    if (!currentAnalysis || !activeReportId) {
      return "I don't have access to analysis data right now. Please run a code analysis first, and I'll be able to provide specific insights about your codebase."
    }

    const totalIssues = issues?.length || 0
    const securityIssues = issues?.filter(issue => issue.type === 'Security').length || 0
    const performanceIssues = issues?.filter(issue => issue.type === 'Performance').length || 0
    const qualityIssues = issues?.filter(issue => issue.type === 'Quality').length || 0
    const highSeverityIssues = issues?.filter(issue => issue.severity === 'High').length || 0
    const qualityScore = currentAnalysis.summary?.quality_score || 0
    const totalFiles = currentAnalysis.summary?.total_files || 0

    if (lowerQuestion.includes('security') || lowerQuestion.includes('vulnerabilit')) {
      if (securityIssues > 0) {
        return `I found ${securityIssues} security issues in your codebase. These include potential vulnerabilities that should be addressed promptly. Check the Issue Detection tab for detailed information about each security concern.`
      } else {
        return "Great news! I didn't detect any security issues in your current analysis. Your code appears to follow good security practices."
      }
    }

    if (lowerQuestion.includes('performance') || lowerQuestion.includes('optim')) {
      if (performanceIssues > 0) {
        return `I identified ${performanceIssues} performance-related issues in your code. These could impact your application's speed and efficiency. Consider reviewing the specific recommendations in the Issue Detection section.`
      } else {
        return "Your code doesn't show any obvious performance issues in the current analysis. Good job on writing efficient code!"
      }
    }

    if (lowerQuestion.includes('quality') || lowerQuestion.includes('score')) {
      return `Your current quality score is ${qualityScore.toFixed(1)}/100. This is based on ${totalIssues} total issues found across ${totalFiles} files. ${qualityScore >= 80 ? 'This is a good score!' : qualityScore >= 60 ? 'There\'s room for improvement.' : 'Consider focusing on the high-priority issues first.'}`
    }

    if (lowerQuestion.includes('critical') || lowerQuestion.includes('high') || lowerQuestion.includes('priority')) {
      if (highSeverityIssues > 0) {
        return `You have ${highSeverityIssues} high-severity issues that require immediate attention. These are the most critical problems that could significantly impact your code quality or security.`
      } else {
        return "Excellent! You don't have any high-severity issues. Your code is in good shape from a critical issues perspective."
      }
    }

    if (lowerQuestion.includes('test') || lowerQuestion.includes('coverage')) {
      const calculatedMetrics = analysisService.calculateMetricsFromAnalysis(currentAnalysis)
      const testCoverage = calculatedMetrics?.test_coverage || 0
      return `Based on the analysis, your estimated test coverage is ${testCoverage.toFixed(1)}%. ${testCoverage >= 80 ? 'This is excellent coverage!' : testCoverage >= 60 ? 'Consider adding more tests to reach 80%+.' : 'Your test coverage could be significantly improved.'}`
    }

    // General response with real data
    return `Based on your analysis of ${totalFiles} files, I found ${totalIssues} issues with a quality score of ${qualityScore.toFixed(1)}/100. ${totalIssues === 0 ? 'Your code looks great!' : 'You can explore the specific issues in the Issue Detection tab.'} Feel free to ask about specific aspects like security, performance, or quality improvements.`
  }

  const handleSuggestedQuestion = (question: string) => {
    setInput(question)
  }

  // Show empty state when no analysis available
  if (!currentAnalysis || !activeReportId) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-3xl font-bold text-foreground mb-2">AI Assistant</h2>
          <p className="text-muted-foreground">Ask questions about your code analysis and get intelligent insights.</p>
        </div>
        <EmptyState
          title="No Analysis Available"
          message="Run a code analysis to start chatting with the AI assistant about your codebase."
          action={{
            label: "Upload Files",
            onClick: () => window.location.href = "/"
          }}
        />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-foreground mb-2">AI Assistant</h2>
        <p className="text-muted-foreground">Ask questions about your code analysis and get intelligent insights.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Chat Interface */}
        <div className="lg:col-span-3">
          <Card className="h-[600px] flex flex-col">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="h-5 w-5" />
                Chat with AI Assistant
              </CardTitle>
              <CardDescription>Get personalized insights about your code quality analysis</CardDescription>
            </CardHeader>

            <CardContent className="flex-1 flex flex-col">
              <ScrollArea className="flex-1 pr-4">
                <div className="space-y-4">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex gap-3 ${message.type === "user" ? "justify-end" : "justify-start"}`}
                    >
                      <div
                        className={`flex gap-3 max-w-[80%] ${
                          message.type === "user" ? "flex-row-reverse" : "flex-row"
                        }`}
                      >
                        <div
                          className={`w-8 h-8 rounded-full flex items-center justify-center ${
                            message.type === "user"
                              ? "bg-primary text-primary-foreground"
                              : "bg-muted text-muted-foreground"
                          }`}
                        >
                          {message.type === "user" ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                        </div>
                        <div
                          className={`rounded-lg p-3 ${
                            message.type === "user"
                              ? "bg-primary text-primary-foreground"
                              : "bg-muted text-muted-foreground"
                          }`}
                        >
                          <p className="text-sm">{message.content}</p>
                          <p className="text-xs opacity-70 mt-1">{message.timestamp.toLocaleTimeString()}</p>
                        </div>
                      </div>
                    </div>
                  ))}

                  {chatLoading && (
                    <div className="flex gap-3">
                      <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center">
                        <Bot className="h-4 w-4 text-muted-foreground" />
                      </div>
                      <div className="bg-muted rounded-lg p-3">
                        <div className="flex space-x-1">
                          <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"></div>
                          <div
                            className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"
                            style={{ animationDelay: "0.1s" }}
                          ></div>
                          <div
                            className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"
                            style={{ animationDelay: "0.2s" }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  )}

                  {chatError && (
                    <div className="flex gap-3">
                      <div className="w-8 h-8 rounded-full bg-red-100 dark:bg-red-950/20 flex items-center justify-center">
                        <AlertCircle className="h-4 w-4 text-red-600" />
                      </div>
                      <div className="bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-800 rounded-lg p-3">
                        <p className="text-sm text-red-600">
                          I'm having trouble connecting to the analysis service. Please try again or check your connection.
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </ScrollArea>

              <div className="flex gap-2 mt-4">
                <Input
                  placeholder="Ask about your code quality, issues, or recommendations..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
                  disabled={chatLoading}
                />
                <Button onClick={handleSendMessage} disabled={chatLoading || !input.trim()}>
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Suggested Questions */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-sm">
                <Lightbulb className="h-4 w-4" />
                Suggested Questions
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {suggestedQuestions.map((question, index) => (
                <Button
                  key={index}
                  variant="ghost"
                  size="sm"
                  className="w-full text-left justify-start h-auto p-2 text-xs"
                  onClick={() => handleSuggestedQuestion(question)}
                >
                  {question}
                </Button>
              ))}
            </CardContent>
          </Card>

          {/* Quick Stats - Now using REAL data */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-sm">
                <TrendingUp className="h-4 w-4" />
                Analysis Summary
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs text-muted-foreground">Quality Score</span>
                <Badge variant="default">
                  {currentAnalysis.summary?.quality_score?.toFixed(1) || 0}/100
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-muted-foreground">Total Issues</span>
                <Badge variant="secondary">{issues?.length || 0}</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-muted-foreground">Files Analyzed</span>
                <Badge variant="outline">{currentAnalysis.summary?.total_files || 0}</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-muted-foreground">Lines of Code</span>
                <Badge variant="outline">
                  {currentAnalysis.summary?.total_lines?.toLocaleString() || 0}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-muted-foreground">High Severity</span>
                <Badge variant={issues?.filter(issue => issue.severity === 'High').length ? "destructive" : "default"}>
                  {issues?.filter(issue => issue.severity === 'High').length || 0}
                </Badge>
              </div>
            </CardContent>
          </Card>

          {/* Analysis Status */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-sm">
                <FileText className="h-4 w-4" />
                Analysis Status
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs text-muted-foreground">Status</span>
                <Badge variant={currentAnalysis.status === 'completed' ? "default" : "secondary"}>
                  {currentAnalysis.status}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-muted-foreground">Report ID</span>
                <span className="text-xs font-mono">{activeReportId?.slice(-8)}</span>
              </div>
              {currentAnalysis.project_id && (
                <div className="flex items-center justify-between">
                  <span className="text-xs text-muted-foreground">Project ID</span>
                  <span className="text-xs font-mono">{currentAnalysis.project_id.slice(-8)}</span>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
