import type { Metadata } from 'next'
import './globals.css'
import { Providers } from '@/lib/providers'

export const metadata: Metadata = {
  title: 'AgentLab',
  description: 'AI Project Management Platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
