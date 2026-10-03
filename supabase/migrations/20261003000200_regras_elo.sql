-- Regras anti-batota da pontuação (Elo):
--  * sem pontos em partidas com menos de 3 minutos, em disputa, sem vencedor, ou com muitas ressincronizações
--  * no máximo 3 partidas com pontos por dia contra o mesmo adversário (dificulta "farming" com contas falsas)
alter table public.matches add column if not exists rated boolean not null default true;
alter table public.matches add column if not exists resyncs int not null default 0;
create index if not exists matches_pair_idx on public.matches (least(host_id, guest_id), greatest(host_id, guest_id), created_at desc);

drop function if exists public.record_match(text,text,uuid,uuid,uuid,text,int,bigint,boolean);
create function public.record_match(
  p_secret text, p_room text, p_host uuid, p_guest uuid, p_winner uuid,
  p_reason text, p_duration int, p_seed bigint, p_disputed boolean default false, p_resyncs int default 0)
returns json language plpgsql security definer set search_path = '' as $$
declare rh int; rg int; eh float; sh float; dh int := 0; dg int := 0; k int := 32; v_rated boolean; v_why text := null; v_pair int;
begin
  if not exists (select 1 from private.server_keys where hash = encode(extensions.digest(p_secret, 'sha256'), 'hex')) then
    raise exception 'chave do servidor inválida';
  end if;
  if p_host is null or p_guest is null or p_host = p_guest then raise exception 'jogadores inválidos'; end if;
  if p_winner is not null and p_winner not in (p_host, p_guest) then raise exception 'vencedor inválido'; end if;
  select rating into rh from public.profiles where id = p_host for update;
  select rating into rg from public.profiles where id = p_guest for update;
  if rh is null or rg is null then raise exception 'perfil em falta'; end if;
  select count(*) into v_pair from public.matches
    where rated and created_at > now() - interval '24 hours'
      and least(host_id, guest_id) = least(p_host, p_guest) and greatest(host_id, guest_id) = greatest(p_host, p_guest);
  v_rated := true;
  if p_disputed then v_rated := false; v_why := 'disputa';
  elsif p_winner is null then v_rated := false; v_why := 'sem_vencedor';
  elsif coalesce(p_duration, 0) < 180 then v_rated := false; v_why := 'curta';
  elsif coalesce(p_resyncs, 0) > 4 then v_rated := false; v_why := 'ressincronizacoes';
  elsif v_pair >= 3 then v_rated := false; v_why := 'limite_diario';
  end if;
  if v_rated then
    eh := 1.0 / (1.0 + power(10.0, (rg - rh) / 400.0));
    sh := case when p_winner = p_host then 1.0 else 0.0 end;
    dh := round(k * (sh - eh));
    dg := -dh;
    update public.profiles set rating = greatest(100, rating + dh), games = games + 1,
      wins = wins + (sh)::int, losses = losses + (1 - sh)::int where id = p_host;
    update public.profiles set rating = greatest(100, rating + dg), games = games + 1,
      wins = wins + (1 - sh)::int, losses = losses + (sh)::int where id = p_guest;
  end if;
  insert into public.matches (room, host_id, guest_id, winner_id, reason, duration_s, seed, host_delta, guest_delta, disputed, rated, resyncs)
  values (p_room, p_host, p_guest, p_winner, left(p_reason, 24), p_duration, p_seed, dh, dg, p_disputed, v_rated, coalesce(p_resyncs, 0));
  return json_build_object('host_delta', dh, 'guest_delta', dg, 'rated', v_rated, 'why', v_why,
    'host_rating', (select rating from public.profiles where id = p_host),
    'guest_rating', (select rating from public.profiles where id = p_guest));
end $$;
revoke execute on function public.record_match(text,text,uuid,uuid,uuid,text,int,bigint,boolean,int) from public, anon, authenticated;
grant execute on function public.record_match(text,text,uuid,uuid,uuid,text,int,bigint,boolean,int) to anon;

-- amigos aceites de um jogador (o servidor de jogo usa isto para limitar convites e "quem está ligado" aos amigos)
create or replace function public.friend_ids(p_secret text, p_user uuid) returns uuid[]
language plpgsql security definer stable set search_path = '' as $$
begin
  if not exists (select 1 from private.server_keys where hash = encode(extensions.digest(p_secret, 'sha256'), 'hex')) then
    raise exception 'chave do servidor inválida';
  end if;
  return coalesce((select array_agg(case when user_id = p_user then friend_id else user_id end)
    from public.friendships where status = 'accepted' and p_user in (user_id, friend_id)), '{}');
end $$;
revoke execute on function public.friend_ids(text,uuid) from public, anon, authenticated;
grant execute on function public.friend_ids(text,uuid) to anon;
