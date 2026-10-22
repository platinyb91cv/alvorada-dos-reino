# Edifícios pintados no Gemini (só texto, fundo branco, vista isométrica sobre o terreno da base): tira o fundo, encontra as pontas
# esquerda/direita do losango de terra e encaixa-o na base do edifício no mapa (mesma escala 2x dos renders), calculando a âncora
# (canto de cima da casa). Os azuis pouco saturados (ardósia, sombras) perdem cor para não ganharem a cor da equipa.
# Uso: python3 integrar_gemini.py <pasta_gemini> <pasta_renders_3d> <pasta_saida>
import sys, json, shutil, colorsys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import numpy as np
FOOT = {'casa': (2, 2), 'armazem': (2, 2), 'ferreiro': (2, 2), 'doca': (2, 2), 'torre': (2, 2), 'quartel': (3, 3), 'arquearia': (3, 3), 'estabulo': (3, 3),
        'templo': (3, 3), 'mercado': (3, 3), 'oficina': (3, 3), 'centro': (3, 3), 'maravilha': (4, 4)}
gem, src, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]); out.mkdir(parents=True, exist_ok=True)
for f in src.glob('*'):
    if not (out / f.name).exists(): shutil.copy(f, out / f.name)
A = json.loads((out / 'anchors.json').read_text())
def cutout(im):
    rgb = im.convert('RGB'); w, h = rgb.size; m = rgb.copy(); key = (255, 0, 255)
    for p in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, 0), (w // 2, h - 1), (0, h // 2), (w - 1, h // 2)]:
        if sum(m.getpixel(p)) > 3 * 215 and m.getpixel(p) != key: ImageDraw.floodfill(m, p, key, thresh=38)
    a = np.array(m); bg = (a[..., 0] == 255) & (a[..., 1] == 0) & (a[..., 2] == 255)
    alpha = Image.fromarray(np.where(bg, 0, 255).astype('uint8')).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(.8))
    o = rgb.convert('RGBA'); o.putalpha(alpha); return o
def calm_blues(im):  # só o azul vivo (bandeiras) fica azul
    a = np.array(im).astype(np.float32) / 255; r, g, b = a[..., 0], a[..., 1], a[..., 2]
    M = a[..., :3].max(-1); m = a[..., :3].min(-1); s = np.where(M > 0, (M - m) / np.maximum(M, 1e-6), 0)
    blue = (b >= r) & (b >= g) & (s > .1) & (s < .5)
    gray = (r + g + b) / 3; k = np.where(blue, .25, 1)[..., None]
    a[..., :3] = gray[..., None] + (a[..., :3] - gray[..., None]) * k
    return Image.fromarray((a * 255).clip(0, 255).astype('uint8'))
for p in sorted(gem.glob('*.png')):
    n = p.stem; t, age = n.rsplit('_', 1); w, h = FOOT[t]
    im = calm_blues(cutout(Image.open(p))); al = np.array(im.getchannel('A')) > 128
    cols = np.where(al.any(0))[0]; xl, xr = cols[0], cols[-1]
    yl = np.where(al[:, xl])[0].mean(); yr = np.where(al[:, xr])[0].mean()
    s = (w + h) * 64 / (xr - xl + 1) * .97
    im2 = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    ax = xl * s + h * 64 * .97; ay = ((yl * s - h * 32 * .97) + (yr * s - w * 32 * .97)) / 2
    bb = im2.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox(); im2 = im2.crop(bb); ax -= bb[0]; ay -= bb[1]
    im2.save(out / f'{n}.png'); A[f'{t}|{age}'] = [round(float(ax), 2), round(float(ay), 2), w, h]; print('ok', n, im2.size, round(float(ax)), round(float(ay)))
(out / 'anchors.json').write_text(json.dumps(A, indent=1))
