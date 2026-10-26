import { writeFile, mkdir, rm } from 'node:fs/promises';
import { runSpriteAtlas } from '/home/claude/platinyb91cv-forge3d-ai/worker/blender';
import { unpackAtlasBundle } from '/home/claude/platinyb91cv-forge3d-ai/lib/sprite-bundle';
const s = (name: string, clip: string, frames: number, loop = true) => ({ name, clip, frames, loop, props: [] as string[] });
// escala dos soldados (1,61 m = 64 px): href = 64·altura/1,61; altura = topo do mastro (m "de jogo")
const H: Record<string, number> = { barcoPesca: 1.01, transporte: 2.04, gale: 1.47, incendiario: 1.17, navioPesado: 2.62, corsario: 2.05 };
async function main() {
  const out = '/tmp/claude-0/work/navios'; await mkdir(out, { recursive: true });
  for (const n of (process.argv[2] ?? Object.keys(H).join(',')).split(',')) {
    const t = Date.now();
    const config = { version: 1, modelForward: '+X' as const, referenceHeightPx: Math.round(64 * H[n] / 1.61), samples: 8, atlasWidth: 4096, webpQuality: 100,
      states: [s('idle', 'Idle', 2), s('walk', 'Walk', 8), s('attack', 'Attack', 6), s('hit', 'Hit', 2), s('death', 'Death', 4, false)] };
    const b = await runSpriteAtlas({ type: 'RENDER_SPRITE_ATLAS', assetId: 'navio0000000', name: n, config }, `/tmp/claude-0/navios/glb/${n}-rig.glb`, `${out}/work-${n}`, AbortSignal.timeout(2400000));
    const r = await unpackAtlasBundle(b);
    await writeFile(`${out}/${n}.webp`, r.webp); await writeFile(`${out}/${n}.json`, JSON.stringify(r.meta)); await writeFile(`${out}/${n}.report.json`, JSON.stringify(r.report)); await writeFile(`${out}/${n}.preview.png`, r.preview); await writeFile(`${out}/${n}.config.json`, JSON.stringify(config, null, 1));
    await rm(`${out}/work-${n}`, { recursive: true, force: true });
    console.log(n, ((Date.now() - t) / 1000).toFixed(0) + 's', JSON.stringify(r.report.warnings));
  }
}
void main().catch(e => { console.error(e instanceof Error ? e.message : e); process.exitCode = 1; });
