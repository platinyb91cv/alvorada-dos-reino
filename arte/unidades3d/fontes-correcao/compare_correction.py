from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,sys,math
O=Path(sys.argv[sys.argv.index('--sources')+1]).resolve()if '--sources'in sys.argv else Path(__file__).resolve().parent.parent
B=Path(sys.argv[sys.argv.index('--baseline')+1]).resolve()if '--baseline'in sys.argv else O.parent/'correcao-aldeao-guerreiro'/'antes'
out=Path(sys.argv[sys.argv.index('--output')+1]).resolve()if '--output'in sys.argv else O.parent/'correcao-aldeao-guerreiro'
out.mkdir(parents=True,exist_ok=True)
rows=[('aldeao',state,d)for state in ['walk','chop','mine','build','farm','forage','butcher','carry']for d in [0,1]]+[('guerreiro','walk',d)for d in [0,1]]
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',19);big=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',28)
extents=[0,0,0,0]
for name,state,direction in rows:
 for root in [B,O]:
  m=json.loads((root/name/'atlas.json').read_text());k=30/m['h']
  for i in m['states'][state]:
   _,_,w,h,ax,ay=m['f'][direction*m['framesPerDirection']+i]
   extents=[max(a,math.ceil(b*k))for a,b in zip(extents,[ax,w-ax,ay,h-ay])]
gx,gy=extents[0]+4,extents[2]+4;bw,bh=extents[0]+extents[1]+8,extents[2]+extents[3]+8
CW,CH=bw*3,bh*3;left=190;gap=24;W=left+16*CW+gap;header=125;RH=CH+28
sheet=Image.new('RGB',(W,header+RH*len(rows)),'#222c39');draw=ImageDraw.Draw(sheet)
draw.text((20,12),'ALDEÃO E GUERREIRO — CORREÇÃO LOCAL DOS ATLAS',font=big,fill='white')
draw.text((20,52),'30 px de altura no jogo → ampliação 3× sem suavização. Mesma câmara, escala e âncora de chão. Quadros pela ordem do atlas.',font=font,fill='#c7d5e5')
draw.text((left,88),'ANTES — primeira revisão ae45420',font=big,fill='#ffcc99');draw.text((left+8*CW+gap,88),'DEPOIS — ferramentas + 3 clips Prime',font=big,fill='#a7efb4')
for row,(name,state,direction)in enumerate(rows):
 yy=header+row*RH;draw.text((12,yy+24),name.upper(),font=font,fill='white');draw.text((12,yy+54),state.upper(),font=font,fill='#8fdbff');draw.text((12,yy+84),['SE','S'][direction],font=big,fill='white')
 for side,root in enumerate([B,O]):
  meta=json.loads((root/name/'atlas.json').read_text());atlas=Image.open(root/name/'atlas.webp').convert('RGBA');ids=meta['states'][state]
  for column,i in enumerate(ids):
   sx,sy,w,h,ax,ay=meta['f'][direction*meta['framesPerDirection']+i];scale=30/meta['h'];tile=atlas.crop((sx,sy,sx+w,sy+h));tile=tile.resize((max(1,round(w*scale)),max(1,round(h*scale))),Image.Resampling.LANCZOS)
   tx,ty=round(gx-ax*scale),round(gy-ay*scale);assert tx>=0 and ty>=0 and tx+tile.width<=bw and ty+tile.height<=bh,(name,state,direction,i,'comparison cell clips sprite')
   cell=Image.new('RGBA',(bw,bh),(45,58,73,255));cd=ImageDraw.Draw(cell);cd.line((0,gy,bw-1,gy),fill=(75,94,113,255));cell.alpha_composite(tile,(tx,ty))
   cell=cell.convert('RGB').resize((CW,CH),Image.Resampling.NEAREST);xx=left+side*(8*CW+gap)+column*CW;sheet.paste(cell,(xx,yy));draw.text((xx+6,yy+CH+3),str(column+1)+' / '+str(len(ids)),font=font,fill='#afc0d4')
sheet.save(out/'comparacao-antes-depois.png',optimize=True)
sheet.resize((W//2,sheet.height//2),Image.Resampling.LANCZOS).save(out/'comparacao-resumo.png',optimize=True)
print(out/'comparacao-antes-depois.png',sheet.size)
