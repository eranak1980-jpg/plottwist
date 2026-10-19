"""Reusable PayPlus links: no provider API calls and no real charges."""
import os, sys, json, sqlite3, base64, hashlib, hmac
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import mipo_commerce as m
os.environ.update(MIPO_COMMERCE_ENABLED='1', MIPO_CHECKOUT_MODE='static_link', PAYPLUS_SECRET_KEY='test-secret', PUBLIC_BASE_URL='https://example.test', MIPO_OWNER_HASH_SECRET='stable-owner-test')
for key in ('PAYPLUS_API_KEY','PAYPLUS_PAYMENT_PAGE_UID'):os.environ.pop(key,None)
for product,key in m.STATIC_LINK_KEYS.items():os.environ[key]='https://payments.payplus.co.il/l/test-'+product
m._provider_post=lambda *args: (_ for _ in ()).throw(AssertionError('API call forbidden'))
db=sqlite3.connect(':memory:');db.row_factory=sqlite3.Row
db.execute('CREATE TABLE games(id INTEGER PRIMARY KEY,status TEXT,access_kind TEXT,max_rounds INTEGER,rounds INTEGER)')
m.init(db)
assert m.checkout_configured()
def callback(order, cents, transaction, **changes):
 payload={'status':'approved','transaction_uid':transaction,'payment_request_uid':'req-'+order['order_id'],'more_info':order['order_id'],'amount':cents/100,'currency_code':'USD',**changes}
 raw=json.dumps(payload,separators=(',',':')).encode()
 headers={'User-Agent':'PayPlus','hash':base64.b64encode(hmac.new(b'test-secret',raw,hashlib.sha256).digest()).decode()}
 return m.process_callback(db,raw,headers)
def reject(call, code):
 try:call()
 except m.CommerceError as e:assert e.code==code,(e.code,code)
 else:raise AssertionError(code+' accepted')
single=m.create_checkout(db,'one_game','single-browser-identity')
assert single['amount_cents']==599
assert parse_qs(urlsplit(single['checkout_url']).query)=={'more_info':[single['order_id']],'more_info_1':['one_game']}
assert m.available(db,'single-browser-identity')['paid_games']==0
reject(lambda:callback(single,799,'tx-wrong-price'),'callback_order_mismatch')
reject(lambda:callback(single,599,'tx-wrong-currency',currency_code='ILS'),'callback_order_mismatch')
reject(lambda:m.process_callback(db,b'{}',{}),'invalid_callback_signature')
reject(lambda:callback(single,599,'tx-unknown',more_info='unknown-order'),'order_not_found')
assert callback(single,599,'tx-single')['status']=='paid'
assert callback(single,599,'tx-single')['idempotent']
assert m.available(db,'single-browser-identity')['paid_games']==1
reject(lambda:m.order_status(db,single['order_id'],'another-browser-id'),'order_not_found')
second=m.create_checkout(db,'one_game','another-browser-id')
reject(lambda:callback(second,599,'tx-single'),'callback_transaction_reused')
assert m.available(db,'another-browser-id')['paid_games']==0
duo=m.create_checkout(db,'two_games','duo-browser-identity')
assert callback(duo,999,'tx-duo')['status']=='paid'
assert m.available(db,'duo-browser-identity')['paid_games']==2
db.execute("INSERT INTO games VALUES(9,'lobby','paid',18,18)")
game=db.execute('SELECT * FROM games WHERE id=9').fetchone()
extension=m.create_checkout(db,'extension','duo-browser-identity',game)
assert callback(extension,299,'tx-extension')['status']=='paid'
assert db.execute('SELECT max_rounds FROM games WHERE id=9').fetchone()[0]==30
os.environ['PAYPLUS_ONE_GAME_LINK']='https://evil.example/l/test'
assert not m.checkout_configured()
print('STATIC_LINKS_PASSED: USD 599/999/299, unique order correlation, signature/price/currency checks, replay protection, owner isolation, extension; provider API calls=0, charges=0')

# HTTP return navigation cannot unlock access; only signed server callbacks can.
import tempfile, threading
from urllib.request import Request, urlopen, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError
os.environ['PAYPLUS_ONE_GAME_LINK']='https://payments.payplus.co.il/l/test-one_game'
os.environ.pop('DATABASE_URL',None);os.environ.pop('OPENAI_API_KEY',None)
tmp=tempfile.TemporaryDirectory();os.environ['DATABASE_PATH']=str(Path(tmp.name)/'http.db')
import kyc_server as k
k.DB=Path(os.environ['DATABASE_PATH']);k.USE_PG=False;k.init()
srv=k.ThreadingHTTPServer(('127.0.0.1',0),k.H)
threading.Thread(target=srv.serve_forever,daemon=True).start()
base='http://127.0.0.1:'+str(srv.server_port)
def req(path,body=None,headers=None):
 data=body if isinstance(body,bytes) else json.dumps(body).encode() if body is not None else None
 with urlopen(Request(base+path,data=data,headers={'Content-Type':'application/json',**(headers or {})}),timeout=5) as r:return json.load(r)
try:
 device='http-static-browser-identity'
 order=req('/api/checkout',{'client_id':device,'product':'one_game'})
 assert order['amount_cents']==599
 assert req('/api/order/'+order['order_id']+'?client_id='+device)['status']=='pending'
 class NoRedirect(HTTPRedirectHandler):
  def redirect_request(self,*args):return None
 body=('more_info='+order['order_id']+'&status=success').encode()
 try:build_opener(NoRedirect).open(Request(base+'/checkout/success',data=body,headers={'Content-Type':'application/x-www-form-urlencoded'}))
 except HTTPError as e:
  assert e.code==303 and e.headers['Location']=='/checkout/success?order='+order['order_id']
 else:raise AssertionError('return did not redirect')
 assert req('/api/access?client_id='+device)['paid_games']==0
 raw=json.dumps({'status':'approved','transaction_uid':'tx-http','payment_request_uid':'req-http','more_info':order['order_id'],'amount':5.99,'currency_code':'USD'},separators=(',',':')).encode()
 sig=base64.b64encode(hmac.new(b'test-secret',raw,hashlib.sha256).digest()).decode()
 for _ in range(2):assert req('/api/payplus/callback',raw,{'User-Agent':'PayPlus','hash':sig})['status']=='paid'
 assert req('/api/access?client_id='+device)['paid_games']==1
 print('STATIC_HTTP_PASSED: checkout -> return remains locked -> signed callback -> one credit; no external calls')
finally:srv.shutdown();tmp.cleanup()
