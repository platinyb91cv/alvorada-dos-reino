# Torre quadrada pintada (fonte/torre2_v1.png) -> torre de nível 2 (quadro torre_2 do atlas edificios-3d), pegada 2x2.
# Escala pela largura da base (cantos esquerdo/direito do pedestal = largura da pegada 2x2, 256 px a 2x, x0,97); âncora = canto de cima
# da pegada; altura do terraço (onde ficam a catapulta e os soldados) medida na pintura.
# Uso: python3 torre2_pintada.py <torre.png> <pasta_saida>   e depois  trocar_no_atlas.py <pasta_saida> <repo> torre_2
import sys, json, math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
src, out = Path(sys.argv[1]), Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
def cutout(im):
    rgb = im.convert('RGB'); w, h = rgb.size; m = rgb.copy(); key = (255, 0, 255)
    for p in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, 0), (w // 2, h - 1), (0, h // 2), (w - 1, h // 2)]:
        if sum(m.getpixel(p)) > 3 * 215 and m.getpixel(p) != key: ImageDraw.floodfill(m, p, key, thresh=38)
    a = np.array(m); bg = (a[..., 0] == 255) & (a[..., 1] == 0) & (a[..., 2] == 255)
    alpha = Image.fromarray(np.where(bg, 0, 255).astype('uint8')).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(.7))
    o = rgb.convert('RGBA'); o.putalpha(alpha); return o
def calm_blues(im):
    a = np.array(im).astype(np.float32) / 255; r, g, b = a[..., 0], a[..., 1], a[..., 2]
    M = a[..., :3].max(-1); m = a[..., :3].min(-1); s = np.where(M > 0, (M - m) / np.maximum(M, 1e-6), 0)
    blue = (b >= r) & (b >= g) & (s > .06) & (s < .5); gray = (r + g + b) / 3; k = np.where(blue, .2, 1)[..., None]
    a[..., :3] = gray[..., None] + (a[..., :3] - gray[..., None]) * k
    return Image.fromarray((a * 255).clip(0, 255).astype('uint8'))
im = calm_blues(cutout(Image.open(src)))
L, Rr, GY = 380, 885, 1100          # cantos esquerdo/direito do pedestal e o chão desses cantos (px da pintura)
DECK = (632, 232)                   # centro do terraço do topo
ZP2 = 2 * 64 / math.sqrt(2) * math.cos(math.pi / 6)
s = 2 * 2 * 64 / (Rr - L) * .97
im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
ax, ay = (L + Rr) / 2 * s, GY * s - 2 * 32
deck = [round((DECK[0] * s - ax) / 2, 1), round((DECK[1] * s - ay) / 2, 1)]   # px do jogo a partir da âncora
topo = round((GY - DECK[1]) * s / ZP2, 2)
bb = im.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox(); im = im.crop(bb); ax -= bb[0]; ay -= bb[1]
im.save(out / 'torre_2.png'); af = out / 'anchors.json'; A = json.loads(af.read_text()) if af.exists() else {}
A['torre|2'] = [round(ax, 2), round(ay, 2), 2, 2]; af.write_text(json.dumps(A, indent=1))
(out / 'torre2_topo.json').write_text(json.dumps({'deck': deck, 'topo': topo})); print('torre_2', im.size, round(s, 3), A['torre|2'], 'terraço', deck, 'altura', topo)
