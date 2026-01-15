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

    const { question } = await req.json()
    
    if (!question) {
      return NextResponse.json(
        { error: "Question manquante" },
        { status: 400 }
      )
    }

    // Forward to Python backend with user_id and organization_id
    const response = await fetch('http://localhost:8000/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question,
        user_id: session.user.id,
        organization_id: session.user.organizationId
      }),
    })

    const data = await response.json()

    if (!response.ok) {
      return NextResponse.json(data, { status: response.status })
    }

    return NextResponse.json(data)
  } catch (error) {
    console.error("Chat error:", error)
    return NextResponse.json(
      { error: "Erreur lors du traitement de la question" },
      { status: 500 }
    )
  }
}
