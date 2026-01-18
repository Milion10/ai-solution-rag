"use client"

import { useState } from "react"
import DocumentUpload from "@/components/documents/DocumentUpload"
import DocumentList from "@/components/documents/DocumentList"

interface DashboardContentProps {
  userRole: string
}

export default function DashboardContent({ userRole }: DashboardContentProps) {
  const [refreshTrigger, setRefreshTrigger] = useState(0)

  const handleUploadComplete = () => {
    setRefreshTrigger(prev => prev + 1)
  }

  return (
    <div className="grid gap-6 md:grid-cols-2">
      {/* Colonne Upload */}
      <div className="space-y-4">
        <div className="rounded-lg border bg-white dark:bg-neutral-950 p-6">
          <h2 className="text-lg font-semibold mb-4">📤 Upload de documents</h2>
          <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-4">
            Ajoutez des documents PDF globaux pour toute l'organisation
          </p>
          <DocumentUpload 
            onUploadComplete={handleUploadComplete} 
            userRole={userRole}
            forceGlobal={true}
          />
        </div>
      </div>

      {/* Colonne Liste des documents */}
      <div className="space-y-4">
        <div className="rounded-lg border bg-white dark:bg-neutral-950 p-6">
          <h2 className="text-lg font-semibold mb-4">📚 Documents disponibles</h2>
          <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-4">
            Liste de tous les documents indexés
          </p>
          <DocumentList 
            refreshTrigger={refreshTrigger} 
            userRole={userRole} 
          />
        </div>
      </div>
    </div>
  )
}
