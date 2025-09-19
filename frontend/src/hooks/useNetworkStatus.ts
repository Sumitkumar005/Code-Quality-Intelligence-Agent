"use client"

import { useState, useEffect } from 'react'

interface NetworkStatus {
  isOnline: boolean
  isOffline: boolean
  connectionType: string | null
  effectiveType: string | null
}

export function useNetworkStatus(): NetworkStatus {
  const [networkStatus, setNetworkStatus] = useState<NetworkStatus>({
    isOnline: typeof navigator !== 'undefined' ? navigator.onLine : true,
    isOffline: typeof navigator !== 'undefined' ? !navigator.onLine : false,
    connectionType: null,
    effectiveType: null
  })

  useEffect(() => {
    const updateNetworkStatus = () => {
      const isOnline = navigator.onLine
      
      // Get connection info if available
      const connection = (navigator as any).connection || 
                        (navigator as any).mozConnection || 
                        (navigator as any).webkitConnection

      setNetworkStatus({
        isOnline,
        isOffline: !isOnline,
        connectionType: connection?.type || null,
        effectiveType: connection?.effectiveType || null
      })
    }

    // Initial check
    updateNetworkStatus()

    // Listen for online/offline events
    window.addEventListener('online', updateNetworkStatus)
    window.addEventListener('offline', updateNetworkStatus)

    // Listen for connection changes if supported
    const connection = (navigator as any).connection || 
                      (navigator as any).mozConnection || 
                      (navigator as any).webkitConnection

    if (connection) {
      connection.addEventListener('change', updateNetworkStatus)
    }

    return () => {
      window.removeEventListener('online', updateNetworkStatus)
      window.removeEventListener('offline', updateNetworkStatus)
      
      if (connection) {
        connection.removeEventListener('change', updateNetworkStatus)
      }
    }
  }, [])

  return networkStatus
}

// Hook for retrying operations when network comes back online
export function useNetworkRetry(
  operation: () => Promise<any>,
  enabled: boolean = true
) {
  const { isOnline, isOffline } = useNetworkStatus()
  const [wasOffline, setWasOffline] = useState(false)

  useEffect(() => {
    if (isOffline) {
      setWasOffline(true)
    }
  }, [isOffline])

  useEffect(() => {
    if (enabled && isOnline && wasOffline) {
      // Network came back online, retry the operation
      operation().catch(console.error)
      setWasOffline(false)
    }
  }, [isOnline, wasOffline, operation, enabled])

  return { isOnline, isOffline }
}