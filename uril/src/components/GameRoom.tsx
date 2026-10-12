'use client';

import { useState } from 'react';
import { WIN_SCORE, type GameState, type RoomView, type Seat } from '@shared/types';
import { gameClient } from '@/lib/socketClient';
import { useGameStore } from '@/lib/gameStore';
import { Board } from './Board';

interface GameRoomProps {
  view: RoomView;
}

export function GameRoom({ view }: GameRoomProps) {
  const notice = useGameStore((s) => s.notice);
  const setNotice = useGameStore((s) => s.setNotice);

  if (!view.game) return <WaitingRoom code={view.code} />;

  const { game } = view;
  const myName = view.players.find((p) => p.seat === view.seat)?.name ?? 'Tu';
  const opponentName = view.players.find((p) => p.seat !== view.seat)?.name ?? 'Adversário';
  const opponentSeat: Seat = view.seat === 0 ? 1 : 0;

  const myTurn = game.status === 'playing' && game.turn === view.seat;

  async function handlePlay(pit: number) {
    const res = await gameClient.sendMove(pit);
    if (!res.ok) setNotice(res.error);
  }

  return (
    <section className="mx-auto flex w-full max-w-4xl flex-col gap-5">
      <header className="flex flex-wrap items-center justify-between gap-3">
        <p className="text-sm text-amber-200/70">
          Sala <span className="font-mono font-bold tracking-widest text-amber-100">{view.code}</span>
        </p>
        <button
          type="button"
          onClick={() => gameClient.leaveRoom()}
          className="rounded-xl bg-red-900/60 px-4 py-2 text-sm font-semibold text-red-100 hover:bg-red-800/70"
        >
          Sair da sala
        </button>
      </header>

      <div className="grid grid-cols-2 gap-3">
        <PlayerCard name={opponentName} score={game.scores[opponentSeat]} active={!myTurn && game.status === 'playing'} />
        <PlayerCard name={myName} score={game.scores[view.seat]} active={myTurn} you />
      </div>

      <TurnBanner game={game} seat={view.seat} opponentName={opponentName} />

      <Board game={game} seat={view.seat} interactive={myTurn} onPlay={handlePlay} />

      <LastMoveLine game={game} seat={view.seat} myName={myName} opponentName={opponentName} />

      {notice && (
        <p role="alert" className="rounded-xl bg-red-900/50 px-4 py-2 text-center text-sm text-red-100">
          {notice}
        </p>
      )}
    </section>
  );
}

function WaitingRoom({ code }: { code: string }) {
  const [copied, setCopied] = useState(false);

  async function copyCode() {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
    } catch {
      // Sem permissão de clipboard: o código continua visível para ser copiado à mão.
    }
  }

  return (
    <section className="mx-auto flex max-w-md flex-col items-center gap-6 rounded-3xl bg-white/5 p-8 text-center">
      <p className="text-sm uppercase tracking-widest text-amber-200/70">Código da sala</p>
      <p className="font-mono text-5xl font-black tracking-[0.3em] text-amber-100">{code}</p>
      <p className="animate-pulse text-amber-200/80">A aguardar adversário…</p>
      <div className="flex gap-3">
        <button
          type="button"
          onClick={copyCode}
          className="rounded-xl bg-amber-700 px-4 py-2 font-semibold text-amber-50 hover:bg-amber-600"
        >
          {copied ? 'Copiado!' : 'Copiar código'}
        </button>
        <button
          type="button"
          onClick={() => gameClient.leaveRoom()}
          className="rounded-xl bg-white/10 px-4 py-2 font-semibold hover:bg-white/20"
        >
          Cancelar
        </button>
      </div>
    </section>
  );
}

function PlayerCard({ name, score, active, you = false }: { name: string; score: number; active: boolean; you?: boolean }) {
  return (
    <div
      className={`flex items-center gap-3 rounded-2xl px-4 py-3 transition-colors ${
        active ? 'bg-amber-400/20 ring-2 ring-amber-300' : 'bg-white/5'
      }`}
    >
      <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-amber-800 text-lg font-bold text-amber-50">
        {name.slice(0, 1).toUpperCase()}
      </div>
      <div className="min-w-0">
        <p className="truncate font-semibold">
          {name}
          {you && <span className="ml-1 text-xs font-normal opacity-70">(tu)</span>}
        </p>
        <p className="text-2xl font-black tabular-nums">
          {score}
          <span className="text-xs font-normal opacity-70"> / {WIN_SCORE} sementes</span>
        </p>
      </div>
    </div>
  );
}

function TurnBanner({ game, seat, opponentName }: { game: GameState; seat: Seat; opponentName: string }) {
  if (game.status === 'finished') {
    const text =
      game.winner === null ? 'Empate!' : game.winner === seat ? 'Venceste!' : `${opponentName} venceu.`;
    return <p className="text-center text-2xl font-black text-amber-200">{text}</p>;
  }

  const myTurn = game.turn === seat;
  return (
    <p
      className={`text-center text-lg font-bold ${myTurn ? 'text-amber-200' : 'text-amber-100/60'}`}
    >
      {myTurn ? 'A tua vez de semear!' : `Vez de ${opponentName}`}
    </p>
  );
}

function LastMoveLine({
  game,
  seat,
  myName,
  opponentName,
}: {
  game: GameState;
  seat: Seat;
  myName: string;
  opponentName: string;
}) {
  const last = game.lastMove;
  if (!last) return null;

  const who = last.player === seat ? myName : opponentName;
  const capture = last.captured > 0 ? ` e capturou ${last.captured}` : '';
  return (
    <p className="text-center text-sm text-amber-100/70">
      {who} semeou a cova {last.pit + 1}
      {capture}.
    </p>
  );
}
