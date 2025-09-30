import type { Metadata } from 'next';
import './globals.css';
import { Providers } from '@/lib/providers';
import { ErrorBoundary } from '@/components/error-boundary';
import { Header } from '@/components/layout/header';
import { Sidebar } from '@/components/layout/sidebar';
import { Footer } from '@/components/layout/footer';

export const metadata: Metadata = {
  title: 'AgentLab',
  description: 'AI Project Management Platform',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <ErrorBoundary>
          <Providers>
            <div className="flex min-h-screen flex-col">
              <Header />
              <div className="flex flex-1">
                <Sidebar />
                <main className="flex-1 p-6">{children}</main>
              </div>
              <Footer />
            </div>
          </Providers>
        </ErrorBoundary>
      </body>
    </html>
  );
}
