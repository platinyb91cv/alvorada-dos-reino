import json,glob,os,re
p='/tmp/claude-0/wt/www/index.html';s=open(p).read()
D={}
for f in sorted(glob.glob('/tmp/claude-0/wt/www/assets/units3d-hd/*.json')):D[os.path.basename(f)[:-5]]=json.load(open(f))
order=['guerreiro','lanceiro','espadachim','arqueiro','besteiro'];D={k:D[k] for k in order if k in D}
i=s.index('const UNIT3D_HD_DATA=');j=s.index('\n',i);s=s[:i]+'const UNIT3D_HD_DATA='+json.dumps(D,separators=(',',':'))+';'+s[j:]
open(p,'w').write(s);print(list(D))
