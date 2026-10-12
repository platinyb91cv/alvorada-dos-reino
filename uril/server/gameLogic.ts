import {
  INITIAL_SEEDS,
  MAX_QUIET_MOVES,
  PIT_COUNT,
  PITS_PER_SIDE,
  SEATS,
  WIN_SCORE,
  ownerOfPit,
  type GameState,
  type LastMove,
  type Seat,
} from '@shared/types';

/**
 * Regras do Uril. Funções puras: nunca mutam o estado recebido.
 * É o único sítio onde o jogo é validado e avançado; o cliente nunca chama isto.
 */

export type MoveResult = { ok: true; state: GameState } | { ok: false; error: string };

const fail = (error: string): MoveResult => ({ ok: false, error });
const opponentOf = (seat: Seat): Seat => (seat === 0 ? 1 : 0);

export function createGame(): GameState {
  return {
    board: Array<number>(PIT_COUNT).fill(INITIAL_SEEDS),
    scores: [0, 0],
    turn: 0,
    status: 'playing',
    winner: null,
    lastMove: null,
    quietMoves: 0,
  };
}

/**
 * Semeia a cova `pit` no sentido anti-horário (índice crescente, 11 → 0).
 * A cova de origem é saltada: se a volta a dar lá chegar, não recebe semente.
 */
export function sow(board: readonly number[], pit: number): { board: number[]; last: number } {
  const next = [...board];
  let seeds = next[pit];
  next[pit] = 0;

  let i = pit;
  while (seeds > 0) {
    i = (i + 1) % PIT_COUNT;
    if (i === pit) continue;
    next[i] += 1;
    seeds -= 1;
  }
  return { board: next, last: i };
}

/**
 * Captura a partir da última cova semeada e propaga para trás enquanto as covas
 * forem do adversário e tiverem exatamente 2 ou 3 sementes.
 * Muta `board` (esvazia as covas capturadas) e devolve o total capturado.
 */
export function collectCaptures(board: number[], last: number, seat: Seat): number {
  let captured = 0;
  let pit = last;

  for (let step = 0; step < PITS_PER_SIDE; step++) {
    if (ownerOfPit(pit) === seat) break;
    const seeds = board[pit];
    if (seeds < 2 || seeds > 3) break;

    captured += seeds;
    board[pit] = 0;
    pit = (pit + PIT_COUNT - 1) % PIT_COUNT;
  }
  return captured;
}

const sideTotal = (board: readonly number[], seat: Seat): number =>
  board.reduce((sum, seeds, pit) => (ownerOfPit(pit) === seat ? sum + seeds : sum), 0);

/**
 * Aplica a jogada de `seat` na cova `pit`, validando primeiro tudo o que é
 * necessário. Devolve o novo estado ou o motivo da recusa.
 */
export function applyMove(state: GameState, seat: Seat, pit: number): MoveResult {
  if (state.status !== 'playing') return fail('O jogo já terminou.');
  if (seat !== state.turn) return fail('Não é a tua vez.');
  if (!Number.isInteger(pit) || pit < 0 || pit >= PIT_COUNT) return fail('Cova inválida.');
  if (ownerOfPit(pit) !== seat) return fail('Essa cova não é tua.');
  if (state.board[pit] === 0) return fail('Essa cova está vazia.');

  const { board, last } = sow(state.board, pit);
  const captured = collectCaptures(board, last, seat);

  const scores: [number, number] = [state.scores[0], state.scores[1]];
  scores[seat] += captured;

  const lastMove: LastMove = { player: seat, pit, captured };
  const next: GameState = {
    ...state,
    board,
    scores,
    turn: opponentOf(seat),
    lastMove,
    quietMoves: captured > 0 ? 0 : state.quietMoves + 1,
  };

  return { ok: true, state: resolveEnd(next) };
}

/** Verifica se a partida acabou depois de uma jogada. */
function resolveEnd(state: GameState): GameState {
  const leader = SEATS.find((seat) => state.scores[seat] >= WIN_SCORE);
  if (leader !== undefined) return { ...state, status: 'finished', winner: leader };

  // Quem tem a vez ficou sem sementes no seu lado: a partida termina.
  const starved = sideTotal(state.board, state.turn) === 0;
  if (starved || state.quietMoves >= MAX_QUIET_MOVES) return endByRemainingSeeds(state);

  return state;
}

/**
 * Fim sem vencedor por pontuação: cada jogador recolhe as sementes do seu lado.
 * Ganha quem tiver mais sementes; empate dá winner = null.
 */
function endByRemainingSeeds(state: GameState): GameState {
  const scores: [number, number] = [
    state.scores[0] + sideTotal(state.board, 0),
    state.scores[1] + sideTotal(state.board, 1),
  ];
  const winner = scores[0] === scores[1] ? null : scores[0] > scores[1] ? 0 : 1;
  return {
    ...state,
    board: Array<number>(PIT_COUNT).fill(0),
    scores,
    status: 'finished',
    winner,
  };
}
