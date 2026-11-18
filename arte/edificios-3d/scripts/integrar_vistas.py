# Vistas da câmara rodada pintadas à mão/IA (Kimi, Grok, ChatGPT…): junta-as ao atlas edificios-3d.webp como quadros <quadro>_rN.
# Entrada: imagens com fundo branco (ou transparente) chamadas <quadro>_r1/_r2/_r3 (.png/.jpg/.webp), ex.: casa_n2_r2.png
#   r1 = vista E (o lado que estava à direita-frente passa para a esquerda-frente), r2 = vista S (as traseiras), r3 = vista O.
# Cada imagem: tira o fundo a partir das bordas, recorta, ajusta a LARGURA à do quadro que já está no jogo (a pegada é quadrada,
# por isso o losango do chão fica do mesmo tamanho), alinha pelo fundo ao centro e herda a âncora desse quadro.
# Vai para o atlas das vistas www/assets/edificios-extra/edificios-3d-vistas-N.webp (páginas até 2048×2048) e BLD3DV_DATA no www/index.html (o principal não muda).
# Ou uma folha com as duas vistas lado a lado: <quadro>_folha.png (esquerda = traseiras _r2, direita = vista E _r1).
# Uso: python3 integrar_vistas.py <pasta_das_imagens> <repo>   [ACERTAR_COR=1 aproxima a cor média à do quadro original] [EXCLUIR=quadro_rN,...]
import sys, os, io, json, hashlib, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageStat
src, repo = Path(sys.argv[1]), Path(sys.argv[2])
EXCL = set(filter(None, os.environ.get('EXCLUIR', '').split(',')))  # vistas que saíram mal (ex.: EXCLUIR=doca_0_r2,oficina_n3_r2): ficam de fora
html_p = repo / 'www/index.html'; html = html_p.read_text(encoding='utf-8')
i = html.index('const BLD3D_DATA='); data = json.loads(html[i + 17:html.index(';', i)])
atlas_p = repo / 'www/assets/edificios-extra' / data['file']; old = Image.open(atlas_p).convert('RGBA')
# quadros originais (só para ler tamanho, âncora e cor); as vistas novas vão para um atlas À PARTE (edificios-3d-vistas.webp,
# BLD3DV_DATA) para o atlas principal não passar de 2048 px
base_tiles = {n: (old.crop((x, y, x + w, y + h)), ax, ay) for n, (x, y, w, h, ax, ay) in data['frames'].items()}
iv = html.index('const BLD3DV_DATA='); jv = html.index('\n', iv); vdata = json.loads(html[iv + 18:html.rindex(';', iv, jv)])
ADIR = repo / 'www/assets/edificios-extra'
tiles = {}  # vistas já integradas (páginas edificios-3d-vistas-N.webp, cada uma até 2048×2048)
pages = [Image.open(ADIR / f).convert('RGBA') for f in vdata.get('files', [])]
for n, fr in vdata.get('frames', {}).items():
    x, y, w, h, ax, ay, pg = fr; tiles[n] = (pages[pg].crop((x, y, x + w, y + h)), ax, ay)

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

# folha do Grok com DUAS vistas lado a lado: <quadro>_folha.png -> esquerda = traseiras (_r2), direita = vista E (_r1)
def split_sheet(path):
    c = cutout(Image.open(path)); a = c.getchannel('A').point(lambda v: 255 if v > 30 else 0); w, h = a.size
    cols = [any(a.getpixel((x, y)) for y in range(0, h, 2)) for x in range(w)]
    segs = []; x = 0
    while x < w:
        if cols[x]:
            x0 = x
            while x < w and cols[x]: x += 1
            segs.append((x0, x))
        x += 1
    segs = [s for s in segs if s[1] - s[0] > w * .08]  # ignora salpicos
    if len(segs) < 2:  # sem coluna vazia entre os dois: corta ao meio
        segs = [(0, w // 2), (w // 2, w)]
    segs = sorted(sorted(segs, key=lambda s: s[0] - s[1])[:2])
    return [c.crop((x0, 0, x1, h)) for x0, x1 in segs]
SHEETS = {}
for p in sorted(src.iterdir()):
    mt = re.match(r'^(.+)_folha\.(png|jpe?g|webp)$', p.name, re.I)
    if mt:
        L, Rr = split_sheet(p); SHEETS[mt.group(1) + '_r2'] = L; SHEETS[mt.group(1) + '_r1'] = Rr; print('folha', p.name, '->', mt.group(1) + '_r2 (esq.),', mt.group(1) + '_r1 (dir.)')
done = []
items = [(p.name, p) for p in sorted(src.iterdir())] + [(n + '.png', im) for n, im in SHEETS.items()]
for name, p in items:
    mt = re.match(r'^(.+)_r([123])\.(png|jpe?g|webp)$', name, re.I)
    if not mt: continue
    base, k = mt.group(1), mt.group(2)
    if f'{base}_r{k}' in EXCL: print('excluída:', f'{base}_r{k}'); continue
    if base not in base_tiles: print('sem quadro original no atlas:', base, '(ignorado)'); continue
    ref, ax, ay = base_tiles[base]
    rb = ref.getchannel('A').point(lambda v: 255 if v > 30 else 0).getbbox(); rw = rb[2] - rb[0]
    c = p if isinstance(p, Image.Image) else cutout(Image.open(p)); cb = c.getchannel('A').point(lambda v: 255 if v > 30 else 0).getbbox(); c = c.crop(cb)
    # escala: a menor entre "mesma largura" e "mesma altura" do original — assim uma vista que perde o pátio/bancas (traseiras de
    # um mercado, de uma oficina) não fica gigante por esticar a casa à largura do lote todo
    rh = rb[3] - rb[1]; s = min(rw / c.width, rh / c.height); c = c.resize((max(1, round(c.width * s)), max(1, round(c.height * s))), Image.LANCZOS)
    if os.environ.get('ACERTAR_COR'): c = match_color(c, ref)
    # tela com a largura do original; o fundo do edifício novo assenta no fundo do original (âncora igual); se for mais alto, a tela cresce para cima
    top = rb[3] - c.height; H = ref.height - min(0, top); off = -min(0, top)
    t = Image.new('RGBA', (ref.width, H)); t.alpha_composite(c, (rb[0] + (rw - c.width) // 2, top + off))  # centrada no original
    tiles[f'{base}_r{k}'] = (t, ax, round(ay + off, 2)); done.append(f'{base}_r{k}'); print('ok', f'{base}_r{k}', t.size)
if not done: print('nenhuma imagem <quadro>_r1/_r2/_r3 encontrada'); sys.exit(1)
order = sorted(tiles, key=lambda n: -tiles[n][0].height); AW = AH = 2048; gap = 2; place = {}; npg = 0; x = y = gap; row = 0; used = [0]
for n in order:
    w, h = tiles[n][0].size
    if x + w + gap > AW: x = gap; y += row + gap; row = 0
    if y + h + gap > AH: npg += 1; x = y = gap; row = 0; used.append(0)
    place[n] = (x, y, npg); x += w + gap; row = max(row, h); used[npg] = max(used[npg], y + h + gap)
for f in vdata.get('files', []): (ADIR / f).unlink(missing_ok=True)
F = {}; files = []; shas = []; total = 0
for pg in range(npg + 1):
    atlas = Image.new('RGBA', (AW, used[pg]))
    for n, (t, ax, ay) in tiles.items():
        px_, py_, p_ = place[n]
        if p_ == pg: atlas.paste(t, (px_, py_)); F[n] = [px_, py_, t.width, t.height, ax, ay, pg]
    buf = io.BytesIO(); atlas.save(buf, 'WEBP', lossless=True, quality=100, method=6); webp = buf.getvalue()
    fn = f'edificios-3d-vistas-{pg + 1}.webp'; (ADIR / fn).write_bytes(webp); files.append(fn); shas.append(hashlib.sha256(webp).hexdigest()); total += len(webp)
vdata = {'files': files, 'scale': data['scale'], 'sha256': shas, 'frames': dict(sorted(F.items()))}
html = html[:iv] + 'const BLD3DV_DATA=' + json.dumps(vdata, separators=(',', ':')) + ';' + html[jv:]; html_p.write_text(html, encoding='utf-8')
print('atlas das vistas:', len(files), 'página(s),', total // 1024, 'KB,', len(F), 'quadros; novos:', ', '.join(done))
