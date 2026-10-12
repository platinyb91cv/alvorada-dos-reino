import http from 'node:http';
import express from 'express';
import { Server } from 'socket.io';
import type { ClientToServerEvents, ServerToClientEvents } from '@shared/types';
import { ROOM_CODE_LENGTH } from '@shared/types';
import { RoomManager, type Room } from './roomManager';

const PORT = Number(process.env.PORT ?? 4000);
const ALLOWED_ORIGINS = (process.env.CORS_ORIGINS ?? 'http://localhost:3000').split(',');
const MAX_NAME_LENGTH = 20;
const STALE_ROOM_MS = 30 * 60 * 1000;
const SWEEP_INTERVAL_MS = 60 * 1000;

const app = express();
app.get('/health', (_req, res) => {
  res.json({ ok: true });
});

const httpServer = http.createServer(app);
const io = new Server<ClientToServerEvents, ServerToClientEvents>(httpServer, {
  cors: { origin: ALLOWED_ORIGINS },
});
const rooms = new RoomManager();

/** Envia a cada jogador da sala a sua própria visão. */
function broadcastRoom(room: Room): void {
  for (const player of room.players) {
    io.to(player.socketId).emit('room:update', rooms.viewFor(room, player));
  }
}

function notifyLeft(socketIds: string[]): void {
  for (const id of socketIds) io.to(id).emit('room:closed', 'O adversário saiu da sala.');
}

/** Nome limpo: sem caracteres de controlo, sem espaços nas pontas, máximo de 20 caracteres. */
function cleanName(raw: unknown): string | null {
  if (typeof raw !== 'string') return null;
  const name = raw.replace(/\p{Cc}/gu, '').trim().slice(0, MAX_NAME_LENGTH);
  return name || null;
}

io.on('connection', (socket) => {
  socket.on('room:create', (payload, ack) => {
    const name = cleanName(payload?.name);
    if (!name) return ack({ ok: false, error: 'Indica um nome.' });

    const result = rooms.create(socket.id, name);
    if (!result.ok) return ack(result);

    broadcastRoom(result.room);
    ack({ ok: true, code: result.room.code });
  });

  socket.on('room:join', (payload, ack) => {
    const name = cleanName(payload?.name);
    if (!name) return ack({ ok: false, error: 'Indica um nome.' });

    const code = String(payload?.code ?? '').trim().toUpperCase();
    if (code.length !== ROOM_CODE_LENGTH) return ack({ ok: false, error: 'O código tem 5 caracteres.' });

    const result = rooms.join(socket.id, code, name);
    if (!result.ok) return ack(result);

    broadcastRoom(result.room);
    ack({ ok: true, code: result.room.code });
  });

  socket.on('game:move', (payload, ack) => {
    const result = rooms.move(socket.id, Number(payload?.pit));
    if (!result.ok) return ack(result);

    broadcastRoom(result.room);
    ack({ ok: true });
  });

  socket.on('room:leave', () => {
    notifyLeft(rooms.leave(socket.id));
  });

  socket.on('disconnect', () => {
    notifyLeft(rooms.leave(socket.id));
  });
});

setInterval(() => {
  for (const id of rooms.sweepStale(STALE_ROOM_MS)) {
    io.to(id).emit('room:closed', 'A sala expirou por falta de adversário.');
  }
}, SWEEP_INTERVAL_MS).unref();

httpServer.listen(PORT, () => {
  console.log(`Uril: servidor Socket.io a correr em http://localhost:${PORT}`);
});
