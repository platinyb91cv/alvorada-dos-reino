# Torre redonda pintada (folha de 4 vistas) -> render a 2x para o atlas edificios-3d (quadro torre_3).
# Tira o fundo branco e o chão pintado, escala para a varanda ficar à altura dos soldados (TOPZ 2,85) e calcula a âncora
# (canto de cima da casa 2x2: o centro da base da torre fica no centro da pegada).
# Uso: python3 torre_pintada.py <folha.png> <pasta_saida>
import sys, json
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, str(Path(__file__).resolve().parent)); from tom_muro import tom_muro  # pedra no cinzento das muralhas (TOM=original para manter)
src, out = Path(sys.argv[1]), Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
def cutout(im):
    if im.mode == 'RGBA' and np.array(im)[..., 3].min() < 10: return im  # já vem com transparência (v3): não mexer no fundo
    rgb = im.convert('RGB'); w, h = rgb.size; m = rgb.copy(); key = (255, 0, 255)
    for p in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, 0), (w // 2, h - 1), (0, h // 2), (w - 1, h // 2)]:
        if sum(m.getpixel(p)) > 3 * 215 and m.getpixel(p) != key: ImageDraw.floodfill(m, p, key, thresh=38)
    a = np.array(m); bg = (a[..., 0] == 255) & (a[..., 1] == 0) & (a[..., 2] == 255)
    bg |= (a[..., :3].min(-1) > 246)   # branco preso entre as pontas das bandeiras
    o = rgb.convert('RGBA'); o.putalpha(Image.fromarray(np.where(bg, 0, 255).astype('uint8'))); return o
V3 = 'v3' in src.name; V2 = 'v2' in src.name or V3
im = cutout(Image.open(src).crop((0, 0, 764, 472)) if not V2 else Image.open(src))  # vista frontal (porta virada para a frente)
a = np.array(im); H, W = a.shape[:2]; yy, xx = np.mgrid[0:H, 0:W]
CX, CY, RA, RB = (615, 1130, 260, 122) if V3 else (622, 1070, 330, 120) if V2 else (408, 392, 98, 33)   # elipse da base da torre na imagem
keep = np.ones((H, W), bool) if V2 else (yy < 335) | (((xx - CX) / RA) ** 2 + ((yy - CY) / RB) ** 2 <= 1) | ((yy < CY) & (np.abs(xx - CX) < RA))
al = np.array(Image.fromarray(np.where(keep, a[..., 3], 0).astype('uint8')).filter(ImageFilter.GaussianBlur(1.2)))
a[..., 3] = np.minimum(a[..., 3], al); im = tom_muro(Image.fromarray(a), val=1.0 if V2 else .86)
DECK = 385 if V3 else 300 if V2 else 118                          # chão da varanda (onde ficam os soldados), ao centro
ZP2 = 2 * 64 / 2 ** .5 * .8660254   # píxeis por unidade de altura a 2x (78,4)
R_CORPO, TOPO = .85, 3.3            # raio do corpo da torre (casas) e altura da varanda: os muros (a meia casa do centro) batem de frente na parede
SX = R_CORPO * 2 * 2 * 64 / 2 ** .5 / (452 if V2 else 136)   # largura do corpo na pintura (px)
SY = TOPO * ZP2 / (CY - DECK)
if V3:  # v3: escala única (a mesma em todas as direções), tirada só do diâmetro do corpo = 1,7 casas; a altura da varanda sai daí
    SX = SY = 1.7 * 2 * 64 / 2 ** .5 / 490; TOPO = (CY - DECK) * SY / ZP2
im = im.resize((round(W * SX), round(H * SY)), Image.LANCZOS)
ax, ay = CX * SX, CY * SY - 64      # centro da pegada 2x2 = (1,1) -> 64 px abaixo do canto de cima
bb = im.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox(); im = im.crop(bb); ax -= bb[0]; ay -= bb[1]
im.save(out / 'torre_3.png')
af = out / 'anchors.json'; A = json.loads(af.read_text()) if af.exists() else {}
A['torre|3'] = [round(ax, 2), round(ay, 2), 2, 2]; af.write_text(json.dumps(A, indent=1)); print('torre_3', im.size, round(SX, 3), round(SY, 3), A['torre|3'], 'varanda', round(TOPO, 2))
