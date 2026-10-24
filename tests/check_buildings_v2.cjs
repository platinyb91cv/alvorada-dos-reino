const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..'),dir=path.join(root,'arte/edificios-v2/publicacao'),web=path.join(root,'www/assets/edificios-v2');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8')),hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const manifest=read(path.join(dir,'manifest.json')),meta=read(path.join(web,'bld-v2.json')),compat=read(path.join(web,'bld-compatibilidade.json')),proof=read(path.join(dir,'atlas.verification.json'));
const html=fs.readFileSync(path.join(root,'www/index.html'),'utf8'),match=html.match(/const BLDART=\{wide:true,ready:false,img:null,meta:(\{[^\r\n]*\}),teams:new Map/);
assert.ok(match,'building metadata/cache initialization missing');const embedded=JSON.parse(match[1]);
assert.equal(manifest.entries.length,37);assert.equal(Object.keys(meta).length,37);assert.deepEqual(Object.keys(meta).sort(),manifest.entries.map(x=>x.key).sort());
assert.deepEqual(embedded,{...meta,...compat});assert.deepEqual(Object.keys(compat).sort(),['mercado|1','mercado|2','oficina|2']);
assert.ok(html.includes("im.src='assets/edificios-v2/bld-atlas-v2.webp'"));assert.equal(proof.atlasSha256,hash(path.join(web,'bld-atlas-v2.webp')));
assert.equal(proof.metadataSha256,hash(path.join(web,'bld-v2.json')));assert.ok(proof.decodedRgbaBytes<=proof.legacyDecodedRgbaBytes,'decoded atlas memory regressed');
for(const e of manifest.entries){const m=meta[e.key];assert.deepEqual(Object.keys(m).sort(),['f','xl','xr','yb','yl']);assert.ok(m.xr>m.xl&&m.yb>=0);const [x,y,w,h]=m.f;assert.ok(x>=0&&y>=0&&w>0&&h>0&&x+w<=proof.atlasDimensions[0]&&y+h<=proof.atlasDimensions[1]);assert.equal(hash(path.join(dir,e.path)),e.sha256);if(e.type==='ruina')assert.equal(e.flagBounds,null);else assert.ok(e.flagBounds&&e.flagBounds[2]<w*.5);}
const baseline=read(path.join(dir,'baseline.json'));assert.ok(Buffer.byteLength(html)<=baseline.indexBytes*1.10,'index growth exceeded 10%');assert.equal(Object.keys(read(path.join(dir,'legacy/bld-atual.json'))).length,40);assert.ok(fs.existsSync(path.join(root,'arte/edificios/bld.json'))&&fs.existsSync(path.join(root,'arte/edificios/bld_atlas_gemini.png')));
console.log('PASS buildings v2: 37 approved frames, 3 legacy variants, bounds, hashes, cache, memory and index budget');
