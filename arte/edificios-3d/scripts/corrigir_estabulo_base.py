import numpy as np,sys
from PIL import Image
def fix(path,out):
  im=Image.open(path).convert('RGBA');A=np.asarray(im).astype(np.float32);h,w=A.shape[:2]
  al=A[...,3]>40;cols=np.arange(w);bot=np.array([np.nonzero(al[:,c])[0].max() if al[:,c].any() else -1 for c in cols])
  Bx=int(np.argmax(bot));By=bot[Bx]
  def fit(x0,x1):
    xs=np.arange(max(0,x0),min(w,x1));xs=xs[bot[xs]>0];p=np.polyfit(xs,bot[xs],1);return p
  pl=fit(Bx-110,Bx-15);pr=fit(Bx+12,Bx+70)
  sl=-pl[0];sr=pr[0]*-1 if pr[0]<0 else -pr[0]
  sl=pl[0]
  # pr slope negative (bot decreases going right) -> sr = -pr[0]
  xL=next(x for x in range(0,Bx) if bot[x]>0 and abs(bot[x]-np.polyval(pl,x))<6)
  xR=next(x for x in range(w-1,Bx,-1) if bot[x]>0 and abs(bot[x]-np.polyval(pr,x))<6)
  print('B',Bx,By,'slopes',round(sl,3),round(-pr[0],3),'corners',xL,xR)
  sR=-pr[0]
  H=( (Bx-xL)+(xR-Bx) )/2
  # mapeamento horizontal por troços (x novo -> x antigo) e corte vertical por coluna (verticais continuam verticais)
  nw=int(round(2*H+ (xL) + (w-1-xR)))  # margens laterais (beirais) mantêm-se
  newB=xL+H
  def oldx(nx):
    if nx<=xL: return nx
    if nx<=newB: return xL+(nx-xL)*(Bx-xL)/H
    if nx<=newB+H: return Bx+(nx-newB)*(xR-Bx)/H
    return xR+(nx-newB-H)
  def shift(ox): # quanto descer a coluna (antiga) para a base ficar a 0,5
    if ox<=Bx: d=(Bx-ox); return (sl-.5)*d - 0  # left: descer
    d=(ox-Bx); return (sR-.5)*d
  # nova imagem: base ideal y = By - 0.5*|nx-newB| ; coluna antiga desce shift, mas também a largura mudou: base nova a 0.5*dist nova
  out_cols=[]
  extra=int(max(0,max(shift(0),shift(w-1))))+4
  N=np.zeros((h+extra,nw,4),np.float32)
  for nx in range(nw):
    ox=oldx(nx);x0=int(np.floor(ox));t=ox-x0;x1=min(w-1,x0+1);x0=max(0,min(w-1,x0))
    col=A[:,x0]*(1-t)+A[:,x1]*t
    # deslocamento vertical: a base antiga nesta coluna está em By - s*|ox-Bx|; a nova deve estar em By - .5*|nx-newB|
    s=sl if ox<=Bx else sR
    oldbase=By-s*abs(ox-Bx);newbase=By-.5*abs(nx-newB);dy=newbase-oldbase
    yy=np.arange(h+extra)-dy;y0=np.floor(yy).astype(int);ty=(yy-y0)[:,None]
    v0=(y0>=0)&(y0<h);v1=(y0+1>=0)&(y0+1<h)
    c0=np.where(v0[:,None],col[np.clip(y0,0,h-1)],0);c1=np.where(v1[:,None],col[np.clip(y0+1,0,h-1)],0)
    N[:,nx]=c0*(1-ty)+c1*ty
  img=Image.fromarray(np.clip(N,0,255).astype(np.uint8),'RGBA');bb=img.getchannel('A').point(lambda v:255 if v>8 else 0).getbbox();img=img.crop((0,bb[1],nw,bb[3]))
  img.save(out);print('novo',img.size,'B novo',newB)
for n in sys.argv[1:]:fix(n+'.png',n+'_fix.png')
