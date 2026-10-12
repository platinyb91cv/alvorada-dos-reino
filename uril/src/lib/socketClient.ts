import { io, type Socket } from 'socket.io-client';
import type { ClientToServerEvents, Result, ServerToClientEvents } from '@shared/types';
import { useGameStore } from './gameStore';

type GameSocket = Socket<ServerToClientEvents, ClientToServerEvents>;

const SERVER_URL = process.env.NEXT_PUBLIC_SOCKET_URL ?? 'http://localhost:4000';
const ACK_TIMEOUT_MS = 5000;

let socket: GameSocket | null = null;

/** Cria a ligação uma única vez e liga os eventos do servidor ao store. */
function getSocket(): GameSocket {
  if (socket) return socket;

  const s: GameSocket = io(SERVER_URL, { autoConnect: false, transports: ['websocket'] });

  s.on('connect', () => {
    useGameStore.getState().setConnected(true);
  });

  s.on('disconnect', () => {
    // O servidor apaga as salas de quem se desliga: voltamos ao lobby.
    const store = useGameStore.getState();
    store.setConnected(false);
    store.setView(null);
    store.setNotice('Ligação ao servidor perdida.');
  });

  s.on('room:update', (view) => {
    const store = useGameStore.getState();
    store.setNotice(null);
    store.setView(view);
  });

  s.on('room:closed', (reason) => {
    const store = useGameStore.getState();
    store.setView(null);
    store.setNotice(reason);
  });

  socket = s;
  return s;
}

/** Envia um evento com ack e resolve com a resposta do servidor (ou erro de timeout). */
function request<T extends object>(send: (ack: (res: Result<T>) => void) => void): Promise<Result<T>> {
  return new Promise((resolve) => {
    const timer = setTimeout(() => resolve({ ok: false, error: 'O servidor não respondeu.' }), ACK_TIMEOUT_MS);
    send((res) => {
      clearTimeout(timer);
      resolve(res);
    });
  });
}

/**
 * API usada pela UI. O cliente só envia intenções (criar, entrar, semear);
 * o estado que recebe do servidor é o único que renderiza.
 */
export const gameClient = {
  connect(): void {
    const s = getSocket();
    if (!s.connected) s.connect();
  },

  createRoom(name: string) {
    return request<{ code: string }>((ack) => getSocket().emit('room:create', { name }, ack));
  },

  joinRoom(code: string, name: string) {
    return request<{ code: string }>((ack) => getSocket().emit('room:join', { code, name }, ack));
  },

  sendMove(pit: number) {
    return request((ack) => getSocket().emit('game:move', { pit }, ack));
  },

  leaveRoom(): void {
    getSocket().emit('room:leave');
    useGameStore.getState().setView(null);
  },
};
