# Alvorada dos Reinos

Jogo de estratégia em tempo real para Android (HTML5 Canvas + Capacitor 8).
Começas na Idade da Pedra com um Centro da Vila e 3 aldeões. Recolhes comida, madeira, ouro e pedra, avanças até à Idade do Ferro e destróis o reino rival (IA com 3 dificuldades).

## Funcionalidades
- Vista isométrica, mapa aleatório 80×80 com lago central navegável, lagos menores, florestas, nevoeiro de guerra e minimapa em losango
- 3 idades (Pedra, Bronze, Ferro) com edifícios que mudam de estilo
- Exército: Guerreiro, Lanceiro, Espadachim, Arqueiro, Besteiro, Cavalaria, Cavalaria Pesada, Cavalaria Arqueira, Sacerdote
- Cerco (Oficina): Aríete, Catapulta, Trebuchet
- Naval (Doca): Barco de Pesca, Transporte (8 lugares), Galé, Navio Incendiário, Navio Pesado; cardumes que reaparecem
- Contra-unidades: bónus por classe (infantaria, arqueiros, cavalaria, cerco, navios) e armadura contra projéteis
- Defesas: Paliçada, Muralha de Pedra, Muralha Fortificada, Portões (aliados passam, inimigos não, Abrir/Fechar), Torre de Vigia → Flechas → Fortificada
- Formações (Livre, Linha, Coluna, Defensiva, Cerco) e comandos (Atacar-mover, Patrulhar, Defender área, Manter posição, Recuar, Parar)
- Caça (gazelas e javalis), 7 tecnologias, Templo com Sacerdotes que curam e convertem, Maravilha (vitória aos 5 min)
- IA com 3 dificuldades: escolhe unidades contra o exército inimigo, constrói muralhas e portões, usa cerco contra muralhas e Maravilhas, pesca e combate na água
- Guardar automático a cada 45 s e ao sair; Continuar no menu; pausa automática; vibração (desligável)

## Testes automáticos
Requer Python 3 + Playwright (`pip install playwright && playwright install chromium`).
```bash
cd tests
python3 run_tests.py      # 31 testes por sistema
python3 run_ai.py 101 202 # partidas IA vs IA com verificação de regras
python3 run_ui.py         # pausa, auto-save, toque longo, desempenho
```

## Gerar o APK

### Opção A: Android Studio (no teu PC)
Requisitos: Node.js 20+, Android Studio (com JDK 21 incluído).

```bash
npm install
npx cap sync android
npx cap open android
```
No Android Studio: **Build → Build App Bundle(s) / APK(s) → Build APK(s)**.
O APK fica em `android/app/build/outputs/apk/debug/app-debug.apk`.

Pela linha de comandos (com o SDK instalado):
```bash
npm run apk        # Linux/macOS
npm run apk:win    # Windows
```

### Opção B: GitHub Actions (sem instalar nada)
1. Cria um repositório no GitHub e faz push desta pasta.
2. O workflow `.github/workflows/build-apk.yml` corre sozinho.
3. Em **Actions → Gerar APK → Artifacts**, descarrega `alvorada-dos-reinos-apk`.

### Instalar no telemóvel
Copia o `app-debug.apk` para o telemóvel e abre-o (permite "instalar apps desconhecidas").

## Testar no browser
```bash
npm run serve      # abre http://localhost:8080
```

## Estrutura
- `www/index.html`: o jogo inteiro (motor, mapa, IA, interface)
- `www/fonts/`: fontes incluídas para funcionar offline
- `android/`: projeto nativo (orientação horizontal, ecrã inteiro, ecrã sempre ligado)

## Controlos
- Toque: selecionar. Toque duplo: todas as unidades do mesmo tipo à vista.
- Com unidades selecionadas, toca no chão (mover), num recurso (recolher), num inimigo (atacar) ou numa obra (construir).
- Arrastar: câmara. Dois dedos: zoom. Botão ⬚: seleção em caixa.
- PC: botão esquerdo seleciona/arrasta caixa, direito dá ordens, WASD/setas movem a câmara, roda faz zoom, espaço pausa.

## Para afinar o jogo
No topo do `<script>` em `www/index.html`:
- `UNITS` e `BLDS`: vida, ataque, custos, tempos
- `TECHS`: custos, tempos e efeitos das tecnologias
- `TOWER`: níveis das torres
- `bonus` em cada unidade: dano extra contra uma classe
- `AGE_COST` e `AGE_TIME`: custo e tempo das idades
- `DIFF`: força da IA, momento do primeiro ataque e tamanho das vagas
- `W`, `H`: tamanho do mapa (80×80)

Depois de editar: `npx cap sync android` e voltar a compilar.

## Atualização visual das unidades (v5)
- Arte nova, original e procedural para aldeões (4 variantes, ferramentas por profissão, carga visível) e para todas as unidades militares, de cerco e o sacerdote.
- Progressão visual por idade (Pedra: couro/vime · Bronze · Ferro) e cor da equipa só em escudo, faixa, capa, penacho e detalhes.
- Sombras, base de seleção na cor da equipa, barra de vida só quando selecionada/em combate/ferida há pouco, cadáveres que caem e desvanecem, faíscas, pó da cavalaria e do cerco.
- Desempenho: sprites gerados uma vez e guardados em cache (LRU com limite de memória), recortados à área visível, com no máximo 10 sprites novos em alta definição por frame.
- `tests/demo_units.py` gera a cena de demonstração; `tests/perf_units.py` mede 50/100/200 unidades em combate.

## Som (v6)
- Todo o áudio é original e sintetizado no próprio código (Web Audio API): não há ficheiros de som.
- Música generativa em modo dórico: menu (harpa), paz (alaúde, flauta, bordão, tambor suave) e batalha (ritmo mais rápido e percussão). Muda sozinha quando há combate à vista.
- 67 efeitos com variações: vozes de seleção e de ordens (sílabas inventadas), machado, picareta, enxada, martelo, espadas (madeira na Idade da Pedra, metal depois), lanças, arcos, bestas, cavalos, cerco, explosões, desabamentos, sacerdotes, barcos, alertas e fanfarras.
- Ambiente: vento, água junto ao lago, pássaros em paz e ruído de batalha.
- Som posicional: volume e lado (esquerda/direita) conforme a posição no ecrã; o que está no nevoeiro não se ouve.
- Limites: máximo de 28 vozes e 7 sons novos por frame; o som não usa o gerador aleatório da simulação, por isso a jogabilidade fica igual.
- Menu de pausa: Som ligado/desligado e volumes de Música, Efeitos e Ambiente (guardados no aparelho).
- `tests/run_audio.py` (14 testes) e `tests/audio_demo.py` (gera uma amostra MP3 com todos os sons e músicas).

## Interface nova e modo online (v7)
- HUD redesenhado: barra de recursos com ícones originais, contador de aldeões em cada recurso e brilho quando o valor sobe ou desce; escudo da idade com barra de progresso; botões laterais com contadores (aldeões ociosos, exército); painel inferior com retrato da unidade (gerado a partir dos sprites do jogo), vida com números, ícones de ataque, armadura, alcance e velocidade, e botões com retratos das unidades e edifícios.
- **Jogar online**: salas com código de 4 letras para 2 jogadores (azul contra vermelho), conversa com frases rápidas, desistir, revanche na mesma sala, retoma automática se a ligação cair e botão "Voltar à partida" se a app fechar.
- Tecnologia: simulação em lockstep (turnos de 100 ms e atraso automático conforme o ping). Os estados são comparados a cada 5 s; se divergirem, o anfitrião reenvia o estado completo.
- Servidor: pasta `server/`. As instruções para o VPS estão em `server/LEIAME-SERVIDOR.md`.
- Testes: `tests/run_online.py` (12 testes com servidor real e dois navegadores) e `LAG=300 python3 tests/run_online_lag.py`.

## Contas Google e base de dados Supabase (v8)
- Para entrar no jogo é preciso uma conta Google, com login através do Supabase. A sessão fica guardada no aparelho, por isso depois do primeiro login dá para jogar contra o computador sem internet.
- Perfil: nome editável, imagem do Google, pontuação Elo, vitórias e derrotas online e contra o computador, histórico das últimas partidas.
- Classificação dos 50 melhores jogadores online.
- Amigos: cada jogador tem um código de amigo de 6 letras. No ecrã de amigos vês quem está ligado ou a jogar e podes convidar um amigo para uma partida (o convite aparece no ecrã dele).
- Salas públicas: quem cria uma sala pode deixá-la aberta a qualquer jogador; as salas abertas aparecem em "Jogar online".
- O servidor de jogo confirma o login de cada jogador no Supabase e regista o resultado só quando os dois jogadores estão de acordo. Se um sair e não voltar, o outro ganha por abandono.
- Ficheiros:
  - `supabase/migrations/*.sql` — tabelas, regras de segurança (RLS) e funções.
  - `supabase/LEIAME-SUPABASE.md` — passos para o Google e o Supabase.
  - `server/alvorada.env` — configuração do servidor (secreta).
- Android: os plugins `@capacitor/browser` e `@capacitor/app` tratam do login no Chrome e do regresso à app (`cv.fabis.alvorada://login-callback`).
- Testes:
  - `tests/run_online.py`: 22 testes com uma imitação do Supabase e dois navegadores.
  - Testes do SQL num Postgres local (PGlite): 19.
