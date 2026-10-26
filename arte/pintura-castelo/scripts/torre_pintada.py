# Torre redonda pintada (folha de 4 vistas) -> render a 2x para o atlas edificios-3d (quadro torre_3).
# Tira o fundo branco e o chão pintado, escala para a varanda ficar à altura dos soldados (TOPZ 2,85) e calcula a âncora
# (canto de cima da casa 2x2: o centro da base da torre fica no centro da pegada).
# Uso: python3 torre_pintada.py <folha.png> <pasta_saida>
import sys, json
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
src, out = Path(sys.argv[1]), Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
def cutout(im):
    rgb = im.convert('RGB'); w, h = rgb.size; m = rgb.copy(); key = (255, 0, 255)
    for p in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, 0), (w // 2, h - 1), (0, h // 2), (w - 1, h // 2)]:
        if sum(m.getpixel(p)) > 3 * 215 and m.getpixel(p) != key: ImageDraw.floodfill(m, p, key, thresh=38)
    a = np.array(m); bg = (a[..., 0] == 255) & (a[..., 1] == 0) & (a[..., 2] == 255)
    o = rgb.convert('RGBA'); o.putalpha(Image.fromarray(np.where(bg, 0, 255).astype('uint8'))); return o
im = cutout(Image.open(src).crop((0, 0, 764, 472)))  # vista frontal (porta virada para a frente)
a = np.array(im); H, W = a.shape[:2]; yy, xx = np.mgrid[0:H, 0:W]
CX, CY, RA, RB = 408, 392, 98, 33   # elipse da base da torre na imagem
keep = (yy < 335) | (((xx - CX) / RA) ** 2 + ((yy - CY) / RB) ** 2 <= 1) | ((yy < CY) & (np.abs(xx - CX) < RA))
al = np.array(Image.fromarray(np.where(keep, a[..., 3], 0).astype('uint8')).filter(ImageFilter.GaussianBlur(1.2)))
a[..., 3] = np.minimum(a[..., 3], al); im = Image.fromarray(a)
DECK = 118                          # chão da varanda (onde ficam os soldados), ao centro
ZP2 = 2 * 64 / 2 ** .5 * .8660254   # píxeis por unidade de altura a 2x (78,4)
s = 2.85 * ZP2 / (CY - DECK)
im = im.resize((round(W * s), round(H * s)), Image.LANCZOS)
ax, ay = CX * s, CY * s - 64        # centro da pegada 2x2 = (1,1) -> 64 px abaixo do canto de cima
bb = im.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox(); im = im.crop(bb); ax -= bb[0]; ay -= bb[1]
im.save(out / 'torre_3.png')
af = out / 'anchors.json'; A = json.loads(af.read_text()) if af.exists() else {}
A['torre|3'] = [round(ax, 2), round(ay, 2), 2, 2]; af.write_text(json.dumps(A, indent=1)); print('torre_3', im.size, round(s, 3), A['torre|3'])
