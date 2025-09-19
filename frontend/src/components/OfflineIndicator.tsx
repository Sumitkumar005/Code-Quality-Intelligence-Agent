"use client"

import { useState, useEffect } from 'react'
import { useNetworkStatus } from '@/hooks/useNetworkStatus'
import { Card, CardContent } from '@/components/ui/card'
import { WifiOff, Wifi } from 'lucide-react'
import { Badge } from '@/components/ui/badge'

export function OfflineIndicator() {
  const { isOffline } = useNetworkStatus()
  const [mounted, setMounted] = useState(false)

  // Only render on client to avoid hydration mismatch
  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted || !isOffline) {
    return null
  }

  return (
    <div className="fixed top-4 right-4 z-50 animate-in slide-in-from-top-2">
      <Card className="border-destructive bg-destructive/10">
        <CardContent className="flex items-center gap-2 p-3">
          <WifiOff className="h-4 w-4 text-destructive" />
          <span className="text-sm font-medium text-destructive">
            You're offline
          </span>
          <Badge variant="destructive" className="text-xs">
            No connection
          </Badge>
        </CardContent>
      </Card>
    </div>
  )
}

// Connection status indicator for the status bar
export function ConnectionStatus() {
  const { isOnline, effectiveType } = useNetworkStatus()
  const [mounted, setMounted] = useState(false)

  // Only render on client to avoid hydration mismatch
  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return (
      <div className="flex items-center gap-2 text-xs text-muted-foreground">
        <Wifi className="h-3 w-3 text-green-600" />
        <span>Online</span>
      </div>
    )
  }

  return (
    <div className="flex items-center gap-2 text-xs text-muted-foreground">
      {isOnline ? (
        <>
          <Wifi className="h-3 w-3 text-green-600" />
          <span>Online</span>
          {effectiveType && (
            <Badge variant="outline" className="text-xs">
              {effectiveType.toUpperCase()}
            </Badge>
          )}
        </>
      ) : (
        <>
          <WifiOff className="h-3 w-3 text-red-600" />
          <span>Offline</span>
        </>
      )}
    </div>
  )
}