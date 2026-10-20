const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const html = fs.readFileSync(path.join(__dirname, '../www/index.html'), 'utf8');
function source(name) {
  const start = html.indexOf('function ' + name + '(');
  const end = html.indexOf('\nfunction ', start + 1);
  assert.ok(start >= 0 && end > start, name);
  return html.slice(start, end);
}
const players = [0, 1, 2].map(() => ({ age: 0, techs: {}, res: { food: 0 }, stats: { gathered: 0 } }));
const ctx = vm.createContext({
  Math, Number, Map, P: players, ME: 0, G: { time: 0 }, AIs: [null, null, null],
  GATHER: vm.runInNewContext('(' + html.match(/const GATHER=(\{[^\n]+\});/)[1] + ')'),
  ents: [], projs: [], resDirty: false, uiDirty: false,
  W: 32, H: 32, resAt: new Array(1024).fill(null),
  inb: (x, y) => x >= 0 && y >= 0 && x < 32 && y < 32,
  idx: (x, y) => y * 32 + x, hyp: Math.hypot,
  approach: () => true, capOf: () => 12, civOf: () => 'none', faceTo() {}, snd() {},
  nearestDrop: () => ({ kind: 'b', o: 0, done: true }),
  removeRes: r => { r.dead = true; }, kill: e => { e.dead = true; },
  relicNear: () => -1, groupMove: units => { for (const u of units) u.state = 'move'; }, toast() {},
});
for (const name of ['alive', 'centerOf', 'pasturePen', 'pastureAllowed', 'watchWorker', 'isPasture', 'renewableFood', 'resKind', 'findRes',
  'farmWorkers', 'orderGather', 'orderAttack', 'orderReturn', 'stopUnit', 'updAnimal',
  'updUnit', 'doCommand', 'unit3dState']) vm.runInContext(source(name), ctx);
function villager(o = 0) {
  return { kind: 'u', type: 'aldeao', o, d: {}, x: 6, y: 6, state: 'idle', path: null,
    pi: 0, cd: 0, scan: 0, anim: 0, work: 0, carry: 0, ctype: null, hitT: 0 };
}
function simulate(u, seconds) { for (let i = 0; i < seconds; i++) ctx.updUnit(u, 1); }

// The real gather/return loop must outlive both the last unit of a farm and 399 food.
const farm = { id: 1, kind: 'b', o: 0, type: 'quinta', d: { farm: 260 },
  tx: 4, ty: 4, w: 3, h: 3, done: true, amt: 1, hp: 90 };
const farmer = villager();
ctx.ents.push(farm, farmer);
ctx.orderGather(farmer, farm);
simulate(farmer, 3000);
assert.ok(players[0].res.food > 399, 'Farm must keep delivering beyond its previous supply');
assert.equal(farm.amt, 1);
assert.equal(farm.hp, 90);
assert.ok(!farm.dead);
farm.amt = 0; // Old saves with an exhausted farm remain productive, too.
const before = players[0].res.food;
simulate(farmer, 100);
assert.ok(players[0].res.food > before);
assert.ok(!farm.dead);

const sheep = { id: 2, kind: 'u', type: 'ovelha', o: 2, x: 7, y: 6,
  d: { tame: 1, meat: 0 }, hp: 12, state: 'move', path: [{ x: 8, y: 6 }], cd: 0, scan: 0 };
const shepherd = villager();
ctx.ents.push(sheep, shepherd);
ctx.doCommand(0, [shepherd], sheep, { x: sheep.x, y: sheep.y }, null, 'livre');
assert.equal(shepherd.state, 'gather');
assert.equal(shepherd.gres, sheep);
assert.equal(shepherd.gkind, 'food');
assert.equal(ctx.unit3dState(shepherd), 'idle', 'Pasturing must not select hunt or butcher poses');
ctx.updAnimal(sheep, 1 / 30);
assert.equal(sheep.state, 'idle');
assert.equal(sheep.path, null);
const milkBefore = players[0].res.food;
simulate(shepherd, 3000);
assert.ok(players[0].res.food > milkBefore + 399);
assert.equal(sheep.hp, 12);
assert.ok(!sheep.dead);
assert.equal(ctx.projs.length, 0);
assert.ok(!('amt' in sheep), 'Live sheep must not acquire a NaN/depleting meat counter');

// AI orders and attacks restored from old saves also become nonlethal pasturing.
const ai = villager(1);
ctx.orderAttack(ai, sheep);
assert.equal(ai.state, 'gather');
const oldHunter = villager();
Object.assign(oldHunter, { state: 'attack', target: sheep, gkind: 'food' });
ctx.updUnit(oldHunter, 1 / 30);
assert.equal(oldHunter.state, 'gather');
assert.equal(oldHunter.gres, sheep);
const soldier = { kind: 'u', type: 'guerreiro', o: 0, d: {} };
ctx.doCommand(0, [soldier], sheep, { x: sheep.x, y: sheep.y }, null, 'livre');
assert.equal(soldier.state, 'move', 'A context click on sheep must not order slaughter');

// Automatic food search can use a live sheep, while finite berries still deplete.
ctx.ents = [sheep];
assert.equal(ctx.findRes('food', 6, 6, 9, 0, false), sheep);
const berry = { id: 3, kind: 'r', rk: 'food', amt: 2, tx: 8, ty: 8, w: 1, h: 1 };
const picker = villager();
ctx.orderGather(picker, berry);
for (let i = 0; i < 4 && !berry.dead; i++) ctx.updUnit(picker, 1);
assert.equal(berry.amt, 0);
assert.ok(berry.dead);
assert.equal(picker.carry, 2);
assert.match(html, /Comida ilimitada ∞/);
assert.match(html, /amt:b\.d\.farm\?b\.d\.farm:q\.am/, 'Old saved farms must normalize to a finite visual fill value');
assert.doesNotMatch(html, /Uma quinta esgotou-se|\+80 por quinta|ovelhas são mansas \(100 de comida\)/);
console.log('PASS: unlimited farm deliveries, living sheep pasturing, AI/old hunter migration, no slaughter animation, finite berries');
