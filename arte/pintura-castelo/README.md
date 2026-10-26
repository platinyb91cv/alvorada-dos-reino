# Castelo pintado: portão de pedra e torre de nível 3

**Versão atual (v2):** `fonte/portao_v2.png` e `fonte/torre_v2.png`, feitas com os prompts de isometria 2:1, pedra cinzenta e sem chão.
- **Portão:** casa do portão de 5 casas. As torres ficam a 2 casas do centro do portão.
  - Os muros a 1 ou 2 casas ficam debaixo dela: os de trás são tapados, os da frente não se desenham.
  - O muro a 3 casas é cortado na parede da torre.
  - Fechado, a grade de ferro desce no arco.
- **Torre redonda:** raio do corpo 0,85, varanda a 3,3.

Os scripts reconhecem a v2 pelo nome do ficheiro. A v1 (folhas de 4 vistas) continua em `fonte/`.

As pinturas de 4 vistas estão em `fonte/`.

- **Portão de pedra:** a vista "lado direito" serve o portão ao longo de x; o espelho dessa vista serve a direção y.
  - As duas torres redondas ficam nas casas de muralha ao lado do portão. Esses muros deixam de ser desenhados (bit 256 do `bldVariant`), mas continuam a bloquear e a aceitar soldados.
  - O estado 0 (fechado) tem portas desenhadas no arco.
- **Torre de nível 3:** vem da vista frontal da torre redonda, sem o chão pintado. A varanda fica a 2,85, a altura onde ficam os soldados.

## Gerar de novo
```
python3 arte/pintura-castelo/scripts/portao_pintado.py arte/pintura-castelo/fonte/portao_v2.png .
python3 arte/pintura-castelo/scripts/torre_pintada.py arte/pintura-castelo/fonte/torre_v2.png /tmp/torre
python3 arte/edificios-3d/scripts/trocar_no_atlas.py /tmp/torre . torre_3
```

## Testes
- `tests/check_castelo_pintado.cjs`
- `tests/e2e/castelo_pintado.py`

As imagens das provas estão em `provas/`.
