'use client'

import Link from 'next/link'
import { useAppStore } from '@/store/app-store'

export function Header() {
  const { toggleSidebar } = useAppStore()

  return (
    <header className="border-b bg-background">
      <div className="flex h-16 items-center px-4">
        <button
          onClick={toggleSidebar}
          className="mr-4 rounded-md p-2 hover:bg-accent"
          aria-label="Toggle sidebar"
        >
          <svg
            className="h-6 w-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 6h16M4 12h16M4 18h16"
            />
          </svg>
        </button>

        <Link href="/" className="flex items-center space-x-2">
          <span className="text-xl font-bold">AgentLab</span>
        </Link>

        <div className="ml-auto flex items-center space-x-4">
          <span className="text-sm text-muted-foreground">
            {process.env.NEXT_PUBLIC_APP_NAME} v{process.env.NEXT_PUBLIC_APP_VERSION}
          </span>
        </div>
      </div>
    </header>
  )
}
