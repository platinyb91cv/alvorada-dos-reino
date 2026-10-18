from pathlib import Path
import json,struct,hashlib,math
from PIL import Image
D=Path(__file__).resolve().parent.parent
for u in ['guerreiro','lanceiro','espadachim','arqueiro','besteiro']:
 b=(D/(u+'.glb')).read_bytes();p=json.loads((D/(u+'.verification.json')).read_text());assert b[:4]==b'glTF' and len(b)==struct.unpack_from('<I',b,8)[0] and len(b)<50000000
 assert hashlib.sha256(b).hexdigest()==p['sha256'];n=struct.unpack_from('<I',b,12)[0];j=json.loads(b[20:20+n]);start=28+n
 assert [j['nodes'][i]['name'] for i in j['skins'][0]['joints']]==p['boneNames'] and p['boneCount']==len(p['boneNames'])==24
 assert all('uri' not in x for x in j.get('images',[])+j.get('buffers',[]))
 def vals(idx):
  a=j['accessors'][idx];v=j['bufferViews'][a['bufferView']];w={'SCALAR':1,'VEC3':3,'VEC4':4}[a['type']];assert a['componentType']==5126
  return [struct.unpack_from('<'+'f'*w,b,start+v.get('byteOffset',0)+a.get('byteOffset',0)+i*v.get('byteStride',w*4)) for i in range(a['count'])]
 triangles=sum(j['accessors'][x['indices']]['count']//3 for m in j['meshes'] for x in m['primitives']);assert triangles==p['triangles']
 assert len(j['animations'])==len(p['clips'])==1
 for a,c in zip(j['animations'],p['clips']):
  ts=[v[0] for s in a['samplers'] for v in vals(s['input'])];assert a['name']==c['name'] and abs(max(ts)-min(ts)-c['durationSeconds'])<1e-6
  channel=next(ch for ch in a['channels'] if ch['target']['path']=='translation' and j['nodes'][ch['target']['node']]['name']=='Hips');v=vals(a['samplers'][channel['sampler']]['output']);delta=[v[-1][k]-v[0][k] for k in range(3)]
  node=channel['target']['node'];scale=[1,1,1]
  while True:
   parent=next((x for x in j['nodes'] if node in x.get('children',[])),None)
   if parent is None:break
   assert 'matrix' not in parent and parent.get('rotation',[0,0,0,1])==[0,0,0,1]
   scale=[x*y for x,y in zip(scale,parent.get('scale',[1,1,1]))];node=j['nodes'].index(parent)
  expected=[delta[k]*scale[k] for k in range(3)];actual=p['rootDisplacementPerWalkCycle']['vectorMeters'];converted=actual
  assert max(abs(x-y) for x,y in zip(expected,converted))<1e-5,(u,expected,converted)
 assert p['forwardAxis']=={'glTF':'+Z','Blender':'-Y','evidence':'Front-facing S render looks along local +Y onto the model; face points -Y. Root travels -Y, stance feet move +Y relative to hips.'}
 assert Image.open(D/(u+'_8dir.png')).size==(1072,1184)
 assert p['heightMeters']>1.4 and p['heightMeters']<2.2 and p['clips'][0]['walkCycles']==1
 print('PASS',u,'hash, embedded textures, skeleton, clip, triangles, root displacement and sheet')
print('PASS: five Meshy pilot packages')
