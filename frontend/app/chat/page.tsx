import ChatInterface from '@/components/chat/ChatInterface';
import { auth } from '@/lib/auth';
import { redirect } from 'next/navigation';
import { User } from 'lucide-react';
import SignOutButton from '@/components/auth/SignOutButton';

export default async function ChatPage() {
  const session = await auth();

  if (!session?.user) {
    redirect('/login');
  }

  // Debug: afficher la session complète
  console.log('[CHAT PAGE] Session user:', {
    id: session.user.id,
    email: session.user.email,
    name: session.user.name,
    role: session.user.role,
    organizationId: session.user.organizationId
  });

  return (
    <main className="flex min-h-screen flex-col">
      <header className="border-b bg-white dark:bg-neutral-950 px-6 py-4">
        <div className="mx-auto max-w-7xl flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">AI Solution 🤖</h1>
            <p className="text-sm text-neutral-600 dark:text-neutral-400">Assistant IA privé pour entreprises</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-sm">
              <User className="h-4 w-4" />
              <span className="font-medium">{session.user.name || session.user.email}</span>
              {session.user.role === "ADMIN" && (
                <span className="px-2 py-0.5 text-xs font-semibold bg-blue-600 text-white rounded">
                  ADMIN
                </span>
              )}
            </div>
            <SignOutButton />
          </div>
        </div>
      </header>
      
      <div className="flex-1">
        <ChatInterface userRole={session.user.role} />
      </div>
    </main>
  );
}
