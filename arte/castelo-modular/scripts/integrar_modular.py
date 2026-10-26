# Corta, empacota e liga ao jogo o conjunto modular (renders de montar_modular.py).
# Muros: coluna de ecrã da casa (±32 px a 2x + 3 px de sobreposição) só nos lados em que o braço continua para o vizinho.
# Pedaços da torre: coluna da casa da pegada onde ficam. Âncora = canto de cima da casa (muros) ou da pegada (torre),
# medida no render; pontos de ligação (caminho de ronda na borda) exportados em sprite px.
# Uso: python3 integrar_modular.py <pasta_renders> <repo>
import sys, json, io, hashlib
from pathlib import Path
import numpy as np
from PIL import Image
src, repo = Path(sys.argv[1]), Path(sys.argv[2]); A = json.loads((src / 'anchors.json').read_text())
HALF, OV = 32, 3
tiles = {}
for name, p in A['pieces'].items():
    im = Image.open(src / f'{name}.png').convert('RGBA'); a = np.array(im); ax, ay = p['anchor']
    cx = ax + (p['col'][0] - p['col'][1]) * 64 if name.startswith('tw_') else ax
    cutL, cutR = p['cut']
    if cutL: a[:, :max(0, int(round(cx - HALF - OV)))] = 0
    if cutR: a[:, int(round(cx + HALF + OV)):] = 0
    al = a[..., 3]; ys, xs = np.where(al > 6)
    if not len(xs): print('VAZIO', name); continue
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    t = Image.fromarray(a[y0:y1, x0:x1])
    links = {k: [round(v[0] - x0, 2), round(v[1] - y0, 2)] for k, v in p.get('links', {}).items()}
    tiles[name] = (t, ax - x0, ay - y0, links)
order = sorted(tiles, key=lambda n: -tiles[n][0].height); AW = 2048; gap = 2; x = y = gap; row = 0; place = {}
for n in order:
    w, h = tiles[n][0].size
    if x + w + gap > AW: x = gap; y += row + gap; row = 0
    place[n] = (x, y); x += w + gap; row = max(row, h)
atlas = Image.new('RGBA', (AW, y + row + gap)); F = {}; LK = {}
for n, (t, ax, ay, links) in tiles.items():
    px, py = place[n]; atlas.paste(t, (px, py)); F[n] = [px, py, t.width, t.height, round(ax, 2), round(ay, 2)]
    if links: LK[n] = links
buf = io.BytesIO(); atlas.save(buf, 'WEBP', lossless=True, quality=100, method=6); webp = buf.getvalue()
(repo / 'www/assets/edificios-extra/castelo-modular.webp').write_bytes(webp)
sha = hashlib.sha256(webp).hexdigest()
data = {'file': 'castelo-modular.webp', 'scale': 2, 'atlasSha256': sha, 'T': A['T'], 'H': A['H'], 'towerR': A['towerR'], 'towerFloor': A['towerFloor'],
        'block': A['block'], 'frames': dict(sorted(F.items())), 'links': dict(sorted(LK.items()))}
html_p = repo / 'www/index.html'; html = html_p.read_text(); line = 'const CMOD_DATA=' + json.dumps(data, separators=(',', ':')) + ';'
if 'const CMOD_DATA=' in html: i = html.index('const CMOD_DATA='); j = html.index('\n', i); html = html[:i] + line + html[j:]
else: i = html.index('const WALL3D_DATA='); html = html[:i] + line + '\n' + html[i:]
html_p.write_text(html)
(repo / 'arte/castelo-modular/verification.json').write_text(json.dumps({'atlasSha256': sha, 'pecas': len(F), 'pxPorCasa2x': A['pxPerUnit'], 'T': A['T'], 'H': A['H'],
    'torre': {'diametro': A['towerR'] * 2, 'piso': A['towerFloor']}, 'sombraDeChao': False, 'block': A['block'], 'creditosMeshy': 0}, indent=1, ensure_ascii=False))
print(atlas.size, len(webp) // 1024, 'KB', len(F), 'peças')
