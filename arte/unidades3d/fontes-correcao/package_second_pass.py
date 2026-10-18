from pathlib import Path
import json,hashlib,zipfile,shutil,sys
O=Path(__file__).resolve().parent.parent;P=O.parent/'correcao-aldeao-guerreiro/segunda-volta';R=O.parent/'alvorada-dos-reino';files=[]
ledger={'provider':'Meshy','mode':'prime','authorizedMaximumCredits':39,'automaticPaidRetries':False,'newCharacterGenerations':0,'clips':[]}
for state in ['mine','build','butcher']:
 row={'state':state}
 for step in ['motion','retarget']:
  data=json.loads((P/f'{state}-{step}-status.json').read_text());assert data['status']=='SUCCEEDED';row[step]={'id':data['id'],'consumedCredits':data['consumed_credits'],'status':data['status']}
 row['sourceGlbSha256']=hashlib.sha256((P/(state+'.glb')).read_bytes()).hexdigest();ledger['clips'].append(row)
ledger['totalConsumedCredits']=sum(c[s]['consumedCredits']for c in ledger['clips']for s in ['motion','retarget']);assert ledger['totalConsumedCredits']==39
(P/'meshy-segunda-volta.json').write_text(json.dumps(ledger,indent=2));shutil.copyfile(P/'meshy-segunda-volta.json',R/'arte/unidades3d/meshy-segunda-volta.json')
if '--ledger-only'in sys.argv:
 print('ACTUAL_MESHY_CREDITS',ledger['totalConsumedCredits']);sys.exit(0)
for name in ['aldeao','guerreiro']:
 allowed=[name+'-jogo.blend',name+'-jogo.glb','atlas.json','atlas.webp','build-report.json','verification.json','correction-verification.json','second-pass-verification.json','stride-verification.json','fixed-camera.json','render-report.json','oito-direcoes.png']
 if name=='aldeao':allowed+=['work-motion-provenance.json','axe-visibility.json','knife-visibility.json']
 for filename in allowed:
  f=O/name/filename;assert f.is_file();files.append((f,'unidades-3d/'+name+'/'+f.name))
 for f in (O/name/'frames').glob('*.png'):files.append((f,'unidades-3d/'+name+'/frames/'+f.name))
 for f in (P/'antes'/name).iterdir():
  if f.is_file():files.append((f,'correcao-aldeao-guerreiro/segunda-volta/antes/'+name+'/'+f.name))
 for f in (P/'antes'/name/'frames').glob('*.png'):files.append((f,'correcao-aldeao-guerreiro/segunda-volta/antes/'+name+'/frames/'+f.name))
for f in (O/'source').iterdir():
 if f.suffix in ['.py','.js']:files.append((f,'unidades-3d/source/'+f.name))
files.append((O/'manifest.json','unidades-3d/manifest.json'))
for state in ['mine','build','butcher']:files.append((P/(state+'.glb'),'correcao-aldeao-guerreiro/segunda-volta/'+state+'.glb'))
# Importer reads status IDs and consumed credits; sanitized records suffice.
sanitized={}
for c in ledger['clips']:
 for step in ['motion','retarget']:
  s=c[step];sanitized['correcao-aldeao-guerreiro/segunda-volta/'+c['state']+'-'+step+'-status.json']={'id':s['id'],'status':s['status'],'consumed_credits':s['consumedCredits']}
for filename in ['meshy-segunda-volta.json','comparacao-antes-depois.png','atlas-alignment-verification.json']:files.append((P/filename,filename))
files.append((R/'arte/unidades3d/CORRECAO-ALDEAO-GUERREIRO.md','README.md'))
hashes={arc:hashlib.sha256(f.read_bytes()).hexdigest()for f,arc in files};target=P/'Fontes-segunda-volta-aldeao-guerreiro.zip'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=5)as z:
 for f,arc in files:z.write(f,arc)
 for arc,data in sanitized.items():z.writestr(arc,json.dumps(data,indent=2))
 z.writestr('package-sha256.json',json.dumps(hashes,indent=2))
with zipfile.ZipFile(target)as z:
 assert z.testzip()is None
 for arc,digest in hashes.items():assert hashlib.sha256(z.read(arc)).hexdigest()==digest
print('SECOND_SOURCE_PACKAGE_VERIFIED',target,target.stat().st_size,len(files))
