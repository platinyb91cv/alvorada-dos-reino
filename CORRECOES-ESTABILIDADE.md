# Correções de estabilidade e gravações

Base: versão mais recente de `vida-aldeia-curral`, commit `ea291ca`. Este ramo preserva as alterações gráficas e as correções de travamento do Claude. Não faz merge nem publica na Play Store.

## Alterações

- Gravações na nuvem alteram apenas o lugar pretendido: partida normal ou Reino. A revisão `updated_at` é comparada no UPDATE; um conflito obriga a reler e preservar o outro lugar. INSERT concorrente é tratado sem upsert destrutivo. O mesmo lugar alterado por outro dispositivo causa conflito seguro, sem substituição automática.
- Operações do mesmo cliente respeitam a ordem; pedidos têm limite de 15 segundos. Um erro de rede mantém a gravação local.
- A conta e a geração da sessão ficam vinculadas ao pedido. Sair, trocar de conta ou entrar como visitante invalida respostas pendentes, inclusive ao voltar à mesma conta.
- Partidas normais locais passam a usar as chaves por conta já usadas pelo Reino. As gravações antigas são migradas; terminar uma partida deixa um marcador vazio para evitar reimportar a cópia antiga.
- A libertação de atlas agrupa os aliases pela mesma fonte, mantendo a imagem da carroça de carga enquanto estiver em uso.
- A pontuação da partida anterior volta a ser escondida ao terminar uma partida local.
- O workflow de APK executa regressões JavaScript e testes de navegador antes de compilar. Neste ramo os APK/AAB ficam em artefactos para revisão; as Releases continuam reservadas ao main/master.

## Validação

- `node tests/check_cloud_saves.cjs`: 10 cenários com o SDK Supabase incluído no jogo e transporte HTTP simulado, incluindo dois clientes concorrentes, INSERT simultâneo, conflito no mesmo lugar, troca de conta, saída/entrada na mesma conta, migração e falha de rede.
- Todos os `tests/*.cjs`.
- Navegador real: `nao_congela.py`, `atlas_leve.py`, `reino_save.py`, `estabilidade.py`. O último verifica o atlas da carroça, pontuação, partidas locais por conta, migração/limpeza e deslocações de câmara com contexto móvel.
- `tests/run_online.py`: dois jogadores, sincronização, recuperação de dessincronização, reconexão/reabertura, desistência, revanche, ranking, amigos e apagar conta, com servidor Node real e serviço de autenticação/base simulados. Não utiliza dados de jogadores reais.
- Consultas de leitura confirmaram na base do projeto as colunas e políticas de acesso necessárias. Não foram feitas alterações de esquema nem gravações em dados reais.

## Executar os testes de navegador

```sh
python -m pip install playwright==1.64.0
python -m playwright install chromium
python -m http.server 8777 --bind 127.0.0.1 --directory www
# Noutro terminal:
mkdir -p test-results
python tests/e2e/nao_congela.py test-results
python tests/e2e/atlas_leve.py test-results
python tests/e2e/reino_save.py test-results
python tests/e2e/estabilidade.py test-results
```

Para usar Chrome local no último teste, definir `ALV_BROWSER` para o executável. Os outros testes seguem o navegador instalado pelo Playwright.

## Limitações e próximo teste

O bloqueio original no telemóvel não foi reproduzido no aparelho afetado. Testes de navegador no computador e sucesso de compilação não garantem ausência de ANR, falta de memória ou problemas específicos do Android. O APK candidato deve ser testado numa partida prolongada até ao Ferro, incluindo suspender/retomar e guardar/continuar. Não desinstalar a app nem apagar os dados para trocar de versão.

A proteção por revisão requer os clientes corrigidos: uma versão antiga que ainda faça upsert incondicional pode substituir a linha. Evitar jogar simultaneamente com APKs de versões diferentes durante a validação.

A revisão visual dos edifícios ficou para uma etapa posterior, a pedido do utilizador.

Documentação oficial utilizada: [UPDATE com filtros e retorno](https://supabase.com/docs/reference/javascript/update), [INSERT e retorno](https://supabase.com/docs/reference/javascript/insert).
