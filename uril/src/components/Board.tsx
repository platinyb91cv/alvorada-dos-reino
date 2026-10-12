'use client';

import type { CSSProperties } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { PITS_PER_SIDE, ownerOfPit, type GameState, type Seat } from '@shared/types';

/** Acima deste número as sementes deixam de ser desenhadas (o número continua visível). */
const MAX_DRAWN_SEEDS = 18;
/** Ângulo áureo: espalha as sementes dentro da cova sem as alinhar. */
const GOLDEN_ANGLE = 2.399963;

const SEED_BACKGROUND = 'radial-gradient(circle at 30% 30%, #f7ead0, #c49b64 60%, #6e4a28)';

interface BoardProps {
  game: GameState;
  /** Lado de quem está a ver: o seu lado fica sempre em baixo. */
  seat: Seat;
  /** false quando não é a vez deste jogador ou o jogo acabou. */
  interactive: boolean;
  onPlay: (pit: number) => void;
}

const range = (n: number) => Array.from({ length: n }, (_, i) => i);

/**
 * Disposição visual. Para o Jogador 1: fundo 0→5, topo 11→6 (fluxo anti-horário).
 * Para o Jogador 2 o tabuleiro roda 180º, para que as suas covas fiquem em baixo.
 */
function layout(seat: Seat): { bottom: number[]; top: number[] } {
  if (seat === 0) {
    return { bottom: range(PITS_PER_SIDE), top: range(PITS_PER_SIDE).map((i) => 11 - i) };
  }
  return { bottom: range(PITS_PER_SIDE).map((i) => 6 + i), top: range(PITS_PER_SIDE).map((i) => 5 - i) };
}

/** Posição de uma semente dentro da cova (em %), em espiral determinística. */
function seedPosition(i: number): CSSProperties {
  const radius = Math.min(26, 6 * Math.sqrt(i));
  const angle = i * GOLDEN_ANGLE;
  return {
    left: `${50 + radius * Math.cos(angle)}%`,
    top: `${50 + radius * Math.sin(angle)}%`,
  };
}

interface PitProps {
  pit: number;
  seeds: number;
  enabled: boolean;
  highlighted: boolean;
  onPlay: (pit: number) => void;
}

function Pit({ pit, seeds, enabled, highlighted, onPlay }: PitProps) {
  const drawn = range(Math.min(seeds, MAX_DRAWN_SEEDS));

  return (
    <button
      type="button"
      disabled={!enabled}
      onClick={() => onPlay(pit)}
      aria-label={`Cova ${pit + 1}, ${seeds} sementes`}
      className={[
        'relative aspect-square w-full rounded-full border-4 border-[#3d2510]',
        'bg-[radial-gradient(circle_at_50%_40%,#7a4a2a,#3a2112_75%)]',
        'shadow-[inset_0_8px_14px_rgba(0,0,0,0.65),0_2px_0_rgba(255,220,160,0.25)]',
        'transition-transform duration-150',
        enabled ? 'cursor-pointer ring-2 ring-amber-300/80 hover:scale-105 active:scale-95' : 'cursor-default',
        highlighted ? 'ring-4 ring-amber-400' : '',
      ].join(' ')}
    >
      <AnimatePresence initial={false}>
        {drawn.map((i) => (
          // x/y em % fazem o centramento; o Framer Motion gere o transform por completo.
          <motion.div
            key={i}
            className="absolute h-[22%] w-[22%] rounded-full shadow-[0_2px_3px_rgba(0,0,0,0.5)]"
            style={{ ...seedPosition(i), background: SEED_BACKGROUND }}
            initial={{ scale: 0, x: '-50%', y: '-50%' }}
            animate={{ scale: 1, x: '-50%', y: '-50%' }}
            exit={{ scale: 0, x: '-50%', y: '-50%' }}
            transition={{ type: 'spring', stiffness: 400, damping: 22 }}
          />
        ))}
      </AnimatePresence>

      <span className="pointer-events-none absolute -right-1 -top-1 z-10 flex min-w-7 items-center justify-center rounded-full bg-[#1f1009]/85 px-1.5 py-0.5 text-sm font-bold tabular-nums text-amber-100 shadow">
        {seeds}
      </span>
    </button>
  );
}

export function Board({ game, seat, interactive, onPlay }: BoardProps) {
  const { bottom, top } = layout(seat);
  const playing = game.status === 'playing';

  const renderPit = (pit: number) => (
    <Pit
      key={pit}
      pit={pit}
      seeds={game.board[pit]}
      enabled={interactive && playing && ownerOfPit(pit) === seat && game.board[pit] > 0}
      highlighted={game.lastMove?.pit === pit}
      onPlay={onPlay}
    />
  );

  return (
    <div className="wood-board mx-auto w-full max-w-4xl rounded-[2.5rem] border-[10px] border-[#6b3f1d] px-4 py-6 shadow-[0_25px_50px_rgba(0,0,0,0.5)] sm:px-10 sm:py-10">
      <div className="grid grid-cols-6 gap-3 sm:gap-6">{top.map(renderPit)}</div>
      <div className="my-4 h-4 rounded-full bg-[#2e1a0c] shadow-[inset_0_2px_4px_rgba(0,0,0,0.8)] sm:my-6" />
      <div className="grid grid-cols-6 gap-3 sm:gap-6">{bottom.map(renderPit)}</div>
    </div>
  );
}
