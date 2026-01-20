"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { MessageSquare, Plus, Trash2, Loader2, MoreVertical, Edit2 } from "lucide-react"
import { cn } from "@/lib/utils"

interface Conversation {
  id: string
  title: string
  created_at: string
  updated_at: string
}

interface ConversationSidebarProps {
  currentConversationId: string | null
  onSelectConversation: (conversationId: string | null) => void
  onNewConversation: () => void
  refreshTrigger?: number
}

export default function ConversationSidebar({
  currentConversationId,
  onSelectConversation,
  onNewConversation,
  refreshTrigger,
}: ConversationSidebarProps) {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [renamingId, setRenamingId] = useState<string | null>(null)
  const [renameValue, setRenameValue] = useState("")

  useEffect(() => {
    loadConversations()
  }, [refreshTrigger])

  const loadConversations = async () => {
    setIsLoading(true)
    try {
      console.log('[ConversationSidebar] Chargement des conversations...')
      const response = await fetch('/api/conversations')
      if (response.ok) {
        const data = await response.json()
        console.log('[ConversationSidebar] Conversations chargées:', data.conversations?.length || 0)
        setConversations(data.conversations || [])
      }
    } catch (error) {
      console.error('Erreur chargement conversations:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDeleteConversation = async (conversationId: string) => {
    if (!confirm('Supprimer cette conversation ?')) return

    try {
      console.log('[ConversationSidebar] Suppression conversation:', conversationId)
      const response = await fetch(`/api/conversations/${conversationId}`, {
        method: 'DELETE',
      })

      if (response.ok) {
        console.log('[ConversationSidebar] Conversation supprimée avec succès')
        setConversations(prev => prev.filter(c => c.id !== conversationId))
        
        // Si on supprime la conversation active, démarrer une nouvelle
        if (currentConversationId === conversationId) {
          onNewConversation()
        }
      } else {
        const errorData = await response.json()
        console.error('[ConversationSidebar] Erreur suppression:', response.status, errorData)
        alert(`Erreur: ${errorData.error || 'Impossible de supprimer'}`)
      }
    } catch (error) {
      console.error('Erreur suppression conversation:', error)
      alert('Erreur lors de la suppression')
    }
  }

  const handleStartRename = (conversationId: string, currentTitle: string) => {
    setRenamingId(conversationId)
    setRenameValue(currentTitle)
  }

  const handleRenameConversation = async (conversationId: string) => {
    if (!renameValue.trim()) {
      setRenamingId(null)
      return
    }

    try {
      const response = await fetch(`/api/conversations/${conversationId}/rename`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: renameValue.trim() }),
      })

      if (response.ok) {
        setConversations(prev =>
          prev.map(c =>
            c.id === conversationId ? { ...c, title: renameValue.trim() } : c
          )
        )
      }
    } catch (error) {
      console.error('Erreur renommage conversation:', error)
    } finally {
      setRenamingId(null)
      setRenameValue("")
    }
  }

  return (
    <div className="flex flex-col h-full bg-neutral-50 dark:bg-neutral-900 border-r border-neutral-200 dark:border-neutral-800">
      {/* Header avec bouton nouvelle conversation */}
      <div className="p-4 border-b border-neutral-200 dark:border-neutral-800">
        <Button
          onClick={onNewConversation}
          className="w-full justify-start gap-2"
          variant="default"
        >
          <Plus className="h-4 w-4" />
          Nouvelle conversation
        </Button>
      </div>

      {/* Liste des conversations */}
      <ScrollArea className="flex-1 p-2">
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-6 w-6 animate-spin text-neutral-400" />
          </div>
        ) : conversations.length === 0 ? (
          <div className="text-center py-8 px-4 text-sm text-neutral-500">
            Aucune conversation
          </div>
        ) : (
          <div className="space-y-1">
            {conversations.map((conversation) => (
              <div
                key={conversation.id}
                className={cn(
                  "group flex items-center gap-2 px-3 py-2.5 rounded-lg transition-colors relative",
                  currentConversationId === conversation.id
                    ? "bg-neutral-200 dark:bg-neutral-800"
                    : "hover:bg-neutral-100 dark:hover:bg-neutral-800/50"
                )}
              >
                <MessageSquare className="h-4 w-4 flex-shrink-0 text-neutral-500" />
                
                <div 
                  className="flex-1 min-w-0 cursor-pointer"
                  onClick={() => onSelectConversation(conversation.id)}
                >
                  {renamingId === conversation.id ? (
                    <input
                      type="text"
                      value={renameValue}
                      onChange={(e) => setRenameValue(e.target.value)}
                      onBlur={() => handleRenameConversation(conversation.id)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                          handleRenameConversation(conversation.id)
                        } else if (e.key === 'Escape') {
                          setRenamingId(null)
                          setRenameValue("")
                        }
                      }}
                      autoFocus
                      className="w-full px-2 py-1 text-sm font-medium bg-white dark:bg-neutral-900 border border-neutral-300 dark:border-neutral-600 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                      onClick={(e) => e.stopPropagation()}
                    />
                  ) : (
                    <p className="text-sm font-medium truncate">
                      {conversation.title || 'Nouvelle conversation'}
                    </p>
                  )}
                </div>

                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-8 w-8 p-0 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <MoreVertical className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="w-48">
                    <DropdownMenuItem
                      onClick={(e: React.MouseEvent) => {
                        e.stopPropagation()
                        handleStartRename(conversation.id, conversation.title || '')
                      }}
                    >
                      <Edit2 className="h-4 w-4 mr-2" />
                      Renommer
                    </DropdownMenuItem>
                    <DropdownMenuItem
                      onClick={(e: React.MouseEvent) => {
                        e.stopPropagation()
                        handleDeleteConversation(conversation.id)
                      }}
                      className="text-red-600 focus:text-red-600"
                    >
                      <Trash2 className="h-4 w-4 mr-2" />
                      Supprimer
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            ))}
          </div>
        )}
      </ScrollArea>
    </div>
  )
}
