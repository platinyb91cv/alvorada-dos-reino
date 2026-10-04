# Alvorada dos Reinos — ficha da Play Store

Tudo o que é preciso para publicar na Google Play Console. Copia e cola cada parte no sítio indicado.

## 1. Ficheiros desta pasta

| Ficheiro | Onde vai na Play Console |
|---|---|
| `icone-512.png` | Presença na loja → Ícone da app (512×512) |
| `grafico-destaque-1024x500.png` | Presença na loja → Gráfico de destaque |
| `captura-1-menu.png` … `captura-5-tutorial.png` | Presença na loja → Capturas de ecrã do telemóvel (1920×1080) |
| `app-release.aab` (sai do GitHub Actions, artefacto **alvorada-play-store**) | Testes / Produção → Criar versão |

## 2. Textos da ficha (português)

**Nome da app** (máx. 30):
```
Alvorada dos Reinos
```

**Descrição curta** (máx. 80):
```
Ergue a tua aldeia, junta um exército e conquista os reinos rivais. Online!
```

**Descrição completa** (máx. 4000):
```
Alvorada dos Reinos é um jogo de estratégia em tempo real feito para o telemóvel.

Começa com um Centro da Vila e três aldeões. Recolhe comida, madeira, ouro e pedra, constrói casas, quintas e quartéis, e faz a tua aldeia crescer da Idade da Pedra até à Idade do Ferro.

⚔️ EXÉRCITOS E BATALHAS
Guerreiros, espadachins, lanceiros, arqueiros, cavalaria, sacerdotes e máquinas de cerco — cada unidade é forte contra umas e fraca contra outras. Forma linhas e colunas, defende, patrulha e derruba as muralhas do rival com aríetes e trebuchets.

🌊 NAVIOS
Constrói uma Doca, pesca, transporta tropas para a outra margem e domina o lago com galés e navios incendiários.

🏰 DEFESAS
Muralhas de madeira e de pedra, portões que só deixam passar os teus, e torres que sobem de nível.

🌐 ONLINE COM AMIGOS
Entra com a tua conta Google, adiciona amigos com o teu código, convida-os para uma partida ou abre uma sala pública. Pontuação Elo, classificação e histórico de partidas.

🏗️ MODO SÓ CONSTRUIR
Sem inimigos: constrói a cidade ao teu ritmo e vê-a crescer.

🎓 TUTORIAL
Um guia passo a passo ensina-te o essencial na primeira partida.

• Três níveis de dificuldade contra o computador
• Guarda automática — continua onde paraste
• Música e sons próprios
• Sem anúncios

Feito em Cabo Verde 🇨🇻
```

**Categoria:** Jogos → Estratégia
**Etiquetas:** Estratégia em tempo real, Construção de cidades, Medieval, Multijogador
**Email de contacto:** fabispaty46@gmail.com
**Website:** https://jogo.krioldns.uk
**Política de privacidade:** https://jogo.krioldns.uk/privacidade.html

## 3. Classificação de conteúdo (questionário IARC)

- Categoria: **Jogo**
- Violência: **Sim** — violência de fantasia/medieval, sem sangue realista, personagens não humanas realistas? → *personagens humanas, sem sangue nem desmembramento*
- Medo, sexualidade, linguagem imprópria, drogas, jogos de azar: **Não**
- Interação entre utilizadores: **Sim** — os jogadores podem conversar durante a partida (mensagens de texto)
- Partilha de localização: **Não** · Compras digitais: **Não**

Resultado esperado: PEGI 7 / Everyone 10+.

## 4. Segurança dos dados (Data safety)

- A app recolhe ou partilha dados? **Sim, recolhe** (não partilha com terceiros)
- Dados cifrados em trânsito: **Sim** · Os utilizadores podem pedir para apagar: **Sim**
- Dados recolhidos:
  - **Informações pessoais → Nome, Endereço de email** — Funcionalidade da app, Gestão de conta — obrigatório para jogar
  - **Fotos → Fotografia de perfil** (da conta Google) — Gestão de conta
  - **Atividade na app → Outras ações (resultados das partidas, pontuação)** — Funcionalidade da app
  - **Mensagens → Outras mensagens na app (conversa)** — Funcionalidade da app — *não guardadas* (marca "processado temporariamente")
- Link para apagar a conta: **https://jogo.krioldns.uk/apagar-conta.html**

## 5. Público-alvo

- Idade-alvo: **13+** (não marcar crianças)
- Anúncios: **Não contém anúncios**

## 6. Assinatura e envio

1. Corre uma vez `bash android/gerar-chave-assinatura.sh` (no teu PC ou no VPS) e cria os 4 segredos no GitHub como o script indica.
2. Faz `git push` (ou Actions → **Gerar APK e AAB** → Run workflow). No fim aparece o artefacto **alvorada-play-store** com o `app-release.aab`.
3. Play Console → Criar app → preenche as secções acima → **Testes internos** → Criar versão → envia o `.aab`.
4. Ativa a **Assinatura de apps do Google Play** (recomendado, já vem ligado por defeito).
5. Contas novas de programador precisam de um **teste fechado com 12 testadores durante 14 dias** antes de poder publicar em produção.

**Importante:** guarda o ficheiro `alvorada-upload.jks` e a palavra-passe num sítio seguro (gestor de senhas). Se se perderem, é preciso pedir à Google para trocar a chave de envio.
