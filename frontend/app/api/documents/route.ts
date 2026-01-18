import { NextRequest, NextResponse } from "next/server"
import { auth } from "@/lib/auth"

export async function POST(req: NextRequest) {
  try {
    const session = await auth()
    
    if (!session?.user) {
      return NextResponse.json(
        { error: "Non authentifié" },
        { status: 401 }
      )
    }

    const formData = await req.formData()
    const file = formData.get('file') as File
    const isOrganizationDoc = formData.get('isOrganizationDoc') === 'true'
    
    if (!file) {
      return NextResponse.json(
        { error: "Aucun fichier fourni" },
        { status: 400 }
      )
    }

    // Forward to Python backend
    const backendFormData = new FormData()
    backendFormData.append('file', file)
    
    // Si document d'organisation, passer organization_id; sinon passer user_id
    console.log('[UPLOAD] Session:', {
      userId: session.user.id,
      organizationId: session.user.organizationId,
      role: session.user.role,
      isOrganizationDoc
    })
    
    // Construire l'URL avec les query parameters
    const url = new URL('http://localhost:8001/api/documents/upload')
    
    if (isOrganizationDoc && session.user.organizationId) {
      url.searchParams.append('organization_id', session.user.organizationId)
      console.log('[UPLOAD] Adding organization_id to query:', session.user.organizationId)
    } else if (session.user.id) {
      url.searchParams.append('user_id', session.user.id)
      console.log('[UPLOAD] Adding user_id to query:', session.user.id)
    }

    const response = await fetch(url.toString(), {
      method: 'POST',
      body: backendFormData,
    })

    const data = await response.json()

    if (!response.ok) {
      return NextResponse.json(data, { status: response.status })
    }

    return NextResponse.json(data)
  } catch (error) {
    console.error("Upload error:", error)
    return NextResponse.json(
      { error: "Erreur lors de l'upload" },
      { status: 500 }
    )
  }
}

export async function GET() {
  try {
    const session = await auth()
    
    if (!session?.user) {
      return NextResponse.json(
        { error: "Non authentifié" },
        { status: 401 }
      )
    }

    // Get documents from Python backend filtered by user and organization
    const params = new URLSearchParams({
      user_id: session.user.id
    })
    
    if (session.user.organizationId) {
      params.append('organization_id', session.user.organizationId)
    }
    
    console.log('[GET DOCS] Session:', {
      userId: session.user.id,
      organizationId: session.user.organizationId,
      role: session.user.role
    })
    console.log('[GET DOCS] Query params:', params.toString())
    
    const response = await fetch(
      `http://localhost:8001/api/documents/documents?${params.toString()}`
    )

    const data = await response.json()

    if (!response.ok) {
      return NextResponse.json(data, { status: response.status })
    }

    return NextResponse.json(data)
  } catch (error) {
    console.error("List documents error:", error)
    return NextResponse.json(
      { error: "Erreur lors de la récupération des documents" },
      { status: 500 }
    )
  }
}
