'use client';

import { useState, type FormEvent } from 'react';
import { ROOM_CODE_LENGTH } from '@shared/types';
import { gameClient } from '@/lib/socketClient';
import { useGameStore } from '@/lib/gameStore';

export function Lobby() {
  const connected = useGameStore((s) => s.connected);
  const notice = useGameStore((s) => s.notice);
  const setNotice = useGameStore((s) => s.setNotice);

  const [name, setName] = useState('');
  const [code, setCode] = useState('');
  const [busy, setBusy] = useState(false);

  /** Devolve o nome limpo ou mostra um aviso e devolve null. */
  function requireName(): string | null {
    const trimmed = name.trim();
    if (!trimmed) setNotice('Escreve o teu nome primeiro.');
    return trimmed || null;
  }

  async function handleCreate() {
    const playerName = requireName();
    if (!playerName) return;

    setBusy(true);
    const res = await gameClient.createRoom(playerName);
    setBusy(false);
    if (!res.ok) setNotice(res.error);
  }

  async function handleJoin(e: FormEvent) {
    e.preventDefault();
    const playerName = requireName();
    if (!playerName) return;
    if (code.trim().length !== ROOM_CODE_LENGTH) {
      setNotice(`O código tem ${ROOM_CODE_LENGTH} caracteres.`);
      return;
    }

    setBusy(true);
    const res = await gameClient.joinRoom(code, playerName);
    setBusy(false);
    if (!res.ok) setNotice(res.error);
  }

  const disabled = busy || !connected;

  return (
    <section className="mx-auto flex w-full max-w-3xl flex-col gap-8">
      <header className="text-center">
        <h1 className="text-4xl font-black tracking-tight text-amber-100">Uril</h1>
        <p className="mt-2 text-amber-200/70">Semeia, captura e chega às 25 sementes.</p>
        <p className="mt-3 text-xs">
          <span className={connected ? 'text-emerald-400' : 'text-red-400'}>●</span>{' '}
          {connected ? 'Ligado ao servidor' : 'A ligar ao servidor…'}
        </p>
      </header>

      <label className="flex flex-col gap-2">
        <span className="text-sm font-semibold text-amber-200">O teu nome</span>
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          maxLength={20}
          placeholder="Ex.: Tito_CV"
          className="rounded-xl border border-amber-900 bg-black/30 px-4 py-3 text-lg outline-none focus:border-amber-400"
        />
      </label>

      <div className="grid gap-6 sm:grid-cols-2">
        <div className="flex flex-col gap-3 rounded-3xl bg-white/5 p-6">
          <h2 className="text-xl font-bold">Criar Nova Sala</h2>
          <p className="text-sm text-amber-200/70">Recebes um código para partilhar com o adversário.</p>
          <button
            type="button"
            onClick={handleCreate}
            disabled={disabled}
            className="mt-auto rounded-xl bg-amber-600 px-4 py-3 font-semibold text-amber-50 hover:bg-amber-500 disabled:opacity-50"
          >
            Criar Nova Sala
          </button>
        </div>

        <form onSubmit={handleJoin} className="flex flex-col gap-3 rounded-3xl bg-white/5 p-6">
          <h2 className="text-xl font-bold">Entrar com Código</h2>
          <input
            value={code}
            onChange={(e) => setCode(e.target.value.toUpperCase())}
            maxLength={ROOM_CODE_LENGTH}
            placeholder="CÓDIGO"
            aria-label="Código da sala"
            className="rounded-xl border border-amber-900 bg-black/30 px-4 py-3 text-center font-mono text-xl tracking-[0.3em] uppercase outline-none focus:border-amber-400"
          />
          <button
            type="submit"
            disabled={disabled}
            className="mt-auto rounded-xl bg-amber-800 px-4 py-3 font-semibold text-amber-50 hover:bg-amber-700 disabled:opacity-50"
          >
            Entrar
          </button>
        </form>
      </div>

      {notice && (
        <p role="alert" className="rounded-xl bg-red-900/50 px-4 py-2 text-center text-sm text-red-100">
          {notice}
        </p>
      )}
    </section>
  );
}
