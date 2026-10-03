#!/usr/bin/env bash
# Alvorada dos Reinos — instalação completa no VPS (Ubuntu, como root)
# Uso:  bash /opt/alvorada/instalar-vps.sh
set -euo pipefail
DOM="${DOM:-jogo.krioldns.uk}"; PORTA="${PORTA:-8090}"; DIR=/opt/alvorada
echo "== 1/6 Pacotes"
apt-get update -y
apt-get install -y curl unzip nginx certbot python3-certbot-nginx
if ! command -v node >/dev/null || [ "$(node -p 'process.versions.node.split(".")[0]')" -lt 18 ]; then
  curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && apt-get install -y nodejs
fi
echo "node $(node -v)"
echo "== 2/6 Dependências do servidor"
cd "$DIR/server" && npm install --omit=dev --no-audit --no-fund
if ss -ltn | grep -q ":$PORTA "; then echo "AVISO: a porta $PORTA já está ocupada. Corre outra vez com PORTA=8095 bash $0"; exit 1; fi
sed -i "s/^PORT=.*/PORT=$PORTA/" "$DIR/server/alvorada.env"
chown -R www-data:www-data "$DIR" && chmod 600 "$DIR/server/alvorada.env"
echo "== 3/6 Serviço systemd"
cat > /etc/systemd/system/alvorada.service <<UNIT
[Unit]
Description=Alvorada dos Reinos - servidor online
After=network.target

[Service]
WorkingDirectory=$DIR/server
EnvironmentFile=$DIR/server/alvorada.env
ExecStart=$(command -v node) server.js
Restart=always
RestartSec=3
User=www-data

[Install]
WantedBy=multi-user.target
UNIT
systemctl daemon-reload && systemctl enable --now alvorada && systemctl restart alvorada
sleep 2; curl -fsS "http://127.0.0.1:$PORTA/health" && echo
echo "== 4/6 nginx"
cat > /etc/nginx/sites-available/$DOM <<NGX
server {
  listen 80;
  server_name $DOM;
  location / {
    proxy_pass http://127.0.0.1:$PORTA;
    proxy_http_version 1.1;
    proxy_set_header Upgrade \$http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host \$host;
    proxy_read_timeout 3600s;
  }
}
NGX
ln -sf /etc/nginx/sites-available/$DOM /etc/nginx/sites-enabled/$DOM
nginx -t && systemctl reload nginx
echo "== 5/6 HTTPS (certbot)"
if ! getent hosts "$DOM" >/dev/null; then echo "AVISO: o DNS de $DOM ainda não aponta para este VPS. Cria o registo A e corre: certbot --nginx -d $DOM"; else
  certbot --nginx -d "$DOM" --non-interactive --agree-tos --register-unsafely-without-email --redirect || echo "AVISO: certbot falhou; corre manualmente: certbot --nginx -d $DOM"; fi
if ! grep -q "^ALV_SERVER_SECRET=..*" "$DIR/server/alvorada.env"; then echo "AVISO: falta a chave do servidor. Corre: bash $DIR/server/trocar-chave.sh (sem ela as partidas não são registadas)"; fi
echo "== 6/6 Verificação"
curl -fsS "https://$DOM/health" && echo && echo "PRONTO: abre https://$DOM no navegador." || echo "Verifica o DNS/HTTPS. Registo: journalctl -u alvorada -n 50"
