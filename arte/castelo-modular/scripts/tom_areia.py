# Põe a pedra cinzenta do conjunto modular (muralhas e torre redonda) no tom areia das peças pintadas (torre de menagem,
# Torre de Catapulta): cada píxel de pedra (pouco saturado) passa a ter a cor média da areia com a sua própria luminosidade
# (mais 25 %), por isso a textura e a luz ficam iguais. Estandartes e bandeiras (azul vivo) e o vazio ficam como estão.
# Uso: python3 tom_areia.py <repo>   (corre depois de integrar_modular.py)
import sys, json, re, io, hashlib
from pathlib import Path
import numpy as np
from PIL import Image
repo = Path(sys.argv[1]); p = repo / 'www/assets/edificios-extra/castelo-modular.webp'
AREIA = np.array([178.6, 161.0, 136.8]); LUM_AREIA = AREIA.mean(); GANHO = 1.25
a = np.array(Image.open(p).convert('RGBA')).astype(np.float32); rgb = a[..., :3]
M = rgb.max(-1); mn = rgb.min(-1); s = (M - mn) / np.maximum(M, 1)
pedra = (a[..., 3] > 0) & (s < .3)
lum = rgb.mean(-1, keepdims=True) * GANHO
novo = np.clip(AREIA / LUM_AREIA * lum, 0, 255)
a[..., :3] = np.where(pedra[..., None], novo, rgb)
buf = io.BytesIO(); Image.fromarray(a.astype('uint8')).save(buf, 'WEBP', lossless=True, quality=100, method=6); webp = buf.getvalue(); p.write_bytes(webp)
sha = hashlib.sha256(webp).hexdigest(); h = repo / 'www/index.html'; html = h.read_text()
m = re.search(r'const CMOD_DATA=(\{[^\n]+\});', html); d = json.loads(m.group(1)); d['atlasSha256'] = sha; d['tom'] = 'areia'
html = html[:m.start(1)] + json.dumps(d, separators=(',', ':')) + html[m.end(1):]; h.write_text(html)
v = repo / 'arte/castelo-modular/verification.json'; vv = json.loads(v.read_text()); vv['atlasSha256'] = sha; vv['tom'] = 'areia (tom_areia.py)'; v.write_text(json.dumps(vv, indent=1, ensure_ascii=False))
print('pedra', int(pedra.sum()), 'px', len(webp) // 1024, 'KB')
