# Integra os atlas Forge3D (armas Meshy) no jogo com nomes novos, preservando os atlas anteriores.
# Uso: python3 integrar.py <pasta_atlas_forge3d> <repo> <pasta_medicoes>
import sys, json, hashlib, math, re, io
from pathlib import Path
from PIL import Image
src, repo, med = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
UNITS = ['guerreiro', 'lanceiro', 'espadachim', 'arqueiro', 'besteiro']
WEAPON = {'guerreiro': 'axe-2', 'lanceiro': 'spear-2', 'espadachim': 'sword-2', 'arqueiro': 'bow-2', 'besteiro': 'crossbow'}
SUFFIX = '-armas-meshy'
# Conversão metros -> tiles na câmara Forge3D: o atlas tem 64 px por altura H do modelo (eixo da câmara),
# o jogo desenha a 30/64, e 1 tile ao longo de x avança 32 px no ecrã = l·cos45 → l = 32·√2·H/30.
TILE_IN_HEIGHTS = 32 * math.sqrt(2) / 30
GAME_FACTOR = 5  # u.anim += dt * v * 5 (www/index.html)
html_path = repo / 'www/index.html'; html = html_path.read_text()
i = html.index('const UNIT3D_DATA='); j = html.index('\n', i)
data = json.loads(html[i + len('const UNIT3D_DATA='):j].rstrip(';'))
out = repo / 'www/assets/units3d'; proofs = {}
for n in UNITS:
    meta = json.loads((src / f'{n}.json').read_text()); rep = json.loads((src / f'{n}.report.json').read_text())
    img = Image.open(src / f'{n}.webp').convert('RGBA'); buf = io.BytesIO()
    img.save(buf, 'WEBP', lossless=True, quality=100, method=6); webp = buf.getvalue()
    name = n + SUFFIX; (out / f'{name}.webp').write_bytes(webp)
    sha = hashlib.sha256(webp).hexdigest()
    heights = rep['walk']['distancePerCycleHeights']; stride = heights / TILE_IN_HEIGHTS
    phase = 2 * math.pi / (GAME_FACTOR * stride)
    m = {'h': meta['h'], 'directions': 8, 'framesPerDirection': meta['framesPerDirection'], 'states': meta['states'],
         'directionLabels': meta['directionLabels'], 'f': meta['f'], 'file': name,
         'locomotion': {'walk': {'phaseScale': round(phase, 6), 'strideTiles': round(stride, 6), 'animFactor': round(phase * GAME_FACTOR, 6)}},
         'atlasSha256': sha}
    (out / f'{name}.json').write_text(json.dumps(m, separators=(',', ':')))
    data[n] = m
    proofs[n] = {'meta': m, 'report': rep, 'webpBytes': len(webp), 'size': img.size, 'walkMeasure': json.loads((med / f'{n}.json').read_text())}
man = json.loads((repo / 'arte/soldados-armados-meshy/armas/manifest.json').read_text())
weap = {it['file'].replace('.glb', ''): it for it in man['items']}
art = repo / 'arte/soldados-armados-meshy'
for n, pr in proofs.items():
    rep, m, w = pr['report'], pr['meta'], weap[WEAPON[n]]
    opt = next(v for v in w['variants'] if v['path'].startswith('otimizados/')); mas = next(v for v in w['variants'] if v['path'].startswith('modelos/'))
    body = repo / f'arte/soldados-meshy/{n}.glb'
    cfg = json.loads((src / f'{n}.config.json').read_text())
    v = {'unit': n, 'atlas': f'www/assets/units3d/{m["file"]}.webp', 'atlasSha256': m['atlasSha256'], 'directions': 8, 'directionLabels': m['directionLabels'],
         'framesPerDirection': m['framesPerDirection'], 'referenceHeightPx': m['h'], 'meshyCredits': 0,
         'body': {'file': f'arte/soldados-meshy/{n}.glb', 'sha256': hashlib.sha256(body.read_bytes()).hexdigest(), 'sourceBranch': 'soldados-meshy-piloto@7cb7cab'},
         'bones': pr['walkMeasure']['bones'], 'boneNames': pr['walkMeasure']['boneNames'],
         'weapon': {'file': f'arte/soldados-armados-meshy/armas/{opt["path"]}', 'sha256': opt['sha256'], 'triangles': opt['triangles'],
                    'masterSha256': mas['sha256'], 'masterTriangles': mas['triangles'], 'originalMeshySha256': w['original']['sha256'],
                    'dimensionsMetres': opt['dimensionsMetres'], 'bone': rep['props'][[k for k in rep['props'] if k != '_models'][0]]['bone'],
                    'orientedIn': rep['props'][[k for k in rep['props'] if k != '_models'][0]]['placedIn']},
         'states': {k: {**sv, 'clip': sv['clip'].split('|')[-1]} for k, sv in rep['states'].items()},
         **({'attackLocalAdaptation': {'sourceClip': 'Idle (Combat Idle Meshy)', 'method': 'camada NLA COMBINE: braços para a frente (towardForward) e tronco -6°, só no estado attack', 'meshyAnimation': False,
             'note': 'Adaptação local autorizada; não é uma animação Meshy nova. Sem recuo nem virote: o disparo é o projétil do jogo.'}} if n == 'besteiro' else {}),
         'checks': rep['checks'], 'clipMeasurements': pr['walkMeasure']['clips'],
         'walk': {**rep['walk'], 'tileInModelHeights': TILE_IN_HEIGHTS, **m['locomotion']['walk']},
         'poseOffsets': cfg['poseOffsets'], 'renderer': 'Forge3D RENDER_SPRITE_ATLAS (platinyb91cv-forge3d-ai fase4-imagens) com SPRITE_PROP_DIR, Blender 5.2.2 Cycles CPU',
         'warnings': rep['warnings'], 'model': rep.get('model')}
    for s_ in v['clipMeasurements'].values():
        if s_: s_.pop('footSeparationSeries', None)
    (art / 'atlas' / f'{n}.verification.json').write_text(json.dumps(v, indent=1, ensure_ascii=False))
    (art / 'configs' / f'{n}.config.json').write_text(json.dumps(cfg, indent=1))
html = html[:i] + 'const UNIT3D_DATA=' + json.dumps(data, separators=(',', ':')) + ';' + html[j:]
html_path.write_text(html)
(Path(sys.argv[3]) / 'integracao.json').write_text(json.dumps({k: {'atlasSha256': v['meta']['atlasSha256'], 'webpBytes': v['webpBytes'], 'size': v['size'], 'locomotion': v['meta']['locomotion']} for k, v in proofs.items()}, indent=1))
print(json.dumps({k: [v['meta']['atlasSha256'][:12], v['webpBytes'], v['size'], v['meta']['locomotion']['walk']] for k, v in proofs.items()}, indent=1))
