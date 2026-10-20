# Integra o atlas do veado Meshy (tipo de jogo "gazela") no jogo: reduz 0,7×, reempacota em 2048 px, WebP sem perdas,
# meta.h = 64·escala (tamanho real no ecrã, como os soldados) e cadência do trote a partir do passo real das patas.
import sys, json, io, math, hashlib
from pathlib import Path
from PIL import Image
src, repo = Path(sys.argv[1]), Path(sys.argv[2]); out = repo / 'www/assets/units3d'
SC = 0.7; TILE = 32 * math.sqrt(2)
# trote: cada perna oscila ±26° com 0,66 m de perna -> 2·0,66·sin26° por meio ciclo, dois pares diagonais por ciclo
STRIDE_M = {'gazela': 2 * 2 * 0.66 * math.sin(math.radians(26))}
data = {}
for n in STRIDE_M:
    m = json.loads((src / f'{n}.json').read_text()); cfg = json.loads((src / f'{n}.config.json').read_text()); rep = json.loads((src / f'{n}.report.json').read_text())
    A = Image.open(src / f'{n}.webp').convert('RGBA'); tiles = []
    for (x, y, w, h, ax, ay) in m['f']:
        t = A.crop((x, y, x + w, y + h)); tiles.append((t.resize((max(1, round(w * SC)), max(1, round(h * SC))), Image.LANCZOS), ax * SC, ay * SC))
    order = sorted(range(len(tiles)), key=lambda i: -tiles[i][0].height); AW = 2048; gap = 2; x = y = gap; row = 0; place = {}
    for i in order:
        w, h = tiles[i][0].size
        if x + w + gap > AW: x = gap; y += row + gap; row = 0
        place[i] = (x, y); x += w + gap; row = max(row, h)
    atlas = Image.new('RGBA', (AW, y + row + gap)); F = []
    for i, (t, ax, ay) in enumerate(tiles): px, py = place[i]; atlas.paste(t, (px, py)); F.append([px, py, t.width, t.height, round(ax, 4), round(ay, 4)])
    buf = io.BytesIO(); atlas.save(buf, 'WEBP', lossless=True, quality=100, method=6); webp = buf.getvalue(); (out / f'{n}.webp').write_bytes(webp)
    scr_per_m = (cfg['referenceHeightPx'] / rep['model']['heightMetres']) * (30 / 64)
    stride = STRIDE_M[n] * scr_per_m / TILE; phase = 2 * math.pi / (5 * stride)
    meta = {'h': round(64 * SC, 4), 'directions': 8, 'framesPerDirection': m['framesPerDirection'], 'states': m['states'], 'directionLabels': m['directionLabels'], 'f': F,
            'locomotion': {'walk': {'phaseScale': round(phase, 6), 'strideTiles': round(stride, 6), 'animFactor': round(phase * 5, 6)}}, 'atlasSha256': hashlib.sha256(webp).hexdigest()}
    (out / f'{n}.json').write_text(json.dumps(meta, separators=(',', ':'))); data[n] = meta
    print(n, atlas.size, len(webp), rep['model']['heightMetres'], meta['locomotion']['walk'])
html = (repo / 'www/index.html').read_text()
line = 'const UNIT3D_FAUNA_DATA=' + json.dumps(data, separators=(',', ':')) + ';'
i = html.index('const UNIT3D_FAUNA_DATA='); j = html.index('\n', i); html = html[:i] + line + html[j:]
(repo / 'www/index.html').write_text(html)
