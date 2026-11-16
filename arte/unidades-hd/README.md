# Soldados HD (h=128)

Aldeão (h=96, 576 quadros com todas as tarefas), guerreiro, lanceiro, espadachim, arqueiro e besteiro (h=128) renderizados de novo a partir dos mesmos GLB de `arte/unidades-armadas/`
(sem novos créditos Meshy), com a câmara, as 8 direções e as fases do `renderizar.py` original.

- Render: Blender (bpy 5.3) Cycles CPU, 512 px (lanceiro 640 px, por causa da lança), 16 amostras + OIDN, fundo transparente.
- Os atlas antigos (h=64) vinham de renders de 128 px ampliados ~1,7×; estes são **reduzidos** (fator < 1), por isso nítidos.
- Atlas: `www/assets/units3d-hd/` (WebP sem perdas, ~2,4 MB cada). Mesma ordem de quadros e estados dos atlas armados.
- No jogo: só com "Resolução: HD" e telemóvel com ≥4 GB (`unit3dHdOn`); senão, ou se falhar, usa os armados (h=64).
- Teste: `tests/check_unit3d_hd.cjs` (hashes, mesmo GLB, h=128, redução, orçamento de memória < 24 M píxeis).

Refazer: `python3 renderizar_hd.py unit=<nome> [res=640]` → `python3 empacotar_hd.py <nome> lossless` → `python3 integrar_hd.py`.

## Cavalaria HD (h=96)

Cavalaria, cavalaria pesada e cavalaria arqueira: rigs montados com `arte/cavalaria-3d/scripts/montar_cavalaria.py`
(cavalo CC0 + espadachim/lanceiro/arqueiro; a pesada com `ARMOR=1`), renderizados com `renderizar_cav_hd.py` (512 px, mesma luz)
e empacotados com `empacotar_cav_hd.py`: ponto de apoio relativo copiado do atlas atual (mesmo sítio no jogo), escala para h=96.
Carregam só quando a unidade aparece (`cavLoad`), com recurso ao atlas atual se falharem. 96 e não 128: o cavalo é largo
(a 128 seriam ~10 M píxeis por atlas).
