"use client"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Upload, BarChart3, AlertTriangle, MessageSquare, FileText, Github, TrendingUp, Building2 } from "lucide-react"

interface SidebarProps {
  activeTab: string
  onTabChange: (tab: string) => void
}

const sidebarItems = [
  { id: "upload", label: "Upload Code", icon: Upload },
  { id: "github", label: "GitHub Analysis", icon: Github },
  { id: "analysis", label: "Analysis", icon: FileText },
  { id: "metrics", label: "Quality Metrics", icon: BarChart3 },
  { id: "trends", label: "Quality Trends", icon: TrendingUp },
  { id: "dashboard", label: "Enterprise", icon: Building2 },
  { id: "issues", label: "Issues", icon: AlertTriangle },
  { id: "chat", label: "AI Assistant", icon: MessageSquare },
]

export function Sidebar({ activeTab, onTabChange }: SidebarProps) {
  return (
    <div className="fixed left-0 top-16 h-[calc(100vh-4rem)] w-64 border-r bg-sidebar">
      <div className="flex flex-col p-4 space-y-2">
        {sidebarItems.map((item) => {
          const Icon = item.icon
          return (
            <Button
              key={item.id}
              variant={activeTab === item.id ? "default" : "ghost"}
              className={cn(
                "w-full justify-start",
                activeTab === item.id && "bg-sidebar-primary text-sidebar-primary-foreground",
              )}
              onClick={() => onTabChange(item.id)}
            >
              <Icon className="mr-2 h-4 w-4" />
              {item.label}
            </Button>
          )
        })}
      </div>
    </div>
  )
}
