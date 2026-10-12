# Uril — multiplayer em tempo real

Uril (Ouril, Mancala de Cabo Verde) para dois jogadores online.
Next.js + React + TypeScript + Tailwind no cliente, Node.js + Express + Socket.io no servidor.

## Correr em desenvolvimento

```bash
cd uril
npm install
npm run dev        # servidor Socket.io em :4000 e Next.js em :3000
```

Testes das regras e typecheck:

```bash
npm test           # 12 testes de node:test sobre server/gameLogic.ts
npm run typecheck
```

Variáveis de ambiente (opcionais):

| Variável | Onde | Predefinição |
|---|---|---|
| `PORT` | servidor | `4000` |
| `CORS_ORIGINS` | servidor (lista separada por vírgulas) | `http://localhost:3000` |
| `NEXT_PUBLIC_SOCKET_URL` | cliente | `http://localhost:4000` |

## Arquitetura

```
shared/types.ts        contratos (GameState, RoomView, eventos Socket.io) — sem regras
server/gameLogic.ts    regras puras: sowing, capturas, fim de jogo
server/roomManager.ts  salas em memória, códigos, máximo 2 jogadores
server/index.ts        Express + Socket.io: liga eventos às salas e à lógica
src/lib/socketClient.ts  ligação Socket.io; envia intenções e atualiza o store
src/lib/gameStore.ts     Zustand: guarda apenas o que o servidor enviou
src/components/Board.tsx tabuleiro em madeira, sementes animadas (Framer Motion)
```

**Anti-cheat:** o cliente nunca importa `gameLogic.ts`. Envia só `{ pit }`; o servidor valida a vez, o dono da cova, se a cova tem sementes e se o jogo está ativo. Depois de cada jogada envia a `RoomView` completa a cada jogador.

## Regras implementadas

- 12 covas: 0–5 pertencem ao Jogador 1 (fundo), 6–11 ao Jogador 2 (topo). Começa com 4 sementes em cada (48).
- Semeadura anti-horária (índice crescente, 11 → 0). A cova de origem é saltada.
- Captura: se a última semente cair numa cova do adversário com 2 ou 3, captura; propaga para trás enquanto as covas do adversário tiverem 2 ou 3.
- Vitória: 25 ou mais sementes capturadas.

### Decisões que não estavam especificadas

Estas escolhas estão centralizadas em `server/gameLogic.ts` e podem mudar:

1. **Sem jogadas possíveis:** se quem tem a vez não tem sementes no seu lado, a partida acaba. Cada jogador fica com as sementes do seu lado.
2. **Limite de empate:** 150 jogadas seguidas sem captura terminam a partida com o mesmo critério.
3. **Desempate por número de sementes:** nos fins sem 25 capturadas, ganha quem tiver mais. Igualdade dá empate (`winner = null`).
4. **Sala:** termina quando um jogador sai ou se desliga. Salas à espera de adversário expiram após 30 minutos.

## Por fazer

- Temporizador por jogada (o mockup mostra "Tempo").
- Reconexão: hoje, desligar-se encerra a sala.
- Chat e emojis do mockup.
- Persistência (Supabase) de resultados e ranking.
