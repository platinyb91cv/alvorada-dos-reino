import { randomInt } from 'node:crypto';
import { applyMove, createGame, type MoveResult } from './gameLogic';
import { ROOM_CODE_LENGTH, type GameState, type RoomView, type Seat } from '@shared/types';

/** Sem I, O, 0 e 1 para evitar confusões ao ler ou ditar o código. */
const CODE_ALPHABET = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';

export interface Player {
  socketId: string;
  name: string;
  seat: Seat;
}

export interface Room {
  code: string;
  players: Player[];
  game: GameState | null;
  createdAt: number;
}

type Outcome<T> = { ok: true } & T | { ok: false; error: string };

const fail = (error: string) => ({ ok: false as const, error });

/**
 * Gere as salas em memória. Cada sala tem no máximo 2 jogadores (lugares 0 e 1).
 * Não conhece as regras do jogo: delega em gameLogic.applyMove.
 */
export class RoomManager {
  private readonly rooms = new Map<string, Room>();
  private readonly roomOfSocket = new Map<string, string>();

  create(socketId: string, name: string): Outcome<{ room: Room }> {
    if (this.roomOfSocket.has(socketId)) return fail('Já estás numa sala. Sai primeiro.');

    const room: Room = {
      code: this.newCode(),
      players: [{ socketId, name, seat: 0 }],
      game: null,
      createdAt: Date.now(),
    };
    this.rooms.set(room.code, room);
    this.roomOfSocket.set(socketId, room.code);
    return { ok: true, room };
  }

  join(socketId: string, code: string, name: string): Outcome<{ room: Room }> {
    if (this.roomOfSocket.has(socketId)) return fail('Já estás numa sala. Sai primeiro.');

    const room = this.rooms.get(code);
    if (!room) return fail('Sala não encontrada.');
    if (room.players.length >= 2) return fail('A sala já está cheia.');

    room.players.push({ socketId, name, seat: 1 });
    room.game = createGame();
    this.roomOfSocket.set(socketId, room.code);
    return { ok: true, room };
  }

  move(socketId: string, pit: number): Outcome<{ room: Room }> {
    const room = this.roomOf(socketId);
    const player = room?.players.find((p) => p.socketId === socketId);
    if (!room || !player) return fail('Não estás numa sala.');
    if (!room.game) return fail('A sala ainda espera pelo adversário.');

    const result: MoveResult = applyMove(room.game, player.seat, pit);
    if (!result.ok) return result;

    room.game = result.state;
    return { ok: true, room };
  }

  /**
   * Remove a sala onde está o socket. Uma sala termina quando alguém sai.
   * Devolve os sockets dos outros jogadores, para serem avisados.
   */
  leave(socketId: string): string[] {
    const room = this.roomOf(socketId);
    if (!room) return [];

    this.deleteRoom(room);
    return room.players.filter((p) => p.socketId !== socketId).map((p) => p.socketId);
  }

  /** Apaga salas à espera de adversário há demasiado tempo. Devolve os sockets afetados. */
  sweepStale(maxAgeMs: number): string[] {
    const cutoff = Date.now() - maxAgeMs;
    const affected: string[] = [];
    for (const room of this.rooms.values()) {
      if (room.game === null && room.createdAt < cutoff) {
        affected.push(...room.players.map((p) => p.socketId));
        this.deleteRoom(room);
      }
    }
    return affected;
  }

  /** Visão de uma sala para um jogador concreto (inclui o seu lugar). */
  viewFor(room: Room, player: Player): RoomView {
    return {
      code: room.code,
      seat: player.seat,
      players: room.players.map(({ name, seat }) => ({ name, seat })),
      game: room.game,
    };
  }

  private roomOf(socketId: string): Room | undefined {
    const code = this.roomOfSocket.get(socketId);
    return code ? this.rooms.get(code) : undefined;
  }

  private deleteRoom(room: Room): void {
    this.rooms.delete(room.code);
    for (const player of room.players) this.roomOfSocket.delete(player.socketId);
  }

  private newCode(): string {
    let code: string;
    do {
      code = Array.from({ length: ROOM_CODE_LENGTH }, () => CODE_ALPHABET[randomInt(CODE_ALPHABET.length)]).join('');
    } while (this.rooms.has(code));
    return code;
  }
}
