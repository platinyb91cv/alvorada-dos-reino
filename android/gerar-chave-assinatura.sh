#!/usr/bin/env bash
# Cria a chave de envio (upload key) da Play Store e mostra os 4 segredos a pôr no GitHub.
# Corre no teu computador ou no VPS:  bash android/gerar-chave-assinatura.sh
# GUARDA o ficheiro alvorada-upload.jks e a palavra-passe num sítio seguro (sem eles não podes atualizar a app).
set -euo pipefail
command -v keytool >/dev/null || { echo "Falta o Java. No Ubuntu: apt install -y openjdk-17-jre-headless"; exit 1; }
OUT=${1:-alvorada-upload.jks}
[ -e "$OUT" ] && { echo "Já existe $OUT — não vou substituir."; exit 1; }
PASS=$(openssl rand -base64 24 | tr -d '/+=' | cut -c1-24)
keytool -genkeypair -v -keystore "$OUT" -alias alvorada -keyalg RSA -keysize 4096 -validity 10000 \
  -storepass "$PASS" -keypass "$PASS" -dname "CN=Alvorada dos Reinos, O=Fabis, C=CV" >/dev/null 2>&1
chmod 600 "$OUT"
echo
echo "Chave criada: $OUT"
echo
echo "No GitHub: repositório → Settings → Secrets and variables → Actions → New repository secret"
echo "Cria estes 4 segredos (nome = valor):"
echo
echo "  ALV_KEY_ALIAS      = alvorada"
echo "  ALV_KEYSTORE_PASS  = $PASS"
echo "  ALV_KEY_PASS       = $PASS"
echo "  ALV_KEYSTORE_B64   = (o texto do ficheiro alvorada-upload.jks.b64 criado agora)"
base64 -w0 "$OUT" > "$OUT.b64"
echo
echo "Depois apaga o .b64 (rm $OUT.b64) e guarda o .jks e a palavra-passe num sítio seguro (ex.: gestor de senhas)."
