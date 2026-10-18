"""Update only the two approved unit atlases in the current main-based checkout."""
from pathlib import Path
import json,re,shutil,hashlib,sys
O=Path(sys.argv[sys.argv.index('--sources')+1]).resolve()if '--sources'in sys.argv else Path(__file__).resolve().parent.parent
repo=Path(sys.argv[sys.argv.index('--repo')+1]).resolve()if '--repo'in sys.argv else O.parent/'alvorada-dos-reino'
p=repo/'www/index.html';html=p.read_text(encoding='utf-8');match=re.search(r'const UNIT3D_DATA=(\{[^\n]+\});',html);data=json.loads(match[1])
for name in ['aldeao','guerreiro']:
 d=O/name;data[name]=json.loads((d/'atlas.json').read_text())
 for ext in ['webp','json']:shutil.copyfile(d/('atlas.'+ext),repo/'www/assets/units3d'/(name+'.'+ext))
 proof=json.loads((d/'verification.json').read_text());stride=json.loads((d/'stride-verification.json').read_text());stride.pop('rows');
 if 'carry'in stride:stride['carry'].pop('rows')
 proof['locomotion']=stride;proof['atlasSha256']=data[name]['atlasSha256'];proof['renderCamera']=json.loads((d/'fixed-camera.json').read_text());proof['correction']=json.loads((d/'build-report.json').read_text())['correction'];proof['correctionChecks']=json.loads((d/'correction-verification.json').read_text())
 if name=='aldeao':proof['axeVisibility']=json.loads((d/'axe-visibility.json').read_text());assert proof['axeVisibility']['sourceModelSha256']==proof['optimizedGlbSha256'];assert len(proof['axeVisibility']['frames'])==48 and min(f['visibleBladeAreaAt30px']for f in proof['axeVisibility']['frames'])>0
 proof['secondPass']=json.loads((d/'second-pass-verification.json').read_text())
 render=json.loads((d/'render-report.json').read_text());assert render['sourceModelSha256']==proof['optimizedGlbSha256'];proof['renderStateClips']={state:sorted({f['clip']for f in render['frames']if f['state']==state})for state in render['states']}
 if name=='aldeao':
  proof['workMotions']=json.loads((d/'work-motion-provenance.json').read_text());proof['knifeVisibility']=json.loads((d/'knife-visibility.json').read_text());assert proof['knifeVisibility']['sourceModelSha256']==proof['optimizedGlbSha256']
  assert min(f['visibleBladeAreaAt30px']for f in proof['knifeVisibility']['frames']if f['direction']in ['SE','S'])>0
 (repo/'arte/unidades3d'/(name+'.verification.json')).write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
html=html[:match.start(1)]+json.dumps(data,separators=(',',':'))+html[match.end(1):]
old="((u.anim/(Math.PI*2))%1+1)%1"
new="((u.anim*(meta.locomotion?.[state]?.phaseScale||1)/(Math.PI*2))%1+1)%1"
a=html.index('function unit3dFrame(');b=html.index('\nfunction ',a+1);function=html[a:b]
if function.count(old)==1:function=function.replace(old,new)
else:assert function.count(new)==1,'Expected a single corrected unit3dFrame phase'
html=html[:a]+function+html[b:]
p.write_text(html,encoding='utf-8',newline='\n')
print('UPDATED_ONLY',list(data)[:2])
