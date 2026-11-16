// Servidor online: o anfitrião não pode impor um estado alterado e ganhar Elo.
// O servidor compara os resumos de estado (hash) que cada jogador envia; com mais de DESYNC_MAX divergências
// confirmadas a partida fica sem pontuação ("dessincronizacao"), mesmo que os dois relatórios de vitória coincidam.
// Corre em modo de desenvolvimento (sem Supabase), numa porta local. Uso: node tests/check_servidor_desync.cjs
'use strict';
const {spawn}=require('child_process'),path=require('path');
const WS=require(path.join(__dirname,'..','server','node_modules','ws'));
const PORT=8797;
const srv=spawn(process.execPath,[path.join(__dirname,'..','server','server.js')],{env:{...process.env,PORT:String(PORT),HOST:'127.0.0.1',SUPABASE_URL:'',DESYNC_MAX:'2'},stdio:['ignore','pipe','pipe']});
let log='';srv.stdout.on('data',d=>log+=d);srv.stderr.on('data',d=>log+=d);
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
function client(name){return new Promise((res,rej)=>{const ws=new WS(`ws://127.0.0.1:${PORT}/ws`);const q=[];const waiters=[];
  ws.on('message',m=>{const o=JSON.parse(m);const i=waiters.findIndex(w=>w.f(o));if(i>=0){waiters.splice(i,1)[0].r(o)}else q.push(o)});
  ws.on('open',()=>{const c={ws,send:o=>ws.send(JSON.stringify(o)),wait:(f,ms=4000)=>new Promise((r,j)=>{const i=q.findIndex(f);if(i>=0)return r(q.splice(i,1)[0]);const w={f,r};waiters.push(w);setTimeout(()=>{const k=waiters.indexOf(w);if(k>=0){waiters.splice(k,1);j(new Error('timeout '+name))}},ms)})};
    c.send({type:'auth',dev:{name}});c.wait(o=>o.type==='authed').then(()=>res(c),rej)});ws.on('error',rej)})}
async function match(mismatches){
  const A=await client('Ana'),B=await client('Rui');
  A.send({type:'create'});const cr=await A.wait(o=>o.type==='created');B.send({type:'join',room:cr.room});await B.wait(o=>o.type==='joined');
  A.send({type:'relay',d:{g:'start',seed:123}});await B.wait(o=>o.type==='relay'&&o.d.g==='start');
  for(let t=50;t<=50*8;t+=50){const bad=t/50<=mismatches;A.send({type:'relay',d:{g:'hash',t,h:bad?111:222,ep:0}});B.send({type:'relay',d:{g:'hash',t,h:222,ep:0}})}
  await sleep(200);
  A.send({type:'result',winner:0,reason:'normal'});B.send({type:'result',winner:0,reason:'normal'});
  const ra=await A.wait(o=>o.type==='rated');A.ws.close();B.ws.close();return ra}
(async()=>{let ok=false;try{
  await sleep(600);
  const limpo=await match(0),batota=await match(3),uma=await match(1);
  console.log(JSON.stringify({sem_divergencias:{why:limpo.why,desyncs:limpo.desyncs},tres_divergencias:{why:batota.why,unrated:batota.unrated,desyncs:batota.desyncs},uma_divergencia:{why:uma.why,desyncs:uma.desyncs}}));
  // sem divergências: só não conta por ser curta (dev); com 3 divergências confirmadas: sem pontuação por dessincronização; 1 divergência tolerada
  ok=limpo.desyncs===0&&limpo.why==='curta'&&batota.desyncs===3&&batota.unrated&&batota.why==='dessincronizacao'&&uma.desyncs===1&&uma.why==='curta'&&/divergência confirmada/.test(log);
}catch(e){console.log('ERRO',e.message)}finally{srv.kill()}
console.log(ok?'PASS: servidor confirma divergências de estado e retira o Elo a partidas dessincronizadas':'FAIL');process.exit(ok?0:1)})();
