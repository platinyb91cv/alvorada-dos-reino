# Troca só alguns edifícios no atlas edificios-3d.webp sem renderizar os outros de novo.
# Cada frame atual é recortado do atlas e os novos vêm dos renders (com anchors.json); depois volta a empacotar tudo.
# Uso: python3 trocar_no_atlas.py <pasta-dos-renders> <repo> mercado_1 mercado_2 [...]
# Opção: DESSAT_TELHADO=1 tira a cor aos azuis acinzentados (telhados de ardósia) para não ficarem com a cor da equipa;
#        os azuis vivos (toldos, estandartes) continuam a ser recoloridos.
import sys, os, json, io, hashlib, colorsys
from pathlib import Path
from PIL import Image
src, repo, names = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3:]
K = .75
html_p = repo / 'www/index.html'; html = html_p.read_text()
i = html.index('const BLD3D_DATA='); j = html.index('\n', i); data = json.loads(html[i + 17:html.index(';', i)])
atlas_p = repo / 'www/assets/edificios-extra' / data['file']; old = Image.open(atlas_p).convert('RGBA')
tiles = {n: (old.crop((x, y, x + w, y + h)), ax, ay) for n, (x, y, w, h, ax, ay) in data['frames'].items()}
A = json.loads((src / 'anchors.json').read_text())
def dessat(im):
    px = im.load()
    for yy in range(im.height):
        for xx in range(im.width):
            r, g, b, a = px[xx, yy]
            if a < 8: continue
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            if 188 <= h * 360 <= 282 and s < .34:
                r2, g2, b2 = colorsys.hsv_to_rgb(h, min(s, .1), v); px[xx, yy] = (round(r2 * 255), round(g2 * 255), round(b2 * 255), a)
    return im
for n in names:
    ax, ay, w, h = A[n.rsplit('_', 1)[0] + '|' + n.rsplit('_', 1)[1]][:4]
    im = Image.open(src / f'{n}.png').convert('RGBA')
    if os.environ.get('DESSAT_TELHADO'): im = dessat(im)
    bb = im.getchannel('A').point(lambda v: 255 if v > 6 else 0).getbbox()
    x0, y0, x1, y1 = max(0, bb[0] - 1), max(0, bb[1] - 1), min(im.width, bb[2] + 1), min(im.height, bb[3] + 1)
    t = im.crop((x0, y0, x1, y1)); t = t.resize((max(1, round(t.width * K)), max(1, round(t.height * K))), Image.LANCZOS)
    tiles[n] = (t, round((ax - x0) * K, 2), round((ay - y0) * K, 2)); print('novo', n, t.size)
order = sorted(tiles, key=lambda n: -tiles[n][0].height); AW = 2048; gap = 2; x = y = gap; row = 0; place = {}
for n in order:
    w, h = tiles[n][0].size
    if x + w + gap > AW: x = gap; y += row + gap; row = 0
    place[n] = (x, y); x += w + gap; row = max(row, h)
atlas = Image.new('RGBA', (AW, y + row + gap)); F = {}
for n, (t, ax, ay) in tiles.items():
    px_, py_ = place[n]; atlas.paste(t, (px_, py_)); F[n] = [px_, py_, t.width, t.height, ax, ay]
buf = io.BytesIO(); atlas.save(buf, 'WEBP', lossless=True, quality=100, method=6); webp = buf.getvalue(); atlas_p.write_bytes(webp)
data['atlasSha256'] = hashlib.sha256(webp).hexdigest(); data['frames'] = dict(sorted(F.items()))
html = html[:i] + 'const BLD3D_DATA=' + json.dumps(data, separators=(',', ':')) + ';' + html[j:]; html_p.write_text(html)
print(atlas.size, len(webp), len(F))
