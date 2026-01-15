"use client"

import { useState, useEffect } from "react"
import { File, Trash2, Loader2, Globe, User } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"

interface Document {
  filename: string
  file_size: number
  uploaded_at: string
  is_indexed: boolean
  scope?: string
}

interface DocumentListProps {
  refreshTrigger?: number
  userRole?: string
}

export default function DocumentList({ refreshTrigger, userRole }: DocumentListProps) {
  const [documents, setDocuments] = useState<Document[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [deletingFile, setDeletingFile] = useState<string | null>(null)
  
  const isAdmin = userRole === "ADMIN"

  const fetchDocuments = async () => {
    try {
      const response = await fetch('/api/documents')
      if (response.ok) {
        const data = await response.json()
        setDocuments(data.documents || [])
      }
    } catch (error) {
      console.error('Error fetching documents:', error)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchDocuments()
  }, [refreshTrigger])

  const handleDelete = async (filename: string) => {
    setDeletingFile(filename)
    try {
      const response = await fetch(`/api/documents/${filename}`, {
        method: 'DELETE'
      })
      if (response.ok) {
        setDocuments(prev => prev.filter(doc => doc.filename !== filename))
      }
    } catch (error) {
      console.error('Error deleting document:', error)
    } finally {
      setDeletingFile(null)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / 1024 / 1024).toFixed(1)} MB`
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-6 w-6 animate-spin text-neutral-500" />
      </div>
    )
  }

  if (documents.length === 0) {
    return (
      <div className="text-center p-8 text-neutral-500">
        <File className="h-12 w-12 mx-auto mb-2 opacity-50" />
        <p className="text-sm">Aucun document uploadé</p>
      </div>
    )
  }

  return (
    <ScrollArea className="h-[400px]">
      <div className="space-y-2 pr-4">
        {documents.map((doc) => {
          const isGlobalDoc = doc.scope === "organization"
          const canDelete = isAdmin || !isGlobalDoc
          
          return (
          <Card key={doc.filename} className="p-3">
            <div className="flex items-start gap-3">
              {/* Icône selon le scope */}
              {isGlobalDoc ? (
                <Globe className="h-5 w-5 text-blue-500 mt-0.5 flex-shrink-0" title="Document global" />
              ) : (
                <User className="h-5 w-5 text-purple-500 mt-0.5 flex-shrink-0" title="Document personnel" />
              )}
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <p className="text-sm font-medium truncate">{doc.filename}</p>
                  {isGlobalDoc && (
                    <span className="text-xs px-2 py-0.5 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded">
                      Global
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-2 mt-1 text-xs text-neutral-500">
                  <span>{formatSize(doc.file_size)}</span>
                  <span>•</span>
                  <span>{formatDate(doc.uploaded_at)}</span>
                  {doc.is_indexed && (
                    <>
                      <span>•</span>
                      <span className="text-green-600 dark:text-green-400">Indexé</span>
                    </>
                  )}
                </div>
              </div>

              {canDelete ? (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleDelete(doc.filename)}
                  disabled={deletingFile === doc.filename}
                >
                  {deletingFile === doc.filename ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Trash2 className="h-4 w-4" />
                  )}
                </Button>
              ) : (
                <div className="w-9" /> // Espacement pour alignement
              )}
            </div>
          </Card>
          )
        })}
      </div>
    </ScrollArea>
  )
}
