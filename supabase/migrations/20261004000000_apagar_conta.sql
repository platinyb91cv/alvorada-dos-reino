-- Apagar a própria conta (exigido pela Google Play para apps com login).
-- Remove o utilizador de auth.users; o perfil e as amizades apagam-se em cascata;
-- nas partidas antigas o jogador fica anónimo (on delete set null).
create or replace function public.delete_my_account() returns void
language plpgsql security definer set search_path = '' as $$
declare me uuid := auth.uid();
begin
  if me is null then raise exception 'sem sessão'; end if;
  delete from auth.users where id = me;
end $$;
revoke execute on function public.delete_my_account() from public, anon;
grant execute on function public.delete_my_account() to authenticated;
