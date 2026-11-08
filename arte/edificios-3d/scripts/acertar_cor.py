# Acerta a cor de edifícios pintados fora (ChatGPT/Grok) à paleta dos que já estão no jogo: as imagens vinham
# mais claras e mais saturadas (V ~0,55, S ~0,60) do que o jogo (V ~0,45, S ~0,45 no Bronze e ~0,32 no Ferro).
# Só mexe na cor (saturação e brilho), nunca na forma. O azul da equipa (bandeiras, toldos) fica intacto para continuar a ser recolorido.
# Uso: python3 acertar_cor.py <pasta> nome:S_alvo:V_alvo [...]
import sys, numpy as np
from pathlib import Path
from PIL import Image
d = Path(sys.argv[1])
for spec in sys.argv[2:]:
    n, ts, tv = spec.split(':'); ts, tv = float(ts), float(tv)
    im = Image.open(d / f'{n}.png').convert('RGBA'); a = np.asarray(im).astype(np.float32) / 255
    hsv = np.asarray(im.convert('RGB').convert('HSV')).astype(np.float32) / 255
    op = a[..., 3] > .9; H, S, V = hsv[..., 0] * 360, hsv[..., 1], hsv[..., 2]
    team = (H >= 188) & (H <= 282) & (S > .35)
    sel = op & ~team; fs = ts / S[sel].mean(); fv = tv / V[sel].mean()
    S2 = np.where(team, S, np.clip(S * fs, 0, 1)); V2 = np.where(team, V, np.clip(V * fv, 0, 1))
    out = Image.merge('HSV', [Image.fromarray((x * 255).round().astype(np.uint8)) for x in (hsv[..., 0], S2, V2)]).convert('RGB')
    rgba = np.dstack([np.asarray(out), (a[..., 3] * 255).round().astype(np.uint8)])
    Image.fromarray(rgba, 'RGBA').save(d / f'{n}.png'); print(n, f'S x{fs:.2f} V x{fv:.2f}')
