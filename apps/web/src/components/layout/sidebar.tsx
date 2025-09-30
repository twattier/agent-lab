'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useAppStore } from '@/store/app-store'
import { cn } from '@/lib/utils'

const navigation = [
  { name: 'Dashboard', href: '/', icon: '📊' },
  { name: 'Projects', href: '/projects', icon: '📁' },
  { name: 'Clients', href: '/clients', icon: '👥' },
]

export function Sidebar() {
  const pathname = usePathname()
  const { sidebarOpen } = useAppStore()

  if (!sidebarOpen) return null

  return (
    <aside className="w-64 border-r bg-background">
      <nav className="flex flex-col gap-1 p-4">
        {navigation.map((item) => {
          const isActive = pathname === item.href
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary text-primary-foreground'
                  : 'hover:bg-accent hover:text-accent-foreground'
              )}
            >
              <span>{item.icon}</span>
              <span>{item.name}</span>
            </Link>
          )
        })}
      </nav>
    </aside>
  )
}
