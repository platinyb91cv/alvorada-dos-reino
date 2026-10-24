# Vida da aldeia 2

Só código; 0 créditos Meshy e nenhuma imagem nova (a vila neutra reutiliza a casa aprovada da idade).

| Melhoria | O que faz |
|---|---|
| Profissões | Ícone sobre o aldeão (selecionado, ocioso ou com zoom ≥1,7): 🪓 lenhador, ⛏️ mineiro, 🪨 pedreiro, 🌾 agricultor, 🐑 pastor, 🏹 caçador, 🎣 pescador, 🫐 coletor, 🔨 construtor, 💤 ocioso. Painel mostra a profissão e o resumo por profissão. |
| Gestão no telemóvel | Botão 🏭: percorre os edifícios de produção parados (depois do primeiro minuto). |
| Defesas ocupadas | Soldados abrigados aparecem no topo das torres, centros e vilas, a olhar em volta (até 3). |
| Formações com vantagens | Lanceiro a ≤2 casas protege arqueiros/besteiros: +2 armadura corpo a corpo. Infantaria parada/em combate com 2+ companheiros a ≤2 casas: +1 armadura e +1 contra flechas. Cavalaria contra inimigo ocupado com outra unidade: +3 de dano (flanco). |
| Caravanas | Com soldados aliados a ≤4 casas à chegada: +25% de ouro. Destruir uma carroça rival dá 60% do ouro da viagem (mín. 40). |
| Vilas neutras | 2 vilas entre os reinos. 2+ soldados por perto sem inimigos durante 20 s → aliada: 2 ouro + 2 comida a cada 5 s, +5 população, abrigo para 5, parceira de comércio. O rival toma-a com 30 s de presença sem defensores. Destruí-la = saque (150 ouro, 100 comida). A IA também as disputa. |
| Aldeia viva | Fumo nas chaminés (casa, centro, ferreiro, vila) e luzes nas janelas à noite (só visual). |

As regras de jogo correm no `step` e são deterministas (sem `Math.random`), por isso funcionam online. Testes: `tests/check_vida_aldeia2.cjs` e os 10 anteriores. Simulação de 14 min com a IA difícil: sem erros; a IA ganhou as duas vilas. Capturas nesta pasta; `jogo.verification.json` tem os valores medidos no jogo (dano protegido 8 vs 10, flanco 10 vs 7, emboscada +50 ouro).
