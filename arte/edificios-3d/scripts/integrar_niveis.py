# Edifícios por nível (Kimi, fundo branco, sem chão) -> frames <tipo>_n2 / <tipo>_n3 no atlas edificios-3d.webp
# Mesmo processo dos edifícios "sem chão": tira o branco (ligado à borda + bolsas fechadas), orla suave, escala pela largura da pegada,
# âncora = canto de baixo do losango; telhados de ardósia sem cor de equipa (DESSAT). Uso: python3 integrar_niveis.py <pasta> <repo> casa:2x2 quartel:3x3 ...
import sys, json, io, hashlib, colorsys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage
src, repo = Path(sys.argv[1]), Path(sys.argv[2]); specs = sys.argv[3:]
html_p = repo/'www/index.html'; html = html_p.read_text()
i = html.index('const BLD3D_DATA='); j = html.index('\n', i); data = json.loads(html[i+17:html.index(';', i)])
atlas_p = repo/'www/assets/edificios-extra'/data['file']; old = Image.open(atlas_p).convert('RGBA'); SC = data['scale']
tiles = {n: (old.crop((x, y, x+w, y+h)), ax, ay) for n, (x, y, w, h, ax, ay) in data['frames'].items()}
def cut(path):
    rgb = np.asarray(Image.open(path).convert('RGB')).astype(np.float32); mn = rgb.min(2); sat = rgb.max(2)-mn
    white = (mn >= 228) & (sat <= 20); lab, n = ndimage.label(white)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    sizes = ndimage.sum(np.ones_like(mn), lab, range(1, n+1))
    pocket = np.zeros(n+1, bool); pocket[1:] = sizes >= 10
    bg = np.isin(lab, list(border)) | (pocket[lab] & (lab > 0) & (mn >= 236))
    d = ndimage.distance_transform_edt(~bg); wa = np.clip((255-mn)/60, 0, 1)
    a = np.where(bg, 0, np.where(d <= 2.2, wa, 1.0)); a = ndimage.uniform_filter(a, 2); a[bg] = 0
    A = np.clip(a, 1e-3, 1)[..., None]; col = np.where(a[..., None] >= .999, rgb, np.clip((rgb-255*(1-A))/A, 0, 255))
    im = Image.fromarray(np.dstack([col, a*255]).astype(np.uint8), 'RGBA'); bb = im.getchannel('A').point(lambda v: 255 if v > 24 else 0).getbbox()
    return im.crop(bb)
def dessat(im):
    px = im.load()
    for yy in range(im.height):
        for xx in range(im.width):
            r, g, b, al = px[xx, yy]
            if al < 8: continue
            h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
            if 188 <= h*360 <= 282 and s < .34:
                r2, g2, b2 = colorsys.hsv_to_rgb(h, min(s, .1), v); px[xx, yy] = (round(r2*255), round(g2*255), round(b2*255), al)
    return im
for sp in specs:
    name, wh = sp.split(':'); W, H = map(int, wh.split('x'))
    for L in (2, 3):
        f = src/f'{name}_nv{L}.png'
        if not f.exists(): continue
        im = cut(f); tw = (W+H)*32*SC*.96; k = tw/im.width
        im = im.resize((round(im.width*k), round(im.height*k)), Image.LANCZOS); im = dessat(im)
        ax = im.width/2; ay = im.height-(W+H)*16*SC
        tiles[f'{name}_n{L}'] = (im, round(ax, 2), round(ay, 2)); print(name, L, im.size, ax, ay)
order = sorted(tiles, key=lambda n: -tiles[n][0].height); AW = 2048; gap = 2; x = y = gap; row = 0; place = {}
for n in order:
    w, h = tiles[n][0].size
    if x+w+gap > AW: x = gap; y += row+gap; row = 0
    place[n] = (x, y); x += w+gap; row = max(row, h)
atlas = Image.new('RGBA', (AW, y+row+gap)); F = {}
for n, (t, ax, ay) in tiles.items():
    px_, py_ = place[n]; atlas.paste(t, (px_, py_)); F[n] = [px_, py_, t.width, t.height, ax, ay]
buf = io.BytesIO(); atlas.save(buf, 'WEBP', lossless=True, quality=100, method=6); webp = buf.getvalue(); atlas_p.write_bytes(webp)
data['atlasSha256'] = hashlib.sha256(webp).hexdigest(); data['frames'] = dict(sorted(F.items()))
html = html[:i]+'const BLD3D_DATA='+json.dumps(data, separators=(',', ':'))+';'+html[j:]; html_p.write_text(html)
vp = repo/'arte/edificios-3d/verification.json'; v = json.loads(vp.read_text()); v['atlasSha256'] = data['atlasSha256']; vp.write_text(json.dumps(v, indent=2, ensure_ascii=False)+'\n')
print(atlas.size, len(webp), len(F))
