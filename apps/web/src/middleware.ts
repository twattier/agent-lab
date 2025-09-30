import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(_request: NextRequest) {
  // Route protection will be implemented with NextAuth.js in future story
  // For now, allow all routes
  return NextResponse.next()
}

export const config = {
  matcher: '/dashboard/:path*',
}
