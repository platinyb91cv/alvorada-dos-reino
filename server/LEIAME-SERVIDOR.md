# Servidor online — Alvorada dos Reinos

O servidor não corre o jogo. Também confirma o login Google de cada jogador no Supabase e regista os resultados com pontuação Elo. A configuração está em `alvorada.env`, que já vem preenchido com o projeto Supabase e a chave secreta do servidor. **Não partilhes esse ficheiro.**

 Só cria salas com um código de 4 letras e passa as ordens de um jogador para o outro. Os dois telemóveis correm a mesma simulação (lockstep). Também serve o próprio jogo, por isso quem estiver num PC pode jogar no navegador em `https://jogo.krioldns.uk`.

- Consumo: cerca de 2–3 KB/s por jogador durante a partida.
- Requisitos: Node.js 18 ou mais recente e o pacote `ws`.

## Instalar no VPS (Ubuntu, como root)

### 1. DNS
No painel do domínio krioldns.uk, cria um registo **A**:

| Nome | Tipo | Valor |
|---|---|---|
| `jogo` | A | `109.199.111.194` |

### 2. Enviar os ficheiros
Corre isto no teu PC, na pasta onde está o zip:

```bash
scp alvorada-dos-reinos.zip root@109.199.111.194:/opt/
```

### 3. Instalar no VPS

```bash
cd /opt && apt-get update && apt-get install -y unzip
unzip -o alvorada-dos-reinos.zip            # cria /opt/alvorada
node -v || (curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && apt-get install -y nodejs)
cd /opt/alvorada/server && npm install --omit=dev
chown www-data /opt/alvorada/server/alvorada.env && chmod 600 /opt/alvorada/server/alvorada.env
ss -ltnp | grep 8090 || echo "porta 8090 livre"
```

Se a porta 8090 estiver ocupada, usa outra porta (por exemplo 8095) no serviço e no nginx.

### 4. Serviço (arranca sozinho e reinicia se falhar)

```bash
cat > /etc/systemd/system/alvorada.service <<'UNIT'
[Unit]
Description=Alvorada dos Reinos - servidor online
After=network.target

[Service]
WorkingDirectory=/opt/alvorada/server
ExecStart=/usr/bin/node server.js
EnvironmentFile=/opt/alvorada/server/alvorada.env
Restart=always
RestartSec=3
User=www-data

[Install]
WantedBy=multi-user.target
UNIT
systemctl daemon-reload && systemctl enable --now alvorada && systemctl status alvorada --no-pager
```

### 5. nginx com HTTPS (o Android exige wss://)

```bash
cat > /etc/nginx/sites-available/jogo.krioldns.uk <<'NGX'
server {
  listen 80;
  server_name jogo.krioldns.uk;
  location / {
    proxy_pass http://127.0.0.1:8090;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_read_timeout 3600s;
  }
}
NGX
ln -sf /etc/nginx/sites-available/jogo.krioldns.uk /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
apt-get install -y certbot python3-certbot-nginx
certbot --nginx -d jogo.krioldns.uk
```

### 6. Verificar

```bash
curl https://jogo.krioldns.uk/health      # {"ok":true,"rooms":0,"players":0}
journalctl -u alvorada -f                 # registo em tempo real
```

## Usar
- No jogo, toca em **Jogar online**, depois em **Criar sala** e envia o código ao teu amigo.
- O amigo toca em **Jogar online**, escreve o código e toca em **Entrar**.
- O endereço do servidor já vem preenchido (`wss://jogo.krioldns.uk/ws`). Se usares outro domínio, muda-o em **Servidor**.

## Atualizar
Envia o zip novo, descompacta-o por cima e corre `systemctl restart alvorada`.

Os dois jogadores têm de ter a mesma versão da app. Se não tiverem, o jogo avisa.

## Contas e base de dados
O Supabase e o login Google configuram-se uma vez. Os passos estão em `../supabase/LEIAME-SUPABASE.md`.

## Testes locais

```bash
cd server && npm install && PORT=8791 node server.js           # sem SUPABASE_URL: modo de desenvolvimento, sem contas
FAKE_LAG=200 PORT=8791 node server.js                           # simula 200 ms de atraso em cada sentido
```
