-- Alvorada dos Reinos: contas (login Google), perfis, pontuação, partidas e amigos
create extension if not exists pgcrypto with schema extensions;

-- ---------- perfis ----------
create table public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  username text not null unique check (char_length(username) between 3 and 16),
  avatar_url text,
  rating int not null default 1000,
  games int not null default 0,
  wins int not null default 0,
  losses int not null default 0,
  sp_wins int not null default 0,
  sp_losses int not null default 0,
  friend_code text not null unique default upper(substr(md5(gen_random_uuid()::text),1,6)),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index profiles_rating_idx on public.profiles (rating desc) where games > 0;

-- cria o perfil quando alguém entra pela primeira vez (nome do Google, sem repetir)
create or replace function public.handle_new_user() returns trigger
language plpgsql security definer set search_path = '' as $$
declare base text; cand text; n int := 0;
begin
  base := coalesce(new.raw_user_meta_data->>'name', new.raw_user_meta_data->>'full_name', split_part(coalesce(new.email,'jogador'),'@',1));
  base := regexp_replace(base, '[^A-Za-z0-9À-ÿ_ .-]', '', 'g');
  base := btrim(left(base, 12));
  if char_length(base) < 3 then base := 'Jogador'; end if;
  cand := base;
  while exists (select 1 from public.profiles where lower(username) = lower(cand)) and n < 50 loop
    cand := left(base, 12) || (100 + floor(random()*900))::int; n := n + 1;
  end loop;
  insert into public.profiles (id, username, avatar_url)
  values (new.id, cand, new.raw_user_meta_data->>'avatar_url');
  return new;
end $$;
create trigger on_auth_user_created after insert on auth.users
  for each row execute function public.handle_new_user();

create or replace function public.touch_updated_at() returns trigger
language plpgsql set search_path = '' as $$ begin new.updated_at := now(); return new; end $$;
create trigger profiles_touch before update on public.profiles
  for each row execute function public.touch_updated_at();

alter table public.profiles enable row level security;
create policy "perfis visíveis a quem tem conta" on public.profiles for select to authenticated using (true);
create policy "cada um edita o seu perfil" on public.profiles for update to authenticated
  using ((select auth.uid()) = id) with check ((select auth.uid()) = id);
-- só o nome e a imagem podem ser mudados pelo jogador; pontuação só pelas funções do servidor
revoke all on public.profiles from anon, authenticated;
grant select on public.profiles to authenticated;
grant update (username, avatar_url) on public.profiles to authenticated;
alter table public.profiles add constraint username_chars check (username ~ '^[A-Za-z0-9À-ÿ_ .-]+$');

-- ---------- partidas online ----------
create table public.matches (
  id bigint generated always as identity primary key,
  room text,
  host_id uuid references public.profiles(id) on delete set null,
  guest_id uuid references public.profiles(id) on delete set null,
  winner_id uuid references public.profiles(id) on delete set null,
  reason text,
  duration_s int,
  seed bigint,
  host_delta int not null default 0,
  guest_delta int not null default 0,
  disputed boolean not null default false,
  created_at timestamptz not null default now()
);
create index matches_host_idx on public.matches (host_id, created_at desc);
create index matches_guest_idx on public.matches (guest_id, created_at desc);
create index matches_winner_idx on public.matches (winner_id);
alter table public.matches enable row level security;
create policy "vejo as minhas partidas" on public.matches for select to authenticated
  using ((select auth.uid()) in (host_id, guest_id));
revoke all on public.matches from anon, authenticated;
grant select on public.matches to authenticated;

-- ---------- amigos ----------
create table public.friendships (
  user_id uuid not null references public.profiles(id) on delete cascade,   -- quem pediu
  friend_id uuid not null references public.profiles(id) on delete cascade, -- quem recebe
  status text not null default 'pending' check (status in ('pending','accepted')),
  created_at timestamptz not null default now(),
  primary key (user_id, friend_id),
  check (user_id <> friend_id)
);
create index friendships_friend_idx on public.friendships (friend_id);
alter table public.friendships enable row level security;
create policy "vejo as minhas amizades" on public.friendships for select to authenticated
  using ((select auth.uid()) in (user_id, friend_id));
revoke all on public.friendships from anon, authenticated;
grant select on public.friendships to authenticated;

-- pedir amizade pelo código de amigo (se o outro já tinha pedido, fica aceite)
create or replace function public.add_friend(p_code text) returns text
language plpgsql security definer set search_path = '' as $$
declare me uuid := auth.uid(); other uuid;
begin
  if me is null then raise exception 'sem sessão'; end if;
  select id into other from public.profiles where friend_code = upper(btrim(p_code));
  if other is null then return 'nao_encontrado'; end if;
  if other = me then return 'proprio'; end if;
  if exists (select 1 from public.friendships where user_id = other and friend_id = me) then
    update public.friendships set status = 'accepted' where user_id = other and friend_id = me;
    return 'aceite';
  end if;
  if exists (select 1 from public.friendships where user_id = me and friend_id = other) then return 'ja_pedido'; end if;
  insert into public.friendships (user_id, friend_id) values (me, other);
  return 'pedido';
end $$;

create or replace function public.respond_friend(p_other uuid, p_accept boolean) returns void
language plpgsql security definer set search_path = '' as $$
declare me uuid := auth.uid();
begin
  if me is null then raise exception 'sem sessão'; end if;
  if p_accept then
    update public.friendships set status = 'accepted' where user_id = p_other and friend_id = me and status = 'pending';
  else
    delete from public.friendships where user_id = p_other and friend_id = me and status = 'pending';
  end if;
end $$;

create or replace function public.remove_friend(p_other uuid) returns void
language plpgsql security definer set search_path = '' as $$
declare me uuid := auth.uid();
begin
  if me is null then raise exception 'sem sessão'; end if;
  delete from public.friendships where (user_id = me and friend_id = p_other) or (user_id = p_other and friend_id = me);
end $$;

-- lista de amigos com os dados do perfil
create or replace function public.my_friends() returns table (
  id uuid, username text, avatar_url text, rating int, wins int, losses int, status text, incoming boolean)
language sql security definer stable set search_path = '' as $$
  select p.id, p.username, p.avatar_url, p.rating, p.wins, p.losses, f.status, (f.friend_id = auth.uid()) as incoming
  from public.friendships f
  join public.profiles p on p.id = case when f.user_id = auth.uid() then f.friend_id else f.user_id end
  where auth.uid() in (f.user_id, f.friend_id)
  order by f.status desc, p.username;
$$;

-- ---------- resultados ----------
-- chave do servidor de jogo (só o resumo SHA-256 fica guardado)
create schema if not exists private;
revoke all on schema private from public, anon, authenticated;
create table private.server_keys (hash text primary key, note text, created_at timestamptz default now());

-- registo de uma partida online (chamado pelo servidor de jogo) com pontuação Elo
create or replace function public.record_match(
  p_secret text, p_room text, p_host uuid, p_guest uuid, p_winner uuid,
  p_reason text, p_duration int, p_seed bigint, p_disputed boolean default false)
returns json language plpgsql security definer set search_path = '' as $$
declare rh int; rg int; eh float; sh float; dh int := 0; dg int := 0; k int := 32;
begin
  if not exists (select 1 from private.server_keys where hash = encode(extensions.digest(p_secret, 'sha256'), 'hex')) then
    raise exception 'chave do servidor inválida';
  end if;
  if p_host is null or p_guest is null or p_host = p_guest then raise exception 'jogadores inválidos'; end if;
  if p_winner is not null and p_winner not in (p_host, p_guest) then raise exception 'vencedor inválido'; end if;
  select rating into rh from public.profiles where id = p_host for update;
  select rating into rg from public.profiles where id = p_guest for update;
  if rh is null or rg is null then raise exception 'perfil em falta'; end if;
  if not p_disputed and p_winner is not null then
    eh := 1.0 / (1.0 + power(10.0, (rg - rh) / 400.0));
    sh := case when p_winner = p_host then 1.0 else 0.0 end;
    dh := round(k * (sh - eh));
    dg := -dh;
    update public.profiles set rating = greatest(100, rating + dh), games = games + 1,
      wins = wins + (sh)::int, losses = losses + (1 - sh)::int where id = p_host;
    update public.profiles set rating = greatest(100, rating + dg), games = games + 1,
      wins = wins + (1 - sh)::int, losses = losses + (sh)::int where id = p_guest;
  end if;
  insert into public.matches (room, host_id, guest_id, winner_id, reason, duration_s, seed, host_delta, guest_delta, disputed)
  values (p_room, p_host, p_guest, p_winner, left(p_reason, 24), p_duration, p_seed, dh, dg, p_disputed);
  return json_build_object('host_delta', dh, 'guest_delta', dg,
    'host_rating', (select rating from public.profiles where id = p_host),
    'guest_rating', (select rating from public.profiles where id = p_guest));
end $$;

-- resultado de um jogo contra o computador (conta para as estatísticas do próprio jogador)
create or replace function public.record_sp(p_win boolean) returns void
language plpgsql security definer set search_path = '' as $$
begin
  if auth.uid() is null then raise exception 'sem sessão'; end if;
  update public.profiles set sp_wins = sp_wins + (case when p_win then 1 else 0 end),
    sp_losses = sp_losses + (case when p_win then 0 else 1 end) where id = auth.uid();
end $$;

-- permissões das funções
revoke execute on function public.add_friend(text), public.respond_friend(uuid, boolean), public.remove_friend(uuid),
  public.my_friends(), public.record_sp(boolean), public.record_match(text,text,uuid,uuid,uuid,text,int,bigint,boolean),
  public.handle_new_user(), public.touch_updated_at() from public, anon, authenticated;
grant execute on function public.add_friend(text), public.respond_friend(uuid, boolean), public.remove_friend(uuid),
  public.my_friends(), public.record_sp(boolean) to authenticated;
grant execute on function public.record_match(text,text,uuid,uuid,uuid,text,int,bigint,boolean) to anon;
