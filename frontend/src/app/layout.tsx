import type React from "react"
import type { Metadata } from "next"
import { GeistSans } from "geist/font/sans"
import { GeistMono } from "geist/font/mono"
import { Analytics } from "@vercel/analytics/next"
import { ThemeProvider } from "../components/theme-provider"
import { GlobalErrorBoundary } from "../components/ErrorBoundary"
import { Suspense } from "react"
import "./globals.css"

export const metadata: Metadata = {
  title: "CodeQuality AI - Intelligent Code Analysis",
  description: "AI-powered code quality analysis and insights for modern development teams",
  generator: "v0.app",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`font-sans ${GeistSans.variable} ${GeistMono.variable} antialiased`}>
        <GlobalErrorBoundary>
          <Suspense fallback={null}>
            <ThemeProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange>
              {children}
            </ThemeProvider>
          </Suspense>
        </GlobalErrorBoundary>
        <Analytics />
      </body>
    </html>
  )
}
