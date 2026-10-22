// Carroça de carga (treina no armazém): os aldeões descarregam nela; leva ao armazém sozinha e volta. Desenho 3D partilhado com a carroça de comércio.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),html=fs.readFileSync(path.join(root,'www/index.html'),'utf8');
assert.match(html,/carrocaCarga:\{name:'Carroça de Carga',[^\n]*cls:'cart'[^\n]*cargo:150/);
assert.match(html,/armazem:\{[^\n]*train:\['carrocaCarga'\]/);
assert.match(html,/const CART_R=5,CART_WAIT=40;/);assert.match(html,/function nearCart\(u\)\{/);assert.match(html,/function cartTick\(dt\)\{/);
assert.match(html,/if\(!d\.naval&&u\.carry>0&&u\.ctype\)\{const c=nearCart\(u\);/,'villagers unload into a parked cart');
assert.match(html,/villageTick\(dt\);cartTick\(dt\);/,'cart logic runs in the deterministic step');
assert.match(html,/ca:e\.cargaN\?\{c:e\.carga,n:e\.cargaN/,'cart load is saved');assert.match(html,/if\(q\.ca\)\{u\.carga=q\.ca\.c/,'cart load is restored');
const step=html.slice(html.indexOf('function cartTick(dt){'),html.indexOf('function nearestDrop('));assert.ok(!/Math\.random|performance\.now/.test(step),'deterministic');
const data=JSON.parse(html.match(/const UNIT3D_CAV_DATA=(\{[^\n]+\});/)[1]);const m=data.carroca;assert.ok(m);
for(const [s,n] of [['idle',2],['walk',8],['hit',2],['death',4]])assert.equal(m.states[s].length,n,s);
const webp=fs.readFileSync(path.join(root,'www/assets/units3d/carroca.webp'));assert.equal(crypto.createHash('sha256').update(webp).digest('hex'),m.atlasSha256);
assert.match(html,/if\(UNIT3D\.carroca\)UNIT3D\.carrocaCarga=UNIT3D\.carroca;/);
const types=JSON.parse(html.match(/const UNIT3D_TYPES=(\[[^\]]+\]);/)[1].replace(/'/g,'"'));for(const t of ['carroca','carrocaCarga','catapulta'])assert.ok(types.includes(t),t);
console.log('PASS: cargo cart (gameplay, save, shared 3D atlas)');
