# Fauna Meshy — veado (tipo de jogo `gazela`)

Modelo gerado pelo utilizador no site meshy.ai (`Meshy_AI_Stag_1020024809_texture.glb`, estático, 338 k triângulos).
Pipeline, sem créditos adicionais:

1. `scripts/reduzir.py` — reduz para 24 000 triângulos e texturas ≤ 2048 px.
2. `scripts/montar_veado.py` — esqueleto de quadrúpede (Root, Hips, Spine, Neck, Head, Antlers, 4 patas de 2 ossos),
   pesos suaves por distância aos ossos (o heat map do Blender falha na malha aberta do Meshy) e clips
   Idle, Graze (pastar), Walk (trote no lugar, pares diagonais), Attack (investida com as hastes), Hit e Death (tomba de lado).
3. `scripts/fauna.ts` — atlas Forge3D de 8 direções (idle 2, graze 4, walk 8, attack 4, hit 2, death 4 quadros).
4. `scripts/integrar_fauna.py` — reduz 0,7×, reempacota em 2048 px, WebP sem perdas e calcula a cadência do trote
   a partir do passo real das patas; escreve `UNIT3D_FAUNA_DATA` no `index.html`.

No jogo: a gazela usa o atlas 3D (8 direções, sem cor de equipa), pasta quando está parada, e a carcaça
mostra a queda e fica deitada na direção em que morreu. A arte 2D antiga continua como reserva se o atlas não carregar.
`scripts/checkveado.py` faz as provas laterais dos clips.
