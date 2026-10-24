from pathlib import Path
import json,hashlib,re,shutil
R=Path(__file__).resolve().parent;repo=R.parent/'alvorada-dos-reino';htmlpath=repo/'www/index.html';units=['aldeao','guerreiro','lanceiro','espadachim','arqueiro','besteiro'];assets=repo/'www/assets/units3d-armados';proofdir=repo/'arte/unidades-armadas';assets.mkdir(parents=True,exist_ok=True);proofdir.mkdir(parents=True,exist_ok=True);metadata={};summary=[]
for unit in units:
 D=R/unit;meta=json.loads((D/'atlas.json').read_text());proof=json.loads((D/'verification.json').read_text());assert meta['directions']==8 and meta['h']==64;assert meta['atlasSha256']==hashlib.sha256((D/'atlas.webp').read_bytes()).hexdigest();assert proof['sha256']==hashlib.sha256((D/(unit+'-jogo.glb')).read_bytes()).hexdigest();assert proof['additionalMeshyCredits']==0
 proof['atlasSha256']=meta['atlasSha256'];proof['locomotion']=meta['locomotion'];proof['render']=json.loads((D/'render-report.json').read_text())
 if proof['render']['sourceModelSha256']!=proof['sha256']:
  removal=json.loads((D/'unused-track-removal.json').read_text());assert unit=='aldeao' and removal['allRetainedAnimationSamplersAndBinaryUnchanged'] and removal['sha256']==proof['sha256'];proof['render']['renderedContainerSha256BeforeRemovingUnusedTrack']=proof['render']['sourceModelSha256'];proof['render']['sourceModelSha256']=proof['sha256'];proof['render']['unusedSourceTrackRemoved']=removal['removed']
 metadata[unit]=meta
 for source,target in [(D/'atlas.webp',assets/(unit+'.webp')),(D/'atlas.json',assets/(unit+'.json')),(D/(unit+'-jogo.glb'),proofdir/(unit+'.glb')),(D/'oito-direcoes.png',proofdir/(unit+'_8dir.png'))]:shutil.copyfile(source,target)
 (proofdir/(unit+'.verification.json')).write_text(json.dumps(proof,indent=2),encoding='utf-8');shutil.copyfile(D/'build-report.json',proofdir/(unit+'.build.json'));shutil.copyfile(D/'stride-verification.json',proofdir/(unit+'.stride.json'));summary.append({'unit':unit,'modelBytes':proof['bytes'],'atlasBytes':(D/'atlas.webp').stat().st_size,'atlasSha256':meta['atlasSha256']})
s=htmlpath.read_text(encoding='utf-8');baseline=len(s.encode());encoded=json.dumps(metadata,separators=(',',':'))
loader="""const UNIT3D_ARMED_DATA=__DATA__;
function loadUnit3dPreferred(type,source){
 const preferred=UNIT3D_ARMED_DATA[type];
 function load(meta,base,fallback){const image=new Image();image.onload=()=>{source.meta=meta;source.img=image;source.teams.clear();source.ready=true};image.onerror=()=>{if(fallback)load(UNIT3D_DATA[type],'assets/units3d/',false);else source.ready=false};image.src=base+type+'.webp?v='+meta.atlasSha256.slice(0,12)}
 load(preferred||UNIT3D_DATA[type],preferred?'assets/units3d-armados/':'assets/units3d/',!!preferred)}
const UNIT3D={};
for(const type of Object.keys(UNIT3D_DATA)){const source={ready:false,img:null,wide:true,teams:new Map(),meta:UNIT3D_DATA[type]};UNIT3D[type]=source;loadUnit3dPreferred(type,source);}
UNIT3D.besteiroPesado=UNIT3D.besteiro;""".replace('__DATA__',encoded)
if 'const UNIT3D_ARMED_DATA=' in s:
 a=s.index('const UNIT3D_ARMED_DATA=');b=s.index('UNIT3D.besteiroPesado=UNIT3D.besteiro;',a)+len('UNIT3D.besteiroPesado=UNIT3D.besteiro;');s=s[:a]+loader+s[b:]
else:
 a=s.index('const UNIT3D={};');b=s.index('UNIT3D.besteiroPesado=UNIT3D.besteiro;',a)+len('UNIT3D.besteiroPesado=UNIT3D.besteiro;');s=s[:a]+loader+s[b:]
htmlpath.write_text(s,encoding='utf-8');scripts=proofdir/'scripts';scripts.mkdir(exist_ok=True)
for name in ['construir.py','renderizar.py','empacotar.py','medir.py','verificar_modelos.py','integrar.py']:
 shutil.copyfile(R/name,scripts/name)
report={'units':summary,'additionalMeshyCredits':0,'legacyAtlasFilesPreserved':True,'branch':'integracao-soldados-armados','indexBytesBeforeThisRun':baseline,'indexBytesAfter':htmlpath.stat().st_size,'legacyFallback':True,'scope':'Five existing Meshy soldiers plus the existing new villager; besteiroPesado reuses besteiro; cavalry/ships/king unchanged'};(proofdir/'integracao.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print('INTEGRATED_SIX_UNITS')
