from pathlib import Path
import subprocess,json
from PIL import Image,ImageDraw
import argparse
p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--blender',default='blender');p.add_argument('--reuse',action='store_true');args=p.parse_args();D=Path(__file__).resolve().parent.parent;O=Path(args.output).resolve()
for u in ['guerreiro','lanceiro','espadachim','arqueiro','besteiro']:
 clips=['Walk','Idle','Attack','Hit','Death']if u in ['guerreiro','lanceiro','espadachim']else(['Idle','Attack','Hit','Death']if u=='arqueiro'else['Idle','Hit','Death'])
 for clip in clips:
  temp=O/u/clip;temp.mkdir(parents=True,exist_ok=True)
  if not (args.reuse and (temp/'render-report.json').exists()):
   with (temp/'render.log').open('w')as log:p=subprocess.run([args.blender,'-b','--python',str(D/'scripts/render_review.py'),'--','--unit',u,'--clip',clip,'--output',str(temp)],stdout=log,stderr=subprocess.STDOUT)
   assert p.returncode==0 and 'PILOT_RENDER_COMPLETE'in(temp/'render.log').read_text(errors='replace'),(u,clip)
  print('COMBAT_RENDERED',u,clip,flush=True)
  if clip=='Walk':
   sheet=Image.new('RGB',(1072,1184),(27,32,38));draw=ImageDraw.Draw(sheet)
   for d,label in enumerate(['SE','S','SW','W','NW','N','NE','E']):
    draw.text((4,d*148+65),label,fill='white')
    for f in range(8):
     im=Image.open(temp/'frames'/f'{d:02d}-{f:02d}.png').convert('RGBA');sheet.paste(im,(48+f*128,d*148),im);draw.text((52+f*128,d*148+130),str(f),fill='white')
   sheet.save(D/(u+'_8dir.png'))
 actions=[c for c in clips if c!='Walk'];sheet=Image.new('RGB',(6*128+70,len(actions)*148),(27,32,38));draw=ImageDraw.Draw(sheet)
 for row,c in enumerate(actions):
  draw.text((2,row*148+60),c,fill='white')
  for f in range(6):
   im=Image.open(O/u/c/'frames'/f'01-{f:02d}.png').convert('RGBA');sheet.paste(im,(70+f*128,row*148),im)
 sheet.save(D/(u+'_combate.png'));print('COMBAT_PREVIEW_COMPLETE',u,flush=True)

import sys
subprocess.run([sys.executable,str(D/'scripts/verify_rendered_previews.py'),'--render-root',str(O)],check=True)
