"""Offline playtest regression: real HTTP, crew history, images, age gate, recap."""
import json, os, re, sys, tempfile, threading
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
tmp=tempfile.TemporaryDirectory()
os.environ['DATABASE_PATH']=str(Path(tmp.name)/'playtest.db')
os.environ.pop('DATABASE_URL',None);os.environ.pop('OPENAI_API_KEY',None)
import kyc_server as k
k.prepare_pack_async=lambda *a,**kw:None
k.init()
server=k.ThreadingHTTPServer(('127.0.0.1',0),k.H)
threading.Thread(target=server.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{server.server_port}'
def call(path,body=None,expected=200):
 r=Request(base+path,data=None if body is None else json.dumps(body).encode(),headers={'Content-Type':'application/json'})
 try:
  with urlopen(r,timeout=5) as response:status=response.status;payload=json.load(response)
 except HTTPError as e:status=e.code;payload=json.load(e)
 assert status==expected,(path,status,payload)
 return payload
try:
 assert not k.editorial_ok(('know','שלום م',['א','ב']),'he')
 assert not k.editorial_ok(('know','שאלה',['א','א']),'he')
 assert not k.editorial_ok(('know','שאלה',None),'he')
 assert k._clean_pack([('know','שאלה',['א','ב']),('know','שאלה م',['א','ב'])],'he')==[('know','שאלה',['א','ב'])]
 names=[{'name':'ערן'},{'name':'ערן המלך'}]
 assert k.question_key('ערן המלך בוחר',names)==k.question_key('ערן בוחר',names)
 assert k.question_key('מערן',names)=='מערן','do not replace a name inside another word'
 keys=[k.question_key(q[1].format(s='ערן'),names) for q in k.room_pack('he')]
 assert len(set(keys))==len(keys)
 assert not k.too_similar(keys[1],{keys[0]}),'distinct short traits must remain available'
 assert not any('דייט' in q[1] for q in k.room_pack('he','משפחה'))
 created=call('/api/create',{'name':'ערן','rounds':18,'language':'he','ai_images_enabled':False})
 code=created['code'];host=created['host'];tokens={'ערן':created['token']}
 for n in ['שחר','שגית','עידן']:
  tokens[n]=call('/api/join',{'code':code,'name':n})['token']
 def state():return call(f'/api/state/{code}?token={tokens["ערן"]}&host={host}')
 def post(action,body,expected=200):return call(f'/api/{code}/{action}',body,expected)
 assert state()['ai_images_enabled'] is False
 post('image-settings',{'host':'wrong','enabled':True},403)
 post('image-settings',{'host':host,'enabled':True});assert state()['ai_images_enabled'] is True
 post('image-settings',{'host':host,'enabled':False})
 seen=set();room_count=0
 for run in range(3):
  post('start',{'host':host})
  post('image-settings',{'host':host,'enabled':True},409)
  for rn in range(18):
   st=state();g=k.game(code);ps=k.players(g['id']);key=k.question_key(st['question'],ps)
   assert key not in seen,(run,rn,st['question']);seen.add(key)
   assert not re.search('[\u0600-\u06ff]',st['question']+' '.join(st['options']))
   assert len(st['options'])==len(set(st['options']))
   assert st['round_insights']==[], 'do not disclose recap during play'
   if st['type']=='room':
    room_count+=1;assert st['subject']['name'] not in st['options']
   else:assert 3<=len(st['options'])<=4
   answer=st['options'][0]
   post('answer',{'token':tokens[st['subject']['name']],'answer':answer})
   assert state()['question']==st['question'],'question stable while waiting for guesses'
   for n,t in tokens.items():
    if n!=st['subject']['name']:post('guess',{'token':t,'guess':st['options'][1]})
   assert state()['reveal']
   post('next',{'host':host})
  final=state();assert final['status']=='finished';assert len(final['round_insights'])==3
  assert all(r['correct']==0 and r['attempts']==3 for r in final['round_insights'])
  assert not final['hero_eligible'] and not final['final_image_eligible']
  assert k.image_payload(k.game(code),k.players(g['id'])) is None
  assert k.prepare_hero_async(g['id'],99)=='disabled'
  with k.cn() as c:assert c.execute('SELECT COUNT(*) AS n FROM image_jobs WHERE game_id=?',(g['id'],)).fetchone()['n']==0
  if run<2:
   fresh=post('freshroom',{'host':host});code=fresh['code'];assert state()['ai_images_enabled'] is False
 assert room_count>=12,room_count
 print('PLAYTEST_54_ROUNDS_3_SAME_CREW_GAMES_NO_REPEATS_CLOSED_CHOICES_FAST_IMAGES_AUTH_RECAP_OK')
finally:
 server.shutdown();server.server_close();tmp.cleanup()
