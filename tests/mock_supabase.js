// Imitação mínima do Supabase (Auth + PostgREST + RPC) para testes locais do login e do modo online.
// A lógica real está no SQL (testado à parte); aqui só se imitam as respostas HTTP.
const http=require('http');
const PORT=+process.env.MOCK_PORT||8795,SECRET=process.env.ALV_SERVER_SECRET||'s3cr3t';
const P=new Map(),M=[],F=[];let mid=1;
const add=(id,username,rating,code)=>P.set(id,{id,username,avatar_url:null,rating:rating||1000,games:0,wins:0,losses:0,sp_wins:0,sp_losses:0,friend_code:code});
add('u-ana','Ana',1000,'AAAAAA');add('u-rui','Rui',1000,'BBBBBB');add('u-eva','Eva',1200,'CCCCCC');
const uidOf=req=>{const a=req.headers.authorization||'';const t=a.replace(/^Bearer /,'');try{return JSON.parse(Buffer.from(t.split('.')[1],'base64url').toString()).sub}catch(e){return null}};
const send=(res,code,obj,h)=>{res.writeHead(code,{'content-type':'application/json','access-control-allow-origin':'*','access-control-allow-headers':'*','access-control-allow-methods':'*','access-control-expose-headers':'*',...(h||{})});res.end(obj==null?'':JSON.stringify(obj))};
const pick=(o,cols)=>{if(!cols||cols==='*')return{...o};const r={};for(const c of cols.split(','))if(!c.includes('('))r[c]=o[c];return r};
http.createServer((req,res)=>{
  if(req.method==='OPTIONS')return send(res,204,null);
  let body='';req.on('data',d=>body+=d);req.on('end',()=>{
    const u=new URL(req.url,'http://x');const q=u.searchParams;const uid=uidOf(req);const B=body?JSON.parse(body):{};
    const p=u.pathname;
    if(p==='/auth/v1/user'){if(!uid||!P.has(uid))return send(res,401,{msg:'invalid'});return send(res,200,{id:uid,aud:'authenticated',email:uid+'@teste'})}
    if(p.startsWith('/auth/v1/logout'))return send(res,204,null);
    if(p==='/rest/v1/profiles'&&req.method==='GET'){if(!uid)return send(res,401,{message:'sem sessão'});
      let rows=[...P.values()];const id=q.get('id');if(id)rows=rows.filter(r=>r.id===id.replace('eq.',''));
      if(q.get('games'))rows=rows.filter(r=>r.games>0);if(q.get('order')==='rating.desc')rows.sort((a,b)=>b.rating-a.rating);
      rows=rows.map(r=>pick(r,q.get('select')));
      if((req.headers.accept||'').includes('vnd.pgrst.object'))return rows.length?send(res,200,rows[0]):send(res,406,{message:'0 rows'});return send(res,200,rows)}
    if(p==='/rest/v1/profiles'&&req.method==='PATCH'){const id=(q.get('id')||'').replace('eq.','');if(id!==uid)return send(res,200,[]);
      if([...P.values()].some(r=>r.id!==id&&r.username.toLowerCase()===String(B.username).toLowerCase()))return send(res,409,{message:'duplicate key value violates unique constraint'});P.get(id).username=B.username;return send(res,204,null)}
    if(p==='/rest/v1/matches'){const rows=M.filter(m=>uid===m.host_id||uid===m.guest_id).slice().reverse().map(m=>({...m,host:{username:P.get(m.host_id).username},guest:{username:P.get(m.guest_id).username}}));return send(res,200,rows)}
    if(p.startsWith('/rest/v1/rpc/')){const fn=p.slice(13);
      if(fn==='record_match'){if(B.p_secret!==SECRET)return send(res,400,{message:'chave do servidor inválida'});const h=P.get(B.p_host),g=P.get(B.p_guest);let dh=0;
        const MIN=+process.env.MOCK_MIN_DUR||180;const pair=M.filter(m=>m.rated&&[m.host_id,m.guest_id].sort().join()===[h.id,g.id].sort().join()).length;
        let rated=true,why=null;if(B.p_disputed){rated=false;why='disputa'}else if(!B.p_winner){rated=false;why='sem_vencedor'}else if((B.p_duration||0)<MIN){rated=false;why='curta'}else if((B.p_resyncs||0)>4){rated=false;why='ressincronizacoes'}else if(pair>=3){rated=false;why='limite_diario'}
        if(rated){const eh=1/(1+Math.pow(10,(g.rating-h.rating)/400));const sh=B.p_winner===h.id?1:0;dh=Math.round(32*(sh-eh));h.rating+=dh;g.rating-=dh;h.games++;g.games++;if(sh){h.wins++;g.losses++}else{g.wins++;h.losses++}}
        M.push({id:mid++,host_id:h.id,guest_id:g.id,winner_id:B.p_winner,reason:B.p_reason,duration_s:B.p_duration,host_delta:dh,guest_delta:-dh,disputed:!!B.p_disputed,rated,resyncs:B.p_resyncs||0,created_at:new Date().toISOString()});
        return send(res,200,{host_delta:dh,guest_delta:-dh,rated,why,host_rating:h.rating,guest_rating:g.rating})}
      if(fn==='friend_ids'){if(B.p_secret!==SECRET)return send(res,400,{message:'chave do servidor inválida'});return send(res,200,F.filter(f=>f.status==='accepted'&&(f.user_id===B.p_user||f.friend_id===B.p_user)).map(f=>f.user_id===B.p_user?f.friend_id:f.user_id))}
      if(!uid)return send(res,401,{message:'sem sessão'});
      if(fn==='delete_my_account'){P.delete(uid);for(let i=F.length-1;i>=0;i--)if(F[i].user_id===uid||F[i].friend_id===uid)F.splice(i,1);for(const m of M){if(m.host_id===uid)m.host_id=null;if(m.guest_id===uid)m.guest_id=null}return send(res,204,null)}
      if(fn==='record_sp'){P.get(uid)[B.p_win?'sp_wins':'sp_losses']++;return send(res,204,null)}
      if(fn==='add_friend'){const o=[...P.values()].find(r=>r.friend_code===String(B.p_code).toUpperCase());if(!o)return send(res,200,'nao_encontrado');if(o.id===uid)return send(res,200,'proprio');
        const rev=F.find(f=>f.user_id===o.id&&f.friend_id===uid);if(rev){rev.status='accepted';return send(res,200,'aceite')}if(F.find(f=>f.user_id===uid&&f.friend_id===o.id))return send(res,200,'ja_pedido');F.push({user_id:uid,friend_id:o.id,status:'pending'});return send(res,200,'pedido')}
      if(fn==='respond_friend'){const f=F.find(f=>f.user_id===B.p_other&&f.friend_id===uid);if(f){if(B.p_accept)f.status='accepted';else F.splice(F.indexOf(f),1)}return send(res,204,null)}
      if(fn==='remove_friend'){for(let i=F.length-1;i>=0;i--){const f=F[i];if((f.user_id===uid&&f.friend_id===B.p_other)||(f.user_id===B.p_other&&f.friend_id===uid))F.splice(i,1)}return send(res,204,null)}
      if(fn==='my_friends'){return send(res,200,F.filter(f=>f.user_id===uid||f.friend_id===uid).map(f=>{const o=P.get(f.user_id===uid?f.friend_id:f.user_id);return{id:o.id,username:o.username,avatar_url:null,rating:o.rating,wins:o.wins,losses:o.losses,status:f.status,incoming:f.friend_id===uid}}))}
    }
    if(p==='/__state')return send(res,200,{P:[...P.values()],M,F});
    send(res,404,{message:'não encontrado: '+p});
  })}).listen(PORT,'127.0.0.1',()=>console.log('mock supabase',PORT));
