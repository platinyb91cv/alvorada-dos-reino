# Vida da aldeia: currais, estradas e gestão de aldeões

Três melhorias integradas no ramo local `integracao-soldados-armados`. Sem novos pedidos ou créditos Meshy. Os modelos, atlas e edifícios aprovados ficam preservados.

## Como usar

- Selecionar um aldeão → Construir → Curral: 80 de madeira, 15 segundos, lote 3×3, capacidade para 8 ovelhas. Depois, selecionar um aldeão e dar uma ordem sobre o curral pronto. Ele conduz ovelhas livres próximas (até 18 tiles), uma de cada vez, e começa a pastorear quando acaba a recolha. Vários aldeões podem repartir esta tarefa. Cada trabalhador recolhe leite de uma ovelha, entrega a comida no depósito e regressa. As ovelhas continuam vivas. A reprodução respeita o limite do curral.
- Construir → Estrada: escolher o início e o fim e confirmar. Custa 2 de pedra por segmento, aplicado ao traçar. Dá +20% de velocidade às unidades terrestres. A procura de caminhos considera esse ganho; não suaviza a rota de forma a abandonar a estrada. Não atravessa água, recursos nem edifícios. Construir um edifício sobre uma estrada remove os segmentos dessa área. Estradas não ocupam slots de edifícios nem impedem a passagem.
- O botão de ociosos continua a localizar trabalhadores parados. O novo botão ⚠ aparece quando há aldeões com falhas de percurso ou sem progresso durante quatro segundos. Um toque seleciona e centra a câmara; toques seguintes percorrem os casos. Trabalhadores imóveis que estão a produzir não contam como bloqueados.

Guardar a partida e recarregar a página para aplicar ao jogo já aberto. Os saves anteriores continuam a funcionar. Os saves novos conservam estradas, rebanhos e condução em curso. As ovelhas de um curral não são fontes de comida para o adversário. Se o curral cair, a ligação deixa de restringir o rebanho.

## Arte e custo de desenho

O curral adapta a cerca, bandeira e acessórios da quinta já aprovada, com chão de relva existente. Existe um desenho procedural de reserva enquanto a arte carrega. As estradas usam a textura de terra existente e pedras desenhadas por código. São desenhadas nos chunks estáticos do terreno; não há modelos 3D adicionais em execução nem novos assets no pacote web. Nenhuma chamada paga foi feita.

## Verificação

Nove testes CJS passaram. `check_village_life.cjs` testa custos e duplicados de estrada, limites de colocação, velocidade, A* real, condução/capacidade/propriedade do curral e deteção de bloqueios. O teste de alimentação foi atualizado para carregar as funções auxiliares novas e continua a confirmar produção ilimitada e ovelhas vivas.

O teste de browser usa o jogo real em Chrome headless, em contexto isolado: três ovelhas conduzidas, 12 HP mantidos, 90 de comida produzidos, 15 segmentos por 30 pedra, velocidade 2,04 contra 1,70 e 13 waypoints sobre estrada. Confirmou guardar/carregar no meio da condução, persistência de estradas e rebanho, snapshot exato e troca de proprietários em ida/volta, seleção pelo botão de bloqueios e botões de construção. Capturas em 1280×850 e 844×390. Não é uma medição num telemóvel físico nem um teste de duas ligações online reais.

Para repetir: correr todos os `tests/*.cjs` com Node. O script `verificar-browser.cjs` requer Playwright disponível para Node e Chrome/Chromium; `CHROME_PATH` permite escolher o executável. Os relatórios e capturas identificam esta revisão. O protocolo passa a `alvorada-19` para impedir partidas online entre clientes com regras diferentes.
