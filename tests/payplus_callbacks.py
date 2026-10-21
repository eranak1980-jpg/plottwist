"""Provider-shaped callbacks: no external requests or charges.

Schema source: PayPlus-Gateway/payplus-payment-gateway,
includes/wc_payplus_gateway.php, set_arrangement_callback.
"""
import os, sys, json, sqlite3, base64, hashlib, hmac
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import mipo_commerce as m
os.environ.update(PAYPLUS_SECRET_KEY='test-secret',MIPO_OWNER_HASH_SECRET='test-owner')
c=sqlite3.connect(':memory:');c.row_factory=sqlite3.Row
c.execute('CREATE TABLE games(id INTEGER PRIMARY KEY,status TEXT,access_kind TEXT,max_rounds INTEGER,rounds INTEGER)');m.init(c)
def order(oid, product='one_game', request=None):
 c.execute("INSERT INTO commerce_orders(id,owner_key,product,amount_cents,currency,status,provider_request_uid,created,updated) VALUES(?,?,?,?,?,'pending',?,'x','x')",(oid,m.owner_key('callback-device-'+oid),product,m.price(product)['amount_cents'],'USD',request))
def payload(oid,uid,amount=5.99,kind='Charge',**changes):
 return {'transaction_type':kind,'transaction':{'uid':uid,'payment_page_request_uid':'req-'+oid,'status_code':'000','approval_number':'123456','amount':amount,'currency':'USD','more_info':oid,**changes},'data':{'card_information':{'uid':'card-not-transaction'},'secure3D':{'status':'failed'}}}
def send(p):
 raw=json.dumps(p,separators=(',',':')).encode()
 return m.process_callback(c,raw,{'User-Agent':'PayPlus','hash':base64.b64encode(hmac.new(b'test-secret',raw,hashlib.sha256).digest()).decode()})
def reject(p,code):
 try:send(p)
 except m.CommerceError as e:assert e.code==code,(e.code,code)
 else:raise AssertionError('accepted '+code)
order('single',request='req-single');p=payload('single','real-shape-single')
assert send(p)['status']=='paid'
assert send(p)['idempotent']
assert m.available(c,'callback-device-single')['paid_games']==1
assert c.execute("SELECT provider_transaction_uid FROM commerce_orders WHERE id='single'").fetchone()[0]=='real-shape-single'
order('duo','two_games',request='req-duo')
assert send(payload('duo','real-shape-duo',9.99))['status']=='paid'
assert m.available(c,'callback-device-duo')['paid_games']==2
order('bad')
for kind in ('Refund','Approval','Check','Token'):
 reject(payload('bad','bad-'+kind,kind=kind),'callback_not_a_charge')
reject(payload('bad','bad-currency',currency='ILS'),'callback_order_mismatch')
reject(payload('bad','bad-price',amount=7.99),'callback_order_mismatch')
reject(payload('bad','fraction',amount=5.994),'callback_amount_missing')
reject(payload('bad',None),'callback_transaction_missing')
reject(payload('bad','real-shape-single'),'callback_transaction_reused')
assert m.available(c,'callback-device-bad')['paid_games']==0
assert send(payload('bad','declined',status_code='004'))['status']=='failed'
assert m.available(c,'callback-device-bad')['paid_games']==0
# A later approval remains valid after a declined attempt.
assert send(payload('bad','late-approved'))['status']=='paid'
order('mismatch',request='expected-request')
reject(payload('mismatch','mismatch'),'callback_order_mismatch')
order('by-request',request='req-by-request')
assert send(payload('', 'by-request-tx',more_info='',payment_page_request_uid='req-by-request'))['status']=='paid'
reject([], 'invalid_callback_payload')
print('PAYPLUS_CALLBACKS_PASSED: official nested transaction schema, single/duo, request binding, declines/late approval, no refund or authorization grants, replay protection, exact USD amount; charges=0')
