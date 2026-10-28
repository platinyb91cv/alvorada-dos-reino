// Concurrency and account boundaries using the shipped Supabase SDK and real client functions.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),html=fs.readFileSync(path.join(root,'www/index.html'),'utf8');
const sdk=fs.readFileSync(path.join(root,'www/vendor/supabase.js'),'utf8');
const code=html.slice(html.indexOf('let cloudEpoch=0;'),html.indexOf('// ---------- Campanha ----------',html.indexOf('let cloudEpoch=0;')));
const clone=x=>JSON.parse(JSON.stringify(x)),realm=t=>({v:1,G:{time:t},X:{reino:{n:1}},P:[{age:0}]});
function deferred(){let resolve;const promise=new Promise(r=>resolve=r);return{promise,resolve}}
function database(){return{rows:new Map(),hook:null,requests:[],clock:0,
 seed(id,row){this.rows.set(id,{user_id:id,data:JSON.stringify(row),updated_at:new Date(++this.clock).toISOString()})},
 async fetch(url,options={}){const u=new URL(url),method=options.method||'GET',body=options.body?JSON.parse(options.body):null;
  const id=u.searchParams.get('user_id')?.slice(3)||body?.user_id,revision=u.searchParams.get('updated_at')?.slice(3);
  const req={method,id,revision,body};this.requests.push(req);if(this.hook)await this.hook(req);
  const send=(data,status=200)=>new Response(JSON.stringify(data),{status,headers:{'content-type':'application/json'}});
  const old=this.rows.get(id);
  if(method==='GET')return send(old?[clone(old)]:[]);
  if(method==='POST'){if(old)return send({code:'23505',message:'duplicate user'},409);const row={...body,updated_at:new Date(++this.clock).toISOString()};this.rows.set(id,row);return send([clone(row)],201)}
  if(method==='PATCH'){if(!old||old.updated_at!==revision)return send([]);const row={...old,...body,updated_at:new Date(++this.clock).toISOString()};this.rows.set(id,row);return send([clone(row)])}
  throw new Error('Unexpected database method '+method)
 }}}
function client(db,id='user-a'){
 const values=new Map(),notices=[],c={console,URL,URLSearchParams,Headers,Request,Response,TextEncoder,TextDecoder,AbortController,WebSocket,crypto,
  setTimeout,clearTimeout,setInterval,clearInterval,fetch:db.fetch.bind(db),localStorage:{getItem:k=>values.get(k)||null,setItem:(k,v)=>values.set(k,String(v)),removeItem:k=>values.delete(k)},
  ACC:{user:{id},preview:false},packJSON:async x=>JSON.stringify(x),unpackJSON:async x=>JSON.parse(x),toast:t=>notices.push(t),
  running:true,NET:{on:false},G:{over:false},serialize:()=>JSON.stringify({v:1,G:{time:1},X:{}}),hasSave:()=>false,SAVE_KEY:'normal',normalSaveKey:()=> 'normal_'+c.ACC.user.id,
  reinoKey:()=> 'alv_reino_v1_'+c.ACC.user.id,reinoCkKey:()=> 'alv_reino_ck_'+c.ACC.user.id,reinoMetaKey:()=> 'alv_reino_meta_'+c.ACC.user.id,
  reinoDef:()=>({t:'Chapter'}),REINO_N:200,$:()=>({hidden:true,lastChild:{},dataset:{}})};
 vm.createContext(c);vm.runInContext(sdk,c);c.ACC.sb=c.supabase.createClient('http://test.invalid','sb_publishable_test',{auth:{persistSession:false,autoRefreshToken:false,detectSessionInUrl:false},global:{fetch:db.fetch.bind(db)}});
 vm.runInContext(code,c);return{c,values,notices}
}
const decoded=(db,id='user-a')=>JSON.parse(db.rows.get(id).data);
async function test(name,run){await run();console.log('PASS '+name)}
(async()=>{
 await test('clear normal retries a stale revision and preserves another device kingdom',async()=>{
  const db=database();db.seed('user-a',{v:2,normal:{v:1},reino:realm(10)});const a=client(db),b=client(db),gate=deferred(),started=deferred();let held=false;
  db.hook=async r=>{if(r.method==='PATCH'&&!held){held=true;started.resolve();await gate.promise}};
  const clearing=a.c.cloudClearNormal();await started.promise;await b.c.cloudPut('reino',realm(999));gate.resolve();assert.equal(await clearing,true);
  assert.equal(decoded(db).reino.G.time,999);assert.equal(decoded(db).normal,null);assert.ok(db.requests.filter(r=>r.method==='PATCH').length>=3)
 });
 await test('a delayed clear never deletes a newer normal save from another device',async()=>{
  const db=database();db.seed('user-a',{v:2,normal:{v:1,G:{time:10}},reino:realm(50)});const a=client(db),b=client(db),gate=deferred(),started=deferred();let held=false;
  db.hook=async r=>{if(r.method==='PATCH'&&!held){held=true;started.resolve();await gate.promise}};
  const clearing=a.c.cloudClearNormal();await started.promise;await b.c.cloudPut('normal',{v:1,G:{time:999}});gate.resolve();assert.equal(await clearing,false);
  assert.equal(decoded(db).normal.G.time,999);assert.equal(decoded(db).reino.G.time,50)
 });
 await test('first insert conflict preserves both slots across two devices',async()=>{
  const db=database(),a=client(db),b=client(db),gate=deferred(),started=deferred();let held=false;
  db.hook=async r=>{if(r.method==='POST'&&!held){held=true;started.resolve();await gate.promise}};
  const save=a.c.cloudPut('normal',{v:1,G:{time:4}});await started.promise;await b.c.cloudPut('reino',realm(30));gate.resolve();await save;
  assert.equal(decoded(db).normal.G.time,4);assert.equal(decoded(db).reino.G.time,30)
 });
 await test('same-client save and clear retain their original ordering',async()=>{
  const db=database(),a=client(db);await Promise.all([a.c.cloudPut('normal',{v:1}),a.c.cloudClearNormal(),a.c.cloudPut('reino',realm(80))]);
  assert.equal(decoded(db).normal,null);assert.equal(decoded(db).reino.G.time,80);assert.ok(db.rows.has('user-a'),'empty slots do not physically delete the shared row')
 });
 await test('a response from a previous account is never adopted locally',async()=>{
  const db=database();db.seed('user-a',{v:2,normal:null,reino:realm(123)});const a=client(db),gate=deferred(),started=deferred();
  db.hook=async r=>{if(r.method==='GET'){started.resolve();await gate.promise}};
  const sync=a.c.reinoCloudSync();await started.promise;a.c.cloudInvalidate();a.c.ACC.user={id:'user-b'};gate.resolve();assert.equal(await sync,false);
  assert.equal(a.values.has('alv_reino_v1_user-b'),false);assert.equal(a.values.has('alv_reino_v1_user-a'),false)
 });
 await test('account changes during compression cannot send a write for the new account',async()=>{
  const db=database(),a=client(db),gate=deferred(),started=deferred();a.c.packJSON=async row=>{started.resolve();await gate.promise;return JSON.stringify(row)};
  const save=a.c.cloudSave(true);await started.promise;a.c.cloudInvalidate();a.c.ACC.user={id:'user-b'};gate.resolve();assert.equal(await save,false);
  assert.equal(db.requests.some(r=>r.method!=='GET'),false);assert.equal(db.rows.size,0)
 });
 await test('signing out and back in to the same account invalidates old work',async()=>{
  const db=database();db.seed('user-a',{v:2,normal:null,reino:realm(123)});const a=client(db),gate=deferred(),started=deferred();
  db.hook=async()=>{started.resolve();await gate.promise};const sync=a.c.reinoCloudSync();await started.promise;a.c.cloudInvalidate();a.c.ACC.user=null;a.c.cloudInvalidate();a.c.ACC.user={id:'user-a'};gate.resolve();assert.equal(await sync,false);assert.equal(a.values.size,0)
 });
 await test('old single-save format migrates without losing the kingdom',async()=>{
  const db=database();db.seed('user-a',realm(90));const a=client(db);await a.c.cloudPut('normal',{v:1,G:{time:2}});
  assert.equal(decoded(db).v,2);assert.equal(decoded(db).reino.G.time,90);assert.equal(decoded(db).normal.G.time,2)
 });
 await test('persistent conflicts stop without an unconditional overwrite',async()=>{
  const db=database();db.seed('user-a',{v:2,normal:null,reino:realm(600)});const a=client(db);
  db.hook=async r=>{if(r.method==='PATCH')db.rows.get(r.id).updated_at=new Date(++db.clock).toISOString()};
  await assert.rejects(a.c.cloudPut('normal',{v:1}),/noutro dispositivo/);assert.equal(db.requests.filter(r=>r.method==='PATCH').length,4);assert.equal(decoded(db).reino.G.time,600);assert.equal(decoded(db).normal,null)
 });
 await test('failed cloud writes leave the local save untouched',async()=>{
  const db=database(),a=client(db);a.values.set('normal','local backup');db.hook=async()=>{throw new Error('offline')};assert.equal(await a.c.cloudSave(true),false);assert.equal(a.values.get('normal'),'local backup')
 });
})().catch(e=>{console.error(e);process.exitCode=1});
