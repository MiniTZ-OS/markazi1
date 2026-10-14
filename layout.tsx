import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Taghdisi Labs Digital',
  description: 'A modern digital agency experience built with Next.js 16 and Tailwind CSS 4.',
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
