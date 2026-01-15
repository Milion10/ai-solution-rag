import { NextRequest, NextResponse } from "next/server"
import { auth } from "@/lib/auth"

export async function DELETE(
  req: NextRequest,
  { params }: { params: Promise<{ filename: string }> }
) {
  try {
    const session = await auth()
    
    if (!session?.user) {
      return NextResponse.json(
        { error: "Non authentifié" },
        { status: 401 }
      )
    }

    const { filename } = await params

    // Forward to Python backend with user_id and role
    const params_query = new URLSearchParams({
      user_id: session.user.id
    })
    
    if (session.user.role) {
      params_query.append('role', session.user.role)
    }
    
    const response = await fetch(
      `http://localhost:8000/api/documents/${filename}?${params_query.toString()}`,
      { method: 'DELETE' }
    )

    const data = await response.json()

    if (!response.ok) {
      return NextResponse.json(data, { status: response.status })
    }

    return NextResponse.json(data)
  } catch (error) {
    console.error("Delete document error:", error)
    return NextResponse.json(
      { error: "Erreur lors de la suppression" },
      { status: 500 }
    )
  }
}
