import { writeFile, mkdir, rm } from 'node:fs/promises';
import { runSpriteAtlas } from '/home/claude/platinyb91cv-forge3d-ai/worker/blender';
import { unpackAtlasBundle } from '/home/claude/platinyb91cv-forge3d-ai/lib/sprite-bundle';
const s = (name: string, clip: string, frames: number, loop = true) => ({ name, clip, frames, loop, props: [] as string[] });
// soldado de 1,61 m = 64 px; catapulta (repouso) ≈ 1,95 m, carroça com cavalo ≈ 2,25 m
const units: Record<string, { glb: string; forward: '-X' | '+X' | '-Y'; href: number; out: string; states: ReturnType<typeof s>[] }> = {
  catapulta: { glb: '/tmp/claude-0/cerco2/catapulta-rig.glb', forward: '+X', href: 78, out: '/tmp/claude-0/work/cerco',
    states: [s('idle', 'Idle', 2), s('walk', 'Walk', 8), s('attack', 'Attack', 6), s('hit', 'Hit', 2), s('death', 'Death', 4, false)] },
  carroca: { glb: '/tmp/claude-0/cerco2/carroca-rig.glb', forward: '-Y', href: 90, out: '/tmp/claude-0/work/cav',
    states: [s('idle', 'Idle', 2), s('walk', 'Walk', 8), s('hit', 'Hit', 2), s('death', 'Death', 4, false)] },
};
async function main() {
  for (const n of (process.argv[2] ?? Object.keys(units).join(',')).split(',')) {
    const u = units[n]; const t = Date.now(); await mkdir(u.out, { recursive: true });
    const config = { version: 1, modelForward: u.forward, referenceHeightPx: u.href, samples: 8, atlasWidth: 4096, webpQuality: 100, states: u.states };
    const b = await runSpriteAtlas({ type: 'RENDER_SPRITE_ATLAS', assetId: 'extra0000000', name: n, config }, u.glb, `${u.out}/work-${n}`, AbortSignal.timeout(2400000));
    const r = await unpackAtlasBundle(b);
    await writeFile(`${u.out}/${n}.webp`, r.webp); await writeFile(`${u.out}/${n}.json`, JSON.stringify(r.meta)); await writeFile(`${u.out}/${n}.report.json`, JSON.stringify(r.report)); await writeFile(`${u.out}/${n}.preview.png`, r.preview); await writeFile(`${u.out}/${n}.config.json`, JSON.stringify(config, null, 1));
    await rm(`${u.out}/work-${n}`, { recursive: true, force: true });
    console.log(n, ((Date.now() - t) / 1000).toFixed(0) + 's', JSON.stringify(r.report.warnings));
  }
}
void main().catch(e => { console.error(e instanceof Error ? e.message : e); process.exitCode = 1; });
