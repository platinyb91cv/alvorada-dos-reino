# Integra os atlas de cerco (aríete, trebuchet) no jogo: reduz 0,7× (continua acima da resolução no ecrã),
# reempacota em 2048 px, WebP sem perdas, meta.h = 64·escala para manter o tamanho real no ecrã.
import sys, json, io, math, hashlib
from pathlib import Path
from PIL import Image
src, repo = Path(sys.argv[1]), Path(sys.argv[2]); out = repo / 'www/assets/units3d'
SC = 0.7; TILE = 32 * math.sqrt(2)  # px de ecrã por casa ao longo de x; ecrã = metros × 30/64 × (href/H)
WHEEL = {'ariete': 0.16 * 1.68, 'trebuchet': 0.16 * 2.37, 'catapulta': 0.4}  # raio real das rodas (m)
H = {'ariete': 1.051 * 1.68, 'trebuchet': 1.113 * 2.37, 'catapulta': 1.95}
data = {}
for n in ['ariete', 'trebuchet', 'catapulta']:
    m = json.loads((src / f'{n}.json').read_text()); cfg = json.loads((src / f'{n}.config.json').read_text()); A = Image.open(src / f'{n}.webp').convert('RGBA')
    tiles = []
    for (x, y, w, h, ax, ay) in m['f']:
        t = A.crop((x, y, x + w, y + h)); W2, H2 = max(1, round(w * SC)), max(1, round(h * SC)); tiles.append((t.resize((W2, H2), Image.LANCZOS), ax * SC, ay * SC))
    order = sorted(range(len(tiles)), key=lambda i: -tiles[i][0].height); AW = 2048; gap = 2; x = y = gap; row = 0; place = {}
    for i in order:
        w, h = tiles[i][0].size
        if x + w + gap > AW: x = gap; y += row + gap; row = 0
        place[i] = (x, y); x += w + gap; row = max(row, h)
    AH = y + row + gap; atlas = Image.new('RGBA', (AW, AH)); F = []
    for i, (t, ax, ay) in enumerate(tiles): px, py = place[i]; atlas.paste(t, (px, py)); F.append([px, py, t.width, t.height, round(ax, 4), round(ay, 4)])
    buf = io.BytesIO(); atlas.save(buf, 'WEBP', lossless=True, quality=100, method=6); webp = buf.getvalue(); (out / f'{n}.webp').write_bytes(webp)
    href = cfg['referenceHeightPx']; scr_per_m = (href / H[n]) * (30 / 64)  # px de ecrã por metro (igual ao soldado: 64/1,61·30/64)
    stride = 2 * math.pi * WHEEL[n] * scr_per_m / TILE  # uma volta das rodas, em casas
    phase = 2 * math.pi / (5 * stride)
    meta = {'h': round(64 * SC, 4), 'directions': 8, 'framesPerDirection': m['framesPerDirection'], 'states': m['states'], 'directionLabels': m['directionLabels'], 'f': F,
            'locomotion': {'walk': {'phaseScale': round(phase, 6), 'strideTiles': round(stride, 6), 'animFactor': round(phase * 5, 6)}}, 'atlasSha256': hashlib.sha256(webp).hexdigest()}
    (out / f'{n}.json').write_text(json.dumps(meta, separators=(',', ':'))); data[n] = meta
    print(n, atlas.size, len(webp), meta['locomotion']['walk'])
html = (repo / 'www/index.html').read_text()
line = 'const UNIT3D_SIEGE_DATA=' + json.dumps(data, separators=(',', ':')) + ';'
if 'const UNIT3D_SIEGE_DATA=' in html:  # já integrado: substitui a linha
    i = html.index('const UNIT3D_SIEGE_DATA='); j = html.index('\n', i); html = html[:i] + line + html[j:]
else:
    k = html.index('// máquinas de cerco Meshy'); html = html[:k] + line + '\n' + html[k:]
(repo / 'www/index.html').write_text(html)
