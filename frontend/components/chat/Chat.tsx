'use client';

import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Send, Loader2, FileText, Paperclip, X } from 'lucide-react';

interface Source {
  filename: string;
  chunk_index: number;
  similarity: number;
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
  attachments?: string[]; // Noms des fichiers attachés
  sources?: Source[];
  confidence?: number;
}

interface ChatProps {
  userRole?: string;
  onUploadComplete?: () => void;
  conversationId?: string | null;
  onConversationCreated?: (conversationId: string) => void;
}

export default function Chat({ userRole, onUploadComplete, conversationId, onConversationCreated }: ChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [attachedFiles, setAttachedFiles] = useState<File[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Charger la conversation quand conversationId change
  useEffect(() => {
    console.log('[Chat] conversationId changé:', conversationId)
    if (conversationId) {
      console.log('[Chat] Chargement conversation:', conversationId)
      loadConversation(conversationId)
    } else {
      // Nouvelle conversation
      console.log('[Chat] Nouvelle conversation - messages vides')
      setMessages([])
    }
  }, [conversationId])

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const loadConversation = async (id: string) => {
    try {
      const response = await fetch(`/api/conversations/${id}`)
      if (response.ok) {
        const data = await response.json()
        setMessages(data.messages || [])
      }
    } catch (error) {
      console.error('Erreur chargement conversation:', error)
    }
  }

  const saveMessage = async (userMsg: Message, assistantMsg: Message): Promise<string | null> => {
    try {
      console.log('[Chat] Sauvegarde conversation, ID:', conversationId)
      const response = await fetch('/api/conversations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          conversation_id: conversationId,
          user_message: userMsg.content,
          assistant_message: assistantMsg.content,
          attachments: userMsg.attachments,
          sources: assistantMsg.sources,
        }),
      })

      if (response.ok) {
        const data = await response.json()
        console.log('[Chat] Conversation sauvegardée:', data)
        // Si c'était une nouvelle conversation, mettre à jour l'ID
        if (!conversationId && data.conversation_id) {
          console.log('[Chat] Nouvelle conversation créée avec ID:', data.conversation_id)
          onConversationCreated?.(data.conversation_id)
          return data.conversation_id
        }
        return conversationId
      } else {
        console.error('[Chat] Erreur sauvegarde:', response.status)
        return null
      }
    } catch (error) {
      console.error('Erreur sauvegarde message:', error)
      return null
    }
  }

  const uploadFilesWithConversationId = async (files: File[], convId: string) => {
    console.log('[Upload] Début upload de', files.length, 'fichier(s) avec conversation_id:', convId);
    try {
      for (const file of files) {
        console.log('[Upload] Upload de:', file.name, 'taille:', file.size);
        const formData = new FormData();
        formData.append('file', file);
        formData.append('isOrganizationDoc', 'false');
        formData.append('conversationId', convId);

        console.log('[Upload] Envoi requête POST /api/documents...');
        const response = await fetch('/api/documents', {
          method: 'POST',
          body: formData,
        });

        console.log('[Upload] Réponse status:', response.status);
        if (!response.ok) {
          const errorText = await response.text();
          console.error(`[Upload] Échec upload de ${file.name}:`, errorText);
        } else {
          const data = await response.json();
          console.log('[Upload] Succès:', data);
        }
      }
      console.log('[Upload] Tous les fichiers uploadés');
      onUploadComplete?.();
    } catch (error) {
      console.error('[Upload] Erreur upload fichiers:', error);
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    const pdfFiles = files.filter(f => f.type === 'application/pdf');
    
    if (pdfFiles.length !== files.length) {
      alert('Seuls les fichiers PDF sont acceptés');
    }
    
    if (pdfFiles.length > 0) {
      setAttachedFiles(prev => [...prev, ...pdfFiles]);
    }
    
    // Reset input pour permettre de resélectionner le même fichier
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const uploadAttachedFiles = async () => {
    if (attachedFiles.length === 0) return true;

    setIsUploading(true);
    try {
      // Upload chaque fichier avec le conversation_id
      for (const file of attachedFiles) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('isOrganizationDoc', 'false');
        
        // Ajouter conversation_id si disponible (pour lier le document à la conversation)
        if (conversationId) {
          formData.append('conversationId', conversationId);
        }

        const response = await fetch('/api/documents', {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          throw new Error(`Échec upload de ${file.name}`);
        }
      }

      onUploadComplete?.();
      return true;
    } catch (error) {
      console.error('Erreur upload:', error);
      alert("Échec de l'upload d'un ou plusieurs documents");
      return false;
    } finally {
      setIsUploading(false);
    }
  };

  const handleRemoveFile = (index: number) => {
    setAttachedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if ((!input.trim() && attachedFiles.length === 0) || isLoading) return;

    const filesToUpload = [...attachedFiles]; // Copie pour garder référence

    const userMessage: Message = {
      role: 'user',
      content: input.trim() || '📎 Document(s) ajouté(s)',
      attachments: filesToUpload.length > 0 ? filesToUpload.map(f => f.name) : undefined,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setAttachedFiles([]); // Vider les fichiers attachés
    setIsLoading(true);

    try {
      // 1️⃣ UPLOAD FICHIERS D'ABORD si nécessaire
      let uploadConvId = conversationId;
      
      // Si pas de conversation_id et qu'on a des fichiers, créer la conversation d'abord
      if (!uploadConvId && filesToUpload.length > 0) {
        // Créer la conversation immédiatement pour avoir l'ID
        const convResponse = await fetch('/api/conversations', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_message: input.trim() || '📎 Document(s) ajouté(s)',
            assistant_message: '...', // Temporaire, sera mis à jour après
            attachments: filesToUpload.map(f => f.name)
          })
        });
        
        if (convResponse.ok) {
          const convData = await convResponse.json();
          uploadConvId = convData.conversation_id;
          console.log('[Chat] Conversation créée pour upload:', uploadConvId);
          onConversationCreated?.(uploadConvId);
        } else {
          const errorText = await convResponse.text();
          console.error('[Chat] Erreur création conversation:', errorText);
        }
      }
      
      // Uploader les fichiers AVANT d'envoyer la question
      if (filesToUpload.length > 0 && uploadConvId) {
        console.log('[Chat] Upload de', filesToUpload.length, 'fichier(s) avec conversation_id:', uploadConvId);
        await uploadFilesWithConversationId(filesToUpload, uploadConvId);
        console.log('[Chat] Upload terminé');
      }

      // 2️⃣ ENVOYER LA QUESTION (avec le conversation_id et l'historique)
      // Prendre les 6 derniers messages (3 échanges user/assistant) pour le contexte
      const recentHistory = messages.slice(-6).map(msg => ({
        role: msg.role,
        content: msg.content
      }));
      
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: userMessage.content,
          conversation_id: uploadConvId,
          history: recentHistory,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error('Erreur API chat:', response.status, errorData);
        throw new Error(errorData.error || 'Erreur lors de la requête');
      }

      const data = await response.json();

      const assistantMessage: Message = {
        role: 'assistant',
        content: data.answer,
        sources: data.sources,
        confidence: data.confidence,
      };

      setMessages((prev) => [...prev, assistantMessage]);
      
      // 3️⃣ SAUVEGARDER/METTRE À JOUR LA CONVERSATION
      if (uploadConvId) {
        // Si on a créé une conversation temporaire pour l'upload, la mettre à jour avec la vraie réponse
        await fetch('/api/conversations', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            conversation_id: uploadConvId,
            user_message: userMessage.content,
            assistant_message: assistantMessage.content,
            sources: assistantMessage.sources,
            attachments: userMessage.attachments
          })
        });
      } else if (!conversationId) {
        // Sinon, créer une nouvelle conversation
        await saveMessage(userMessage, assistantMessage);
      }
    } catch (error) {
      console.error('Erreur:', error);
      const errorMessage: Message = {
        role: 'assistant',
        content: "Désolé, une erreur s'est produite. Vérifiez que le backend est démarré.",
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="mx-auto flex h-full max-w-4xl flex-col px-4 py-6">
      {/* Messages */}
      <ScrollArea className="flex-1 pr-4" ref={scrollRef}>
        <div className="space-y-4">
          {messages.length === 0 && (
            <div className="flex h-[60vh] items-center justify-center text-center">
              <div>
                <h2 className="mb-2 text-2xl font-bold text-gray-800">
                  Bonjour ! 👋
                </h2>
                <p className="text-gray-600">
                  Posez-moi des questions sur vos documents.
                </p>
              </div>
            </div>
          )}

          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${
                message.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              <Card
                className={`max-w-[80%] p-4 ${
                  message.role === 'user'
                    ? 'bg-blue-500 text-white'
                    : 'bg-white'
                }`}
              >
                <p className="whitespace-pre-wrap">{message.content}</p>

                {/* Fichiers attachés (pour messages user) */}
                {message.attachments && message.attachments.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1.5">
                    {message.attachments.map((filename, idx) => (
                      <div
                        key={idx}
                        className={`flex items-center gap-1.5 rounded-md px-2 py-1 text-xs ${
                          message.role === 'user'
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-100 text-gray-700'
                        }`}
                      >
                        <FileText className="h-3 w-3" />
                        <span className="max-w-[150px] truncate">{filename}</span>
                      </div>
                    ))}
                  </div>
                )}

                {/* Sources */}
                {message.sources && message.sources.length > 0 && (
                  <div className="mt-3 border-t pt-3">
                    <p className="mb-2 text-xs font-semibold text-gray-600">
                      📚 Sources ({message.confidence?.toFixed(1)}% confiance)
                    </p>
                    <div className="space-y-1">
                      {message.sources.map((source, idx) => (
                        <div
                          key={idx}
                          className="flex items-center gap-2 text-xs text-gray-600"
                        >
                          <FileText className="h-3 w-3" />
                          <span>
                            {source.filename} (chunk {source.chunk_index},{' '}
                            {(source.similarity * 100).toFixed(1)}% similaire)
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </Card>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <Card className="max-w-[80%] bg-white p-4">
                <div className="flex items-center gap-2 text-gray-600">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Recherche dans les documents...</span>
                </div>
              </Card>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Input */}
      <form onSubmit={handleSubmit} className="mt-4">
        {/* Fichiers attachés (style ChatGPT/Gemini) */}
        {attachedFiles.length > 0 && (
          <div className="mb-2 flex flex-wrap gap-2">
            {attachedFiles.map((file, index) => (
              <div
                key={index}
                className="flex items-center gap-2 rounded-lg border bg-blue-50 px-3 py-2 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400"
              >
                <FileText className="h-4 w-4" />
                <span className="max-w-[200px] truncate text-sm font-medium">
                  {file.name}
                </span>
                <button
                  type="button"
                  onClick={() => handleRemoveFile(index)}
                  className="ml-1 rounded-full p-0.5 hover:bg-blue-200 dark:hover:bg-blue-800"
                  disabled={isUploading}
                >
                  <X className="h-3 w-3" />
                </button>
              </div>
            ))}
          </div>
        )}

        <div className="flex gap-2">
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            multiple
            onChange={handleFileSelect}
            className="hidden"
          />
          <Button
            type="button"
            variant="outline"
            size="icon"
            onClick={() => fileInputRef.current?.click()}
            disabled={isLoading || isUploading}
            title="Joindre un document PDF"
          >
            <Paperclip className="h-4 w-4" />
          </Button>
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Posez votre question..."
            disabled={isLoading}
            className="flex-1"
          />
          <Button 
            type="submit" 
            disabled={isLoading || isUploading || (!input.trim() && attachedFiles.length === 0)} 
            className="flex-shrink-0"
          >
            {isLoading || isUploading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>
      </form>
    </div>
  );
}
