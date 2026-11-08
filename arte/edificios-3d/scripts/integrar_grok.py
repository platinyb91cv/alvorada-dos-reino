# Edifícios pintados no Grok (fundo branco, lote em losango) -> renders prontos para trocar_no_atlas.py.
# Para cada imagem: tira o fundo branco (só o branco ligado à borda, com a orla suavizada), mede os cantos do lote
# (esquerdo, direito, de baixo), endireita a inclinação para 2:1 se for preciso (só na vertical), escala para a
# pegada certa (2 px por px do mundo, como os renders do Blender) e calcula a âncora = canto de cima do lote.
# Uso: python3 integrar_grok.py <pasta-fonte> <pasta-saida> nome_idade:WxH [...]
import sys, json
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage
src, out = Path(sys.argv[1]), Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
anchors = json.loads((out / 'anchors.json').read_text()) if (out / 'anchors.json').exists() else {}
rep = json.loads((out / 'medidas.json').read_text()) if (out / 'medidas.json').exists() else {}
FIT = .97  # o lote pintado tem a orla de relva um pouco para fora do losango
for spec in sys.argv[3:]:
    name, wh = spec.split(':'); fw, fh = map(int, wh.split('x'))
    rgb = np.asarray(Image.open(src / f'{name}.png').convert('RGB')).astype(np.float32)
    mn = rgb.min(2); sat = rgb.max(2) - mn
    white = (mn >= 236) & (sat <= 14)
    lab, _ = ndimage.label(white); border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(border))
    # orla: perto do fundo, a transparência segue o quanto o píxel se afasta do branco
    # orla: os geradores esbatem a borda do lote para branco; numa faixa de 10 px junto ao fundo, os píxeis claros e pouco
    # saturados são fundo misturado. A transparência segue a distância ao branco e a cor passa a ser a do chão opaco mais próximo
    # (sem isto ficava uma orla esbranquiçada à volta do lote, como um autocolante)
    dist_bg = ndimage.distance_transform_edt(~bg)
    near = (dist_bg <= 10) & ~bg
    pale = np.clip((mn - 150) / 90, 0, 1) * np.clip(1 - sat / 60, 0, 1)    # 1 = quase branco
    ramp = np.clip(dist_bg / 10, 0, 1)
    a = np.where(bg, 0.0, np.where(near, np.clip(1 - pale * (1 - ramp * .6), 0, 1) * np.clip((255 - mn) / 60, 0, 1) ** .5, 1.0))
    a = ndimage.uniform_filter(a, 3); a[bg] = 0
    a = np.minimum(a, ndimage.minimum_filter(a, 3) * .5 + a * .5)        # recolhe 1 px a borda
    solid0 = a >= .97
    idx = ndimage.distance_transform_edt(~solid0, return_distances=False, return_indices=True)
    col = rgb[idx[0], idx[1]]; col = np.where(solid0[..., None], rgb, col)  # cor da orla = chão opaco mais próximo
    rgba = np.dstack([col, a * 255]).astype(np.uint8)
    solid = a > .5
    ys, xs = np.nonzero(solid)
    def pt(sel):
        return float(xs[sel].mean()), float(ys[sel].mean())
    L = pt(xs <= xs.min() + 2); R = pt(xs >= xs.max() - 2); B = pt(ys >= ys.max() - 2)
    sL = (B[1] - L[1]) / max(1, B[0] - L[0]); sR = (B[1] - R[1]) / max(1, R[0] - B[0]); slope = (sL + sR) / 2
    im = Image.fromarray(rgba, 'RGBA'); W0, H0 = im.size
    sy = .5 / slope if abs(slope - .5) > .03 else 1.0  # dentro de 0,47-0,53 não se mexe na imagem
    target = (fw + fh) * 64 * FIT; k = target / (R[0] - L[0])
    im = im.resize((round(W0 * k), round(H0 * k * sy)), Image.LANCZOS)
    L2 = (L[0] * k, L[1] * k * sy); R2 = (R[0] * k, R[1] * k * sy)
    # âncora: canto de cima do losango (pegada fw x fh); com a pegada quadrada fica a meio, 1/4 da largura acima da linha L-R
    span = R2[0] - L2[0]; ax = L2[0] + span * fh / (fw + fh); ay = L2[1] - span * fh / (fw + fh) / 2
    bb = im.getchannel('A').getbbox(); im = im.crop(bb); ax -= bb[0]; ay -= bb[1]
    im.save(out / f'{name}.png')
    anchors[name.rsplit('_', 1)[0] + '|' + name.rsplit('_', 1)[1]] = [round(ax, 2), round(ay, 2), im.width, im.height]
    rep[name] = {'inclinacao_esq': round(sL, 3), 'inclinacao_dir': round(sR, 3), 'correcao_vertical': round(sy, 3), 'escala': round(k, 3), 'tamanho': im.size, 'pegada': [fw, fh]}
    print(name, rep[name])
(out / 'anchors.json').write_text(json.dumps(anchors, indent=1)); (out / 'medidas.json').write_text(json.dumps(rep, indent=1, ensure_ascii=False))
