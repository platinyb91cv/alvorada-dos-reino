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

## Modelos GLB (Tripo, Meshy…)
O mercado vem de um modelo GLB gerado no Tripo. O `montar_edificios.py` importa-o, encaixa-o na pegada do edifício (3×3) com escala uniforme, assenta-o no chão e renderiza-o com a mesma câmara e luz dos outros:
```
GLB_MAP="mercado=/caminho/mercado.glb" ONLY=mercado ED_OUT=/tmp/merc TEX_DIR=<texturas> blender -b --python arte/edificios-3d/scripts/montar_edificios.py
DESSAT_TELHADO=1 python3 arte/edificios-3d/scripts/trocar_no_atlas.py /tmp/merc . mercado_1 mercado_2
```
- `GLB_ROT="mercado=90"` roda o modelo se a frente ficar virada para o lado errado.
- O `trocar_no_atlas.py` substitui só esses quadros no atlas, sem renderizar os outros edifícios de novo.
- `DESSAT_TELHADO=1` tira o azul acinzentado do telhado, para que só os toldos levem a cor da equipa.

O GLB original (56 MB) não está no repositório; só o render entra no atlas.
