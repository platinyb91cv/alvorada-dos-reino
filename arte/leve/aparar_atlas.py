# Atlas mais leves para o telemóvel, sem perder qualidade: tira dos atlas só as peças que o jogo já não desenha
# (foram substituídas por arte nova) e volta a empacotar as restantes com os mesmos píxeis e as mesmas âncoras.
#   bld-atlas-v2.webp  -> bld-atlas-leve.webp  : só a quinta e as ruínas (o resto vem de edificios-3d)
#   portoes-3d.webp    -> portoes-3d-leve.webp : só os portões de madeira (os de pedra vêm de portoes-pintados)
#   muralhas-3d.webp   -> muralhas-3d-leve.webp: só a paliçada (pedra e fortificada vêm de castelo-modular)
# Os atlas originais ficam no repositório (fonte e testes); o jogo carrega os leves. Gera arte/leve/verification.json.
# Uso: python3 arte/leve/aparar_atlas.py <repo>
import sys, json, io, hashlib
from pathlib import Path
from PIL import Image
repo = Path(sys.argv[1] if len(sys.argv) > 1 else '.'); html_p = repo / 'www/index.html'; html = html_p.read_text()
sha = lambda b: hashlib.sha256(b).hexdigest()
def pack(tiles, AW=2048, gap=2):
    order = sorted(tiles, key=lambda n: (-tiles[n].height, n)); x = y = gap; row = 0; place = {}
    for n in order:
        w, h = tiles[n].size
        if x + w + gap > AW: x = gap; y += row + gap; row = 0
        place[n] = (x, y); x += w + gap; row = max(row, h)
    W = max(px + tiles[n].width for n, (px, py) in place.items()) + gap
    atlas = Image.new('RGBA', (W, y + row + gap))
    for n, (px, py) in place.items(): atlas.paste(tiles[n], (px, py))
    buf = io.BytesIO(); atlas.save(buf, 'WEBP', lossless=True, quality=100, method=6); return atlas, buf.getvalue(), place
def json_at(name):
    i = html.index('const ' + name + '='); j = html.index('=', i) + 1; d = 0
    for k in range(j, len(html)):
        c = html[k]
        if c == '{': d += 1
        elif c == '}':
            d -= 1
            if d == 0: return i, j, k + 1, json.loads(html[j:k + 1])
proof = {}
# --- portões e muralhas 3D (frames [x,y,w,h,ax,ay]) ---
for name, keep, out in [('GATE3D_DATA', lambda k: k.startswith('madeira'), 'portoes-3d-leve.webp'), ('WALL3D_DATA', lambda k: k.startswith('madeira'), 'muralhas-3d-leve.webp')]:
    i, j, e, data = json_at(name)
    src_name = data.get('fonte', data['file']); src = repo / 'www/assets/edificios-extra' / src_name; old = Image.open(src).convert('RGBA')
    frames = {k: f for k, f in data.get('framesFonte', data['frames']).items() if keep(k)}
    tiles = {k: old.crop((f[0], f[1], f[0] + f[2], f[1] + f[3])) for k, f in frames.items()}
    atlas, webp, place = pack(tiles); (repo / 'www/assets/edificios-extra' / out).write_bytes(webp)
    new = dict(data); new['file'] = out; new['fonte'] = src_name; new['atlasSha256'] = sha(webp)
    new['frames'] = {k: [place[k][0], place[k][1], f[2], f[3], f[4], f[5]] for k, f in sorted(frames.items())}
    new.pop('framesFonte', None)
    html = html[:j] + json.dumps(new, separators=(',', ':')) + html[e:]
    proof[name] = {'fonte': src_name, 'fonteSha256': sha(src.read_bytes()), 'leve': out, 'leveSha256': sha(webp), 'tamanho': atlas.size,
                   'mbDescodificado': [round(old.width * old.height * 4 / 2**20, 1), round(atlas.width * atlas.height * 4 / 2**20, 1)],
                   'peças': len(frames), 'mapa': {k: [frames[k][:4], new['frames'][k][:4]] for k in frames}}
# --- edifícios antigos (meta {xl,xr,yb,yl,f:[x,y,w,h]}) ---
i = html.index('const BLDART={wide:true,ready:false,img:null,meta:'); j = html.index('meta:', i) + 5; d = 0
for k in range(j, len(html)):
    c = html[k]
    if c == '{': d += 1
    elif c == '}':
        d -= 1
        if d == 0: e = k + 1; break
meta = json.loads(html[j:e]); KEEP = ['quinta|0', 'quinta|1', 'ruina|0', 'ruina|1']
src = repo / 'www/assets/edificios-v2/bld-atlas-v2.webp'; old = Image.open(src).convert('RGBA')
tiles = {k: old.crop((meta[k]['f'][0], meta[k]['f'][1], meta[k]['f'][0] + meta[k]['f'][2], meta[k]['f'][1] + meta[k]['f'][3])) for k in KEEP}
atlas, webp, place = pack(tiles, AW=1024); (repo / 'www/assets/edificios-v2/bld-atlas-leve.webp').write_bytes(webp)
newm = {k: {**meta[k], 'f': [place[k][0], place[k][1], meta[k]['f'][2], meta[k]['f'][3]]} for k in KEEP}
html = html[:j] + json.dumps(newm, separators=(',', ':')) + html[e:]
html = html.replace("im.src='assets/edificios-v2/bld-atlas-v2.webp'", "im.src='assets/edificios-v2/bld-atlas-leve.webp?v=" + sha(webp)[:12] + "'")
proof['BLDART'] = {'fonte': 'bld-atlas-v2.webp', 'fonteSha256': sha(src.read_bytes()), 'leve': 'bld-atlas-leve.webp', 'leveSha256': sha(webp), 'tamanho': atlas.size,
                   'mbDescodificado': [round(old.width * old.height * 4 / 2**20, 1), round(atlas.width * atlas.height * 4 / 2**20, 1)], 'peças': len(KEEP),
                   'mapa': {k: [meta[k]['f'], newm[k]['f']] for k in KEEP}}
html_p.write_text(html); (repo / 'arte/leve/verification.json').write_text(json.dumps(proof, ensure_ascii=False, indent=1))
for k, v in proof.items(): print(k, v['leve'], v['tamanho'], 'MB', v['mbDescodificado'], 'peças', v['peças'])
