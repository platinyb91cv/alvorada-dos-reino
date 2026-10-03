-- chave do servidor de jogo (VPS) para registar resultados: só o resumo SHA-256 fica na base de dados
insert into private.server_keys (hash, note) values ('272cc0c874d8d8c50e18842e503707f778e81849f6495d3240f08857ad8fcd7b', 'servidor jogo.krioldns.uk') on conflict do nothing;
