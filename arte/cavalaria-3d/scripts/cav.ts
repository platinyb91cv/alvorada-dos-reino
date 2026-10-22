import { writeFile, mkdir, rm } from 'node:fs/promises';
import { runSpriteAtlas } from '/home/claude/platinyb91cv-forge3d-ai/worker/blender';
import { unpackAtlasBundle } from '/home/claude/platinyb91cv-forge3d-ai/lib/sprite-bundle';
const s = (name: string, clip: string, frames: number, loop = true) => ({ name, clip, frames, loop, props: [] as string[] });
// Altura de referência proporcional à altura real (soldado de 1,61 m = 64 px): o jogo desenha meta.h=64 a 30 px.
const units: Record<string, { glb: string; forward: '-X' | '+X' | '-Y'; href: number }> = {
  cavaleiro: { glb: '/tmp/claude-0/cav/cavaleiro-rig.glb', forward: '-Y', href: 98 },
  cavPesada: { glb: '/tmp/claude-0/cav/cavPesada-rig.glb', forward: '-Y', href: 98 },
  cavArqueira: { glb: '/tmp/claude-0/cav/cavArqueira-rig.glb', forward: '-Y', href: 98 },
};
async function main() {
  const out = '/tmp/claude-0/work/cav'; await mkdir(out, { recursive: true });
  for (const n of (process.argv[2] ?? Object.keys(units).join(',')).split(',')) {
    const u = units[n]; const t = Date.now();
    const config = { version: 1, modelForward: u.forward, referenceHeightPx: u.href, samples: 8, atlasWidth: 4096, webpQuality: 100,
      states: [s('idle', 'Idle', 2), s('walk', 'Walk', 8), s('trot', 'Trot', 8), s('attack', 'Attack', 6), s('hit', 'Hit', 2), s('death', 'Death', 4, false)] };
    const b = await runSpriteAtlas({ type: 'RENDER_SPRITE_ATLAS', assetId: 'cavalo000000', name: n, config }, u.glb, `${out}/work-${n}`, AbortSignal.timeout(2400000));
    const r = await unpackAtlasBundle(b);
    await writeFile(`${out}/${n}.webp`, r.webp); await writeFile(`${out}/${n}.json`, JSON.stringify(r.meta)); await writeFile(`${out}/${n}.report.json`, JSON.stringify(r.report)); await writeFile(`${out}/${n}.preview.png`, r.preview); await writeFile(`${out}/${n}.config.json`, JSON.stringify(config, null, 1));
    await rm(`${out}/work-${n}`, { recursive: true, force: true });
    console.log(n, ((Date.now() - t) / 1000).toFixed(0) + 's', JSON.stringify(r.report.states), JSON.stringify(r.report.warnings));
  }
}
void main().catch(e => { console.error(e instanceof Error ? e.message : e); process.exitCode = 1; });
