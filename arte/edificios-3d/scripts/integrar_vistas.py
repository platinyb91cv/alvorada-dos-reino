# Vistas da câmara rodada pintadas à mão/IA (Kimi, Grok, ChatGPT…): junta-as ao atlas edificios-3d.webp como quadros <quadro>_rN.
# Entrada: imagens com fundo branco (ou transparente) chamadas <quadro>_r1/_r2/_r3 (.png/.jpg/.webp), ex.: casa_n2_r2.png
#   r1 = vista E (o lado que estava à direita-frente passa para a esquerda-frente), r2 = vista S (as traseiras), r3 = vista O.
# Cada imagem: tira o fundo a partir das bordas, recorta, ajusta a LARGURA à do quadro que já está no jogo (a pegada é quadrada,
# por isso o losango do chão fica do mesmo tamanho), alinha pelo fundo ao centro e herda a âncora desse quadro.
# Depois volta a empacotar o atlas e atualiza BLD3D_DATA no www/index.html.
# Uso: python3 integrar_vistas.py <pasta_das_imagens> <repo>   [ACERTAR_COR=1 aproxima a cor média à do quadro original]
import sys, os, io, json, hashlib, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageStat
src, repo = Path(sys.argv[1]), Path(sys.argv[2])
html_p = repo / 'www/index.html'; html = html_p.read_text(encoding='utf-8')
i = html.index('const BLD3D_DATA='); j = html.index('\n', i); data = json.loads(html[i + 17:html.index(';', i)])
atlas_p = repo / 'www/assets/edificios-extra' / data['file']; old = Image.open(atlas_p).convert('RGBA')
tiles = {n: (old.crop((x, y, x + w, y + h)), ax, ay) for n, (x, y, w, h, ax, ay) in data['frames'].items()}

def cutout(im):  # fundo claro ligado às bordas -> transparente (as imagens com alfa ficam como estão)
    if im.mode == 'RGBA' and im.getchannel('A').getextrema()[0] < 250: return im
    rgb = im.convert('RGB'); w, h = rgb.size; key = (255, 0, 255); m = rgb.copy()
    for p in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, 0), (w // 2, h - 1), (0, h // 2), (w - 1, h // 2)]:
        if sum(m.getpixel(p)) > 3 * 215: ImageDraw.floodfill(m, p, key, thresh=40)
    r, g, b = m.split()
    mask = ImageChops.multiply(ImageChops.multiply(r.point(lambda v: 255 if v == 255 else 0), g.point(lambda v: 255 if v == 0 else 0)), b.point(lambda v: 255 if v == 255 else 0))
    a = ImageChops.invert(mask).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(.7)); o = rgb.convert('RGBA'); o.putalpha(a); return o

def match_color(t, ref):  # média e contraste de cada canal (só píxeis opacos) iguais aos do quadro original
    def st(im):
        a = im.getchannel('A').point(lambda v: 255 if v > 128 else 0); s = ImageStat.Stat(im.convert('RGB'), mask=a); return s.mean, s.stddev
    (m1, s1), (m0, s0) = st(t), st(ref); r, g, b, a = t.split(); ch = []
    for k, c in enumerate((r, g, b)):
        k2 = s0[k] / max(1, s1[k]); ch.append(c.point(lambda v, k=k, k2=k2: max(0, min(255, round((v - m1[k]) * k2 + m0[k])))))
    return Image.merge('RGBA', (*ch, a))

done = []
for p in sorted(src.iterdir()):
    mt = re.match(r'^(.+)_r([123])\.(png|jpe?g|webp)$', p.name, re.I)
    if not mt: continue
    base, k = mt.group(1), mt.group(2)
    if base not in tiles: print('sem quadro original no atlas:', base, '(ignorado)'); continue
    ref, ax, ay = tiles[base]
    rb = ref.getchannel('A').point(lambda v: 255 if v > 30 else 0).getbbox(); rw = rb[2] - rb[0]
    c = cutout(Image.open(p)); cb = c.getchannel('A').point(lambda v: 255 if v > 30 else 0).getbbox(); c = c.crop(cb)
    s = rw / c.width; c = c.resize((max(1, round(c.width * s)), max(1, round(c.height * s))), Image.LANCZOS)
    if os.environ.get('ACERTAR_COR'): c = match_color(c, ref)
    # tela com a largura do original; o fundo do edifício novo assenta no fundo do original (âncora igual); se for mais alto, a tela cresce para cima
    top = rb[3] - c.height; H = ref.height - min(0, top); off = -min(0, top)
    t = Image.new('RGBA', (ref.width, H)); t.alpha_composite(c, (rb[0], top + off))
    tiles[f'{base}_r{k}'] = (t, ax, round(ay + off, 2)); done.append(f'{base}_r{k}'); print('ok', f'{base}_r{k}', t.size)
if not done: print('nenhuma imagem <quadro>_r1/_r2/_r3 encontrada'); sys.exit(1)
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
html = html[:i] + 'const BLD3D_DATA=' + json.dumps(data, separators=(',', ':')) + ';' + html[j:]; html_p.write_text(html, encoding='utf-8')
print('atlas', atlas.size, len(webp) // 1024, 'KB,', len(F), 'quadros; novos:', ', '.join(done))
