"""Readiness is enforced by the server, not just by disabled UI controls."""
import json,os,sys,tempfile,threading
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
tmp=tempfile.TemporaryDirectory();os.environ['DATABASE_PATH']=str(Path(tmp.name)/'ready.db');os.environ.pop('DATABASE_URL',None);os.environ.pop('OPENAI_API_KEY',None)
import kyc_server as k
k.init();k.schedule_image_after_action=lambda *_:None
server=k.ThreadingHTTPServer(('127.0.0.1',0),k.H);threading.Thread(target=server.serve_forever,daemon=True).start()
def req(path,body=None,status=200):
 try:
  with urlopen(Request(f'http://127.0.0.1:{server.server_port}'+path,data=json.dumps(body).encode() if body is not None else None,headers={'Content-Type':'application/json'})) as r:code=r.status;data=json.load(r)
 except HTTPError as e:code=e.code;data=json.load(e)
 assert code==status,(path,code,data)
 return data
try:
 req('/api/create',{'name':'Host','topics':['דייטים'],'spice':2},400)
 h=req('/api/create',{'name':'Host','topics':['דייטים'],'spice':2,'adults_confirmed':True})
 g=req('/api/join',{'name':'Guest','code':h['code']});path='/api/'+h['code'];game=k.game(h['code'])
 assert req(path+'/start',{'host':h['host']},409)['error']=='photos_required'
 with k.cn() as c:c.execute("UPDATE players SET photo_data='fixture',photo_consent=1 WHERE game_id=?",(game['id'],))
 assert req(path+'/start',{'host':h['host']},409)['error']=='adults_confirmation_required'
 req(path+'/adultconfirm',{'token':'bad','confirmed':True},403)
 req(path+'/adultconfirm',{'token':h['token'],'confirmed':False},400)
 req(path+'/adultconfirm',{'token':h['token'],'confirmed':True})
 req(path+'/start',{'host':h['host']},409)
 req(path+'/adultconfirm',{'token':g['token'],'confirmed':True})
 st=req('/api/state/'+h['code']+'?token='+g['token']);assert st['adult_required'] and st['adults_ready'] and st['me']['adult_confirmed']
 req(path+'/start',{'host':h['host']})
 # Retry only deletes a failed job, with host/run/round authorization.
 game=k.game(h['code']);run=game['image_run'];k.prepare_hero_async=lambda *_:'idle'
 with k.cn() as c:c.execute("INSERT INTO image_jobs(game_id,image_run,round_no,status) VALUES(?,?,0,'failed')",(game['id'],run))
 req(path+'/hero',{'host':'bad','retry':True},403)
 req(path+'/hero',{'host':h['host'],'retry':True,'image_run':run-1},409)
 req(path+'/hero',{'host':h['host'],'retry':True,'image_run':run,'round':1},409)
 req(path+'/hero',{'host':h['host'],'retry':True,'image_run':run,'round':0})
 with k.cn() as c:
  assert not c.execute('SELECT * FROM image_jobs WHERE game_id=?',(game['id'],)).fetchone()
  c.execute("INSERT INTO image_jobs(game_id,image_run,round_no,status) VALUES(?,?,0,'running')",(game['id'],run))
 req(path+'/hero',{'host':h['host'],'retry':True,'image_run':run,'round':0})
 with k.cn() as c:assert c.execute('SELECT status FROM image_jobs WHERE game_id=?',(game['id'],)).fetchone()['status']=='running'
 print('PHOTO_READINESS_INDIVIDUAL_ADULT_CONSENT_AUTH_STALE_RETRY_ACTIVE_JOB_PRESERVED_OK')
finally:server.shutdown();server.server_close()
