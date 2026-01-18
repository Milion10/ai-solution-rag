import { auth } from '@/lib/auth';
import { redirect } from 'next/navigation';
import { User, ArrowLeft } from 'lucide-react';
import SignOutButton from '@/components/auth/SignOutButton';
import Link from 'next/link';
import DashboardContent from '@/components/dashboard/DashboardContent';

export default async function DashboardPage() {
  const session = await auth();

  if (!session?.user) {
    redirect('/login');
  }

  // Seuls les ADMIN peuvent accéder au dashboard
  if (session.user.role !== 'ADMIN') {
    redirect('/chat');
  }

  return (
    <main className="flex min-h-screen flex-col">
      <header className="border-b bg-white dark:bg-neutral-950 px-6 py-4">
        <div className="mx-auto max-w-7xl flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link 
              href="/chat"
              className="flex items-center gap-2 text-sm text-neutral-600 hover:text-neutral-900 dark:text-neutral-400 dark:hover:text-neutral-100"
            >
              <ArrowLeft className="h-4 w-4" />
              Retour au chat
            </Link>
            <div className="h-6 w-px bg-neutral-300 dark:bg-neutral-700" />
            <div>
              <h1 className="text-2xl font-bold">Dashboard Admin 🛠️</h1>
              <p className="text-sm text-neutral-600 dark:text-neutral-400">Gestion des documents</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-sm">
              <User className="h-4 w-4" />
              <span className="font-medium">{session.user.name || session.user.email}</span>
              <span className="px-2 py-0.5 text-xs font-semibold bg-blue-600 text-white rounded">
                ADMIN
              </span>
            </div>
            <SignOutButton />
          </div>
        </div>
      </header>
      
      <div className="flex-1 bg-neutral-50 dark:bg-neutral-900">
        <div className="mx-auto max-w-7xl px-6 py-8">
          <DashboardContent userRole={session.user.role || 'USER'} />
        </div>
      </div>
    </main>
  );
}
