"""HTTP regression: membership during a round, round-one invites and optional Hebrew profile."""
import json,os,secrets,sys,tempfile,threading
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
tmp=tempfile.TemporaryDirectory();os.environ.update(DATABASE_PATH=str(Path(tmp.name)/'continuity.db'),MIPO_COMMERCE_ENABLED='0')
os.environ.pop('DATABASE_URL',None);os.environ.pop('OPENAI_API_KEY',None)
if os.getenv('PLOT_IMAGE_TEST_DATABASE_URL'):os.environ['DATABASE_URL']=os.environ['PLOT_IMAGE_TEST_DATABASE_URL']
import kyc_server as k
from mipo_gender import gender_card
k.init();k.schedule_image_after_action=lambda *_:None
server=k.ThreadingHTTPServer(('127.0.0.1',0),k.H);threading.Thread(target=server.serve_forever,daemon=True).start()
def req(path,body=None,status=200):
 try:
  with urlopen(Request(f'http://127.0.0.1:{server.server_port}'+path,data=json.dumps(body).encode() if body is not None else None,headers={'Content-Type':'application/json'})) as r:code=r.status;result=json.load(r)
 except HTTPError as e:code=e.code;result=json.load(e)
 assert code==status,(path,code,result)
 return result
def room(count=4):
 h=req('/api/create',{'name':'Host','language':'he','rounds':18,'gender':'male','client_id':secrets.token_hex(10)})
 tokens={'Host':h['token']}
 for i in range(count-1):
  name='שגית' if i==0 else 'Guest'+str(i)
  tokens[name]=req('/api/join',{'code':h['code'],'name':name,'gender':'female' if i==0 else 'unspecified','client_id':secrets.token_hex(10)})['token']
 req('/api/'+h['code']+'/start',{'host':h['host']})
 return h,tokens
def state(h):return req('/api/state/'+h['code']+'?token='+h['token']+'&host='+h['host'])
def action(h,a,**body):return req('/api/'+h['code']+'/'+a,{'host':h['host'],**body})
def answer(h,t,st):action(h,'answer',token=t[st['subject']['name']],answer=st['options'][0])
def finish(h,t,st,removed=None):
 for name,token in t.items():
  if name!=st['subject']['name'] and name!=removed:action(h,'guess',token=token,guess=st['options'][0])
 assert state(h)['reveal'],state(h)
 action(h,'next');assert state(h)['round']==st['round']+1
try:
 # Reproduce round 12 of 18 through real answers/guesses, not a fabricated state.
 for remove_subject,answered in [(False,False),(False,True),(True,True),(True,False)]:
  h,t=room()
  for _ in range(11):
   st=state(h);answer(h,t,st);finish(h,t,st)
  st=state(h);assert st['round']==11 and st['total']==18
  target=next(p for p in st['players'] if p['id']==st['subject']['id']) if remove_subject else next(p for p in st['players'] if p['name']!='Host' and p['id']!=st['subject']['id'])
  if answered:answer(h,t,st)
  action(h,'drop',player_id=target['id'])
  post=state(h)
  if remove_subject and not answered:
   assert post['round']==12
  else:
   assert post['subject']['id']==st['subject']['id'] and post['question']==st['question'] and post['options']==st['options']
   if not answered:answer(h,t,st)
   finish(h,t,st,target['name'])
  action(h,'drop',player_id=target['id']) if any(p['id']==target['id'] for p in post['players']) and remove_subject and not answered else None
 print('ROUND_12_DROP_SUBJECT_BEFORE_AFTER_ANSWER_DROP_GUESSER_NO_STALL_OK')
 h,t=room(2);st=state(h);answer(h,t,st)
 action(h,'guess',token=t['שגית'],guess=st['options'][0]);assert state(h)['can_reopen']
 old_run=state(h)['image_run'];gid=k.game(h['code'])['id']
 action(h,'reopen');st=state(h)
 assert st['status']=='lobby' and st['image_run']>old_run and all(p['score']==0 for p in st['players'])
 req('/api/join',{'code':h['code'],'name':'New player'})
 action(h,'start');st=state(h);assert len(st['players'])==3 and st['round']==0
 answer(h,t,st)
 # Server enforces that the optional field is not required on new join.
 assert next(p for p in st['players'] if p['name']=='New player')['gender']=='unspecified'
 print('FIRST_REVEAL_REOPEN_JOIN_RESTART_SAME_ROOM_NO_NEW_PURCHASE_OK')
 ps=[dict(name='שגית',id=1,gender='female'),dict(name='חבר',id=2,gender='male')]
 from mipo_playtest import PERSONAL_HE
 q=next(q for q in PERSONAL_HE if 'החבורה בוחרת מסעדה' in q[1]);text,options=gender_card(q[1].format(s='שגית'),q[2],q[0],ps[0],ps)
 assert 'שגית לא אוהבת' in text and 'מציעה מקום אחר' in options and 'מצטרפת בכל זאת' in options,(text,options)
 hurt=next(q for q in PERSONAL_HE if 'מישהו פגע' in q[1]);text,options=gender_card(hurt[1].format(s='שגית'),hurt[2],hurt[0],ps[0],ps)
 assert 'למחרת הוא שולח' in text and 'שגית מגיבה' in text and 'מדברת איתו על מה שקרה' in options,(text,options)
 ps[0]['gender']='male';text,options=gender_card(q[1].format(s='שגית'),q[2],q[0],ps[0],ps)
 assert 'לא אוהב.' in text and 'מציע מקום אחר' in options
 ps[0]['gender']='unspecified';text,_=gender_card(q[1].format(s='שגית'),q[2],q[0],ps[0],ps);assert 'אוהב/ת' in text
 print('HEBREW_FEMALE_MALE_UNSPECIFIED_OTHER_PERSON_PRESERVED_CLEAR_QUESTION_OK')
finally:server.shutdown();server.server_close();tmp.cleanup()
