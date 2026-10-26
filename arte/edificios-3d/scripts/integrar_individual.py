# Edifícios repintados um a um (Gemini/ChatGPT, fundo branco): tira o fundo (a partir das bordas), ajusta a largura à do render 3D
# e alinha pelo fundo ao centro, para a âncora no mapa ficar igual. Ficheiros: <nome>_pintada.(png|jpg), ex. casa_1_pintada.png
# Uso: python3 integrar_individual.py <pasta_pinturas> <pasta_renders> <pasta_saida>
import sys, shutil, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageChops
pin, src, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]); out.mkdir(parents=True, exist_ok=True)
for f in src.glob('*'):
    if not (out / f.name).exists(): shutil.copy(f, out / f.name)
def cutout(im):  # fundo branco ligado às bordas -> transparente
    rgb = im.convert('RGB'); w, h = rgb.size; key = (255, 0, 255)
    m = rgb.copy()
    for p in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, 0), (w // 2, h - 1), (0, h // 2), (w - 1, h // 2)]:
        if sum(m.getpixel(p)) > 3 * 225: ImageDraw.floodfill(m, p, key, thresh=40)
    r, g, b = m.split(); mask = ImageChops.multiply(ImageChops.multiply(r.point(lambda v: 255 if v == 255 else 0), g.point(lambda v: 255 if v == 0 else 0)), b.point(lambda v: 255 if v == 255 else 0))
    a = ImageChops.invert(mask).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(.7)); o = rgb.convert('RGBA'); o.putalpha(a); return o
A = json.loads((out / 'anchors.json').read_text())
for p in sorted(list(pin.glob('*_pintada.png')) + list(pin.glob('*_pintada.jpg')) + list(pin.glob('*_pintada.jpeg'))):
    n = p.stem.replace('_pintada', ''); orig = Image.open(src / f'{n}.png').convert('RGBA')
    ob = orig.getchannel('A').point(lambda v: 255 if v > 30 else 0).getbbox(); ow = ob[2] - ob[0]
    c = cutout(Image.open(p)); cb = c.getchannel('A').point(lambda v: 255 if v > 30 else 0).getbbox(); c = c.crop(cb)
    s = ow / c.width; c = c.resize((max(1, round(c.width * s)), max(1, round(c.height * s))), Image.LANCZOS)
    res = Image.new('RGBA', orig.size); x = ob[0]; y = ob[3] - c.height
    if y < 0:  # mais alto que o render: a tela cresce para cima e a âncora desce o mesmo
        res = Image.new('RGBA', (orig.width, orig.height - y)); k = n.replace('_', '|', 1); A[k][1] += -y; y = 0
    res.alpha_composite(c, (x, y)); res.save(out / f'{n}.png'); print('ok', n, c.size)
(out / 'anchors.json').write_text(json.dumps(A, indent=1))
