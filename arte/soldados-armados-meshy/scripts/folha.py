# Folha: estados x direções escolhidas, a 64 px (2x) — uso: folha.py atlas_dir unit out.png [dirs]
import sys, json
from PIL import Image, ImageDraw
d, unit, out = sys.argv[1], sys.argv[2], sys.argv[3]
dirs = [int(x) for x in (sys.argv[4] if len(sys.argv) > 4 else '0,1,3,5').split(',')]
L = ['SE','S','SW','W','NW','N','NE','E']
m = json.load(open(f'{d}/{unit}.json')); A = Image.open(f'{d}/{unit}.webp').convert('RGBA')
fpd = m['framesPerDirection']; cell = 96; sc = 1.4
rows = [(di, st) for di in dirs for st in m['states']]
W = cell * max(len(v) for v in m['states'].values()) + 90
img = Image.new('RGBA', (W, cell * len(rows)), (236, 230, 214, 255)); dr = ImageDraw.Draw(img)
for r, (di, st) in enumerate(rows):
    dr.text((4, r * cell + 40), f'{L[di]} {st}', fill=(0, 0, 0, 255))
    for c, fi in enumerate(m['states'][st]):
        x, y, w, h, ax, ay = m['f'][di * fpd + fi]
        fr = A.crop((x, y, x + w, y + h)).resize((int(w * sc), int(h * sc)), Image.LANCZOS)
        ox, oy = 90 + c * cell + cell // 2, r * cell + cell - 8
        img.alpha_composite(fr, (int(ox - ax * sc), int(oy - ay * sc)))
        dr.line((ox - 3, oy, ox + 3, oy), fill=(200, 0, 0, 255))
img.save(out)
