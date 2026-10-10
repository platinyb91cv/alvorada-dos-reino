#!/usr/bin/env bash
# =====================================================================
#  Alvorada dos Reinos — estúdio de IA para criar a arte do jogo
#  Instala numa máquina com GPU NVIDIA (testado a pensar numa RTX 3090 24 GB):
#    • ComfyUI  (porta 8188) com:
#        - FLUX.1 Kontext [dev]  → imagens e "a mesma personagem noutra pose"
#        - Qwen-Image + Qwen-Image-Edit → imagens e edição por instruções
#        - Wan 2.2 (5B; 14B opcional) → imagem → vídeo (animações)
#    • Hunyuan3D 2.1 (porta 7860) → imagem → modelo 3D com textura
#
#  Uso:   bash instalar-ia.sh
#  Opções (variáveis antes do comando):
#    HF_TOKEN=hf_xxx   token do Hugging Face (só se algum modelo pedir login)
#    WAN14B=1          também o Wan 2.2 14B (melhor, +30 GB de disco)
#    SEM3D=1           não instalar o Hunyuan3D
#    BASE=/caminho     pasta de instalação (padrão: /opt/ia ou ~/ia)
# =====================================================================
set -uo pipefail
VERDE='\033[1;32m';AMAR='\033[1;33m';VERM='\033[1;31m';NC='\033[0m'
ok(){ echo -e "${VERDE}✔ $*${NC}"; }
aviso(){ echo -e "${AMAR}⚠ $*${NC}"; }
erro(){ echo -e "${VERM}✖ $*${NC}"; }
passo(){ echo -e "\n${VERDE}=== $* ===${NC}"; }

SUDO=""; if [ "$(id -u)" != "0" ]; then SUDO="sudo"; fi
if [ -z "${BASE:-}" ]; then if [ -w /opt ] || [ -n "$SUDO" ]; then BASE=/opt/ia; else BASE="$HOME/ia"; fi; fi
$SUDO mkdir -p "$BASE" && $SUDO chown -R "$(id -u):$(id -g)" "$BASE"
LOG="$BASE/instalacao.log"; exec > >(tee -a "$LOG") 2>&1
echo "Instalação em $BASE  (registo: $LOG)"

# ---------------------------------------------------------------------
passo "1/6 Verificar a máquina"
if ! command -v nvidia-smi >/dev/null; then erro "Não encontro a placa NVIDIA (nvidia-smi). Escolhe uma máquina com GPU e drivers instalados."; exit 1; fi
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
CUDAV=$(nvidia-smi | grep -oP 'CUDA Version:\s*\K[0-9]+\.[0-9]+' || echo "12.1")
CMAJ=${CUDAV%%.*}; CMIN=${CUDAV##*.}; CNUM=$((CMAJ*10+CMIN))
if   [ $CNUM -ge 128 ]; then TORCH_IDX=cu128
elif [ $CNUM -ge 124 ]; then TORCH_IDX=cu124
else TORCH_IDX=cu121; fi
T3D_IDX=$([ $CNUM -ge 124 ] && echo cu124 || echo cu121)
ok "Driver suporta CUDA $CUDAV → PyTorch $TORCH_IDX"
LIVRE=$(df -BG --output=avail "$BASE" | tail -1 | tr -dc 0-9)
PRECISO=$(( 100 + ${WAN14B:-0}*30 ))
if [ "${LIVRE:-0}" -lt "$PRECISO" ]; then
  erro "Só há ${LIVRE} GB livres em $BASE e são precisos pelo menos ${PRECISO} GB."
  echo "   Na Vast.ai o disco escolhe-se ao alugar (barra 'Disk Space') e não se pode aumentar depois:"
  echo "   aluga uma máquina nova com 150 GB de disco e apaga esta. (Para continuar mesmo assim: FORCAR=1 bash instalar-ia.sh)"
  [ "${FORCAR:-0}" = "1" ] || exit 1
else ok "Disco livre: ${LIVRE} GB"; fi

# ---------------------------------------------------------------------
passo "2/6 Pacotes do sistema"
if command -v apt-get >/dev/null; then
  $SUDO apt-get update -y
  $SUDO env DEBIAN_FRONTEND=noninteractive apt-get install -y git git-lfs wget curl build-essential ffmpeg libgl1 libglib2.0-0 ninja-build unzip
else aviso "Sistema sem apt: instala à mão git, ffmpeg, build-essential e ninja."; fi
if ! command -v uv >/dev/null; then curl -LsSf https://astral.sh/uv/install.sh | sh; fi
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
command -v uv >/dev/null && ok "uv $(uv --version | cut -d' ' -f2)" || { erro "Falhou a instalação do uv"; exit 1; }

# ---------------------------------------------------------------------
passo "3/6 ComfyUI"
cd "$BASE"
[ -f ComfyUI/main.py ] || { rm -rf ComfyUI; git clone --depth 1 https://github.com/comfyanonymous/ComfyUI.git; }
cd ComfyUI && git pull --ff-only || true
[ -d .venv ] || uv venv -p 3.12 .venv
source .venv/bin/activate
uv pip install --index-url "https://download.pytorch.org/whl/$TORCH_IDX" torch torchvision torchaudio
uv pip install -r requirements.txt
uv pip install "huggingface_hub[hf_transfer]" hf_transfer opencv-python-headless imageio-ffmpeg
cd custom_nodes
[ -f ComfyUI-Manager/__init__.py ] || rm -rf ComfyUI-Manager; [ -d ComfyUI-Manager ] || git clone --depth 1 https://github.com/ltdrdata/ComfyUI-Manager.git
[ -f ComfyUI-VideoHelperSuite/__init__.py ] || rm -rf ComfyUI-VideoHelperSuite; [ -d ComfyUI-VideoHelperSuite ] || git clone --depth 1 https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git
for d in ComfyUI-Manager ComfyUI-VideoHelperSuite; do [ -f "$d/requirements.txt" ] && uv pip install -r "$d/requirements.txt"; done
cd ..
python -c "import torch;print('GPU:',torch.cuda.get_device_name(0),'| CUDA ok' if torch.cuda.is_available() else 'SEM CUDA')"
deactivate
ok "ComfyUI instalado"

# ---------------------------------------------------------------------
passo "4/6 Descarregar os modelos (demora: ~90 GB)"
cat > "$BASE/baixar_modelos.py" <<'PY'
# Procura os ficheiros certos em cada repositório (os nomes mudam com as versões) e põe-nos nas pastas do ComfyUI.
import os, re, sys, shutil
from huggingface_hub import HfApi, hf_hub_download
os.environ.setdefault("HF_HUB_ENABLE_HF_TRANSFER","1")
M=sys.argv[1]; WAN14=os.environ.get("WAN14B")=="1"
api=HfApi(token=os.environ.get("HF_TOKEN") or None)
falhas=[]
def get(repos, padrao, pasta, preferir=None, nome=None):
    """repos: lista de repositórios a tentar; padrao: regex no caminho; preferir: regex de desempate"""
    for repo in repos:
        try: files=api.list_repo_files(repo)
        except Exception as e: print(f"  · {repo}: não acessível ({type(e).__name__})"); continue
        c=[f for f in files if re.search(padrao,f,re.I) and f.endswith((".safetensors",".pth",".gguf"))]
        if preferir: c=sorted(c,key=lambda f:(not re.search(preferir,f,re.I),len(f)))
        else: c=sorted(c,key=len)
        if not c: continue
        f=c[0]; dest=os.path.join(M,pasta,nome or os.path.basename(f))
        if os.path.exists(dest) and os.path.getsize(dest)>1_000_000: print(f"  ✔ já existe {pasta}/{os.path.basename(dest)}"); return
        os.makedirs(os.path.dirname(dest),exist_ok=True)
        try: tam=api.get_paths_info(repo,[f])[0].size or 0
        except Exception: tam=0
        livre=shutil.disk_usage(os.path.dirname(dest)).free
        if tam and livre<tam+1_000_000_000:
            print(f"  ✖ {os.path.basename(f)}: precisa de {tam/1e9:.1f} GB e só há {livre/1e9:.1f} GB livres no disco"); falhas.append(os.path.basename(f)); return
        print(f"  ↓ {repo} :: {f}  ({tam/1e9:.1f} GB)",flush=True)
        tmp=os.path.join(M,".baixar");os.makedirs(tmp,exist_ok=True)
        try:
            # descarrega direto para o disco do ComfyUI (sem cópia extra na cache)
            p=hf_hub_download(repo,f,local_dir=tmp,token=os.environ.get("HF_TOKEN") or None)
            shutil.move(p,dest);shutil.rmtree(tmp,ignore_errors=True)
            print(f"  ✔ {pasta}/{os.path.basename(dest)}  ({os.path.getsize(dest)/1e9:.1f} GB)"); return
        except Exception as e:
            shutil.rmtree(tmp,ignore_errors=True);print(f"  ✖ {os.path.basename(f)}: {str(e)[:160]}")
    falhas.append(f"{pasta} ← {padrao}")
print("FLUX.1 Kontext [dev]")
get(["Comfy-Org/flux1-kontext-dev_ComfyUI"], r"diffusion_models/.*kontext.*fp8.*", "diffusion_models", preferir=r"scaled")
get(["comfyanonymous/flux_text_encoders"], r"^clip_l\.safetensors$", "text_encoders")
get(["comfyanonymous/flux_text_encoders"], r"t5xxl_fp8.*\.safetensors$", "text_encoders", preferir=r"scaled")
get(["Comfy-Org/Lumina_Image_2.0_Repackaged","Comfy-Org/flux1-kontext-dev_ComfyUI","black-forest-labs/FLUX.1-schnell"], r"(^|/)ae\.safetensors$", "vae")
print("Qwen-Image + Qwen-Image-Edit")
get(["Comfy-Org/Qwen-Image_ComfyUI"], r"diffusion_models/qwen_image_fp8", "diffusion_models", preferir=r"e4m3fn")
get(["Comfy-Org/Qwen-Image_ComfyUI"], r"text_encoders/qwen_2\.5_vl_7b_fp8", "text_encoders", preferir=r"scaled")
get(["Comfy-Org/Qwen-Image_ComfyUI"], r"vae/qwen_image_vae", "vae")
get(["Comfy-Org/Qwen-Image-Edit_ComfyUI"], r"diffusion_models/qwen_image_edit.*fp8", "diffusion_models", preferir=r"25\d\d")  # versão mais recente primeiro
print("Wan 2.2 (imagem → vídeo)")
get(["Comfy-Org/Wan_2.2_ComfyUI_Repackaged"], r"diffusion_models/wan2\.2_ti2v_5B", "diffusion_models", preferir=r"fp16")
get(["Comfy-Org/Wan_2.2_ComfyUI_Repackaged"], r"vae/wan2\.2_vae", "vae")
get(["Comfy-Org/Wan_2.2_ComfyUI_Repackaged","Comfy-Org/Wan_2.1_ComfyUI_repackaged"], r"text_encoders/umt5_xxl_fp8", "text_encoders", preferir=r"scaled")
if WAN14:
    get(["Comfy-Org/Wan_2.2_ComfyUI_Repackaged"], r"diffusion_models/wan2\.2_i2v_high_noise_14B_fp8", "diffusion_models", preferir=r"scaled")
    get(["Comfy-Org/Wan_2.2_ComfyUI_Repackaged"], r"diffusion_models/wan2\.2_i2v_low_noise_14B_fp8", "diffusion_models", preferir=r"scaled")
    get(["Comfy-Org/Wan_2.2_ComfyUI_Repackaged","Comfy-Org/Wan_2.1_ComfyUI_repackaged"], r"vae/wan_2\.1_vae", "vae")
print("\nResumo:", "tudo descarregado ✔" if not falhas else "faltam: "+"; ".join(falhas))
if falhas: print("Se algum pede login: cria um token em https://huggingface.co/settings/tokens, aceita a licença do modelo na página dele e corre de novo com HF_TOKEN=...")
PY
cd "$BASE/ComfyUI" && source .venv/bin/activate
HF_HOME="$BASE/hf-cache" WAN14B="${WAN14B:-0}" HF_TOKEN="${HF_TOKEN:-}" python "$BASE/baixar_modelos.py" "$BASE/ComfyUI/models"
deactivate

# ---------------------------------------------------------------------
if [ "${SEM3D:-0}" != "1" ]; then
passo "5/6 Hunyuan3D 2.1 (imagem → 3D)"
cd "$BASE"
[ -f Hunyuan3D-2.1/requirements.txt ] || { rm -rf Hunyuan3D-2.1; git clone --depth 1 https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1.git; }
cd Hunyuan3D-2.1
[ -d .venv ] || uv venv -p 3.10 .venv
source .venv/bin/activate
( set -e
  uv pip install --index-url "https://download.pytorch.org/whl/$T3D_IDX" torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1
  uv pip install -r requirements.txt
  uv pip install setuptools wheel ninja
  cd hy3dpaint/custom_rasterizer && uv pip install --no-build-isolation -e . && cd ../..
  cd hy3dpaint/DifferentiableRenderer && bash compile_mesh_painter.sh && cd ../..
  mkdir -p hy3dpaint/ckpt
  [ -f hy3dpaint/ckpt/RealESRGAN_x4plus.pth ] || wget -q -O hy3dpaint/ckpt/RealESRGAN_x4plus.pth https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth
) && ok "Hunyuan3D 2.1 instalado (os pesos descarregam-se sozinhos na 1.ª vez que abrir)" || aviso "O Hunyuan3D não instalou por completo (vê $LOG). O ComfyUI funciona na mesma."
deactivate
else aviso "Hunyuan3D saltado (SEM3D=1)"; fi

# ---------------------------------------------------------------------
passo "6/6 Scripts para ligar e desligar"
cat > "$BASE/iniciar-ia.sh" <<EOF
#!/usr/bin/env bash
# Liga o ComfyUI (8188) e o Hunyuan3D (7860) em segundo plano. Só aceitam ligações locais: usa o túnel SSH.
cd "$BASE/ComfyUI" && nohup .venv/bin/python main.py --listen 127.0.0.1 --port 8188 --enable-cors-header "*" > "$BASE/comfyui.log" 2>&1 &
echo "ComfyUI a arrancar…  (registo: $BASE/comfyui.log)"
if [ -d "$BASE/Hunyuan3D-2.1/.venv" ]; then
  cd "$BASE/Hunyuan3D-2.1" && HF_HOME="$BASE/hf-cache" nohup .venv/bin/python gradio_app.py --model_path tencent/Hunyuan3D-2.1 --subfolder hunyuan3d-dit-v2-1 --texgen_model_path tencent/Hunyuan3D-2.1 --low_vram_mode --host 127.0.0.1 --port 7860 > "$BASE/hunyuan3d.log" 2>&1 &
  echo "Hunyuan3D a arrancar…  (registo: $BASE/hunyuan3d.log — a 1.ª vez descarrega ~15 GB)"
fi
echo "Nota: os dois juntos não cabem na memória da GPU ao mesmo tempo a trabalhar. Usa um de cada vez."
EOF
cat > "$BASE/parar-ia.sh" <<'EOF'
#!/usr/bin/env bash
pkill -f "ComfyUI/main.py" && echo "ComfyUI parado"; pkill -f "gradio_app.py" && echo "Hunyuan3D parado"; true
EOF
chmod +x "$BASE/iniciar-ia.sh" "$BASE/parar-ia.sh"
ok "Pronto!"
IP=$(curl -s --max-time 5 ifconfig.me || echo "IP_DO_SERVIDOR")
cat <<EOF

=====================================================================
  1) Ligar:      bash $BASE/iniciar-ia.sh
  2) No TEU computador abre um túnel (deixa a janela aberta):
       ssh -L 8188:localhost:8188 -L 7860:localhost:7860 $(whoami)@$IP
     (se a máquina alugada usa outra porta SSH, junta  -p PORTA)
  3) No navegador:
       ComfyUI   → http://localhost:8188   (menu Workflow → Browse Templates:
                   "Flux Kontext", "Qwen Image", "Qwen Image Edit", "Wan 2.2")
       Hunyuan3D → http://localhost:7860
  4) Desligar:   bash $BASE/parar-ia.sh
=====================================================================
EOF
