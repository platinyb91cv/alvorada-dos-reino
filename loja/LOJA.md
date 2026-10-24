# Loja do Reino — como funciona e como ligar

A loja já está no jogo (menu principal → **Loja**), mas **desligada**. Os jogadores veem os artigos com "em breve" e nada é cobrado.

Só vende aparência; nada dá vantagem em combate. O único bónus é **+100 de ouro com um anúncio**, e só contra a IA, uma vez por partida. Nunca aparece online nem no Desafio diário.

## Artigos (ids = ids dos produtos na Play Console)

| id | O que dá | Preço sugerido |
|---|---|---|
| `capas_reais` | 6 capas novas para o Rei | 0,99 € |
| `cor_turquesa`, `cor_rosa`, `cor_esmeralda`, `cor_indigo` | cor do reino (edifícios, bandeiras, soldados) | 0,99 € cada |
| `pacote_real` | capas reais + as 4 cores | 2,99 € |
| `sem_anuncios` | sem anúncios; o bónus de ouro passa a ser dado sem anúncio | 1,99 € |
| `apoio_fundador` | moldura de Fundador no perfil + Pacote Real | 4,99 € |
| `passe` | passe da temporada (em breve, ainda sem conteúdo) | — |

Os artigos estão em `LOJA_ITENS`, no `www/index.html`.

## Experimentar sem pagar
Abre o jogo com `?loja=teste` no endereço, por exemplo `http://localhost:8777/index.html?loja=teste`. As compras e o anúncio são simulados.

O teste automático está em `tests/e2e/loja.py`.

## Ligar as compras de verdade
1. **Conta de comerciante do Google Play.** Não é possível a partir de Cabo Verde. É preciso uma empresa ou residência fiscal num país suportado (por exemplo Portugal) ou uma editora parceira.
2. **Produtos na Play Console.** Em Monetizar → Produtos → Produtos na app, cria os ids da tabela como produtos únicos (não consumíveis).
3. **Plugin de compras no APK.**
   - Instala-o com `npm i cordova-plugin-purchase` e depois corre `npx cap sync android`.
   - No arranque, regista os produtos com `CdvPurchase.store.register(...)`.
   - No evento `approved`, chama `LOJA.give(id)`.
4. **Verificação no servidor.** Valida o recibo da compra no servidor (Google Play Developer API) e guarda as compras na conta do jogador. Assim não se perdem ao trocar de telemóvel e não podem ser forjadas.
5. **Ligar no código.** Em `LOJA_CFG`, põe `pagamentos:true`.

## Ligar os anúncios de verdade
1. **AdMob.** Cria uma conta AdMob e confirma que paga para o teu país. Depois cria uma unidade "Anúncio com recompensa".
2. **Plugin no APK.** Corre `npm i @capacitor-community/admob` e depois `npx cap sync android`. Põe o App ID no `AndroidManifest.xml`.
3. **Ligar no código.** Em `LOJA_CFG`, põe `anuncios:true` e `admobId:'<id da unidade>'`.
4. **Play Console.** Declara "Contém anúncios" na ficha e no formulário de Segurança dos dados.

## Estado
- **Interface, desbloqueios, cores, capas e moldura no jogo:** testados no modo de teste.
- **Adaptadores `PAY` (CdvPurchase) e `ADS` (AdMob):** escritos mas **NOT TESTED**, porque os plugins ainda não estão no APK.
- **Compras guardadas:** por agora ficam só no telemóvel (`localStorage`). Têm de passar para a conta no servidor antes de ligar os pagamentos.
