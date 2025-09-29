import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'AgentLab',
  description: 'AI Development Platform with BMAD Method Automation',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
