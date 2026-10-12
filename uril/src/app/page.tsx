'use client';

import { useEffect } from 'react';
import { GameRoom } from '@/components/GameRoom';
import { Lobby } from '@/components/Lobby';
import { useGameStore } from '@/lib/gameStore';
import { gameClient } from '@/lib/socketClient';

/** Sem sala: lobby. Com sala: sala de espera ou tabuleiro, conforme o servidor indicar. */
export default function HomePage() {
  const view = useGameStore((s) => s.view);

  useEffect(() => {
    gameClient.connect();
  }, []);

  return <main className="min-h-screen px-4 py-8 sm:py-12">{view ? <GameRoom view={view} /> : <Lobby />}</main>;
}
