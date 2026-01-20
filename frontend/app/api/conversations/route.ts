import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@/lib/auth';
import { prisma } from '@/lib/prisma';

// GET - Liste des conversations de l'utilisateur
export async function GET(req: NextRequest) {
  try {
    const session = await auth();

    if (!session?.user?.id) {
      return NextResponse.json({ error: 'Non authentifié' }, { status: 401 });
    }

    const conversations = await prisma.conversation.findMany({
      where: {
        userId: session.user.id,
      },
      orderBy: {
        updatedAt: 'desc',
      },
      select: {
        id: true,
        title: true,
        createdAt: true,
        updatedAt: true,
      },
    });

    return NextResponse.json({ conversations });
  } catch (error) {
    console.error('Erreur GET conversations:', error);
    return NextResponse.json(
      { error: 'Erreur serveur' },
      { status: 500 }
    );
  }
}

// POST - Créer ou mettre à jour une conversation
export async function POST(req: NextRequest) {
  try {
    const session = await auth();

    if (!session?.user?.id) {
      return NextResponse.json({ error: 'Non authentifié' }, { status: 401 });
    }

    const body = await req.json();
    const { conversation_id, user_message, assistant_message, sources } = body;

    let conversation;

    if (conversation_id) {
      // Mettre à jour une conversation existante
      conversation = await prisma.conversation.update({
        where: { id: conversation_id },
        data: {
          updatedAt: new Date(),
          messages: {
            create: [
              {
                role: 'user',
                content: user_message,
              },
              {
                role: 'assistant',
                content: assistant_message,
                sources: sources ? JSON.stringify(sources) : null,
              },
            ],
          },
        },
        include: {
          messages: {
            orderBy: { createdAt: 'asc' },
            take: 1,
          },
        },
      });
    } else {
      // Créer une nouvelle conversation
      // Générer un titre à partir de la première question
      const title = user_message.slice(0, 50) + (user_message.length > 50 ? '...' : '');

      conversation = await prisma.conversation.create({
        data: {
          userId: session.user.id,
          title,
          messages: {
            create: [
              {
                role: 'user',
                content: user_message,
              },
              {
                role: 'assistant',
                content: assistant_message,
                sources: sources ? JSON.stringify(sources) : null,
              },
            ],
          },
        },
      });
    }

    return NextResponse.json({ 
      success: true,
      conversation_id: conversation.id,
    });
  } catch (error) {
    console.error('Erreur POST conversation:', error);
    return NextResponse.json(
      { error: 'Erreur serveur' },
      { status: 500 }
    );
  }
}
