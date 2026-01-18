"use client"

import { useState } from "react"
import Chat from "./Chat"

interface ChatInterfaceProps {
  userRole?: string
}

export default function ChatInterface({ userRole }: ChatInterfaceProps) {
  const [refreshDocuments, setRefreshDocuments] = useState(0)

  const handleUploadComplete = () => {
    setRefreshDocuments(prev => prev + 1)
  }

  return (
    <div className="flex h-full">
      {/* Chat Area - Pleine largeur */}
      <div className="flex-1">
        <Chat userRole={userRole} onUploadComplete={handleUploadComplete} />
      </div>
    </div>
  )
}
