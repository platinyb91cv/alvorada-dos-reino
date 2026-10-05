// Alvorada dos Reinos — servidor de salas para jogar online com amigos.
// Não corre o jogo: guarda as salas (código de 4 letras) e retransmite as mensagens entre os dois jogadores.
// Também serve os ficheiros do jogo (pasta www) para quem quiser jogar no navegador.
'use strict';
const http=require('http'),fs=require('fs'),path=require('path'),crypto=require('crypto');
const {WebSocketServer}=require('ws');
const PORT=+process.env.PORT||8090;
const HOST=process.env.HOST||'127.0.0.1';
const WWW=process.env.WWW||path.join(__dirname,'..','www');
const LAG=+process.env.FAKE_LAG||0;          // só para testes: atraso artificial (ms)
// Supabase: valida o login Google dos jogadores e regista os resultados (pontuação Elo)
const SB_URL=(process.env.SUPABASE_URL||'').replace(/\/$/,'');
const SB_KEY=process.env.SUPABASE_KEY||'';                // chave publicável (sb_publishable_…)
const SB_SECRET=process.env.ALV_SERVER_SECRET||'';        // chave do servidor para registar partidas
const DEV=!SB_URL;                                        // sem Supabase: modo de desenvolvimento (aceita nomes)
const FORFEIT_MS=+process.env.FORFEIT_MS||90000;        // um resultado de um só jogador só conta se o outro estiver desligado há tanto tempo
const LONE_MAX_MS=+process.env.LONE_MAX_MS||600000;      // se o outro continuar ligado e calado, a partida fica em disputa (sem Elo)
const FRIENDS_TTL=60000;
const ROOM_TTL=10*60*1000,REJOIN_MS=3*60*1000,MAX_ROOMS=500;
const ABC='ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
const rooms=new Map();
const users=new Map(); // id → ws (um ligação por conta)
async function sbFetch(path,opt){const r=await fetch(SB_URL+path,{...opt,headers:{apikey:SB_KEY,'content-type':'application/json',...(opt&&opt.headers||{})}});const t=await r.text();let j=null;try{j=t?JSON.parse(t):null}catch(e){}if(!r.ok)throw new Error((j&&(j.message||j.msg))||('HTTP '+r.status));return j}
async function verifyUser(token){
  const u=await sbFetch('/auth/v1/user',{headers:{Authorization:'Bearer '+token}});
  const rows=await sbFetch('/rest/v1/profiles?select=id,username,avatar_url,rating&id=eq.'+encodeURIComponent(u.id),{headers:{Authorization:'Bearer '+token}});
  const p=rows&&rows[0];if(!p)throw new Error('perfil em falta');
  return{id:p.id,name:p.username,avatar:p.avatar_url||null,rating:p.rating}}
async function friendsOf(ws){
  if(DEV)return null; // desenvolvimento: sem restrições
  if(ws.fr&&Date.now()-ws.frT<FRIENDS_TTL)return ws.fr;
  try{const ids=await sbFetch('/rest/v1/rpc/friend_ids',{method:'POST',body:JSON.stringify({p_secret:SB_SECRET,p_user:ws.user.id})});ws.fr=new Set(ids||[]);ws.frT=Date.now()}
  catch(e){log('erro ao ler amigos',e.message);ws.fr=ws.fr||new Set()}
  return ws.fr}
const pub=u=>u?{id:u.id,name:u.name,avatar:u.avatar,rating:u.rating}:null;
const REASON=r=>/^resign/.test(r)?'resign':r==='peer_quit'||r==='forfeit'||r==='abandono'?'abandono':r==='wonder'?'wonder':'normal';
async function recordMatch(r,winnerSlot,reason,disputed){
  const M=r.match;if(!M||M.done)return;M.done=true;clearTimeout(M.timer);
  const dur=Math.round((Date.now()-M.t0)/1000);
  const host=M.host,guest=M.guest;let res={host_delta:0,guest_delta:0,host_rating:host.rating,guest_rating:guest.rating};
  if(!DEV&&SB_SECRET){
    const body={p_secret:SB_SECRET,p_room:r.code,p_host:host.id,p_guest:guest.id,p_winner:winnerSlot==null?null:(winnerSlot===0?host.id:guest.id),p_reason:REASON(reason),p_duration:dur,p_seed:M.seed||0,p_disputed:!!disputed,p_resyncs:M.snaps||0};
    try{res=await sbFetch('/rest/v1/rpc/record_match',{method:'POST',body:JSON.stringify(body)})}
    catch(e){
      // base de dados ainda sem a migração nova (sem p_resyncs): tenta a versão antiga
      if(/p_resyncs|function|not find/i.test(e.message)){try{delete body.p_resyncs;res=await sbFetch('/rest/v1/rpc/record_match',{method:'POST',body:JSON.stringify(body)})}catch(e2){log('erro ao registar partida',r.code,e2.message);return}}
      else{log('erro ao registar partida',r.code,e.message);return}}
  }else{res.rated=!disputed&&winnerSlot!=null&&dur>=180;if(!res.rated)res.why=disputed?'disputa':dur<180?'curta':'sem_vencedor'
  }
  log('partida registada',r.code,'vencedor',winnerSlot,REASON(reason),disputed?'(disputa)':'','duração',dur+'s','ressincronizações',M.snaps||0,JSON.stringify(res));
  const out=[[0,res.host_delta,res.host_rating],[1,res.guest_delta,res.guest_rating]];
  for(const [s,delta,rating] of out){const p=r.p[s];if(p&&p.user)p.user.rating=rating;if(p&&p.ws)send(p.ws,{type:'rated',delta,rating,disputed:!!disputed,unrated:res.rated===false,why:res.why||null})}}
function onResult(r,slot,m){
  const M=r.match;if(!M||M.done)return;const w=m.winner===0||m.winner===1?m.winner:null;
  M.reports[slot]={w,reason:String(m.reason||'normal'),at:Date.now()};
  const a=M.reports[0],b=M.reports[1];
  if(a&&b){if(a.w===b.w)recordMatch(r,a.w,a.reason==='normal'?b.reason:a.reason,false);else recordMatch(r,null,'disputa',true);return}
  // só um relatório: conta apenas se o outro jogador estiver desligado há FORFEIT_MS (abandono);
  // se o outro continuar ligado, espera pelo relatório dele (um cliente alterado não ganha sozinho)
  clearInterval(M.timer);M.timer=setInterval(()=>{
    if(M.done){clearInterval(M.timer);return}
    const x=M.reports[0]||M.reports[1];const s=M.reports[0]?0:1;const o=r.p[1-s];const now=Date.now();
    const offFor=!o?Infinity:o.ws?0:now-(o.left||now);
    if(offFor>=FORFEIT_MS){recordMatch(r,x.w,'abandono',false);return}
    if(now-x.at>LONE_MAX_MS)recordMatch(r,null,'disputa',true)},Math.min(5000,FORFEIT_MS/3))}
const log=(...a)=>console.log(new Date().toISOString(),...a);
const MIME={'.html':'text/html; charset=utf-8','.js':'text/javascript','.css':'text/css','.json':'application/json','.png':'image/png','.svg':'image/svg+xml','.woff2':'font/woff2','.ico':'image/x-icon','.webmanifest':'application/manifest+json'};
const server=http.createServer((req,res)=>{
  const url=decodeURIComponent((req.url||'/').split('?')[0]);
  if(url==='/health'){res.writeHead(200,{'content-type':'application/json'});res.end(JSON.stringify({ok:true,rooms:rooms.size,players:[...rooms.values()].reduce((n,r)=>n+r.p.filter(x=>x&&x.ws).length,0)}));return}
  let f=path.normalize(path.join(WWW,url==='/'?'index.html':url));
  if(!f.startsWith(path.normalize(WWW))){res.writeHead(403);res.end();return}
  fs.stat(f,(e,st)=>{if(e||!st.isFile()){res.writeHead(404);res.end('404');return}
    res.writeHead(200,{'content-type':MIME[path.extname(f)]||'application/octet-stream','cache-control':'no-cache'});fs.createReadStream(f).pipe(res)});
});
const wss=new WebSocketServer({server,path:'/ws',maxPayload:8*1024*1024});
function code(){for(let k=0;k<50;k++){let c='';for(let i=0;i<4;i++)c+=ABC[crypto.randomInt(ABC.length)];if(!rooms.has(c))return c}return null}
const send=(ws,o)=>{if(ws&&ws.readyState===1)ws.send(typeof o==='string'?o:JSON.stringify(o))};
const other=(r,slot)=>r.p[1-slot];
function leave(ws,final){
  const r=ws.room&&rooms.get(ws.room);if(!r)return;const s=ws.slot,me=r.p[s];if(!me||me.ws!==ws)return;
  me.ws=null;me.left=Date.now();
  const o=other(r,s);if(o&&o.ws)send(o.ws,{type:'peer_left',final:!!final});
  if(final&&r.match&&!r.match.done&&o)recordMatch(r,1-s,'abandono',false);
  if(final||!r.started){r.p[s]=null}
  r.last=Date.now();ws.room=null;
  if(!r.p.some(x=>x&&x.ws))r.empty=Date.now();
}
wss.on('connection',(ws,req)=>{
  ws.alive=true;ws.on('pong',()=>ws.alive=true);ws.n=0;ws.t0=Date.now();
  ws.on('message',async raw=>{
    // limite simples de mensagens (turnos são 10/s; folga para estado completo e conversa)
    const now=Date.now();if(now-ws.t0>10000){ws.t0=now;ws.n=0}if(++ws.n>600){send(ws,{type:'error',msg:'Demasiadas mensagens'});return}
    let m;try{m=JSON.parse(raw)}catch(e){return}
    const r=ws.room&&rooms.get(ws.room);
    if(m.type==='auth'){
      if(m.refresh&&ws.user){const t=m.token?String(m.token):ws.tok;if(!t||DEV)return;verifyUser(t).then(u=>{if(u.id!==ws.user.id)return;ws.tok=t;Object.assign(ws.user,u)}).catch(()=>{});return}
      if(DEV){ws.user={id:'dev-'+crypto.randomBytes(4).toString('hex'),name:String(m.dev&&m.dev.name||'Jogador').slice(0,16),avatar:null,rating:1000};users.set(ws.user.id,ws);send(ws,{type:'authed',user:pub(ws.user)});return}
      if(!m.token){send(ws,{type:'error',code:'auth',msg:'É preciso entrar com a conta Google'});return}
      verifyUser(String(m.token)).then(u=>{ws.user=u;ws.tok=String(m.token);const old=users.get(u.id);if(old&&old!==ws&&!old.room){try{old.close()}catch(e){}}users.set(u.id,ws);send(ws,{type:'authed',user:pub(u)})})
        .catch(e=>{log('login recusado',e.message);send(ws,{type:'error',code:'auth',msg:'Sessão inválida. Entra outra vez com o Google.'})});
      return}
    if(m.type!=='ping'&&!ws.user){send(ws,{type:'error',code:'auth',msg:'É preciso entrar com a conta Google'});return}
    switch(m.type){
    case 'list':send(ws,{type:'rooms',rooms:[...rooms.values()].filter(x=>x.public&&!x.started&&x.p[0]&&x.p[0].ws&&!x.p[1]).slice(0,30).map(x=>({room:x.code,host:pub(x.p[0].user)}))});break;
    case 'presence':{const fr=await friendsOf(ws);const on={};for(const id of (Array.isArray(m.ids)?m.ids:[]).slice(0,200)){if(fr&&!fr.has(id))continue;const w=users.get(id);if(w&&w.readyState===1){const R=w.room&&rooms.get(w.room);on[id]=R&&R.started&&!(R.match&&R.match.done)?'playing':'online'}}send(ws,{type:'presence',on});break}
    case 'invite':{const now=Date.now();if(now-(ws.invT||0)<2500)break;ws.invT=now;const w=users.get(m.to);const R=rooms.get(String(m.room||''));
      if(!R||R.p[0]?.ws!==ws){send(ws,{type:'error',msg:'Cria uma sala primeiro'});break}
      const fr=await friendsOf(ws);if(fr&&!fr.has(m.to)){ws.fr=null;const fr2=await friendsOf(ws);if(!fr2.has(m.to)){send(ws,{type:'error',msg:'Só podes convidar amigos'});break}}
      if(w&&w.readyState===1){send(w,{type:'invite',from:pub(ws.user),room:R.code});(ws.invFrom=ws.invFrom||new Set());w.invFrom=w.invFrom||new Set();ws.invFrom.add(w.user.id);send(ws,{type:'invited',ok:true,name:w.user&&w.user.name})}else send(ws,{type:'invited',ok:false});break}
    case 'decline':{const w=users.get(m.to);if(w&&w.invFrom&&w.invFrom.has(ws.user.id))send(w,{type:'declined',from:pub(ws.user)});break}
    case 'result':if(r&&r.match)onResult(r,ws.slot,m);break;
    case 'ping':if(LAG)setTimeout(()=>send(ws,{type:'pong',t:m.t}),LAG*2);else send(ws,{type:'pong',t:m.t});break;
    case 'create':{
      if(ws.room)leave(ws,true);if(rooms.size>=MAX_ROOMS){send(ws,{type:'error',msg:'Servidor cheio, tenta mais tarde'});break}
      const c=code();if(!c){send(ws,{type:'error',msg:'Tenta outra vez'});break}
      const token=crypto.randomBytes(12).toString('hex');
      rooms.set(c,{code:c,p:[{ws,user:ws.user,name:ws.user.name,token},null],started:false,public:!!m.public,created:Date.now(),last:Date.now(),v:m.v});
      ws.room=c;ws.slot=0;send(ws,{type:'created',room:c,token,slot:0});log('sala criada',c);break}
    case 'join':{
      const c=String(m.room||'').toUpperCase().trim(),R=rooms.get(c);
      if(!R){send(ws,{type:'error',msg:'Sala não encontrada. Confirma o código.'});break}
      if(R.v&&m.v&&R.v!==m.v){send(ws,{type:'error',msg:'Versões diferentes do jogo. Atualizem os dois para a mesma versão.'});break}
      if(R.p[1]){send(ws,{type:'error',msg:'A sala já está cheia'});break}
      if(!R.p[0]){send(ws,{type:'error',msg:'O anfitrião saiu da sala'});break}
      if(!DEV&&R.p[0].user&&R.p[0].user.id===ws.user.id){send(ws,{type:'error',msg:'Não podes jogar contra ti próprio'});break}
      if(ws.room)leave(ws,true);
      const token=crypto.randomBytes(12).toString('hex');R.p[1]={ws,user:ws.user,name:ws.user.name,token};ws.room=c;ws.slot=1;R.last=Date.now();R.empty=0;
      send(ws,{type:'joined',room:c,token,slot:1,peer:pub(R.p[0].user)});send(R.p[0].ws,{type:'peer_join',user:pub(ws.user)});log('entrou na sala',c);break}
    case 'rejoin':{
      const c=String(m.room||'').toUpperCase(),R=rooms.get(c);const s=R?R.p.findIndex(x=>x&&x.token===m.token&&(DEV||!x.user||x.user.id===ws.user.id)):-1;
      if(s<0){send(ws,{type:'error',code:'norejoin',msg:'Essa partida já não existe'});break}
      const me=R.p[s];if(me.ws&&me.ws!==ws){try{me.ws.close()}catch(e){}}
      me.ws=ws;me.left=0;ws.room=c;ws.slot=s;R.last=Date.now();R.empty=0;
      const o=other(R,s);send(ws,{type:'rejoined',slot:s,peer:o?pub(o.user):null,peerOnline:!!(o&&o.ws)});if(o&&o.ws)send(o.ws,{type:'peer_back'});log('voltou à sala',c,s);break}
    case 'relay':{
      if(!r)break;const o=other(r,ws.slot);r.last=Date.now();
      if(m.d&&m.d.g==='start'&&ws.slot===0&&r.p[1]){r.started=true;r.public=false;r.match={t0:Date.now(),seed:+m.d.seed||0,host:r.p[0].user,guest:r.p[1].user,reports:[null,null],done:false}}
      // partida guardada retomada: o anfitrião envia o estado completo em vez de 'start'
      else if(m.d&&m.d.g==='snap'&&m.d.resume&&ws.slot===0&&r.p[1]&&!r.started){r.started=true;r.public=false;r.match={t0:Date.now(),seed:0,host:r.p[0].user,guest:r.p[1].user,reports:[null,null],done:false,resumed:true}}
      if(m.d&&m.d.g==='snap'&&r.match&&!r.match.done)r.match.snaps=(r.match.snaps||0)+1;
      if(o&&o.ws){const out=JSON.stringify({type:'relay',d:m.d});if(LAG)setTimeout(()=>send(o.ws,out),LAG);else send(o.ws,out)}
      break}
    // «Gravar e sair»: a partida fica suspensa (sem vencedor nem derrota por abandono)
    case 'suspend':{if(r&&r.match&&!r.match.done){r.match.done=true;clearInterval(r.match.timer);log('partida suspensa (gravada)',r.code)}break}
    case 'leave':leave(ws,true);break;
    }
  });
  ws.on('close',()=>{leave(ws,false);if(ws.user&&users.get(ws.user.id)===ws)users.delete(ws.user.id)});
  ws.on('error',()=>{});
});
// ligações mortas e salas abandonadas
setInterval(()=>{
  for(const ws of wss.clients){if(!ws.alive){ws.terminate();continue}ws.alive=false;try{ws.ping()}catch(e){}}
  const now=Date.now();
  for(const [c,r] of rooms){
    for(let s=0;s<2;s++){const p=r.p[s];if(p&&!p.ws&&p.left&&now-p.left>REJOIN_MS){if(r.match&&!r.match.done)recordMatch(r,1-s,'abandono',false);r.p[s]=null;const o=r.p[1-s];if(o&&o.ws)send(o.ws,{type:'peer_left',final:true})}}
    if(!r.p.some(x=>x&&x.ws)&&now-(r.empty||r.last)>ROOM_TTL)rooms.delete(c);
    else if(!r.p[0]&&!r.p[1])rooms.delete(c);
  }
},20000);
server.listen(PORT,HOST,()=>log(`Alvorada: servidor em http://${HOST}:${PORT}  (WebSocket em /ws, jogo em ${WWW})`+(DEV?'  [modo de desenvolvimento: sem Supabase]':`  [contas: ${SB_URL}${SB_SECRET?'':' — falta ALV_SERVER_SECRET, as partidas não são registadas'}]`)));
