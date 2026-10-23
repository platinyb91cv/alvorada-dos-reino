# Recorta cada peça de muralha à coluna de ecrã da sua casa (|x| < 16 px do jogo = 32 px a 2×), empacota num atlas
# WebP sem perdas e escreve WALL3D_DATA no index.html.
import sys, json, io, hashlib
from pathlib import Path
from PIL import Image
src, repo = Path(sys.argv[1]), Path(sys.argv[2]); J = json.loads((src / 'anchors.json').read_text()); A = J['anchor']; half = J['clipHalfPx']
tiles = {}
for name, (ax, ay) in A.items():
    im = Image.open(src / f'{name}.png').convert('RGBA'); x0c, x1c = round(ax - half - 3), round(ax + half + 3)  # 3 px de sobreposição: sem a linha clara nas juntas (bordas suavizadas)
    a = im.getchannel('A'); px = a.load()
    for y in range(im.height):
        for x in list(range(0, max(0, x0c))) + list(range(min(im.width, x1c), im.width)): px[x, y] = 0
    im.putalpha(a); bb = a.point(lambda v: 255 if v > 6 else 0).getbbox()
    x0, y0, x1, y1 = bb[0], max(0, bb[1] - 1), bb[2], min(im.height, bb[3] + 1)
    tiles[name] = (im.crop((x0, y0, x1, y1)), ax - x0, ay - y0)
order = sorted(tiles, key=lambda n: -tiles[n][0].height); AW = 1024; gap = 2; x = y = gap; row = 0; place = {}
for n in order:
    w, h = tiles[n][0].size
    if x + w + gap > AW: x = gap; y += row + gap; row = 0
    place[n] = (x, y); x += w + gap; row = max(row, h)
atlas = Image.new('RGBA', (AW, y + row + gap)); F = {}
for n, (t, ax, ay) in tiles.items():
    px_, py_ = place[n]; atlas.paste(t, (px_, py_)); F[n] = [px_, py_, t.width, t.height, round(ax, 2), round(ay, 2)]
buf = io.BytesIO(); atlas.save(buf, 'WEBP', lossless=True, quality=100, method=6); webp = buf.getvalue()
(repo / 'www/assets/edificios-extra/muralhas-3d.webp').write_bytes(webp)
data = {'file': 'muralhas-3d.webp', 'scale': 2, 'atlasSha256': hashlib.sha256(webp).hexdigest(), 'frames': dict(sorted(F.items()))}
html = (repo / 'www/index.html').read_text(); line = 'const WALL3D_DATA=' + json.dumps(data, separators=(',', ':')) + ';'
i = html.index('const WALL3D_DATA='); j = html.index('\n', i); html = html[:i] + line + html[j:]
(repo / 'www/index.html').write_text(html); print(atlas.size, len(webp), len(F))
