import os,tempfile,importlib,sys,json
from pathlib import Path
tmp=tempfile.TemporaryDirectory()
os.environ['DATABASE_PATH']=str(Path(tmp.name)/'qa.db')
import kyc_server as k
k.init()

def make_game(rounds=8,spice=1):
 with k.cn() as c:
  cur=c.execute("INSERT INTO games(code,host,status,round_no,topics,custom_context,spice,custom_questions,prize,rounds,created) VALUES(?,?,?,?,?,?,?,?,?,?,?)",('QA123','host','playing',0,'[]','',spice,'[]','QA Prize',rounds,k.now()))
  gid=cur.lastrowid
  for name in ['Eran','Shai','Avi']:
   c.execute("INSERT INTO players(game_id,name,token,joined) VALUES(?,?,?,?)",(gid,name,name.lower(),k.now()))
 return k.game('QA123')

g=make_game()
ps=k.players(g['id'])
assert k.total_rounds(g)==8
for rn in range(8):
 with k.cn() as c:c.execute("UPDATE games SET round_no=? WHERE id=?",(rn,g['id']))
 g=k.game('QA123')
 typ,text,opts,sub=k.qdata(g,ps)
 assert sub is not None and text and len(opts)>=2, (rn,typ,text,opts)

# Memory-based PlotTwist should stay playable and produce concrete options.
with k.cn() as c:
 c.execute("UPDATE games SET round_no=5,memory=? WHERE id=?",(json.dumps([
  {'round':0,'subject':'Eran','question':'עם מי Eran היה יוצא לחופשה?','answer':'Shai','type':'room'},
  {'round':1,'subject':'Shai','question':'מה Shai היה עושה בדייט?','answer':'זורם','type':'know'},
  {'round':2,'subject':'Avi','question':'מי Avi סומך עליו?','answer':'Eran','type':'room'}
 ]),g['id']))
g=k.game('QA123');typ,text,opts,sub=k.qdata(g,ps)
assert str(typ).startswith('callback') and len(opts)>=2
assert k.interactive_prompt(g,typ,text,opts[0],sub) is not None
print('QA_SMOKE_OK')
