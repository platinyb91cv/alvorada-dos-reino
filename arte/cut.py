from PIL import Image
from rembg import remove, new_session
import json,sys
im=Image.open('sheet.png').convert('RGB')
BOX={'guerreiro':(25,348,112,507),'espadachim':(113,350,204,507),'lanceiro':(215,348,297,508),'arqueiro':(313,355,382,507),'besteiro':(410,370,490,504),
 'cavaleiro':(524,342,644,505),'cavPesada':(650,342,760,510),'cavArqueira':(765,344,890,508),
 'ariete':(904,352,1020,508),'catapulta':(1032,357,1188,508),'trebuchet':(1192,322,1362,524),'sacerdote':(1392,350,1502,515)}
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
