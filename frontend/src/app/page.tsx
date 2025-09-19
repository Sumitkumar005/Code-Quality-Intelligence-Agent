"use client"

import { useState } from "react"
import { Header } from "../components/header"
import { Sidebar } from "../components/sidebar"
import { FileUpload } from "../components/file-upload"
import { AnalysisResults } from "../components/analysis-results"
import { QualityMetrics } from "../components/quality-metrics"
import { IssueDetection } from "../components/issue-detection"
import { ChatInterface } from "../components/chat-interface"
import { GitHubAnalyzer } from "../components/advanced/github-analyzer"
import { QualityTrendsChart } from "../components/charts/quality-trends-chart"
import { EnterpriseDashboard } from "../components/advanced/enterprise-dashboard"
import { AnalysisProvider } from "../contexts"
import { OfflineIndicator } from "../components/OfflineIndicator"

export default function HomePage() {
  const [activeTab, setActiveTab] = useState("upload")
  const [analysisData, setAnalysisData] = useState(null)

  const handleAnalysisComplete = (data: any) => {
    setAnalysisData(data)
    // Switch to analysis tab when complete
    if (data && data.status === 'completed') {
      setActiveTab("analysis")
    }
  }

  return (
    <AnalysisProvider>
      <div className="min-h-screen bg-background">
        <OfflineIndicator />
        <Header />
        <div className="flex">
          <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />
          <main className="flex-1 p-6 ml-64">
            {activeTab === "upload" && <FileUpload onAnalysisComplete={handleAnalysisComplete} />}
            {activeTab === "github" && <GitHubAnalyzer onAnalysisComplete={handleAnalysisComplete} />}
            {activeTab === "analysis" && <AnalysisResults data={analysisData} />}
            {activeTab === "metrics" && <QualityMetrics />}
            {activeTab === "trends" && <QualityTrendsChart />}
            {activeTab === "dashboard" && <EnterpriseDashboard />}
            {activeTab === "issues" && <IssueDetection />}
            {activeTab === "chat" && <ChatInterface />}
          </main>
        </div>
      </div>
    </AnalysisProvider>
  )
}
