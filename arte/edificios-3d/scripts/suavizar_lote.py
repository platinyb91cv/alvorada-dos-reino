# O chão pintado de cada lote (relva, terra, empedrado) acabava numa aresta reta em losango e o edifício parecia
# uma imagem colada no terreno. Isto desvanece a orla do lote para o terreno do jogo, mas só nos píxeis que têm a cor
# do chão do próprio lote (paleta tirada da orla); cercas, muros, paredes e telhados não mudam.
# A largura da orla varia com ruído, para a borda não ficar reta. Trabalha nos renders (2 px por px do mundo).
# Só nas arestas da frente: nas de trás o edifício cobre o chão e a cor das paredes confunde-se com a do chão.
# Uso: python3 suavizar_lote.py <pasta-renders> nome:WxH [...]   (lê anchors.json da mesma pasta)
import sys, json
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage
d0 = Path(sys.argv[1]); A = json.loads((d0 / 'anchors.json').read_text())
rng = np.random.default_rng(7)
def palette(px, k=5):
    c = px[rng.choice(len(px), min(len(px), 4000), replace=False)]
    cent = c[rng.choice(len(c), k, replace=False)]
    for _ in range(12):
        lab = ((c[:, None, :] - cent[None]) ** 2).sum(2).argmin(1)
        cent = np.array([c[lab == i].mean(0) if (lab == i).any() else cent[i] for i in range(k)])
    return cent
for spec in sys.argv[2:]:
    n, wh = spec.split(':'); fw, fh = map(int, wh.split('x'))
    ax, ay = A[n.rsplit('_', 1)[0] + '|' + n.rsplit('_', 1)[1]][:2]
    im = Image.open(d0 / f'{n}.png').convert('RGBA'); a = np.asarray(im).astype(np.float32)
    H, W = a.shape[:2]; yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    s = .97; X = xx - ax; Y = yy - ay
    tx = (X / (64 * s) + Y / (32 * s)) / 2; ty = (Y / (32 * s) - X / (64 * s)) / 2
    d = np.minimum(fw - tx, fh - ty)   # distância às arestas da FRENTE do lote, em casas (dentro > 0); atrás o edifício cobre o chão
    dall = np.minimum(np.minimum(tx, fw - tx), np.minimum(ty, fh - ty))
    rgb = a[..., :3]; al = a[..., 3] / 255
    ring = (d > .02) & (d < .14) & (dall > .02) & (al > .9)
    pal = palette(rgb[ring])
    dist = np.sqrt(((rgb[..., None, :] - pal[None, None]) ** 2).sum(-1)).min(-1)
    g = np.clip(1 - (dist - 16) / 26, 0, 1)                           # 1 = cor do chão do lote
    g = ndimage.uniform_filter(g, 3)
    noise = ndimage.gaussian_filter(rng.random((H, W)).astype(np.float32), 9); noise = (noise - noise.min()) / (np.ptp(noise) + 1e-6)
    band = .26 + .22 * noise                                          # largura da orla: 0,26-0,48 casas, irregular
    t = np.clip(d / band, 0, 1); f = t * t * (3 - 2 * t)
    keep = (tx < -.02) | (ty < -.02)                                  # fora das arestas de trás: paredes e telhados, não se mexe
    fade = np.where(keep, 1.0, np.where(d < 0, 0.0, 1 - g * (1 - f)))  # fora das arestas da frente é só orla pintada (risca clara): sai
    na = (al * fade * 255).round().clip(0, 255).astype(np.uint8)
    out = a.copy(); out[..., 3] = na
    Image.fromarray(out.astype(np.uint8), 'RGBA').save(d0 / f'{n}.png')
    print(n, 'píxeis de chão desvanecidos', int(((al > .5) & (fade < .5)).sum()))
