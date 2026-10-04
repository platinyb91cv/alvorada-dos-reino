from PIL import Image
from rembg import remove, new_session
import json,sys
im=Image.open('sheet.png').convert('RGB')
BOX={'v_ocioso':(440,112,494,240),'v_madeira':(507,112,571,240),'v_pedra':(584,108,646,240),'v_ouro':(660,112,721,240),'v_agricultura':(734,112,804,239),'v_caca':(807,112,878,241),'v_construcao':(880,112,954,240),'v_transporte':(959,112,1026,236),
 'barcoPesca':(1003,607,1091,738),'transporte':(1102,610,1201,736),'gale':(1206,630,1320,746),'incendiario':(1330,617,1406,741),'navioPesado':(1412,592,1509,746)}
model=sys.argv[1] if len(sys.argv)>1 else 'isnet-general-use'
ses=new_session(model)
for k,b in BOX.items():
  x0,y0,x1,y1=b;pad=0
  cr=im.crop(b)
  big=cr.resize((cr.width*4,cr.height*4),Image.LANCZOS)
  out=remove(big,session=ses)
  out=out.resize(cr.size,Image.LANCZOS)
  out.save(f'cut_{k}.png')
  print(k,out.getbbox())
