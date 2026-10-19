from pathlib import Path
import json,struct,hashlib,math,argparse
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('--assets',default=str(Path(__file__).resolve().parent.parent));p.add_argument('--previous');p.add_argument('--source');args=p.parse_args();D=Path(args.assets)
def read(p):
 b=p.read_bytes();assert b[:4]==b'glTF' and len(b)==struct.unpack_from('<I',b,8)[0];n=struct.unpack_from('<I',b,12)[0];j=json.loads(b[20:20+n]);return j,b[28+n:28+n+j['buffers'][0]['byteLength']],b
width={5120:1,5121:1,5122:2,5123:2,5125:4,5126:4};dims={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}
def packed(j,b,i):
 a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];assert not a.get('sparse');w=width[a['componentType']]*dims[a['type']];o=v.get('byteOffset',0)+a.get('byteOffset',0);return b''.join(b[o+k*v.get('byteStride',w):o+k*v.get('byteStride',w)+w]for k in range(a['count']))
def rows(j,b,i):
 a=j['accessors'][i];assert a['componentType']==5126;return list(struct.iter_unpack('<'+'f'*dims[a['type']],packed(j,b,i)))
def digest(j,b,a):
 h=hashlib.sha256()
 for c in a['channels']:
  s=a['samplers'][c['sampler']];h.update(j['nodes'][c['target']['node']]['name'].encode());h.update(c['target']['path'].encode());h.update(packed(j,b,s['input']));h.update(packed(j,b,s['output']))
 return h.hexdigest()
for u in ['guerreiro','lanceiro','espadachim','arqueiro','besteiro']:
 j,b,raw=read(D/(u+'.glb'));proof=json.loads((D/(u+'.verification.json')).read_text());assert len(raw)<50000000 and hashlib.sha256(raw).hexdigest()==proof['sha256'];assert proof['glbBytes']==len(raw)
 names=[j['nodes'][i]['name']for i in j['skins'][0]['joints']];assert names==proof['boneNames']and len(names)==proof['boneCount']==24
 expected=['Idle','Walk','Attack','Hit','Death']if u!='besteiro'else['Idle','Walk','Hit','Death'];assert [a['name']for a in j['animations']]==expected
 assert all('uri'not in x for x in j.get('images',[])+j.get('buffers',[]));assert len({digest(j,b,a)for a in j['animations']})==len(expected)
 triangles=sum(j['accessors'][q['indices']]['count']//3 for m in j['meshes']for q in m['primitives']);assert triangles==proof['triangles']
 for a,c,pr in zip(j['animations'],proof['clips'],proof['sourceProof']):
  assert c['name']==a['name']and digest(j,b,a)==c['animationSha256']==pr['outputAnimationSha256'];ts=[v[0]for s in a['samplers']for v in rows(j,b,s['input'])];assert abs(max(ts)-min(ts)-c['durationSeconds'])<1e-7
  target=next(ch for ch in a['channels']if j['nodes'][ch['target']['node']]['name']=='Hips'and ch['target']['path']=='translation');v=rows(j,b,a['samplers'][target['sampler']]['output']);extent=[max(r[k]for r in v)-min(r[k]for r in v)for k in range(3)]
  if a['name']in ['Idle','Attack','Hit']:assert extent[0]==extent[2]==0 and c['horizontalRootRangeMeters']<1e-8
  if a['name']=='Walk'and u in ['arqueiro','besteiro']:assert pr['sourceAnimationSha256']==pr['outputAnimationSha256']and pr['retainedExistingValues']
  if args.source and pr['source']!='previous pilot GLB':
   sj,sb,sraw=read(Path(args.source)/u/'motions.glb');assert hashlib.sha256(sraw).hexdigest()==pr['sourceFileSha256'];sa=next(x for x in sj['animations']if x['name']==pr['source']);assert digest(sj,sb,sa)==pr['sourceAnimationSha256']
   assert len(sa['channels'])==len(a['channels'])
   for new,old in zip(a['channels'],sa['channels']):
    ns=a['samplers'][new['sampler']];os=sa['samplers'][old['sampler']];assert j['nodes'][new['target']['node']]['name']==sj['nodes'][old['target']['node']]['name']and new['target']['path']==old['target']['path'];assert packed(j,b,ns['input'])==packed(sj,sb,os['input'])
    if pr['rootLocked']and j['nodes'][new['target']['node']]['name']=='Hips'and new['target']['path']=='translation':assert [r[1]for r in rows(j,b,ns['output'])]==[r[1]for r in rows(sj,sb,os['output'])]
    else:assert packed(j,b,ns['output'])==packed(sj,sb,os['output'])
 if args.previous:
  oj,ob,oraw=read(Path(args.previous)/(u+'.glb'));assert b[:len(ob)]==ob
  for key in ['nodes','meshes','skins','materials','images']:assert j[key]==oj[key]
 assert Image.open(D/(u+'_8dir.png')).size==(1072,1184)
 print('PASS',u,len(expected),'distinct clips, 24 bones, root locks, SHA-256, preserved source curves and geometry')
print('PASS: combat pilots; no game integration')
