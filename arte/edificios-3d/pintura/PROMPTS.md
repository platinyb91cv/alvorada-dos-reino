# Repintar os edifícios 3D com IA (ChatGPT / Gemini)

Envia **uma folha de cada vez** (`eraX_..._A.png`, `_B.png`, `_C.png`) com o prompt da era dela.
Guarda o resultado com o mesmo nome e `_pintada` no fim. Por exemplo, `era1_pedra_A.png` passa a `era1_pedra_A_pintada.png`.

## Era 1 — Idade da Pedra (`era1_pedra_A.png`, `era1_pedra_B.png`)
```
Repaint this reference image as REALISTIC medieval-village RTS game art (quality of Age of Empires IV / Manor Lords / a high-end Unreal Engine 5 render seen from an isometric camera). It is an early "Stone Age" village: rough hand-hewn timber, log and plank walls, wattle-and-daub panels, thick shaggy straw thatch roofs with visible bundles and a darker ridge, rope lashings, wooden pegs, mud and trampled earth, simple wooden platforms and fences, firewood piles, barrels, sacks.
STRICT RULES: keep EXACTLY the same buildings, positions, sizes, camera angle, silhouettes and layout as the input — do not move, rotate, resize, add or remove anything. Only replace materials, lighting and detail. Realistic PBR materials, weathering, moss, dirt at the base, soft ambient occlusion, warm late-morning sunlight from the top-left, natural colors (not cartoon, not plastic). Keep the patch of trampled earth under each building. Keep any small flags/banners BLUE (#2850C8). Pure plain white background (#FFFFFF) everywhere else: no grass, no sky, no text, no extra shadows outside the buildings. Output 1536x1024.
```

## Era 2 — Idade do Bronze (`era2_bronze_A.png`, `era2_bronze_B.png`)
```
Repaint this reference image as REALISTIC medieval-village RTS game art (quality of Age of Empires IV / Manor Lords / a high-end Unreal Engine 5 render seen from an isometric camera). It is a "Bronze Age" village growing richer: rubble-stone foundations, half-timbered walls with dark oak beams and cream lime plaster, terracotta clay-tile roofs with individual tiles, slight sag and moss, brick chimneys, plank doors with iron hinges, wooden shutters, sandstone towers with mortar joints, market stalls with striped canvas awnings, barrels, crates, hay.
STRICT RULES: keep EXACTLY the same buildings, positions, sizes, camera angle, silhouettes and layout as the input — do not move, rotate, resize, add or remove anything. Only replace materials, lighting and detail. Realistic PBR materials, weathering, dirt at the base, soft ambient occlusion, warm late-morning sunlight from the top-left, natural colors (not cartoon, not plastic). Keep the patch of trampled earth under each building. Keep every flag, banner and the blue awning stripes BLUE (#2850C8). Pure plain white background (#FFFFFF) everywhere else: no grass, no sky, no text, no extra shadows outside the buildings. Output 1536x1024.
```

## Era 3 — Idade do Ferro (`era3_ferro_A.png`, `era3_ferro_B.png`, `era3_ferro_C.png`)
```
Repaint this reference image as REALISTIC medieval RTS game art (quality of Age of Empires IV / Manor Lords / a high-end Unreal Engine 5 render seen from an isometric camera). It is a prosperous "Iron Age" medieval town: dressed sandstone ashlar walls with crisp mortar joints, grey-brown slate roofs, two-storey half-timbered houses with jettied upper floor, iron-banded doors and studs, lead-glass windows, crenellated battlements, conical slate tower roofs with gilded finials, a golden dome on the wonder, heraldic banners, carts, barrels, crates.
STRICT RULES: keep EXACTLY the same buildings, positions, sizes, camera angle, silhouettes and layout as the input — do not move, rotate, resize, add or remove anything. Only replace materials, lighting and detail. Realistic PBR materials, weathering, dirt at the base, soft ambient occlusion, warm late-morning sunlight from the top-left, natural colors (not cartoon, not plastic). Keep the patch of trampled earth under each building. Keep every flag, banner and the blue awning stripes BLUE (#2850C8). Pure plain white background (#FFFFFF) everywhere else: no grass, no sky, no text, no extra shadows outside the buildings. Output 1536x1024.
```

## Se não sair bem
- Se mudou a forma ou a posição de algum edifício, responde: `Keep the exact same shapes, positions and sizes as the input image; only repaint the surfaces.`
- Se ficou com aspeto de desenho animado, responde: `More realistic: photographic materials, less saturated, finer detail.`
- Se o fundo não ficou branco, responde: `Make the background pure flat white #FFFFFF.`

## Integrar no jogo (para o Claude/Codex)
```
python3 arte/edificios-3d/scripts/integrar_pintura.py arte/edificios-3d/pintura/era1_pedra_A.json era1_pedra_A_pintada.png <renders> <saida>
# repetir para cada folha com a mesma <saida>, depois:
python3 arte/edificios-3d/scripts/integrar_edificios.py <saida> .
```
