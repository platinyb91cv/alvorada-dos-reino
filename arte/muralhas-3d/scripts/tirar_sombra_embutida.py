# Tira dos atlas 3D a sombra projetada que o "apanha-sombras" (shadow catcher) do Blender deixou embutida nas imagens:
# píxeis pretos (RGB <= 10) meio transparentes. Era a causa das faixas pretas debaixo das muralhas (até 82% de opacidade),
# e ficava sombra a dobrar porque o jogo já projeta a sua (shadowOf). A pedra nunca é preta pura, por isso não é tocada.
# Uso: python3 tirar_sombra_embutida.py <repo>
import sys, json, re, io, hashlib
from pathlib import Path
import numpy as np
from PIL import Image
repo = Path(sys.argv[1]); html_p = repo / 'www/index.html'; html = html_p.read_text()
PROOF = {'WALL3D_DATA': ('arte/muralhas-3d/verification.json', ('atlas', 'sha256')), 'GATE3D_DATA': ('arte/portoes-3d/verification.json', ('atlas', 'sha256')),
         'BLD3D_DATA': ('arte/edificios-3d/verification.json', ('atlasSha256',))}
for name, (pf, keys) in PROOF.items():
    m = re.search(r'const ' + name + r'=(\{[^\n]+\});', html); d = json.loads(m.group(1))
    p = repo / 'www/assets/edificios-extra' / d['file']; a = np.array(Image.open(p).convert('RGBA'))
    sh = (a[..., :3].max(-1) <= 10) & (a[..., 3] > 0) & (a[..., 3] < 240); a[sh] = 0
    buf = io.BytesIO(); Image.fromarray(a).save(buf, 'WEBP', lossless=True, quality=100, method=6); webp = buf.getvalue(); p.write_bytes(webp)
    sha = hashlib.sha256(webp).hexdigest(); d['atlasSha256'] = sha
    html = html[:m.start(1)] + json.dumps(d, separators=(',', ':')) + html[m.end(1):]
    v = json.loads((repo / pf).read_text()); o = v
    for k in keys[:-1]: o = o[k]
    o[keys[-1]] = sha; v['sombraEmbutidaRemovida'] = int(sh.sum()); (repo / pf).write_text(json.dumps(v, indent=1, ensure_ascii=False))
    print(name, 'tirados', int(sh.sum()), 'px', len(webp) // 1024, 'KB')
html_p.write_text(html)
