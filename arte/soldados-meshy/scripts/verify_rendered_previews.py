from pathlib import Path
from PIL import Image
import json,hashlib
import argparse
p=argparse.ArgumentParser();p.add_argument('--render-root',required=True);args=p.parse_args();D=Path(__file__).resolve().parent.parent;O=Path(args.render_root).resolve();frames=list(O.glob('*/*/frames/*.png'));assert len(frames)==306,len(frames)
for p in frames:
 im=Image.open(p).convert('RGBA');box=im.getchannel('A').getbbox();assert box and box[0]>0 and box[1]>0 and box[2]<im.width and box[3]<im.height,(str(p),box)
for u in ['guerreiro','lanceiro','espadachim','arqueiro','besteiro']:
 p=D/(u+'.verification.json');j=json.loads(p.read_text());j['blenderReimport']={}
 for report in (O/u).glob('*/render-report.json'):
  r=json.loads(report.read_text());assert r['sourceModelSha256']==j['sha256']and r['selectedClip']==report.parent.name and r['bones']==24 and r['triangles']==j['triangles'];j['blenderReimport'][r['selectedClip']]={'bones':24,'durationSeconds':r['durationSeconds'],'renderedFrames':len(r['frames']),'poseSampleSha256':hashlib.sha256(json.dumps(r['samples'],sort_keys=True).encode()).hexdigest()}
 assert len({v['poseSampleSha256']for v in j['blenderReimport'].values()})==len(j['blenderReimport'])
 p.write_text(json.dumps(j,indent=2)+'\n')
print('PASS: 306 unclipped frames; each rendered clip reimported and distinct; all source hashes match')
