# Provas visuais: antes/depois a 30 px reais e ampliação 4× nearest, e prova das 8 direções com âncoras e limites.
# Uso: python3 provas.py <repo> <saida>
import sys, json
from pathlib import Path
from PIL import Image, ImageDraw
repo, out = Path(sys.argv[1]), Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
U = repo / 'www/assets/units3d'; L = ['SE', 'S', 'SW', 'W', 'NW', 'N', 'NE', 'E']
STATES = ['idle', 'walk', 'attack', 'hit', 'death']; BG = (58, 92, 52, 255)
def load(name):
    m = json.loads((U / f'{name}.json').read_text()); return m, Image.open(U / f'{name}.webp').convert('RGBA')
def sprite(m, A, d, fi, scale):
    x, y, w, h, ax, ay = m['f'][d * m['framesPerDirection'] + fi]
    t = A.crop((x, y, x + w, y + h)); W, H = max(1, round(w * scale)), max(1, round(h * scale))
    return t.resize((W, H), Image.LANCZOS), ax * scale, ay * scale
def row(m, A, d, st, cell=(40, 44)):
    ids = m['states'][st]; im = Image.new('RGBA', (cell[0] * 8, cell[1]), BG)
    for c, fi in enumerate(ids):
        t, ax, ay = sprite(m, A, d, fi, 30 / m['h']); gx, gy = c * cell[0] + cell[0] // 2, cell[1] - 6
        im.alpha_composite(t, (max(0, round(gx - ax)), max(0, round(gy - ay))))
    return im
for n in ['guerreiro', 'lanceiro', 'espadachim', 'arqueiro', 'besteiro']:
    old = load(n); new = load(n + '-armas-meshy')
    blocks = []
    for label, (m, A) in (('ANTES', old), ('DEPOIS', new)):
        for d in (0, 1):
            for st in STATES: blocks.append((f'{label} {L[d]} {st}', row(m, A, d, st)))
    w30 = blocks[0][1].width; h30 = blocks[0][1].height
    sheet = Image.new('RGBA', (110 + w30 + 10 + w30 * 4, len(blocks) * h30 * 4 + 30), (24, 24, 24, 255)); dr = ImageDraw.Draw(sheet)
    dr.text((110, 8), '30 px reais', fill='white'); dr.text((110 + w30 + 10, 8), 'mesmos píxeis ampliados 4x (nearest)', fill='white')
    for k, (lab, im) in enumerate(blocks):
        y = 30 + k * h30 * 4; dr.text((6, y + 10), lab, fill=(255, 220, 150) if lab.startswith('DEPOIS') else (200, 200, 200))
        sheet.alpha_composite(im, (110, y)); sheet.alpha_composite(im.resize((w30 * 4, h30 * 4), Image.NEAREST), (110 + w30 + 10, y))
    sheet.convert('RGB').save(out / f'{n}-antes-depois-30px.png')
    # 8 direções: 1.º quadro de cada estado a 64 px, com âncora (vermelho) e retângulo do quadro (amarelo).
    m, A = new; cw, ch = 120, 130
    pr = Image.new('RGBA', (cw * 5 + 60, ch * 8), (236, 230, 214, 255)); dr = ImageDraw.Draw(pr)
    for d in range(8):
        dr.text((4, d * ch + 60), L[d], fill='black')
        for c, st in enumerate(STATES):
            fi = m['states'][st][len(m['states'][st]) // 2]; x, y, w, h, ax, ay = m['f'][d * m['framesPerDirection'] + fi]
            t = A.crop((x, y, x + w, y + h)); gx, gy = 60 + c * cw + cw // 2, d * ch + ch - 10
            ox, oy = round(gx - ax), round(gy - ay); pr.alpha_composite(t, (max(0, ox), max(0, oy)))
            dr.rectangle((ox, oy, ox + w - 1, oy + h - 1), outline=(220, 170, 0)); dr.line((gx - 5, gy, gx + 5, gy), fill='red'); dr.line((gx, gy - 5, gx, gy + 5), fill='red')
            if d == 0: dr.text((60 + c * cw + 4, 2), st, fill='black')
    pr.convert('RGB').save(out / f'{n}-8-direcoes-ancoras.png')
print('ok')
