# Estúdio de IA — Alvorada dos Reinos

Servidor com GPU NVIDIA (ex.: RTX 3090 24 GB) para criar a arte do jogo.

## Instalar (uma vez)

No servidor, por SSH:

```bash
curl -fsSL https://raw.githubusercontent.com/platinyb91cv/alvorada-dos-reino/main/ia/instalar-ia.sh -o instalar-ia.sh
bash instalar-ia.sh
```

Opções: `WAN14B=1 bash instalar-ia.sh` (animação de melhor qualidade, +30 GB) · `SEM3D=1` (sem 3D) · `HF_TOKEN=hf_...` (se algum modelo pedir login no Hugging Face).

Demora 30–90 min (≈100 GB de downloads).

## Usar

1. No servidor: `bash /opt/ia/iniciar-ia.sh`
2. No teu computador: `ssh -L 8188:localhost:8188 -L 7860:localhost:7860 utilizador@IP` (mais `-p PORTA` se for preciso)
3. Abre **http://localhost:8188** (ComfyUI) ou **http://localhost:7860** (Hunyuan3D)
4. Desligar: `bash /opt/ia/parar-ia.sh`. Desliga também a máquina alugada quando não a usas.

No ComfyUI: **Workflow → Browse Templates** e escolhe Flux Kontext, Qwen Image, Qwen Image Edit ou Wan 2.2. Os modelos já estão no sítio.

## Receitas para o jogo

**Personagem nova (folha de poses):** Qwen Image ou Flux, com o mesmo pedido que foi usado para o Rei (fundo magenta #FF00FF, grelha 4×2, virado para a direita, túnica azul).

**Mesma personagem noutra pose:** Flux Kontext. Carrega a imagem e escreve, por exemplo: *"Same king, same style and magenta background, now walking with his left leg clearly forward"*.

**Animação a partir de uma imagem:** Wan 2.2, com um pedido como *"the king walks in place to the right, side view, the camera does not move, magenta background"*. Envia o vídeo ao Claude: ele tira os quadros e monta a animação no jogo.

**3D → animações perfeitas:** Hunyuan3D (imagem → modelo .glb) → mixamo.com (esqueleto + andar/atacar/morrer, grátis) → Blender (câmara isométrica, fundo transparente, renderizar as poses) → envia os PNG ao Claude.

## Licenças (o jogo é comercial)

- **Qwen-Image e Wan 2.2:** Apache 2.0, uso comercial livre.
- **FLUX.1 Kontext [dev]:** podes usar as imagens no jogo, mas não podes vender o modelo como serviço.
- **Hunyuan3D 2.1:** a licença da Tencent exclui a UE, o Reino Unido e a Coreia do Sul. Confirma antes de vender o jogo nesses países.
