import type { Metadata } from 'next';
import type { ReactNode } from 'react';
import './globals.css';

export const metadata: Metadata = {
  title: 'Uril',
  description: 'Uril (Ouril), jogo de semeadura tradicional de Cabo Verde, multiplayer em tempo real.',
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="pt">
      <body className="min-h-screen bg-[radial-gradient(ellipse_at_top,#4a2c15,#1b120c_70%)] text-amber-50 antialiased">
        {children}
      </body>
    </html>
  );
}
