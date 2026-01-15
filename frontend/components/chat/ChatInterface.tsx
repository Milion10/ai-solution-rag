"use client"

import { useState } from "react"
import Chat from "./Chat"
import DocumentUpload from "@/components/documents/DocumentUpload"
import DocumentList from "@/components/documents/DocumentList"
import { Card } from "@/components/ui/card"
import { FileText, ChevronLeft, ChevronRight } from "lucide-react"
import { Button } from "@/components/ui/button"

interface ChatInterfaceProps {
  userRole?: string
}

export default function ChatInterface({ userRole }: ChatInterfaceProps) {
  const [refreshDocuments, setRefreshDocuments] = useState(0)
  const [sidebarOpen, setSidebarOpen] = useState(true)

  const handleUploadComplete = () => {
    setRefreshDocuments(prev => prev + 1)
  }

  return (
    <div className="flex h-full">
      {/* Sidebar Documents */}
      <div 
        className={`border-r bg-neutral-50 dark:bg-neutral-900 transition-all duration-300 ${
          sidebarOpen ? 'w-80' : 'w-0'
        } overflow-hidden`}
      >
        <div className="p-4 space-y-4 w-80">
          <div className="flex items-center gap-2 mb-4">
            <FileText className="h-5 w-5" />
            <h2 className="font-semibold">Documents</h2>
          </div>

          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-medium mb-2">Upload</h3>
              <DocumentUpload onUploadComplete={handleUploadComplete} userRole={userRole} />
            </div>

            <div>
              <h3 className="text-sm font-medium mb-2">Mes documents</h3>
              <DocumentList refreshTrigger={refreshDocuments} userRole={userRole} />
            </div>
          </div>
        </div>
      </div>

      {/* Toggle Button */}
      <div className="relative">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="absolute top-4 -left-3 z-10 h-8 w-8 p-0 rounded-full border bg-white dark:bg-neutral-950 shadow-md"
        >
          {sidebarOpen ? (
            <ChevronLeft className="h-4 w-4" />
          ) : (
            <ChevronRight className="h-4 w-4" />
          )}
        </Button>
      </div>

      {/* Chat Area */}
      <div className="flex-1">
        <Chat />
      </div>
    </div>
  )
}
