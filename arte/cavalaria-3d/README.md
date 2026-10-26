# Cavalaria 3D (0 créditos)

**Cavalo:** `fontes/Horse.blend`, do *Farm Animals Pack* do Quaternius, licença **CC0**
(ver `fontes/Quaternius-License.txt`; fonte: https://opengameart.org/content/lowpoly-animated-farm-animal-pack).
Tem esqueleto e as animações Idle, Run (galope), Death, Jump e Walk, todas no lugar, sem deslocar a raiz.

**Cavaleiros:** os soldados Meshy já existentes em `arte/unidades-armadas/`, sem gerar nada novo:

| Unidade do jogo | Cavaleiro | Arma |
|---|---|---|
| `cavaleiro` (Cavalaria) | espadachim | espada |
| `cavPesada` (Cavalaria Pesada) | lanceiro | lança |
| `cavArqueira` (Cavalaria Arqueira) | arqueiro | arco |

`scripts/montar_cavalaria.py` faz o seguinte:
- põe o cavaleiro à escala (cavalo de 2,25 m até ao topo da cabeça, cavaleiro de 1,70 m) e senta-o na sela;
- dobra as pernas em pose de montar, com os sinais escolhidos pela geometria;
- junta os dois esqueletos num só (ossos do cavaleiro com prefixo `R_`, presos ao `Torso` do cavalo);
- acrescenta uma manta azul moldada ao dorso, que no jogo toma a cor da equipa;
- coze os clips combinados:

| Clip | Cavalo | Cavaleiro (tronco) |
|---|---|---|
| Idle | Idle | Idle |
| Walk | Run (galope) | Idle |
| Attack | Idle | Attack |
| Hit | Idle | Hit |
| Death | Death (tomba de lado com o cavaleiro) | Death |

As pernas do cavaleiro ficam fixas em todos os clips.

`scripts/cav.ts` gera os atlas Forge3D de 8 direções (idle 2, walk 8, attack 6, hit 2, death 4). Depois,
`scripts/integrar_cav.py` reduz 0,7×, calcula a cadência do galope (cerca de 3 m por ciclo) e escreve `UNIT3D_CAV_DATA`.

Regenerar:
```
HORSE=fontes/Horse.blend RIDER=../unidades-armadas/espadachim.glb OUT=cavaleiro-rig.glb blender -b --python scripts/montar_cavalaria.py
```
Os GLB montados (cerca de 10 MB cada) não ficam no repositório: são regeneráveis a partir das fontes, e o sha256 de cada um está em `verification.json`.
