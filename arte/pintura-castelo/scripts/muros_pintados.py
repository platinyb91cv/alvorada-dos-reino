# Muralhas de pedra pintadas (fonte/muro_x_v3.png e muro_y_v3.png) -> www/assets/edificios-extra/muralhas-pintadas.webp + PWALL_DATA.
#
# Regras (pedido do Fabis): mesma escala em píxeis por casa para tudo (2x: um passo em x = (64,32) px, um passo em y = (-64,32),
# uma unidade de altura = 78,4 px); âncora pelo chão; eixos 2:1; segmentos retos sem torres nas pontas.
#
# As pinturas têm perspetiva (a ponta perto é ~1,3x maior) e eixos que não são 2:1. Por isso cada muro é endireitado por uma
# homografia que leva os 4 cantos da FACE DA FRENTE (medidos na pintura) ao retângulo certo no plano do jogo, com o caminho de
# ronda a H = 1,3. O comprimento sai da escala média ao longo do muro; depois ajusta-se (1-4 %) para que um número inteiro de
# ameias caiba em N casas: as N fatias de 1 casa (uma por posição, tx % N) emendam sem corte, também da última para a primeira.
# Fatias: coluna de 64 px (2x) por casa, centrada na casa, como as muralhas 3D. Pontas: "fim" = ponta visível (+x / +y) tirada da
# ponta verdadeira da pintura; "ini" = ponta escondida (-x / -y) recortada pela caixa do muro; "iso" = muro sozinho.
# Uso: python3 muros_pintados.py <repo> [pasta_provas]
import sys, json, io, hashlib, math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
repo = Path(sys.argv[1]); prov = Path(sys.argv[2]) if len(sys.argv) > 2 else None
H = 1.3; ZP2 = 2 * 64 / 2 ** .5 * math.cos(math.pi / 6); OV = 3; ZTOP = 2.3
def S(x, y, z=0.0): return np.array([64 * (x - y), 32 * (x + y) - ZP2 * z])
def homog(src, dst):  # matriz 3x3 que leva src -> dst (4 pares)
    A = []
    for (x, y), (u, v) in zip(src, dst):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y, -u], [0, 0, 0, x, y, 1, -v * x, -v * y, -v]]
    _, _, Vt = np.linalg.svd(np.array(A, float)); return Vt[-1].reshape(3, 3) / Vt[-1][-1]
def aplica(Hm, p): q = Hm @ np.array([p[0], p[1], 1.0]); return q[:2] / q[2]
def limpa_orla(im):  # orlas coloridas: píxeis meio transparentes levam a cor do vizinho opaco
    a = np.array(im.convert('RGBA')).astype(np.float32); al = a[..., 3]
    op = Image.fromarray(np.where(al > 250, 255, 0).astype('uint8'))
    rgb = Image.fromarray(a[..., :3].astype('uint8')); blur = np.array(rgb.filter(ImageFilter.GaussianBlur(2))).astype(np.float32)
    w = np.array(op.filter(ImageFilter.GaussianBlur(2))).astype(np.float32)[..., None] / 255
    edge = (al > 0) & (al < 250)
    fill = np.where(w > .05, blur / np.maximum(w, .05) * 1.0, a[..., :3])
    a[..., :3] = np.where(edge[..., None], np.clip(fill, 0, 255), a[..., :3]); a[..., 3] = np.where(al < 40, 0, al)
    return Image.fromarray(a.astype('uint8'))
# medidas na pintura (px da imagem): cantos da face da frente  [longe-baixo, longe-cima, perto-baixo, perto-cima], espessura
MUROS = {
  'x': dict(f='muro_x_v3.png', quad=[(33, 469), (33, 222), (1080, 1212), (1080, 890)], esp=.95),
  'y': dict(f='muro_y_v3.png', quad=[(1228, 482), (1228, 215), (160, 1213), (160, 900)], esp=.70, passo=1.0)}  # y: 7 merlões de trás a 64 px = 1 casa (contados); a deteção automática falha nos blocos baixos da frente
def mundo_quad(ax, L, esp):  # mesmos cantos no mundo: o muro acaba em 0 (ponta perto = +x ou +y) e vai até -L; frente a +esp/2
    h = esp / 2
    if ax == 'x': return [S(-L, h), S(-L, h, H), S(0, h), S(0, h, H)]
    return [S(h, -L), S(h, -L, H), S(h, 0), S(h, 0, H)]
def endireita(ax, L):
    m = MUROS[ax]; im = limpa_orla(Image.open(repo / 'arte/pintura-castelo/fonte' / m['f']))
    dst = mundo_quad(ax, L, m['esp']); Hf = homog(m['quad'], dst)
    W0, H0 = im.size; cs = [aplica(Hf, p) for p in [(0, 0), (W0, 0), (0, H0), (W0, H0)]]
    x0 = math.floor(min(c[0] for c in cs)) - 4; y0 = math.floor(min(c[1] for c in cs)) - 4; x1 = math.ceil(max(c[0] for c in cs)) + 4; y1 = math.ceil(max(c[1] for c in cs)) + 4
    T = np.array([[1, 0, -x0], [0, 1, -y0], [0, 0, 1.0]]) @ Hf; Hi = np.linalg.inv(T); Hi /= Hi[2, 2]
    out = im.transform((x1 - x0, y1 - y0), Image.PERSPECTIVE, tuple(Hi.flatten()[:8]), Image.BICUBIC)
    return out, np.array([x0, y0], float)  # píxel (u,v) da saída = ponto de ecrã (u+x0, v+y0)
def periodo(out, org, ax, L, esp):  # passo das ameias (em casas): inícios dos merlões no topo da silhueta (fila de trás), sem a inclinação
    a = np.array(out)[..., 3] > 128; cols = np.where(a.any(0))[0]; us = np.arange(cols[0] + 20, cols[-1] - 20)
    top = np.array([np.argmax(a[:, u]) for u in us], float); top -= np.polyval(np.polyfit(us, top, 1), us)
    m = top < -6; st = [us[i] for i in range(1, len(us)) if m[i] and not m[i - 1]]; d = [x for x in np.diff(st) if x > 20]
    return float(np.mean(d)) / 64.0   # 64 px de ecrã (2x) = 1 casa ao longo de qualquer dos eixos
def caixa(ax, a0, a1, esp, org):  # envolvente no ecrã de uma caixa do muro entre a0 e a1 ao longo do eixo
    h = esp / 2 + .05; P = []
    for t in (a0, a1):
        for s in (-h, h):
            for z in (0, ZTOP): P.append((S(t, s, z) if ax == 'x' else S(s, t, z)) - org)
    cr = lambda o, p, q: (p[0] - o[0]) * (q[1] - o[1]) - (p[1] - o[1]) * (q[0] - o[0])
    P = sorted(tuple(map(float, p)) for p in P); hull, up = [], []
    for p in P:
        while len(hull) >= 2 and cr(hull[-2], hull[-1], p) <= 0: hull.pop()
        hull.append(p)
    for p in reversed(P):
        while len(up) >= 2 and cr(up[-2], up[-1], p) <= 0: up.pop()
        up.append(p)
    return [tuple(p) for p in hull[:-1] + up[:-1]]
def recorta(out, org, ax, t0, esp, extra_l=0, extra_r=0, clip=None):
    """Coluna da casa que vai de t0 a t0+1 ao longo do eixo (centro na linha do meio do muro). Âncora = canto de cima da casa."""
    c = S(t0 + .5, 0) if ax == 'x' else S(0, t0 + .5)
    u0 = int(round(c[0] - org[0] - 32 - OV - extra_l)); u1 = int(round(c[0] - org[0] + 32 + OV + extra_r))
    im = out.crop((u0, 0, u1, out.height))
    if clip is not None:
        m = Image.new('L', out.size, 0); ImageDraw.Draw(m).polygon(caixa(ax, clip[0], clip[1], esp, org), fill=255)
        a = np.array(im); a[..., 3] = np.minimum(a[..., 3], np.array(m.crop((u0, 0, u1, out.height)))); im = Image.fromarray(a)
    top = (S(t0, -.5) if ax == 'x' else S(-.5, t0)) - org   # canto de cima da casa (o centro da base fica 32 px abaixo)
    bb = im.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox(); im = im.crop((0, bb[1], im.width, bb[3]))
    return im, (top[0] - u0, top[1] - bb[1])
def junta(esq, dir_):  # muro sozinho: metade esquerda de uma ponta + metade direita da outra, unidas na coluna do meio da casa
    (a, (ax_a, ay_a)), (b, (ax_b, ay_b)) = esq, dir_
    L_ = max(ax_a, ax_b); R_ = max(a.width - ax_a, b.width - ax_b); T_ = max(ay_a, ay_b); B_ = max(a.height - ay_a, b.height - ay_b)
    out = Image.new('RGBA', (int(math.ceil(L_ + R_)), int(math.ceil(T_ + B_))))
    la = a.crop((0, 0, int(round(ax_a)), a.height)); rb = b.crop((int(round(ax_b)), 0, b.width, b.height))
    out.alpha_composite(la, (int(round(L_ - ax_a)), int(round(T_ - ay_a)))); out.alpha_composite(rb, (int(round(L_)), int(round(T_ - ay_b))))
    return out, (L_, T_)
tiles, info = {}, {}
for ax in ('x', 'y'):
    m = MUROS[ax]; q = m['quad']
    # comprimento pela escala média ao longo do muro (lado longe e lado perto), sem esticar a altura
    def esc(hpx, sl_a, sl_b): kv = H * ZP2 / hpx; return kv * (abs(sl_a) + abs(sl_b))
    sl_f = (q[2][1] - q[0][1]) / (q[2][0] - q[0][0])
    L0 = abs(q[2][0] - q[0][0]) * (esc(q[1][1] - q[0][1] if False else q[0][1] - q[1][1], sl_f, .6) + esc(q[2][1] - q[3][1], sl_f, .6)) / 2 / 64
    out, org = endireita(ax, L0); p = m.get('passo') or periodo(out, org, ax, L0, m['esp'])
    best = min(((n, k) for n in (1, 2, 3, 4) for k in range(1, 9)), key=lambda nk: (abs(nk[0] / (nk[1] * p) - 1) + .002 * nk[0]))
    N, K = best; alvo = N / K; L = L0
    for _ in range(0 if m.get('passo') else 4):  # ajusta o comprimento até o passo medido bater certo com N casas / K ameias
        L *= alvo / p; out, org = endireita(ax, L); p = periodo(out, org, ax, L, m['esp'])
    if m.get('passo'): L = L0 * alvo / p; out, org = endireita(ax, L)
    f = L / L0; p2 = p
    mid = -L / 2 - N / 2; esp = m['esp']
    for j in range(N):
        t0 = math.floor(mid) + j
        tiles[f'{ax}_mid_{j}'] = recorta(out, org, ax, t0, esp)
    # ponta visível: a última casa da pintura (o muro acaba em 0); a face da ponta passa da coluna para o lado da frente
    # ponta escondida (-x / -y): a ponta verdadeira do lado longe da pintura (recortar pela caixa deixava passar ameias de trás)
    if ax == 'x':
        tiles['x_fim'] = recorta(out, org, ax, -1, esp, extra_r=64); tiles['x_ini'] = recorta(out, org, ax, -L, esp, extra_l=64)
        tiles['x_iso'] = junta(tiles['x_ini'], tiles['x_fim'])
    else:
        tiles['y_fim'] = recorta(out, org, ax, -1, esp, extra_l=64); tiles['y_ini'] = recorta(out, org, ax, -L, esp, extra_r=64)
        tiles['y_iso'] = junta(tiles['y_fim'], tiles['y_ini'])
    info[ax] = dict(N=N, ameias=K, passo_medido=round(p, 3), passo_final=round(p2, 3), esticado=round(f, 3), comprimento=round(L, 2), espessura=esp)
    if prov: out.save(prov / f'endireitado_{ax}.png')
    print(ax, info[ax])
order = sorted(tiles, key=lambda n: -tiles[n][0].height); AW = 1024; gap = 2; x = y = gap; row = 0; place = {}
for n in order:
    w, h = tiles[n][0].size
    if x + w + gap > AW: x = gap; y += row + gap; row = 0
    place[n] = (x, y); x += w + gap; row = max(row, h)
atlas = Image.new('RGBA', (AW, y + row + gap)); F = {}
for n, (t, (ax_, ay_)) in tiles.items():
    px_, py_ = place[n]; atlas.paste(t, (px_, py_)); F[n] = [px_, py_, t.width, t.height, round(ax_, 2), round(ay_, 2)]
buf = io.BytesIO(); atlas.save(buf, 'WEBP', lossless=True, method=6); webp = buf.getvalue()
(repo / 'www/assets/edificios-extra/muralhas-pintadas.webp').write_bytes(webp)
meta = {'file': 'muralhas-pintadas.webp', 'scale': 2, 'atlasSha256': hashlib.sha256(webp).hexdigest(), 'walk': H, 'nx': info['x']['N'], 'ny': info['y']['N'],
        'espX': info['x']['espessura'], 'espY': info['y']['espessura'], 'frames': dict(sorted(F.items()))}
html_p = repo / 'www/index.html'; html = html_p.read_text(); line = 'const PWALL_DATA=' + json.dumps(meta, separators=(',', ':')) + ';'
if 'const PWALL_DATA=' in html: i = html.index('const PWALL_DATA='); j = html.index('\n', i); html = html[:i] + line + html[j:]
else: i = html.index('const WALL3D_DATA='); html = html[:i] + line + '\n' + html[i:]
html_p.write_text(html)
(repo / 'arte/pintura-castelo/muros_medidas.json').write_text(json.dumps(info, indent=1, ensure_ascii=False))
print(atlas.size, len(webp) // 1024, 'KB', len(F), 'quadros')
