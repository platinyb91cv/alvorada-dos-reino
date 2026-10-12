import { test } from 'node:test';
import assert from 'node:assert/strict';
import { applyMove, collectCaptures, createGame, sow } from './gameLogic';
import { PIT_COUNT, WIN_SCORE, type GameState } from '@shared/types';

/** Cria um estado de teste com um tabuleiro e pontuação à medida. */
function stateWith(board: number[], overrides: Partial<GameState> = {}): GameState {
  return { ...createGame(), board, ...overrides };
}

const total = (board: number[]) => board.reduce((a, b) => a + b, 0);

test('estado inicial: 12 covas com 4 sementes (48 no total), pontuação 0, vez do Jogador 1', () => {
  const game = createGame();
  assert.equal(game.board.length, PIT_COUNT);
  assert.deepEqual(game.board, Array(12).fill(4));
  assert.equal(total(game.board), 48);
  assert.deepEqual(game.scores, [0, 0]);
  assert.equal(game.turn, 0);
  assert.equal(game.status, 'playing');
});

test('semeadura: a cova de origem é saltada quando a volta a apanha', () => {
  // 12 sementes na cova 0: 1..11 recebem uma cada, a 0 é saltada, a 12.ª cai na 1.
  const { board, last } = sow([12, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 0);
  assert.deepEqual(board, [0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]);
  assert.equal(last, 1);
});

test('semeadura não muta o tabuleiro recebido', () => {
  const original = [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
  sow(original, 0);
  assert.deepEqual(original, [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]);
});

test('captura simples: última semente num par do adversário (1 → 2) é capturada', () => {
  const game = stateWith([0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1]);
  const result = applyMove(game, 0, 5);
  assert.ok(result.ok);
  assert.equal(result.state.scores[0], 2);
  assert.equal(result.state.board[6], 0);
  assert.equal(result.state.turn, 1);
  assert.equal(result.state.lastMove?.captured, 2);
});

test('captura encadeada: propaga para trás enquanto as covas do adversário tiverem 2 ou 3', () => {
  // A cova 5 com 3 sementes cai em 6, 7 e 8: 6→2, 7→3, 8→2. Captura 8, 7 e 6 (2+3+2 = 7).
  const game = stateWith([0, 0, 0, 0, 0, 3, 1, 2, 1, 0, 0, 1]);
  const result = applyMove(game, 0, 5);
  assert.ok(result.ok);
  assert.equal(result.state.scores[0], 7);
  assert.deepEqual(result.state.board, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]);
});

test('a captura para quando a cova anterior não tem 2 ou 3 sementes', () => {
  // A cova 5 com 3 sementes cai em 6, 7 e 8: 6→2, 7→4, 8→2. Só a 8 é capturada (a 7 tem 4).
  const game = stateWith([0, 0, 0, 0, 0, 3, 1, 3, 1, 0, 0, 1]);
  const result = applyMove(game, 0, 5);
  assert.ok(result.ok);
  assert.equal(result.state.scores[0], 2);
  assert.deepEqual(result.state.board, [0, 0, 0, 0, 0, 0, 2, 4, 0, 0, 0, 1]);
});

test('collectCaptures muta o tabuleiro e não captura cova do próprio lado', () => {
  const board = [0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0];
  assert.equal(collectCaptures(board, 5, 0), 0);
  assert.equal(collectCaptures(board, 6, 0), 2);
  assert.deepEqual(board, [0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0]);
});

test('sem captura se a última semente cair no próprio lado', () => {
  const game = stateWith([1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0]);
  const result = applyMove(game, 0, 0);
  assert.ok(result.ok);
  assert.equal(result.state.scores[0], 0);
  assert.equal(result.state.quietMoves, 1);
});

test('recusas: vez errada, cova do adversário, cova vazia, cova inválida', () => {
  const game = stateWith([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]);
  assert.equal(applyMove(game, 1, 6).ok, false);
  assert.equal(applyMove(game, 0, 7).ok, false);
  assert.equal(applyMove(stateWith([0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1]), 0, 2).ok, false);
  assert.equal(applyMove(game, 0, 12).ok, false);
  assert.equal(applyMove(game, 0, 1.5).ok, false);
});

test('recusa jogadas depois de a partida terminar', () => {
  const finished = stateWith([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], { status: 'finished', winner: 0 });
  assert.equal(applyMove(finished, 0, 0).ok, false);
});

test('vitória ao atingir 25 sementes capturadas', () => {
  const game = stateWith([0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1], { scores: [WIN_SCORE - 2, 0] });
  const result = applyMove(game, 0, 5);
  assert.ok(result.ok);
  assert.equal(result.state.scores[0], WIN_SCORE);
  assert.equal(result.state.status, 'finished');
  assert.equal(result.state.winner, 0);
});

test('fim por falta de sementes: quem fica sem jogadas perde as sementes do seu lado', () => {
  // Jogador 1 move a cova 4 → 5. Jogador 2 não tem sementes: o jogo acaba.
  const game = stateWith([0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0]);
  const result = applyMove(game, 0, 4);
  assert.ok(result.ok);
  assert.equal(result.state.status, 'finished');
  assert.deepEqual(result.state.scores, [1, 0]);
  assert.equal(result.state.winner, 0);
});
