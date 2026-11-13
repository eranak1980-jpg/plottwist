"""Gender-independent question identities and verified purchases in existing rooms."""
import json,os,secrets,sys,tempfile,threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.request import Request,urlopen
from urllib.error import HTTPError
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
tmp=tempfile.TemporaryDirectory();os.environ.update(DATABASE_PATH=str(Path(tmp.name)/'repeat-purchase.db'),MIPO_COMMERCE_ENABLED='1',MIPO_OWNER_HASH_SECRET='test-reuse-owner')
os.environ.pop('DATABASE_URL',None);os.environ.pop('OPENAI_API_KEY',None)
if os.getenv('PLOT_IMAGE_TEST_DATABASE_URL'):os.environ['DATABASE_URL']=os.environ['PLOT_IMAGE_TEST_DATABASE_URL']
import kyc_server as k
from mipo_gender import gender_card
k.init();k.prepare_pack_async=lambda *_:None;k.schedule_image_after_action=lambda *_:None
server=k.ThreadingHTTPServer(('127.0.0.1',0),k.H);threading.Thread(target=server.serve_forever,daemon=True).start()
def req(p,body=None,status=200):
 try:
  with urlopen(Request(f'http://127.0.0.1:{server.server_port}'+p,data=json.dumps(body).encode() if body is not None else None,headers={'Content-Type':'application/json'}),timeout=20) as r:code=r.status;d=json.load(r)
 except HTTPError as e:code=e.code;d=json.load(e)
 assert code==status,(p,code,d)
 return d

def room():
 client=secrets.token_hex(12);h=req('/api/create',{'client_id':client,'name':'Host','language':'he','gender':'male','ai_images_enabled':False})
 guest=req('/api/join',{'code':h['code'],'name':'Guest','gender':'female','client_id':secrets.token_hex(12)})
 return h,guest,client

def state(h):return req('/api/state/'+h['code']+'?token='+h['token']+'&host='+h['host'])
def act(h,a,**d):return req('/api/'+h['code']+'/'+a,{'host':h['host'],**d})
def order(client,paid=False,games=1):
 ident=secrets.token_hex(12);owner=k.commerce.owner_key(client)
 with k.cn() as c:
  c.execute('INSERT INTO commerce_orders(id,owner_key,product,amount_cents,currency,status,created,updated) VALUES(?,?,?,?,?,?,?,?)',(ident,owner,'one_game' if games==1 else 'two_games',599 if games==1 else 999,'USD','paid' if paid else 'pending',k.now(),k.now()))
  if paid:c.execute('INSERT INTO commerce_entitlements(id,order_id,owner_key,games_total,games_remaining,created) VALUES(?,?,?,?,?,?)',(ident,ident,owner,games,games,k.now()))
 return ident

def credit(ident):
 with k.cn() as c:return c.execute('SELECT games_remaining FROM commerce_entitlements WHERE id=?',(ident,)).fetchone()['games_remaining']
try:
 # All curated subject variants retain one identity, even across legacy history.
 person={'id':1,'name':'שגית','gender':'male'}
 for typ,template,options in k.PERSONAL_HE:
  original=k.question_key(template.format(s=person['name']),[person])
  for gender in ('male','female','unspecified'):
   person['gender']=gender;text,_=gender_card(template.format(s=person['name']),options,typ,person,[person])
   assert k.question_key(text,[person])==original,(template,text)
 print('ALL_REVIEWED_CARDS_MALE_FEMALE_UNSPECIFIED_STABLE_IDENTITY_OK')
 # A paid 18-round run across two spotlight players must not reuse a card.
 h,g,client=room();oid=order(client,True,2);before=state(h)
 with ThreadPoolExecutor(max_workers=5) as pool:
  results=list(pool.map(lambda _:act(h,'applypurchase',order_id=oid,client_id=client),range(5)))
 assert credit(oid)==1 and all(r['code']==h['code'] for r in results)
 st=state(h);assert st['access_kind']=='paid' and st['total']==18
 assert [(p['id'],p['gender']) for p in st['players']]==[(p['id'],p['gender']) for p in before['players']]
 act(h,'start');tokens={'Host':h['token'],'Guest':g['token']};seen=set()
 for rn in range(18):
  st=state(h);identity=k.question_key(st['question'],[dict(p) for p in st['players']]);assert identity not in seen,(rn,st['question']);seen.add(identity)
  with k.cn() as c:card=json.loads(c.execute('SELECT round_card FROM games WHERE code=?',(h['code'],)).fetchone()['round_card'])
  assert card['identity']==identity
  subject=st['subject']['name'];choice=st['options'][0]
  act(h,'answer',token=tokens[subject],answer=choice)
  act(h,'guess',token=tokens[next(n for n in tokens if n!=subject)],guess=choice)
  act(h,'next')
 assert state(h)['status']=='finished'
 print('PAID_18_ROUNDS_TWO_SUBJECTS_NO_REPEATED_CARD_SAME_ROOM_SINGLE_CREDIT_OK')
 # A second order restarts a finished room in place; players and tokens remain.
 oid2=order(client,True);act(h,'applypurchase',order_id=oid2,client_id=client)
 st=state(h);assert st['status']=='lobby' and st['round']==0 and st['code']==h['code'] and len(st['players'])==2
 act(h,'applypurchase',order_id=oid2,client_id=client);assert credit(oid2)==0
 # Pending orders and someone else's owner identity cannot upgrade a room.
 h2,g2,c2=room();pending=order(c2)
 req('/api/'+h2['code']+'/applypurchase',{'host':h2['host'],'client_id':c2,'order_id':pending},409)
 req('/api/'+h2['code']+'/applypurchase',{'host':'bad','client_id':c2,'order_id':pending},403)
 req('/api/'+h2['code']+'/applypurchase',{'host':h2['host'],'client_id':client,'order_id':oid},403)
 assert state(h2)['access_kind']=='trial'
 # Mid-trial upgrade preserves the current question, answer, guests and progress.
 act(h2,'start');st=state(h2);act(h2,'answer',token=h2['token'],answer=st['options'][0])
 oid3=order(c2,True);act(h2,'applypurchase',order_id=oid3,client_id=c2);after=state(h2)
 assert after['status']=='playing' and after['round']==st['round'] and after['question']==st['question'] and after['answered'] and after['total']==18
 print('FINISHED_ROOM_RESTART_MID_TRIAL_UPGRADE_AUTH_VERIFIED_ONLY_IDEMPOTENT_OK')
 # Transfer the checkout's reserved AI envelope, keeping old run charges intact.
 os.environ['OPENAI_API_KEY']='test-no-external-calls'
 h3,g3,c3=room();paid=order(c3,True)
 with k.cn() as c:
  c.execute('INSERT INTO budget_order_holds(order_id,slots_remaining,created) VALUES(?,?,?)',(paid,1,k.now()))
  k.budget._refresh(c)
 act(h3,'applypurchase',order_id=paid,client_id=c3)
 act(h3,'applypurchase',order_id=paid,client_id=c3)
 with k.cn() as c:
  assert c.execute('SELECT slots_remaining FROM budget_order_holds WHERE order_id=?',(paid,)).fetchone()['slots_remaining']==0
  game=k.game(h3['code'])
  allocation=c.execute('SELECT a.* FROM budget_active b JOIN budget_allocations a ON a.session_id=b.session_id WHERE b.game_id=?',(game['id'],)).fetchone()
  assert allocation['kind']=='paid' and allocation['image_limit']==k.budget.IMAGE_LIMIT
 assert credit(paid)==0
 print('PREPAID_AI_ENVELOPE_TRANSFER_NO_DOUBLE_CREDIT_OR_RESERVATION_OK')
 # A returning host can save a lobby before paying and unlock that exact lobby.
 os.environ.pop('OPENAI_API_KEY',None)
 _,_,returning=room()
 setup={'client_id':returning,'name':'Returning Host','language':'he','gender':'female',
        'topics':['משפחה'],'context':'משפחה','prize':'Pizza','rounds':13,'ai_images_enabled':True}
 req('/api/create',setup,409)
 pending=req('/api/create',dict(setup,save_for_checkout=True))
 assert pending['payment_required']
 req('/api/join',{'code':pending['code'],'name':'Guest','client_id':secrets.token_hex(12)})
 req('/api/'+pending['code']+'/start',{'host':pending['host']},402)
 paid=order(returning,True)
 with k.cn() as c:
  target=k.game(pending['code'])
  c.execute('UPDATE commerce_orders SET target_game_id=? WHERE id=?',(target['id'],paid))
 assert req('/api/order/'+paid+'?client_id='+returning)['room_code']==pending['code']
 act(pending,'applypurchase',order_id=paid,client_id=returning)
 act(pending,'applypurchase',order_id=paid,client_id=returning)
 restored=state(pending)
 assert restored['access_kind']=='paid' and restored['total']==13 and restored['prize']=='Pizza'
 assert restored['language']=='he' and restored['ai_images_enabled'] and len(restored['players'])==2
 assert restored['me']['gender']=='female' and credit(paid)==0
 act(pending,'start')
 print('UNPAID_LOBBY_LOCKS_START_AND_PRESERVES_SETUP_AFTER_VERIFIED_PAYMENT_OK')
finally:server.shutdown();server.server_close();tmp.cleanup()
