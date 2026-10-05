-- Alvorada dos Reinos: conquistas, gravação na nuvem e desafio diário

-- 1) Conquistas (cada utilizador só vê e escreve as suas)
create table if not exists public.achievements (
  user_id uuid not null references auth.users(id) on delete cascade,
  code text not null check (char_length(code) between 2 and 32),
  at timestamptz not null default now(),
  primary key (user_id, code)
);
alter table public.achievements enable row level security;
drop policy if exists achievements_select_own on public.achievements;
create policy achievements_select_own on public.achievements for select to authenticated using ((select auth.uid()) = user_id);
drop policy if exists achievements_insert_own on public.achievements;
create policy achievements_insert_own on public.achievements for insert to authenticated with check ((select auth.uid()) = user_id);

-- 2) Gravação na nuvem (uma partida por utilizador, comprimida)
create table if not exists public.cloud_saves (
  user_id uuid primary key references auth.users(id) on delete cascade,
  data text not null check (octet_length(data) <= 3000000),
  updated_at timestamptz not null default now()
);
alter table public.cloud_saves enable row level security;
drop policy if exists cloud_saves_select_own on public.cloud_saves;
create policy cloud_saves_select_own on public.cloud_saves for select to authenticated using ((select auth.uid()) = user_id);
drop policy if exists cloud_saves_insert_own on public.cloud_saves;
create policy cloud_saves_insert_own on public.cloud_saves for insert to authenticated with check ((select auth.uid()) = user_id);
drop policy if exists cloud_saves_update_own on public.cloud_saves;
create policy cloud_saves_update_own on public.cloud_saves for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
drop policy if exists cloud_saves_delete_own on public.cloud_saves;
create policy cloud_saves_delete_own on public.cloud_saves for delete to authenticated using ((select auth.uid()) = user_id);

-- 3) Desafio diário: todos leem a tabela do dia; só se escreve pela função
create table if not exists public.daily_scores (
  day date not null,
  user_id uuid not null references auth.users(id) on delete cascade,
  username text not null,
  secs int not null check (secs between 60 and 86400),
  at timestamptz not null default now(),
  primary key (day, user_id)
);
create index if not exists daily_scores_day_secs on public.daily_scores (day, secs);
alter table public.daily_scores enable row level security;
drop policy if exists daily_scores_read on public.daily_scores;
create policy daily_scores_read on public.daily_scores for select to authenticated using (true);

create or replace function public.submit_daily(p_day date, p_secs int) returns void
language plpgsql security definer set search_path = '' as $$
declare v_name text;
begin
  if auth.uid() is null then raise exception 'sem sessão'; end if;
  if p_day < (now() at time zone 'utc')::date - 1 or p_day > (now() at time zone 'utc')::date + 1 then raise exception 'dia inválido'; end if;
  if p_secs < 60 or p_secs > 86400 then raise exception 'tempo inválido'; end if;
  select username into v_name from public.profiles where id = auth.uid();
  if v_name is null then raise exception 'sem perfil'; end if;
  insert into public.daily_scores (day, user_id, username, secs) values (p_day, auth.uid(), v_name, p_secs)
  on conflict (day, user_id) do update set secs = least(public.daily_scores.secs, excluded.secs), username = excluded.username, at = now();
end $$;
revoke all on function public.submit_daily(date, int) from public, anon;
grant execute on function public.submit_daily(date, int) to authenticated;
