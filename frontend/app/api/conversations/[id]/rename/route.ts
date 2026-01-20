import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@/lib/auth';
import { prisma } from '@/lib/prisma';

// PATCH - Renommer une conversation
export async function PATCH(
  req: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const session = await auth();

    if (!session?.user?.id) {
      return NextResponse.json({ error: 'Non authentifié' }, { status: 401 });
    }

    const { id } = await params;
    const { title } = await req.json();

    if (!title || !title.trim()) {
      return NextResponse.json({ error: 'Titre manquant' }, { status: 400 });
    }

    // Vérifier que la conversation appartient à l'utilisateur
    const conversation = await prisma.conversation.findFirst({
      where: {
        id: id,
        userId: session.user.id,
      },
    });

    if (!conversation) {
      return NextResponse.json(
        { error: 'Conversation non trouvée' },
        { status: 404 }
      );
    }

    // Mettre à jour le titre
    const updatedConversation = await prisma.conversation.update({
      where: { id: id },
      data: { title: title.trim() },
    });

    return NextResponse.json({ success: true, conversation: updatedConversation });
  } catch (error: any) {
    console.error('Erreur PATCH conversation:', error);
    return NextResponse.json(
      { error: 'Erreur serveur', details: error?.message },
      { status: 500 }
    );
  }
}
