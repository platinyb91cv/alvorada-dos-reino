import sys,json
for l in sys.stdin:
  if l.startswith('SEED'):
    sd,js=l.split(' ',2)[1],l.split(' ',2)[2];d=json.loads(js);print(sd,{k:d[k] for k in ['overT','winner','cross','shipLand','stuck','idleV','neg','pop','dup','bad','saveOk','wallsBuilt','gatePass','siege','priests','conv','ships','shipKills','fish','techs','ages','dmgWall']},d.get('ci'),d.get('si'),d.get('ii'))
    print('   tipos:',d['types'])
  else: print(l.strip()[:400])
