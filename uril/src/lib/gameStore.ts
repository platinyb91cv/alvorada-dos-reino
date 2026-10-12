import { create } from 'zustand';
import type { RoomView } from '@shared/types';

/**
 * Estado local da UI. Não calcula nada do jogo: guarda apenas o que o servidor enviou.
 */
interface GameStore {
  connected: boolean;
  view: RoomView | null;
  /** Mensagem para o jogador (erro de jogada, adversário saiu, etc.). */
  notice: string | null;
  setConnected: (connected: boolean) => void;
  setView: (view: RoomView | null) => void;
  setNotice: (notice: string | null) => void;
}

export const useGameStore = create<GameStore>()((set) => ({
  connected: false,
  view: null,
  notice: null,
  setConnected: (connected) => set({ connected }),
  setView: (view) => set({ view }),
  setNotice: (notice) => set({ notice }),
}));
