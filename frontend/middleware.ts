import { auth } from "@/lib/auth"
import { NextResponse } from "next/server"

export default auth((req) => {
  const isLoggedIn = !!req.auth
  const isAuthPage = req.nextUrl.pathname.startsWith('/login') || 
                     req.nextUrl.pathname.startsWith('/signup')

  // Si connecté et sur page auth, rediriger vers /chat
  if (isLoggedIn && isAuthPage) {
    return NextResponse.redirect(new URL('/chat', req.url))
  }

  // Si non connecté et sur page protégée, rediriger vers /login
  if (!isLoggedIn && !isAuthPage && req.nextUrl.pathname.startsWith('/chat')) {
    return NextResponse.redirect(new URL('/login', req.url))
  }

  return NextResponse.next()
})

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
}
