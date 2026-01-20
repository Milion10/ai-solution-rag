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
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
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

  const saveMessage = async (userMsg: Message, assistantMsg: Message) => {
    try {
      console.log('[Chat] Sauvegarde conversation, ID:', conversationId)
      const response = await fetch('/api/conversations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          conversation_id: conversationId,
          user_message: userMsg.content,
          assistant_message: assistantMsg.content,
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
        }
      } else {
        console.error('[Chat] Erreur sauvegarde:', response.status)
      }
    } catch (error) {
      console.error('Erreur sauvegarde message:', error)
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.type === 'application/pdf') {
        setSelectedFile(file);
      } else {
        alert('Seuls les fichiers PDF sont acceptés');
      }
    }
  };

  const handleUploadFile = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('isOrganizationDoc', 'false'); // Toujours privé pour les uploads via chat

    try {
      const response = await fetch('/api/documents', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      // Notification de succès
      onUploadComplete?.();
      setSelectedFile(null);
      
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (error) {
      console.error('Erreur upload:', error);
      alert("Échec de l'upload du document");
    } finally {
      setIsUploading(false);
    }
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      role: 'user',
      content: input.trim(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: userMessage.content,
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
      
      // Sauvegarder la conversation
      await saveMessage(userMessage, assistantMessage);
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
        {/* File preview */}
        {selectedFile && (
          <div className="mb-2 flex items-center gap-2 rounded-lg border bg-neutral-50 p-3 dark:bg-neutral-900">
            <FileText className="h-4 w-4 text-blue-500" />
            <span className="flex-1 truncate text-sm">{selectedFile.name}</span>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={handleRemoveFile}
              className="h-6 w-6 p-0"
            >
              <X className="h-4 w-4" />
            </Button>
            <Button
              type="button"
              onClick={handleUploadFile}
              disabled={isUploading}
              size="sm"
            >
              {isUploading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                'Uploader'
              )}
            </Button>
          </div>
        )}

        <div className="flex gap-2">
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            onChange={handleFileSelect}
            className="hidden"
          />
          <Button
            type="button"
            variant="outline"
            size="icon"
            onClick={() => fileInputRef.current?.click()}
            disabled={isLoading || isUploading}
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
          <Button type="submit" disabled={isLoading || !input.trim()}>
            {isLoading ? (
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
