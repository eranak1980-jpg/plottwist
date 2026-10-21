"""Launch budget contracts: no external requests or paid model calls."""
import os,sys,tempfile,json,base64,hmac,hashlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
tmp=tempfile.TemporaryDirectory();os.environ['DATABASE_PATH']=str(Path(tmp.name)/'launch.db');os.environ.pop('DATABASE_URL',None)
if os.getenv('PLOT_IMAGE_TEST_DATABASE_URL'):os.environ['DATABASE_URL']=os.environ['PLOT_IMAGE_TEST_DATABASE_URL']
os.environ.update(OPENAI_API_KEY='test-only-never-used',MIPO_COMMERCE_ENABLED='1',MIPO_CHECKOUT_MODE='static_link',PAYPLUS_SECRET_KEY='test-secret',PUBLIC_BASE_URL='https://example.test',MIPO_OWNER_HASH_SECRET='stable-test')
import kyc_server as k
import kyc_budget as b
import mipo_commerce as m
for product,key in m.STATIC_LINK_KEYS.items():os.environ[key]='https://payments.payplus.co.il/l/test-'+product
m._provider_post=lambda *args: (_ for _ in ()).throw(AssertionError('External API forbidden'))
k.init()
def reset():
 with k.cn() as c:
  for t in ['budget_calls','budget_active','budget_sessions','budget_allocations','budget_order_holds','commerce_transactions','commerce_entitlements','commerce_orders','trial_claims','games']:c.execute('DELETE FROM '+t)
  c.execute('UPDATE launch_budget SET sessions=0,reserved_micro=0 WHERE id=1')
def liability():
 with k.cn() as c:return int(c.execute('SELECT reserved_micro FROM launch_budget WHERE id=1').fetchone()['reserved_micro'])
def checkout(client,product='one_game'):
 with k.cn() as c:return m.create_checkout(c,product,client)
def pay(order,status='approved'):
 payload={'status':status,'transaction_uid':'tx-'+order['order_id'],'payment_request_uid':'req-'+order['order_id'],'more_info':order['order_id'],'amount':order['amount_cents']/100,'currency_code':'USD'}
 raw=json.dumps(payload).encode();headers={'User-Agent':'PayPlus','hash':base64.b64encode(hmac.new(b'test-secret',raw,hashlib.sha256).digest()).decode()}
 with k.cn() as c:return m.process_callback(c,raw,headers)
def insert_game(c,gid,access='paid',status='playing',ent=''):
 c.execute('INSERT INTO games(id,code,status,access_kind,entitlement_id,created) VALUES(?,?,?,?,?,?)',(gid,'T'+str(gid),status,access,ent,m.utcnow()))
def expect_limit(fn):
 try:fn()
 except b.BudgetLimit:pass
 else:raise AssertionError('Budget limit bypassed')
reset()
# A full duo checkout consumes its entire envelope before any external redirect;
# even at the ceiling the two paid games transfer it without re-reserving.
with patch.object(b,'CAP',2*b.SESSION_RESERVE):
 order=checkout('duo-device-0001','two_games');assert liability()==b.CAP
 assert checkout('duo-device-0001','two_games')['order_id']==order['order_id']
 expect_limit(lambda:checkout('blocked-device-0001'))
 assert pay(order,'declined')['status']=='failed';assert liability()==b.CAP
 assert pay(order)['status']=='paid';assert pay(order)['idempotent'];assert liability()==b.CAP
 for gid in [201,202]:
  with k.cn() as c:
   access=m.allocate_new_game(c,'duo-device-0001','paid',gid)
   insert_game(c,gid,ent=access['entitlement_id']);b.admit(c,gid)
  assert liability()==b.CAP
  k.init();assert liability()==b.CAP,'restart restored consumed order slots'
 with k.cn() as c:assert c.execute('SELECT slots_remaining FROM budget_order_holds WHERE order_id=?',(order['order_id'],)).fetchone()['slots_remaining']==0
# Finished games release unused reserves, retain unknown calls and final retry
# capacity; completion and callback repeats do not free incurred spend.
with b.scope(k.cn,201,'image:0'):
 b.finish(b.begin('image','unknown-model'),status='unknown_or_failed')
with k.cn() as c:
 c.execute("UPDATE games SET status='finished' WHERE id=201");b.complete(c,201)
assert liability()==b.SESSION_RESERVE+5*b.IMAGE_ALLOWANCE
for _ in range(4):
 with b.scope(k.cn,201,'image:99'):b.finish(b.begin('image','unknown-model'),status='unknown_or_failed')
with b.scope(k.cn,201,'image:99'):expect_limit(lambda:b.begin('image','unknown-model'))
assert liability()==b.SESSION_RESERVE+5*b.IMAGE_ALLOWANCE
k.init();assert liability()==b.SESSION_RESERVE+5*b.IMAGE_ALLOWANCE
with k.cn() as c:b.resume(c,201)
assert liability()==2*b.SESSION_RESERVE
# Existing in-flight costs are retained after completion, including a late result
# whose measured cost exceeds the provisional per-attempt allowance.
with b.scope(k.cn,202,'image:2'):ticket=b.begin('image','gpt-image-2.5-flare')
with k.cn() as c:c.execute("UPDATE games SET status='finished' WHERE id=202");b.complete(c,202)
b.finish(ticket,{'input_tokens_details':{'text_tokens':0,'image_tokens':0},'output_tokens':10000})
assert liability()==b.SESSION_RESERVE+300000+4*b.IMAGE_ALLOWANCE
# A trial uses its derived 8-round envelope, and retains its three-per-operation
# retry guard. Migrating the historical schema keeps unknown charge history.
reset()
with k.cn() as c:insert_game(c,301,'trial');b.admit(c,301)
assert liability()==b.TRIAL_RESERVE<b.SESSION_RESERVE
with k.cn() as c:
 c.execute('DELETE FROM budget_allocations');c.execute('UPDATE launch_budget SET reserved_micro=9300000 WHERE id=1')
k.init();assert liability()==b.TRIAL_RESERVE
# Race new trials against checkouts: the global row prevents oversubscription.
reset()
def race(i):
 try:
  if i%2:return bool(checkout('concurrent-device-'+str(i)))
  with k.cn() as c:insert_game(c,400+i,'trial');return bool(b.admit(c,400+i))
 except b.BudgetLimit:return False
with patch.object(b,'CAP',3*b.SESSION_RESERVE):
 with ThreadPoolExecutor(max_workers=8) as pool:out=list(pool.map(race,range(16)))
 assert any(out) and not all(out) and liability()<=b.CAP
 with k.cn() as c:before=c.execute('SELECT COUNT(*) AS n FROM commerce_orders').fetchone()['n']
 with patch.object(b,'CAP',liability()):expect_limit(lambda:checkout('must-not-create-order'))
 with k.cn() as c:assert c.execute('SELECT COUNT(*) AS n FROM commerce_orders').fetchone()['n']==before
print('LAUNCH_BUDGET_PASSED: migration, trial envelope, checkout-before-redirect, replay-safe duo transfer, failed/late/duplicate callback holds, completion, final retries, unknown/late costs, concurrent cap; real charges=0')
# Real HTTP entry points with AI enabled, fully stubbed generation: a signed
# callback must lead to paid/18 questions, not silently fall back to trial/8.
import threading
from urllib.request import Request,urlopen
from urllib.error import HTTPError
reset();k.prepare_pack_async=lambda *args:None;k.schedule_image_after_action=lambda *args:None
srv=k.ThreadingHTTPServer(('127.0.0.1',0),k.H);threading.Thread(target=srv.serve_forever,daemon=True).start()
def request(path,body):
 try:
  with urlopen(Request('http://127.0.0.1:'+str(srv.server_port)+path,data=json.dumps(body).encode(),headers={'Content-Type':'application/json'})) as r:return r.status,json.load(r)
 except HTTPError as e:return e.code,json.load(e)
try:
 with patch.object(b,'CAP',b.SESSION_RESERVE):
  status,order=request('/api/checkout',{'client_id':'http-paid-launch-device','product':'one_game'});assert status==201
  assert request('/api/checkout',{'client_id':'http-paid-launch-device','product':'one_game'})[1]['order_id']==order['order_id']
  assert request('/api/checkout',{'client_id':'http-no-capacity-device','product':'one_game'})==(429,{'error':'pilot_limit'})
  pay(order)
  status,room=request('/api/create',{'name':'Paid Host','client_id':'http-paid-launch-device','rounds':30});assert status==200,(status,room)
  g=k.game(room['code']);assert g['access_kind']=='paid' and g['max_rounds']==18 and g['rounds']==18
  assert request('/api/create',{'name':'No Capacity','client_id':'http-no-capacity-device'})==(429,{'error':'pilot_limit'})
  with k.cn() as c:assert not c.execute('SELECT 1 FROM trial_claims WHERE owner_key=?',(m.owner_key('http-no-capacity-device'),)).fetchone()
finally:srv.shutdown()
print('LAUNCH_BUDGET_HTTP_PASSED: fail before redirect, checkout refresh idempotent, signed payment -> paid 18Q at capacity, blocked trial rollback; real charges=0')
