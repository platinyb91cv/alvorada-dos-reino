#!/usr/bin/env bash
# Troca a chave secreta do servidor de jogo (ALV_SERVER_SECRET).
# A chave nova é gerada AQUI no VPS e nunca sai daqui: para o Supabase só vai o resumo SHA-256.
# Uso:  bash /opt/alvorada/server/trocar-chave.sh
set -euo pipefail
ENV=/opt/alvorada/server/alvorada.env
[ -f "$ENV" ] || { echo "Falta $ENV"; exit 1; }
NEW=$(openssl rand -hex 32)
HASH=$(printf %s "$NEW" | sha256sum | cut -d' ' -f1)
BAK="$ENV.bak.$(date +%Y%m%d%H%M%S)"
cp -p "$ENV" "$BAK"
echo
echo "1) No Supabase (SQL Editor), corre esta linha e confirma que deu Success:"
echo
echo "   insert into private.server_keys(hash, note) values ('$HASH', 'chave $(date +%F)');"
echo
read -r -p "Já correste a linha acima? (s/n) " R
[ "$R" = "s" ] || { echo "Cancelado. Nada foi alterado."; rm -f "$BAK"; exit 1; }
if grep -q '^ALV_SERVER_SECRET=' "$ENV"; then sed -i "s/^ALV_SERVER_SECRET=.*/ALV_SERVER_SECRET=$NEW/" "$ENV"; else echo "ALV_SERVER_SECRET=$NEW" >> "$ENV"; fi
chmod 600 "$ENV"
systemctl restart alvorada && sleep 2 && systemctl is-active alvorada
echo
echo "2) Por fim, apaga as chaves antigas no Supabase (SQL Editor):"
echo
echo "   delete from private.server_keys where hash <> '$HASH';"
echo
echo "Resumo da chave nova (não é secreto): $HASH"
echo "Confirmação: o alvorada.env tem agora a chave com resumo $(grep '^ALV_SERVER_SECRET=' "$ENV" | cut -d= -f2 | tr -d '\n' | sha256sum | cut -c1-8)… (tem de começar igual ao de cima)"
echo "IMPORTANTE: corre este script só UMA vez; se o repetires, usa a linha de insert da última execução."
