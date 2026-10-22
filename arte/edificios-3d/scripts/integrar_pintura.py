# Aplica uma folha repintada por IA (mesma grelha de referencia_casas_torres.png) aos renders 3D: cada célula volta ao tamanho
# e posição originais (âncoras iguais), o fundo branco sai, e a silhueta 3D (alargada 3 px) limita a pintura.
# Uso: python3 integrar_pintura.py <folha.json> <folha_pintada.png> <pasta_renders> <pasta_saida>  (repetir para cada folha, mesma saída)
import sys, json, shutil
from pathlib import Path
from PIL import Image, ImageFilter, ImageChops
here = Path(__file__).resolve().parent.parent / 'pintura'
info = json.loads(Path(sys.argv[1]).read_text())
painted, src, out = Image.open(sys.argv[2]).convert('RGB'), Path(sys.argv[3]), Path(sys.argv[4]); out.mkdir(parents=True, exist_ok=True)
if painted.size != (1536, 1024): painted = painted.resize((1536, 1024), Image.LANCZOS)
for f in src.glob('*'):
    if not (out / f.name).exists(): shutil.copy(f, out / f.name)
for n, d in info.items():
    x, y = d['pos']; w, h = d['size']; x0, y0, x1, y1 = d['bbox']
    cell = painted.crop((x, y, x + w, y + h)).resize((x1 - x0, y1 - y0), Image.LANCZOS).convert('RGBA')
    orig = Image.open(src / f'{n}.png').convert('RGBA'); oa = orig.crop((x0, y0, x1, y1)).getchannel('A')
    sil = oa.point(lambda v: 255 if v > 40 else 0).filter(ImageFilter.MaxFilter(7))  # silhueta do 3D (com 3 px de folga)
    r, g, b = cell.split(); white = ImageChops.darker(ImageChops.darker(r, g), b).point(lambda v: 255 if v > 238 else 0)
    a = ImageChops.multiply(sil, ImageChops.invert(white)).filter(ImageFilter.GaussianBlur(.6))
    # sombras/terra semitransparentes do render original mantêm-se onde a pintura é branca
    cell.putalpha(a); res = orig.copy(); base = Image.new('RGBA', orig.size); base.paste(cell, (x0, y0)); res.alpha_composite(base)
    res.save(out / f'{n}.png'); print('ok', n)
