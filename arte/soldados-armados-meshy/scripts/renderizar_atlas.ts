// Copiar para a raiz do repositório Forge3D (ramo fase4-imagens) e correr: CORPOS=<arte/soldados-meshy> ARMAS=<armas/otimizados> OUT=<saida> npx tsx renderizar_atlas.ts
// Requer Blender 5.2 (BLENDER_PATH), BLENDER_TRANSPORT=direct e WORKER_MAX_MEMORY_MB=3072. Zero chamadas Meshy.
import { writeFile, mkdir, rm } from 'node:fs/promises';
import { runSpriteAtlas } from './worker/blender';
import { unpackAtlasBundle } from './lib/sprite-bundle';
import { presetConfig, type SpritePresetId } from './lib/sprite-presets';
// Soldado -> predefinição Forge3D e arma Meshy (pasta SPRITE_PROP_DIR). Escudos/aljava procedimentais retirados: o pacote não os inclui.
const map: Record<string, [SpritePresetId, string, string]> = { guerreiro: ['alvorada-guerreiro-armado', 'axe', 'axe-2'], lanceiro: ['alvorada-lanceiro', 'spear', 'spear-2'], espadachim: ['alvorada-espadachim', 'sword', 'sword-2'], arqueiro: ['alvorada-arqueiro', 'bow', 'bow-2'], besteiro: ['alvorada-besteiro', 'crossbow', 'crossbow'] };
export function soldierConfig(n: string, extra: Record<string, unknown> = {}) {
  const [preset, id, model] = map[n]; const c = presetConfig(preset);
  // Eixo da pega escolhido na pose neutra (1.º quadro de Death: braços caídos, polegar para a frente), sem as correções de transporte.
  const neutral = ['guerreiro', 'espadachim', 'lanceiro'].includes(n) ? { placeIn: 'death', placeAt: 0 } : {};
  const props: any[] = c.props.filter(p => p.id === id).map(p => ({ ...p, model, ...neutral }));
  // Escudo Meshy (site meshy.ai, reduzido) no antebraço esquerdo da infantaria
  const sh = c.props.find(p => p.id === 'shield'); if (sh && process.env.ESCUDO !== '0') props.push({ ...sh, model: 'shield' });
  const ra = (part: 'upperArm' | 'forearm') => ({ names: [part === 'forearm' ? 'RightForeArm' : 'RightArm'], role: part, side: 'right' as const });
  // Pega de transporte: cotovelo dobrado em Idle/Walk/Hit para a arma ficar erguida ao lado do corpo, em vez de espetada para a frente.
  const carry = (deg: number) => [{ bone: ra('forearm'), mode: 'towardForward' as const, degrees: deg, states: ['idle', 'walk', 'hit'] }];
  const la = { names: ['LeftForeArm'], role: 'forearm' as const, side: 'left' as const };
  // Arqueiro: arco orientado na pose de disparo; ao andar/parado o cotovelo esquerdo dobra para o arco ficar de pé, à frente.
  const bowCarry = n === 'arqueiro' ? [{ bone: la, mode: 'towardForward' as const, degrees: Number(process.env.BOWCARRY ?? 70), states: ['idle', 'walk', 'hit'] }] : [];
  const extraOffsets = [...bowCarry, ...(['guerreiro', 'espadachim', 'lanceiro'].includes(n) ? carry(Number(process.env.CARRY ?? 85)) : [])];
  return { ...c, props, poseOffsets: [...c.poseOffsets, ...extraOffsets], states: c.states.map(s => ({ ...s, props: s.props.filter(x => x === id || (x === 'shield' && props.some(p => p.id === 'shield'))), ...(n === 'arqueiro' && s.name === 'attack' ? { range: [0.4, 1] as [number, number] } : {}) })), samples: 8, ...extra };
}
async function main() {
  process.env.SPRITE_PROP_DIR ??= process.env.ARMAS ?? 'armas'; // pasta com axe-2.glb, spear-2.glb, sword-2.glb, bow-2.glb, crossbow.glb (otimizados/)
  const out = process.env.OUT ?? 'atlas-saida'; await mkdir(out, { recursive: true });
  for (const n of (process.argv[2] ?? Object.keys(map).join(',')).split(',')) {
    const t = Date.now(); let config: any = soldierConfig(n);
    if (process.env.ROT) config.props = config.props.map((p: any) => ({ ...p, rotation: JSON.parse(process.env.ROT!) }));
    if (process.env.ONLY) { const keep = process.env.ONLY.split(','); config.states = config.states.filter((s: any) => keep.includes(s.name)); config.poseOffsets = config.poseOffsets.map((o: any) => o.states ? { ...o, states: o.states.filter((x: string) => keep.includes(x)) } : o).filter((o: any) => !o.states || o.states.length); config.props = config.props.map((p: any) => keep.includes(p.placeIn) ? p : { ...p, placeIn: undefined, placeAt: 0 }); delete config.measure; config.aliases = {}; }
    const b = await runSpriteAtlas({ type: 'RENDER_SPRITE_ATLAS', assetId: 'soldado00000', name: n, config }, `${process.env.CORPOS ?? 'corpos'}/${n}.glb`, `${out}/work-${n}`, AbortSignal.timeout(2400000));
    const r = await unpackAtlasBundle(b);
    await writeFile(`${out}/${n}.webp`, r.webp); await writeFile(`${out}/${n}.json`, JSON.stringify(r.meta)); await writeFile(`${out}/${n}.report.json`, JSON.stringify(r.report)); await writeFile(`${out}/${n}.preview.png`, r.preview); await writeFile(`${out}/${n}.config.json`, JSON.stringify(config, null, 1));
    await rm(`${out}/work-${n}`, { recursive: true, force: true });
    console.log(n, ((Date.now() - t) / 1000).toFixed(0) + 's', JSON.stringify(r.report.props), JSON.stringify((r.report.warnings as string[])));
  }
}
if (process.argv[1]?.endsWith('renderizar_atlas.ts')) void main().catch(e => { console.error(e instanceof Error ? e.message : e); process.exitCode = 1; });
