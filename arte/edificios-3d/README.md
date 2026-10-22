# Edifícios 3D

Casa, armazém, quartel, arquearia, estábulo, doca, torre (níveis 1–3), ferreiro, templo, mercado, oficina, Centro da Vila e maravilha, uma imagem por era.

Usam a mesma câmara, luz, contorno e materiais dos portões e muralhas 3D. A biblioteca de primitivas é `arte/portoes-3d/scripts/montar_portao2.py`.

Custo: 0 créditos.

## Gerar de novo
```
LIB=arte/portoes-3d/scripts/montar_portao2.py ED_OUT=/tmp/edif SAMPLES=32 blender -b --python arte/edificios-3d/scripts/montar_edificios.py
python3 arte/edificios-3d/scripts/integrar_edificios.py /tmp/edif .
```

Variáveis opcionais:
- `ONLY=casa,centro` gera só esses edifícios.
- `TEX_DIR=<texturas Poly Haven>` usa as texturas reais (CC0), as mesmas dos portões.
- `GPU=1` renderiza com CUDA.

O integrador recorta cada imagem e empacota tudo em `www/assets/edificios-extra/edificios-3d.webp`. Também escreve `BLD3D_DATA` no `www/index.html`.

## No jogo
`bldSprite` chama `bld3dSprite` antes da arte pintada. A idade que falta usa a idade mais próxima, e a torre escolhe a imagem pelo nível.

A Vila, o curral e a quinta continuam com a arte pintada.

O teste está em `tests/check_edificios3d.cjs`.
