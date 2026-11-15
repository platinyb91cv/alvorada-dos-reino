import numpy as np, subprocess, sys
src,dst,start,L,X=sys.argv[1],sys.argv[2],float(sys.argv[3]),float(sys.argv[4]),3.0
sr=48000
raw=subprocess.run(['ffmpeg','-loglevel','error','-ss',str(start),'-t',str(L+X),'-i',src,'-ac','1','-ar',str(sr),'-f','f32le','-'],capture_output=True).stdout
a=np.frombuffer(raw,np.float32).copy();n=int(L*sr);x=int(X*sr)
a=a[:n+x]
body=a[:n].copy();tail=a[n:n+x];r=np.linspace(0,1,x,dtype=np.float32)
body[:x]=body[:x]*np.sqrt(r)+tail*np.sqrt(1-r)  # emenda: fim cruza com o início
body*=0.5/max(1e-6,np.sqrt(np.mean(body**2))*4)  # nível médio parecido entre ficheiros
body=np.clip(body,-1,1)
subprocess.run(['ffmpeg','-loglevel','error','-y','-f','f32le','-ar',str(sr),'-ac','1','-i','-','-c:a','libopus','-b:a','40k',dst],input=body.tobytes())
