"use client"

import { useState } from "react"
import Chat from "./Chat"
import ConversationSidebar from "./ConversationSidebar"
import { Button } from "@/components/ui/button"
import { ChevronLeft, ChevronRight } from "lucide-react"

interface ChatInterfaceProps {
  userRole?: string
}

export default function ChatInterface({ userRole }: ChatInterfaceProps) {
  const [refreshDocuments, setRefreshDocuments] = useState(0)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null)
  const [refreshConversations, setRefreshConversations] = useState(0)

  const handleUploadComplete = () => {
    setRefreshDocuments(prev => prev + 1)
  }

  const handleNewConversation = () => {
    console.log('[ChatInterface] Nouvelle conversation - reset ID')
    setCurrentConversationId(null)
    // Le Chat component se réinitialisera quand conversationId devient null
  }

  const handleSelectConversation = (conversationId: string | null) => {
    console.log('[ChatInterface] Sélection conversation:', conversationId)
    setCurrentConversationId(conversationId)
  }

  const handleConversationCreated = (conversationId: string) => {
    console.log('[ChatInterface] Conversation créée:', conversationId)
    setCurrentConversationId(conversationId)
    setRefreshConversations(prev => prev + 1) // Rafraîchir la sidebar
  }

  return (
    <div className="flex h-full relative">
      {/* Sidebar des conversations */}
      {sidebarOpen && (
        <div className="w-64 flex-shrink-0">
          <ConversationSidebar
            currentConversationId={currentConversationId}
            onSelectConversation={handleSelectConversation}
            onNewConversation={handleNewConversation}
            refreshTrigger={refreshConversations}
          />
        </div>
      )}

      {/* Toggle Button */}
      <Button
        variant="ghost"
        size="sm"
        onClick={() => setSidebarOpen(!sidebarOpen)}
        className="absolute left-0 top-4 z-10 h-8 w-8 p-0 rounded-r-md rounded-l-none border-l-0"
        style={{ left: sidebarOpen ? '256px' : '0' }}
      >
        {sidebarOpen ? (
          <ChevronLeft className="h-4 w-4" />
        ) : (
          <ChevronRight className="h-4 w-4" />
        )}
      </Button>

      {/* Chat Area */}
      <div className="flex-1">
        <Chat 
          userRole={userRole} 
          onUploadComplete={handleUploadComplete}
          conversationId={currentConversationId}
          onConversationCreated={handleConversationCreated}
        />
      </div>
    </div>
  )
}
