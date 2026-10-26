# Testes de ponta a ponta (navegador real, Playwright)

Servir o jogo com `cd www && python3 -m http.server 8777` e correr:

| Script | O que verifica |
|---|---|
| `teste_missoes.py` | As 6 missões da Campanha e os capítulos 1–16 de *O meu Reino* (todos os tipos: fundação, lobos, vagas, rival, Rei, Maravilha, forte, economia, campeão, cerco). Cumpre os objetivos e confirma a vitória e o progresso gravado. Testa também a derrota, o botão **Guardar** (mensagem visível por cima da pausa e confirmação no botão), **Continuar** depois de recarregar, e a reconstrução do Centro no cerco. |
| `producao.py` | "Modo produção": cada missão corre sozinha, sem atalhos, durante 6 min de jogo, mais 7 capítulos de combate e uma escaramuça de 10 min contra a IA difícil. Regista erros, o pior tempo por passo da simulação e o FPS. |
| `diario.py` | Desafio do dia dentro do reino: suspende a missão em curso, cumpre-o, grava o melhor tempo e retoma a missão. |
| `queda.py` | O Rei morre → «O reino caiu» → botão «Recomeçar o capítulo». |
| `menu.py` | Textos dos objetivos no menu da campanha e o tempo da Maravilha no jogo. |

Os ficheiros `ultimo-resultado-*.json` são os resultados da última execução.
