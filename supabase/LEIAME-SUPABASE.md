# Contas, login Google e base de dados (Supabase)

Projeto Supabase: **qjwdgjlimlslrccuppdb** (`https://qjwdgjlimlslrccuppdb.supabase.co`), na organização "alvorada dos reinos".
O jogo já vem configurado com este endereço e com a chave publicável. Essa chave pode estar dentro da app.

## O que fica guardado
| Tabela | Conteúdo | Quem pode ver ou mudar |
|---|---|---|
| `profiles` | nome, imagem, pontuação Elo, vitórias e derrotas, jogos contra o computador, código de amigo | Todos os jogadores com conta podem ver. Cada um só muda o próprio nome e a imagem. |
| `matches` | partidas online: vencedor, motivo, duração, pontos ganhos e perdidos | Só os dois jogadores da partida. |
| `friendships` | pedidos de amizade e amigos | Só os envolvidos, e sempre através das funções. |
| `private.server_keys` | resumo SHA-256 da chave do servidor de jogo | Ninguém pela API. |

Os resultados online só entram através da função `record_match`, que exige a chave secreta do servidor. Assim, um jogador não consegue dar pontos a si próprio.

## 1. Criar as tabelas (uma vez)
No Supabase, abre **SQL Editor → New query**. Cola e corre, por esta ordem:
1. `migrations/20261003000000_alvorada_online.sql`
2. `migrations/20261003000100_server_key.sql`

Se preferires, posso ser eu a aplicá-las pelo conector do Supabase. Basta aprovares o pedido quando aparecer.

## 2. Credenciais Google (Google Cloud Console)
1. Abre https://console.cloud.google.com, cria um projeto (por exemplo, "Alvorada dos Reinos") e vai a **APIs e serviços**.
2. Em **Ecrã de consentimento OAuth**, escolhe "Externo" e preenche:
   - nome da app: Alvorada dos Reinos;
   - o teu email de suporte;
   - o domínio `krioldns.uk`.
   - Depois publica a app em "Em produção".
3. Em **Credenciais → Criar credenciais → ID de cliente OAuth → Aplicação Web**:
   - Origens JavaScript autorizadas: `https://jogo.krioldns.uk`
   - URIs de redirecionamento autorizados: `https://qjwdgjlimlslrccuppdb.supabase.co/auth/v1/callback`
4. Copia o **ID de cliente** e o **Segredo do cliente**.

## 3. Ativar o Google no Supabase
1. Vai a **Authentication → Sign In / Providers → Google**. Ativa o fornecedor, cola o ID de cliente e o segredo e guarda.
2. Em **Authentication → URL Configuration**:
   - Site URL: `https://jogo.krioldns.uk`
   - Redirect URLs (acrescenta as três):
     - `cv.fabis.alvorada://login-callback` (é por aqui que a app Android volta depois do login)
     - `https://jogo.krioldns.uk/**`
     - `http://localhost:8080/**` (para testes no PC)

## Como funciona o login na app Android
1. O botão "Entrar com Google" abre o Google numa aba do Chrome. O Google não deixa fazer login dentro de uma WebView.
2. Depois do login, o Google volta para `cv.fabis.alvorada://login-callback`.
3. O Android reabre o jogo, que troca o código pela sessão (PKCE).
4. A sessão fica guardada no telemóvel. Sem internet, dá para jogar contra o computador com a última sessão.

## Verificar
- Depois de entrares pela primeira vez, aparece uma linha na tabela `profiles` (Table Editor) com o teu nome do Google.
- Corre a partida online de teste e confirma que aparece uma linha em `matches`.
