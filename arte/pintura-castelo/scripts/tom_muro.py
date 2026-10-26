# Põe a pedra pintada (bege) no cinzento das muralhas 3D, mantendo madeira, bandeiras e telhados.
import os
import numpy as np
from PIL import Image
def tom_muro(im, val=.86):
    if os.environ.get('TOM') == 'original': return im
    a = np.array(im.convert('RGBA')).astype(np.float32) / 255; rgb = a[..., :3]
    M = rgb.max(-1); m = rgb.min(-1); d = M - m; s = np.where(M > 0, d / np.maximum(M, 1e-6), 0)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]; dd = np.maximum(d, 1e-6)
    h = np.where(d == 0, 0, np.where(M == r, ((g - b) / dd) % 6, np.where(M == g, (b - r) / dd + 2, (r - g) / dd + 4))) * 60
    pedra = (h > 12) & (h < 65) & (s > .08) & ((s < .58) & (M > .3) | (s < .85) & (M > .55))
    ns = .1 + (s - .08) * .12; nv = M * val
    C = nv * ns; X = C * (1 - np.abs((h / 60) % 2 - 1)); mm = nv - C; k = (h // 60).astype(int) % 6; z = 0 * C
    out = np.zeros_like(rgb)
    for i, (R, G, B) in enumerate([(C, X, z), (X, C, z), (z, C, X), (z, X, C), (X, z, C), (C, z, X)]):
        sel = k == i
        for j, ch in enumerate((R, G, B)): out[..., j] = np.where(sel, ch + mm, out[..., j])
    a[..., :3] = np.where(pedra[..., None], out, rgb)
    return Image.fromarray((a * 255).clip(0, 255).astype('uint8'))
