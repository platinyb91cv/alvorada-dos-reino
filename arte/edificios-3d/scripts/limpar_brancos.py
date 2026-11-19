# Limpa o fundo branco que ficou PRESO dentro das vistas pintadas (Grok): entre a grua e a parede da oficina, debaixo do alpendre
# da arquearia, nas aberturas do topo das torres e do campanário… O cutout do integrar_vistas.py só tira o fundo ligado às bordas;
# estas zonas fechadas ficavam brancas no jogo com a câmara rodada.
# Regra: manchas fechadas de branco/cinza muito claro, quase sem cor e lisas (sem textura) passam a transparentes, com uma orla de
# 1 px para não deixar halo. O Mercado fica de fora (o toldo da banca é branco liso de propósito).
# Uso: python3 limpar_brancos.py <repo>   (reescreve as páginas edificios-3d-vistas-N.webp e o BLD3DV_DATA no www/index.html)
import sys, io, json, hashlib
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage
repo = Path(sys.argv[1]); html_p = repo / 'www/index.html'; html = html_p.read_text(encoding='utf-8')
iv = html.index('const BLD3DV_DATA='); jv = html.index('\n', iv); v = json.loads(html[iv + 18:html.rindex(';', iv, jv)])
A = repo / 'www/assets/edificios-extra'
pages = [np.array(Image.open(A / f).convert('RGBA')) for f in v['files']]
FORA = ('mercado',)
import os; DRY = bool(os.environ.get('DRY')); NOME = ''

def limpa(t):
    a = t[..., 3].astype(int); rgb = t[..., :3].astype(int); mx = rgb.max(-1); mn = rgb.min(-1)
    m = (a > 200) & (mn > 200) & (mx - mn < 20)
    lab, k = ndimage.label(m); out = np.zeros_like(m); n = 0
    for c in range(1, k + 1):
        s = lab == c; sz = int(s.sum())
        if sz < 10: continue
        L = rgb[s].mean(-1)
        # grande e lisa (fundo preso atrás de colunas/grua) ou pequena e quase branca pura (aberturas de torre e campanário,
        # com a orla suavizada); o resto tem textura: é parede/tecido pintado, não fundo
        if not ((L.min() > 212 and L.std() <= 6) or (sz < 80 and L.mean() >= 238)): continue
        if DRY: print('  ', NOME, sz, round(L.mean()), round(L.std(), 1))
        out |= s; n += sz
    if not n: return 0
    halo = ndimage.binary_dilation(out, iterations=1) & ~out & (mn > 180) & (a > 0)
    t[out, 3] = 0; t[halo, 3] = (t[halo, 3] * .35).astype(np.uint8)
    return n

tot = {}
for name, (x, y, w, h, ax, ay, pg) in v['frames'].items():
    if name.startswith(FORA): continue
    NOME = name; t = pages[pg][y:y + h, x:x + w]; n = limpa(t)
    if n: tot[name] = n
if DRY: sys.exit(0)
files, shas = [], []
for f, p in zip(v['files'], pages):
    buf = io.BytesIO(); Image.fromarray(p).save(buf, 'WEBP', lossless=True, quality=100, method=6); b = buf.getvalue()
    (A / f).write_bytes(b); files.append(f); shas.append(hashlib.sha256(b).hexdigest())
v['sha256'] = shas
html = html[:iv] + 'const BLD3DV_DATA=' + json.dumps(v, separators=(',', ':')) + ';' + html[jv:]; html_p.write_text(html, encoding='utf-8')
print('limpos:', ', '.join(f'{k} ({n} px)' for k, n in sorted(tot.items(), key=lambda q: -q[1])))
