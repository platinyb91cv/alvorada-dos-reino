// Botão Guardar: mensagem por cima dos ecrãs, confirmação no próprio botão e verificação da escrita.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const html=fs.readFileSync(path.join(__dirname,'..','www/index.html'),'utf8');
const z=+html.match(/#toast\{[^}]*z-index:(\d+)/)[1];const screens=[...html.matchAll(/\.(?:screen|modal)\{[^}]*z-index:(\d+)/g)].map(m=>+m[1]);
assert.ok(screens.length&&screens.every(v=>z>v),'toast above pause/menu screens');
assert.match(html,/function saveGame\(silent\)\{ \/\/ devolve \{ok,msg\}/);
assert.match(html,/if\(localStorage\.getItem\(key\)!==data\)throw new Error\('verify'\)/,'save is read back');
assert.match(html,/\$\('bSave'\)\.onclick=\(\)=>\{sfx\('click'\);const res=saveGame\(false\);saveBtnFlash\(res\);if\(res\.ok\)cloudSave\(false\)\};/);
assert.match(html,/'✓ Guardado às '/);assert.match(html,/A partida já terminou: não há nada para guardar/);assert.match(html,/usa «Gravar e sair»/);
assert.match(html,/Partida guardada ✔ — usa «Continuar» no menu para voltar/);
assert.match(html,/const kills=t=>\(typeof G!=='undefined'&&G&&G\.obj/);
console.log('PASS: save button confirms (toast on top, button state, read-back)');
