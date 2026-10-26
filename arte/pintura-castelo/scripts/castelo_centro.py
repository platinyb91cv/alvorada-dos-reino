# Castelo pintado (fonte/castelo_centro.png) -> Centro da Vila na Idade do Ferro (quadro centro_2 do atlas edificios-3d).
# Mesma escala por casa: a distância entre as torres dos cantos esquerdo e direito (centros da base) = largura da pegada 3x3
# (384 px a 2x, x0,97 de folga). A âncora é o canto de cima da pegada, tirada do chão das torres dos cantos (que ficam nos
# cantos esquerdo e direito da pegada). Azuis acinzentados (telhados de ardósia) perdem cor; estandartes azuis levam a cor da equipa.
# Uso: python3 castelo_centro.py <castelo.png> <pasta_saida>   e depois  trocar_no_atlas.py <pasta_saida> <repo> centro_2
import sys, json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
src, out = Path(sys.argv[1]), Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
def cutout(im):
    rgb = im.convert('RGB'); w, h = rgb.size; m = rgb.copy(); key = (255, 0, 255)
    for p in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, 0), (w // 2, h - 1), (0, h // 2), (w - 1, h // 2)]:
        if sum(m.getpixel(p)) > 3 * 215 and m.getpixel(p) != key: ImageDraw.floodfill(m, p, key, thresh=38)
    a = np.array(m); bg = (a[..., 0] == 255) & (a[..., 1] == 0) & (a[..., 2] == 255)
    bg |= (np.array(rgb).min(-1) > 246)   # branco preso entre bandeiras e ameias
    alpha = Image.fromarray(np.where(bg, 0, 255).astype('uint8')).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(.7))
    o = rgb.convert('RGBA'); o.putalpha(alpha); return o
def calm_blues(im):
    a = np.array(im).astype(np.float32) / 255; r, g, b = a[..., 0], a[..., 1], a[..., 2]
    M = a[..., :3].max(-1); m = a[..., :3].min(-1); s = np.where(M > 0, (M - m) / np.maximum(M, 1e-6), 0)
    blue = (b >= r) & (b >= g) & (s > .06) & (s < .5); gray = (r + g + b) / 3; k = np.where(blue, .2, 1)[..., None]
    a[..., :3] = gray[..., None] + (a[..., :3] - gray[..., None]) * k
    return Image.fromarray((a * 255).clip(0, 255).astype('uint8'))
_src = Image.open(src)
im = calm_blues(_src.convert('RGBA') if _src.mode == 'RGBA' and np.array(_src)[..., 3].min() < 10 else cutout(_src))  # v5 já vem com transparência
V3 = 'v3' in src.name; V4 = 'v4' in src.name; V5 = 'v5' in src.name
# centros da base das torres dos cantos esquerdo/direito e o seu chão (px da pintura); v3 = castelo com topos planos (inclinação da base 0,51)
L, Rr, GY = (48, 1200, 860) if V5 else (115, 910, 624) if V4 else (128, 1415, 627) if V3 else (131, 1121, 790)
# v4: câmara do Gemini mais alta (base com inclinação 0,63 em vez de 0,50): achata-se a imagem na vertical por SQ para a base ficar 2:1
SQ = .5 / .6275 if V4 else 1.0   # v5 (torre de menagem simples, como no Stronghold): base 0,52, sem correção
# v3: sítios onde ficam os soldados (topo das torres, casa do portão, caminhos de ronda) e o Rei (terraço da torre de menagem), em px da pintura
STAND = {'rei': (885, 338), 't_frente': (815, 728), 't_esq': (128, 398), 't_dir': (1410, 398), 't_tras': (760, 135), 'portao': (495, 608),
         'm_fe2': (683, 700), 'm_fd1': (1050, 660), 'm_fe1': (270, 540), 'm_fd2': (1230, 570), 'm_te': (450, 345), 'm_td': (1185, 390)} if V3 else {}
if V5: STAND = {'rei': (620, 330), 't_frente': (630, 520), 't_esq': (230, 385), 't_dir': (1020, 375), 'portao': (440, 470), 'm_fe2': (530, 500),
                'm_fd1': (760, 490), 'm_fe1': (330, 430), 'm_fd2': (900, 430), 't_tras': (620, 230), 'm_te': (400, 300), 'm_td': (840, 300)}
elif V4: STAND = {'rei': (520, 225), 't_frente': (515, 632), 't_esq': (115, 378), 't_dir': (910, 380), 'portao': (365, 575), 'm_fe2': (440, 560),
                'm_fd1': (640, 610), 'm_fe1': (195, 495), 'm_fd2': (790, 525), 'm_te': (300, 352), 'm_td': (730, 350)}
s = 2 * 3 * 64 / (Rr - L) * .97     # largura da pegada 3x3 a 2x
im = im.resize((round(im.width * s), round(im.height * s * SQ)), Image.LANCZOS)
ax, ay = (L + Rr) / 2 * s, GY * s * SQ - 3 * 32   # canto de cima = canto esquerdo/direito sobe 96 px a 2x
stand = {k: [round((x * s - ax) / 2, 1), round((y * s * SQ - ay) / 2, 1)] for k, (x, y) in STAND.items()}  # px do jogo (1x) a partir da âncora
bb = im.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox(); im = im.crop(bb); ax -= bb[0]; ay -= bb[1]
im.save(out / 'centro_2.png'); af = out / 'anchors.json'; A = json.loads(af.read_text()) if af.exists() else {}
A['centro|2'] = [round(ax, 2), round(ay, 2), 3, 3]; af.write_text(json.dumps(A, indent=1)); print('centro_2', im.size, round(s, 3), A['centro|2'])
(out / 'castelo_stand.json').write_text(json.dumps(stand)); print('sitios', stand)
