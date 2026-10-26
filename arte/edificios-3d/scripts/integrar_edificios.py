# Recorta cada render de edifício pela sua opacidade, empacota num atlas WebP sem perdas e escreve BLD3D_DATA no index.html.
# Uso: python3 integrar_edificios.py <pasta-dos-renders> <repo>
import sys, json, io, hashlib
from pathlib import Path
from PIL import Image
src, repo = Path(sys.argv[1]), Path(sys.argv[2]); A = json.loads((src / 'anchors.json').read_text())
tiles = {}; K = .75  # atlas a 1,5× do ecrã (renders a 2×): cabe em 2048 px e poupa memória no telemóvel
for key, (ax, ay, w, h) in A.items():
    name = key.replace('|', '_'); im = Image.open(src / f'{name}.png').convert('RGBA')
    bb = im.getchannel('A').point(lambda v: 255 if v > 6 else 0).getbbox()
    x0, y0, x1, y1 = max(0, bb[0] - 1), max(0, bb[1] - 1), min(im.width, bb[2] + 1), min(im.height, bb[3] + 1)
    t = im.crop((x0, y0, x1, y1)); t = t.resize((max(1, round(t.width * K)), max(1, round(t.height * K))), Image.LANCZOS)
    tiles[name] = (t, (ax - x0) * K, (ay - y0) * K)
order = sorted(tiles, key=lambda n: -tiles[n][0].height); AW = 2048; gap = 2; x = y = gap; row = 0; place = {}
for n in order:
    w, h = tiles[n][0].size
    if x + w + gap > AW: x = gap; y += row + gap; row = 0
    place[n] = (x, y); x += w + gap; row = max(row, h)
atlas = Image.new('RGBA', (AW, y + row + gap)); F = {}
for n, (t, ax, ay) in tiles.items():
    px_, py_ = place[n]; atlas.paste(t, (px_, py_)); F[n] = [px_, py_, t.width, t.height, round(ax, 2), round(ay, 2)]
buf = io.BytesIO(); atlas.save(buf, 'WEBP', lossless=True, quality=100, method=6); webp = buf.getvalue()
(repo / 'www/assets/edificios-extra/edificios-3d.webp').write_bytes(webp)
data = {'file': 'edificios-3d.webp', 'scale': 2 * K, 'atlasSha256': hashlib.sha256(webp).hexdigest(), 'frames': dict(sorted(F.items()))}
html = (repo / 'www/index.html').read_text(); line = 'const BLD3D_DATA=' + json.dumps(data, separators=(',', ':')) + ';'
i = html.index('const BLD3D_DATA='); j = html.index('\n', i); html = html[:i] + line + html[j:]
(repo / 'www/index.html').write_text(html); print(atlas.size, len(webp), len(F))
