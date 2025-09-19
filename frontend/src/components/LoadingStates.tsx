"use client"

import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Loader2, AlertCircle, FileX, Wifi, RefreshCw, Clock, AlertTriangle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

// Loading spinner component
export function LoadingSpinner({ size = 'default', text }: { size?: 'sm' | 'default' | 'lg', text?: string }) {
  const sizeClasses = {
    sm: 'h-4 w-4',
    default: 'h-6 w-6',
    lg: 'h-8 w-8'
  }

  return (
    <div className="flex items-center justify-center p-4">
      <div className="flex items-center gap-2">
        <Loader2 className={`${sizeClasses[size]} animate-spin text-muted-foreground`} />
        {text && <span className="text-sm text-muted-foreground">{text}</span>}
      </div>
    </div>
  )
}

// Inline loading component for buttons and small areas
export function InlineLoader({ text = "Loading..." }: { text?: string }) {
  return (
    <div className="flex items-center gap-2 text-sm text-muted-foreground">
      <Loader2 className="h-4 w-4 animate-spin" />
      <span>{text}</span>
    </div>
  )
}

// Progress loading component
export function ProgressLoader({ 
  progress, 
  message, 
  title = "Processing..." 
}: { 
  progress: number
  message?: string
  title?: string 
}) {
  return (
    <Card className="max-w-md mx-auto">
      <CardContent className="p-6">
        <div className="flex items-center gap-3 mb-4">
          <Loader2 className="h-5 w-5 animate-spin text-primary" />
          <CardTitle className="text-lg">{title}</CardTitle>
        </div>
        
        <div className="space-y-3">
          <div className="w-full bg-muted rounded-full h-2">
            <div 
              className="bg-primary h-2 rounded-full transition-all duration-300 ease-out"
              style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
            />
          </div>
          
          <div className="flex justify-between items-center">
            <span className="text-sm text-muted-foreground">
              {message || "Processing your request..."}
            </span>
            <Badge variant="outline">{Math.round(progress)}%</Badge>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

// Skeleton loading for quality metrics
export function QualityMetricsSkeleton() {
  return (
    <div className="space-y-6">
      <div>
        <Skeleton className="h-8 w-64 mb-2" />
        <Skeleton className="h-4 w-96" />
      </div>

      {/* Key Metrics Skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[1, 2, 3].map((i) => (
          <Card key={i}>
            <CardHeader>
              <Skeleton className="h-4 w-32" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-8 w-16 mb-2" />
              <Skeleton className="h-2 w-full mb-2" />
              <Skeleton className="h-3 w-24" />
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Charts Skeleton */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {[1, 2].map((i) => (
          <Card key={i}>
            <CardHeader>
              <Skeleton className="h-6 w-48" />
              <Skeleton className="h-4 w-64" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-[300px] w-full" />
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

// Skeleton loading for issue detection
export function IssueDetectionSkeleton() {
  return (
    <div className="space-y-6">
      <div>
        <Skeleton className="h-8 w-48 mb-2" />
        <Skeleton className="h-4 w-80" />
      </div>

      {/* Tabs Skeleton */}
      <div className="space-y-4">
        <div className="flex space-x-2">
          {[1, 2, 3, 4, 5].map((i) => (
            <Skeleton key={i} className="h-10 w-24" />
          ))}
        </div>

        {/* Issues Skeleton */}
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <Card key={i}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Skeleton className="h-4 w-4" />
                    <div>
                      <Skeleton className="h-5 w-48 mb-1" />
                      <Skeleton className="h-4 w-32" />
                    </div>
                  </div>
                  <Skeleton className="h-8 w-8" />
                </div>
              </CardHeader>
            </Card>
          ))}
        </div>
      </div>
    </div>
  )
}

// Skeleton loading for enterprise dashboard
export function EnterpriseDashboardSkeleton() {
  return (
    <div className="space-y-6">
      <div>
        <Skeleton className="h-8 w-64 mb-2" />
        <Skeleton className="h-4 w-96" />
      </div>

      {/* Key Stats Skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i}>
            <CardHeader>
              <Skeleton className="h-4 w-32" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-8 w-16 mb-1" />
              <Skeleton className="h-3 w-24" />
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Charts Grid Skeleton */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i}>
            <CardHeader>
              <Skeleton className="h-6 w-48" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-[200px] w-full" />
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

// Error state component
interface ErrorStateProps {
  title?: string
  message?: string
  onRetry?: () => void
  showRetry?: boolean
  type?: 'error' | 'network' | 'timeout' | 'auth' | 'notFound'
}

export function ErrorState({ 
  title,
  message,
  onRetry,
  showRetry = true,
  type = 'error'
}: ErrorStateProps) {
  const getErrorConfig = () => {
    switch (type) {
      case 'network':
        return {
          icon: <Wifi className="h-12 w-12 text-destructive mb-4" />,
          defaultTitle: "Connection Error",
          defaultMessage: "Unable to connect to the server. Please check your internet connection and try again."
        }
      case 'timeout':
        return {
          icon: <Clock className="h-12 w-12 text-destructive mb-4" />,
          defaultTitle: "Request Timeout",
          defaultMessage: "The request took too long to complete. Please try again."
        }
      case 'auth':
        return {
          icon: <AlertTriangle className="h-12 w-12 text-destructive mb-4" />,
          defaultTitle: "Authentication Error",
          defaultMessage: "You don't have permission to access this resource."
        }
      case 'notFound':
        return {
          icon: <FileX className="h-12 w-12 text-destructive mb-4" />,
          defaultTitle: "Not Found",
          defaultMessage: "The requested resource could not be found."
        }
      default:
        return {
          icon: <AlertCircle className="h-12 w-12 text-destructive mb-4" />,
          defaultTitle: "Something went wrong",
          defaultMessage: "An unexpected error occurred. Please try again."
        }
    }
  }

  const config = getErrorConfig()

  return (
    <Card className="max-w-md mx-auto">
      <CardContent className="flex flex-col items-center justify-center p-6 text-center">
        {config.icon}
        <CardTitle className="mb-2">{title || config.defaultTitle}</CardTitle>
        <CardDescription className="mb-4">{message || config.defaultMessage}</CardDescription>
        {showRetry && onRetry && (
          <Button onClick={onRetry} variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Try Again
          </Button>
        )}
      </CardContent>
    </Card>
  )
}

// Inline error component for smaller spaces
export function InlineError({ 
  message, 
  onRetry 
}: { 
  message: string
  onRetry?: () => void 
}) {
  return (
    <div className="flex items-center gap-2 p-3 bg-destructive/10 border border-destructive/20 rounded-lg">
      <AlertCircle className="h-4 w-4 text-destructive flex-shrink-0" />
      <span className="text-sm text-destructive flex-1">{message}</span>
      {onRetry && (
        <Button size="sm" variant="outline" onClick={onRetry}>
          <RefreshCw className="h-3 w-3" />
        </Button>
      )}
    </div>
  )
}

// Empty state component
interface EmptyStateProps {
  title?: string
  message?: string
  action?: {
    label: string
    onClick: () => void
  }
}

export function EmptyState({ 
  title = "No data available",
  message = "Run an analysis to see results here.",
  action
}: EmptyStateProps) {
  return (
    <Card className="max-w-md mx-auto">
      <CardContent className="flex flex-col items-center justify-center p-6 text-center">
        <FileX className="h-12 w-12 text-muted-foreground mb-4" />
        <CardTitle className="mb-2">{title}</CardTitle>
        <CardDescription className="mb-4">{message}</CardDescription>
        {action && (
          <Button onClick={action.onClick} variant="default">
            {action.label}
          </Button>
        )}
      </CardContent>
    </Card>
  )
}