"use client"

import { useState, useCallback } from "react"
import { useDropzone } from "react-dropzone"
import { Upload, File, X, Loader2, CheckCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"

interface UploadedFile {
  file: File
  progress: number
  status: 'pending' | 'uploading' | 'success' | 'error'
  error?: string
}

interface DocumentUploadProps {
  onUploadComplete?: () => void
  userRole?: string
}

export default function DocumentUpload({ onUploadComplete, userRole }: DocumentUploadProps) {
  const [files, setFiles] = useState<UploadedFile[]>([])
  const [isOrganizationDoc, setIsOrganizationDoc] = useState(false)
  
  const isAdmin = userRole === "ADMIN"

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles = acceptedFiles.map(file => ({
      file,
      progress: 0,
      status: 'pending' as const
    }))
    setFiles(prev => [...prev, ...newFiles])
    
    // Auto-upload pour les non-admins, manuel pour les admins (ils doivent choisir le scope)
    if (!isAdmin) {
      newFiles.forEach((uploadFile, index) => {
        uploadDocument(uploadFile, files.length + index)
      })
    }
  }, [files.length, isAdmin])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    multiple: true
  })

  const uploadDocument = async (uploadFile: UploadedFile, index: number) => {
    setFiles(prev => {
      const updated = [...prev]
      updated[index] = { ...updated[index], status: 'uploading', progress: 0 }
      return updated
    })

    // Capturer la valeur actuelle de isOrganizationDoc au moment de l'upload
    const shouldBeOrgDoc = isAdmin && isOrganizationDoc
    
    const formData = new FormData()
    formData.append('file', uploadFile.file)
    // USER: always personal docs, ADMIN: can choose
    formData.append('isOrganizationDoc', shouldBeOrgDoc.toString())
    
    console.log('[DocumentUpload] Uploading:', uploadFile.file.name, 'isOrganizationDoc:', shouldBeOrgDoc)

    try {
      const response = await fetch('/api/documents', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Upload failed')
      }

      setFiles(prev => {
        const updated = [...prev]
        updated[index] = { ...updated[index], status: 'success', progress: 100 }
        return updated
      })

      // Notify parent
      setTimeout(() => {
        onUploadComplete?.()
      }, 500)

    } catch (error) {
      setFiles(prev => {
        const updated = [...prev]
        updated[index] = { 
          ...updated[index], 
          status: 'error', 
          error: 'Échec de l\'upload' 
        }
        return updated
      })
    }
  }

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
  }

  const uploadPendingFiles = () => {
    files.forEach((file, index) => {
      if (file.status === 'pending') {
        uploadDocument(file, index)
      }
    })
  }

  const hasPendingFiles = files.some(f => f.status === 'pending')

  return (
    <div className="space-y-4">
      {/* Toggle pour ADMIN uniquement */}
      {isAdmin && (
        <div className="space-y-3">
          <div className="flex items-center gap-3 p-3 bg-neutral-50 dark:bg-neutral-900 rounded-lg">
            <input
              type="checkbox"
              id="org-doc-toggle"
              checked={isOrganizationDoc}
              onChange={(e) => setIsOrganizationDoc(e.target.checked)}
              className="w-4 h-4 rounded border-neutral-300"
            />
            <label htmlFor="org-doc-toggle" className="text-sm font-medium cursor-pointer">
              📄 Document global (accessible à tous les membres)
            </label>
          </div>
          {hasPendingFiles && (
            <Button
              onClick={uploadPendingFiles}
              className="w-full"
              size="sm"
            >
              <Upload className="h-4 w-4 mr-2" />
              Uploader {files.filter(f => f.status === 'pending').length} document(s)
            </Button>
          )}
        </div>
      )}
      
      {!isAdmin && (
        <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg text-sm text-blue-900 dark:text-blue-100">
          👤 Vos documents sont personnels et privés
        </div>
      )}

      <Card
        {...getRootProps()}
        className={`border-2 border-dashed p-8 text-center cursor-pointer transition-colors ${
          isDragActive 
            ? 'border-neutral-900 dark:border-neutral-50 bg-neutral-50 dark:bg-neutral-900' 
            : 'border-neutral-300 dark:border-neutral-700 hover:border-neutral-400 dark:hover:border-neutral-600'
        }`}
      >
        <input {...getInputProps()} />
        <Upload className="mx-auto h-12 w-12 text-neutral-400 mb-4" />
        <p className="text-lg font-medium mb-2">
          {isDragActive ? 'Déposez vos fichiers ici' : 'Glissez-déposez vos PDFs'}
        </p>
        <p className="text-sm text-neutral-500">
          ou cliquez pour sélectionner des fichiers
        </p>
      </Card>

      {files.length > 0 && (
        <div className="space-y-2">
          {files.map((uploadFile, index) => (
            <Card key={index} className="p-4">
              <div className="flex items-center gap-3">
                <File className="h-8 w-8 text-neutral-500 flex-shrink-0" />
                
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">
                    {uploadFile.file.name}
                  </p>
                  <p className="text-xs text-neutral-500">
                    {(uploadFile.file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>

                {uploadFile.status === 'uploading' && (
                  <Loader2 className="h-5 w-5 animate-spin text-neutral-500" />
                )}
                {uploadFile.status === 'success' && (
                  <CheckCircle className="h-5 w-5 text-green-500" />
                )}
                {uploadFile.status === 'error' && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeFile(index)}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                )}
              </div>

              {uploadFile.status === 'error' && uploadFile.error && (
                <p className="text-xs text-red-500 mt-2">{uploadFile.error}</p>
              )}
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
