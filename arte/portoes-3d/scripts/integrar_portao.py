# Empacota os portões 3D (render a 2× do ecrã) num atlas WebP sem perdas e escreve GATE3D_DATA no index.html.
import sys, json, io, hashlib
from pathlib import Path
from PIL import Image
src, repo = Path(sys.argv[1]), Path(sys.argv[2]); A = json.loads((src / 'anchors.json').read_text())['anchor']
tiles = {}
for name, (ax, ay) in A.items():
    im = Image.open(src / f'{name}.png').convert('RGBA'); bb = im.getchannel('A').point(lambda v: 255 if v > 6 else 0).getbbox()
    x0, y0, x1, y1 = max(0, bb[0] - 1), max(0, bb[1] - 1), min(im.width, bb[2] + 1), min(im.height, bb[3] + 1)
    tiles[name] = (im.crop((x0, y0, x1, y1)), ax - x0, ay - y0)
order = sorted(tiles, key=lambda n: -tiles[n][0].height); AW = 2048; gap = 2; x = y = gap; row = 0; place = {}
for n in order:
    w, h = tiles[n][0].size
    if x + w + gap > AW: x = gap; y += row + gap; row = 0
    place[n] = (x, y); x += w + gap; row = max(row, h)
atlas = Image.new('RGBA', (AW, y + row + gap)); F = {}
for n, (t, ax, ay) in tiles.items():
    px, py = place[n]; atlas.paste(t, (px, py)); F[n] = [px, py, t.width, t.height, round(ax, 2), round(ay, 2)]
buf = io.BytesIO(); atlas.save(buf, 'WEBP', lossless=True, quality=100, method=6); webp = buf.getvalue()
out = repo / 'www/assets/edificios-extra/portoes-3d.webp'; out.write_bytes(webp)
data = {'file': 'portoes-3d.webp', 'scale': 2, 'atlasSha256': hashlib.sha256(webp).hexdigest(), 'frames': dict(sorted(F.items()))}
html = (repo / 'www/index.html').read_text(); line = 'const GATE3D_DATA=' + json.dumps(data, separators=(',', ':')) + ';'
i = html.index('const GATE3D_DATA='); j = html.index('\n', i); html = html[:i] + line + html[j:]
(repo / 'www/index.html').write_text(html); print(atlas.size, len(webp), len(F))
