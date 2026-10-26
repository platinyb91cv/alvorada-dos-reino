# Casa do portão pintada (folha de 4 vistas) -> atlas www/assets/edificios-extra/portoes-pintados.webp + PGATE_DATA no index.html.
# A vista "lado direito" é a do portão ao longo de x; a direção y é o espelho. As torres ficam nas casas de muralha ao lado
# (centros em x=-0,5 e x=1,5) e o meio do portão no centro da casa do portão. Ajusta-se a perspetiva da pintura (mais de frente)
# à do jogo com escala + cisalhamento vertical (as verticais continuam verticais). O chão pintado sai; o estado 0 (fechado)
# leva portas e grade desenhadas no arco.
# Uso: python3 portao_pintado.py <folha.png> <repo> [pasta_provas]
import sys, json, io, hashlib
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, str(Path(__file__).resolve().parent)); from tom_muro import tom_muro  # pedra no cinzento das muralhas (TOM=original para manter)
src, repo = Path(sys.argv[1]), Path(sys.argv[2]); prov = Path(sys.argv[3]) if len(sys.argv) > 3 else None
def cutout(im):
    rgb = im.convert('RGB'); w, h = rgb.size; m = rgb.copy(); key = (255, 0, 255)
    for p in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, 0), (w // 2, h - 1), (0, h // 2), (w - 1, h // 2)]:
        if sum(m.getpixel(p)) > 3 * 215 and m.getpixel(p) != key: ImageDraw.floodfill(m, p, key, thresh=38)
    a = np.array(m); bg = (a[..., 0] == 255) & (a[..., 1] == 0) & (a[..., 2] == 255)
    bg |= (a[..., :3].min(-1) > 246)   # branco preso entre as pontas das bandeiras
    o = rgb.convert('RGBA'); o.putalpha(Image.fromarray(np.where(bg, 0, 255).astype('uint8'))); return o
V2 = 'v2' in src.name
im = cutout(Image.open(src).crop((768, 0, 1532, 472)) if not V2 else Image.open(src))
a = np.array(im); H, W = a.shape[:2]; yy, xx = np.mgrid[0:H, 0:W]
# linha do chão (base das torres e da casa do portão), medida na pintura; tudo abaixo dela é chão pintado e sai
LX = [130, 152, 190, 275, 315, 322, 405, 450, 470, 560, 610, 632, 650]
LY = [330, 352, 356, 358, 348, 364, 396, 400, 446, 452, 446, 418, 405]
base = np.interp(xx, LX, LY)
keep = (yy < base) & ~((xx < 150) & (yy > 250)) & ~((xx > 636) & (yy > 280))
if V2: keep = np.ones_like(keep)  # a v2 já vem sem chão
al = np.array(Image.fromarray(np.where(keep, a[..., 3], 0).astype('uint8')).filter(ImageFilter.GaussianBlur(1.0)))
a[..., 3] = np.minimum(a[..., 3], al); im = tom_muro(Image.fromarray(a), val=1.0 if V2 else .86)
# portas fechadas + grade em baixo, desenhadas no arco (para o estado 0)
def fechado_v1(img):
    o = img.copy(); d = ImageDraw.Draw(o, 'RGBA')
    L0, L1, R0, R1, AP = (322, 364), (322, 288), (405, 396), (405, 302), (363, 258)
    arco = [L0, L1, (330, 272), (343, 262), AP, (384, 266), (397, 280), R1, R0]
    d.polygon(arco, fill=(92, 58, 30, 255))
    for k in range(1, 7):  # tábuas
        t = k / 7; x = L0[0] + (R0[0] - L0[0]) * t; yb = L0[1] + (R0[1] - L0[1]) * t
        d.line([(x, yb), (x, 262 + abs(t - .5) * 34)], fill=(54, 32, 14, 255), width=2)
    for f in (.32, .7):     # ferragens
        d.line([(L0[0], L0[1] - (L0[1] - L1[1]) * f), (R0[0], R0[1] - (R0[1] - R1[1]) * f)], fill=(40, 38, 36, 255), width=3)
    d.line([((L0[0] + R0[0]) / 2, (L0[1] + R0[1]) / 2), ((L0[0] + R0[0]) / 2, 262)], fill=(36, 22, 10, 255), width=3)
    for k in range(0, 9):   # grade
        t = k / 8; x = L0[0] + (R0[0] - L0[0]) * t
        d.line([(x, 266 + abs(t - .5) * 30), (x, 290 + abs(t - .5) * 26 + t * 12)], fill=(30, 30, 32, 230), width=2)
    return o
def fechado_v2(img):  # grade de ferro em baixo no arco (as portas ficam abertas para fora)
    o = img.copy(); d = ImageDraw.Draw(o, 'RGBA')
    L0, R0 = (465, 880), (625, 965); top = lambda x: 700 - 40 * np.sin(np.pi * min(1, max(0, (x - 465) / 160))) + (x - 465) * .28
    for k in range(9):
        x = 465 + 160 * k / 8; yb = L0[1] + (R0[1] - L0[1]) * k / 8
        d.line([(x, top(x)), (x, yb - 4)], fill=(38, 38, 42, 255), width=5); d.polygon([(x - 4, yb - 6), (x + 4, yb - 6), (x, yb + 6)], fill=(30, 30, 34, 255))
    for f in (.15, .38, .6, .82):
        d.line([(465, 700 + (880 - 700) * f), (625, 745 + (965 - 745) * f)], fill=(44, 44, 48, 255), width=5)
    return o
fechado = fechado_v2 if V2 else fechado_v1
SX, SY = (.33, .37) if V2 else (.43, .55)                     # escala horizontal / vertical (a casa do portão fica à altura das muralhas, ~1,3)
T0, T1 = ((235, 668), (1010, 1108)) if V2 else ((220, 330), (532, 415))       # centros da base das torres na pintura
SPAN = 2.0 if V2 else 1.0             # distância (casas) de cada torre ao centro do portão
K = (.5 * SX * (T1[0] - T0[0]) - SY * (T1[1] - T0[1])) / (T1[0] - T0[0])   # cisalhamento para a muralha descer 1:2
assert abs(SX * (T1[0] - T0[0]) - 2 * SPAN * 64) < 4, 'torres fora das casas'
def warp(img):
    ow, oh = round(W * SX), round(H * SY + K * W) + 2
    return img.transform((ow, oh), Image.AFFINE, (1 / SX, 0, 0, -K / (SX * SY), 1 / SY, 0), Image.BICUBIC)
MID = ((T0[0] + T1[0]) / 2, (T0[1] + T1[1]) / 2)
AX, AY = MID[0] * SX, MID[1] * SY + K * MID[0] - 32   # canto de cima da casa do portão (centro = +32 px a 2x)
frames, tiles = {}, {}
for st, img in ((0, fechado(im)), (1, im), (2, im)):
    w = warp(img)
    for d in ('x', 'y'):
        t = w if d == 'x' else w.transpose(Image.FLIP_LEFT_RIGHT); ax = AX if d == 'x' else t.width - AX
        bb = t.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox(); t = t.crop(bb)
        tiles[f'pedra_{d}_{st}'] = (t, ax - bb[0], AY - bb[1])
order = sorted(tiles, key=lambda n: -tiles[n][0].height); AW = 1024; gap = 2; x = y = gap; row = 0
atlas_parts = []
for n in order:
    t = tiles[n][0]
    if x + t.width + gap > AW: x = gap; y += row + gap; row = 0
    atlas_parts.append((n, x, y)); x += t.width + gap; row = max(row, t.height)
atlas = Image.new('RGBA', (AW, y + row + gap))
for n, px, py in atlas_parts:
    t, ax, ay = tiles[n]; atlas.paste(t, (px, py)); frames[n] = [px, py, t.width, t.height, round(ax, 2), round(ay, 2)]
buf = io.BytesIO(); atlas.save(buf, 'WEBP', lossless=True, method=6); webp = buf.getvalue()
(repo / 'www/assets/edificios-extra/portoes-pintados.webp').write_bytes(webp)
# alturas do caminho de ronda (soldados): casa do portão e torres, em unidades do jogo
ZP2 = 2 * 64 / 2 ** .5 * .8660254
meta = {'file': 'portoes-pintados.webp', 'scale': 2, 'atlasSha256': hashlib.sha256(webp).hexdigest(), 'walk': round((MID[1] - (610 if V2 else 176)) * SY / ZP2, 2), 'span': SPAN,
        'towerTop': round((T1[1] - (640 if V2 else 140)) * SY / ZP2, 2), 'rTorre': round((300 if V2 else 150) * SX / (2 * 64 * 2 ** .5), 2), 'frames': dict(sorted(frames.items()))}
html = (repo / 'www/index.html').read_text(); line = 'const PGATE_DATA=' + json.dumps(meta, separators=(',', ':')) + ';'
if 'const PGATE_DATA=' in html:
    i = html.index('const PGATE_DATA='); j = html.index('\n', i); html = html[:i] + line + html[j:]
else:
    i = html.index('const GATE3D_DATA='); html = html[:i] + line + '\n' + html[i:]
(repo / 'www/index.html').write_text(html)
if prov:
    prov.mkdir(parents=True, exist_ok=True)
    for n in ('pedra_x_0', 'pedra_x_2', 'pedra_y_2'): tiles[n][0].save(prov / f'{n}.png')
print(atlas.size, len(webp), 'walk', meta['walk'], 'torre', meta['towerTop'], 'K', round(K, 3))
