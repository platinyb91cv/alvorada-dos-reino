/**
 * Contratos partilhados entre servidor e cliente.
 * Este ficheiro não contém lógica de jogo: as regras vivem só em server/gameLogic.ts.
 */

// ---------- Constantes do jogo ----------

export const PIT_COUNT = 12;
export const PITS_PER_SIDE = 6;
export const INITIAL_SEEDS = 4;
export const WIN_SCORE = 25;
/** Fim de jogo por limite: N jogadas seguidas sem captura terminam a partida. */
export const MAX_QUIET_MOVES = 150;
export const ROOM_CODE_LENGTH = 5;

// ---------- Jogadores ----------

/** 0 = Jogador 1 (covas 0-5, fundo). 1 = Jogador 2 (covas 6-11, topo). */
export type Seat = 0 | 1;
export const SEATS: readonly Seat[] = [0, 1];

/** Dono de uma cova: 0-5 pertencem ao Jogador 1, 6-11 ao Jogador 2. */
export const ownerOfPit = (pit: number): Seat => (pit < PITS_PER_SIDE ? 0 : 1);

// ---------- Estado do jogo ----------

export interface LastMove {
  player: Seat;
  pit: number;
  captured: number;
}

export interface GameState {
  /** 12 covas com sementes. */
  board: number[];
  /** Sementes capturadas por cada jogador. */
  scores: [number, number];
  /** Quem tem a vez de semear. */
  turn: Seat;
  status: 'playing' | 'finished';
  /** Com status 'finished': vencedor, ou null em empate. */
  winner: Seat | null;
  lastMove: LastMove | null;
  /** Jogadas consecutivas sem captura (usado no limite de empate). */
  quietMoves: number;
}

// ---------- Salas ----------

export interface PlayerInfo {
  name: string;
  seat: Seat;
}

/** Visão de uma sala tal como é enviada a cada jogador (inclui o seu lugar). */
export interface RoomView {
  code: string;
  seat: Seat;
  players: PlayerInfo[];
  /** null enquanto a sala espera pelo segundo jogador. */
  game: GameState | null;
}

// ---------- Socket.io ----------

export type Result<T extends object = object> = ({ ok: true } & T) | { ok: false; error: string };
export type Ack<T extends object = object> = (res: Result<T>) => void;

export interface ClientToServerEvents {
  'room:create': (payload: { name: string }, ack: Ack<{ code: string }>) => void;
  'room:join': (payload: { code: string; name: string }, ack: Ack<{ code: string }>) => void;
  'room:leave': () => void;
  'game:move': (payload: { pit: number }, ack: Ack) => void;
}

export interface ServerToClientEvents {
  'room:update': (view: RoomView) => void;
  'room:closed': (reason: string) => void;
}
