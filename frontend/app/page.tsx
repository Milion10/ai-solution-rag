import Link from "next/link"
import { Button } from "@/components/ui/button"

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-neutral-50 to-neutral-100 dark:from-neutral-950 dark:to-neutral-900 p-4">
      <div className="text-center space-y-6 max-w-2xl">
        <h1 className="text-5xl font-bold tracking-tight">
          AI Solution 🤖
        </h1>
        <p className="text-xl text-neutral-600 dark:text-neutral-400">
          Votre assistant IA pour analyser et interroger vos documents
        </p>
        <div className="flex gap-4 justify-center pt-4">
          <Button asChild size="lg">
            <Link href="/signup">
              Commencer
            </Link>
          </Button>
          <Button asChild variant="outline" size="lg">
            <Link href="/login">
              Se connecter
            </Link>
          </Button>
        </div>
      </div>
    </div>
  )
}
