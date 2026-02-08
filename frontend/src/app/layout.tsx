import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { PlayerProvider } from '@/contexts/PlayerContext';
import { AuthProvider } from '@/contexts/AuthContext';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import PlayerBar from '@/components/PlayerBar';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: {
    default: 'MusicLib - Free AI Background Music',
    template: '%s | MusicLib',
  },
  description:
    'Download free AI-generated background music for your videos, podcasts, and projects. Royalty-free, no attribution required.',
  openGraph: {
    title: 'MusicLib - Free AI Background Music',
    description:
      'Download free AI-generated background music for your videos, podcasts, and projects.',
    type: 'website',
    siteName: 'MusicLib',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={inter.className}>
        <AuthProvider>
          <PlayerProvider>
            <div className="flex min-h-screen flex-col">
              <Header />
              <main className="flex-1">{children}</main>
              <Footer />
              <PlayerBar />
            </div>
          </PlayerProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
