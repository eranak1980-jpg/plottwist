import base64
import hashlib
import hmac
import json
import os
import sqlite3
import tempfile
import threading
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import mipo_commerce as commerce


os.environ['PAYPLUS_SECRET_KEY'] = 'test-secret'
os.environ['MIPO_OWNER_HASH_SECRET'] = 'owner-secret'

c = sqlite3.connect(':memory:')
c.row_factory = sqlite3.Row
c.execute("CREATE TABLE games(id INTEGER PRIMARY KEY,status TEXT,access_kind TEXT,max_rounds INTEGER,rounds INTEGER)")
commerce.init(c)

assert commerce.quote(18, 1)['total_cents'] == 799
assert commerce.quote(30, 1)['total_cents'] == 1098
assert commerce.quote(30, 2)['total_cents'] == 1598
assert commerce.quote(19, 1)['extra_cents'] == 299

trial = commerce.allocate_new_game(c, 'device-identity-0001', '', 1)
assert trial['access_kind'] == 'trial' and trial['max_rounds'] == 8
try:
    commerce.allocate_new_game(c, 'device-identity-0001', 'trial', 2)
    raise AssertionError('duplicate trial was accepted')
except commerce.CommerceError as exc:
    assert exc.code == 'trial_already_used'

qa_token = 'test-owner-qa-token'
os.environ['MIPO_QA_TOKEN_HASH'] = hashlib.sha256(qa_token.encode()).hexdigest()
qa = commerce.allocate_new_game(c, 'qa-device-identity', 'qa', 20, qa_token)
assert qa['access_kind'] == 'qa' and qa['max_rounds'] == 8
assert commerce.allocate_new_game(c, 'qa-device-identity', 'qa', 21, qa_token)['access_kind'] == 'qa'
try:
    commerce.allocate_new_game(c, 'qa-device-identity', 'qa', 22, 'wrong-token')
    raise AssertionError('invalid owner QA token was accepted')
except commerce.CommerceError as exc:
    assert exc.code == 'invalid_qa_access' and exc.status == 403

key = commerce.owner_key('paid-device-identity')
c.execute("INSERT INTO commerce_entitlements(id,order_id,owner_key,games_total,games_remaining,created) VALUES('ent','paid-order',?,2,2,'2026-01-01')", (key,))
assert commerce.allocate_new_game(c, 'paid-device-identity', '', 3)['access_kind'] == 'paid'
assert commerce.allocate_replay(c, key) == 'ent'
try:
    commerce.allocate_replay(c, key)
    raise AssertionError('third game was accepted')
except commerce.CommerceError as exc:
    assert exc.code == 'payment_required'

c.execute("INSERT INTO games(id,status,access_kind,max_rounds,rounds) VALUES(10,'lobby','paid',18,18)")
owner = commerce.owner_key('extension-device')
c.execute("INSERT INTO commerce_orders(id,owner_key,product,amount_cents,currency,status,provider_request_uid,target_game_id,created,updated) VALUES('ext-order',?,'extension',299,'USD','pending','request-1',10,'x','x')", (owner,))
payload = {'status': 'approved', 'transaction_uid': 'tx-1', 'payment_request_uid': 'request-1', 'more_info': 'ext-order', 'amount': 2.99, 'currency_code': 'USD'}
raw = json.dumps(payload, separators=(',', ':')).encode()
signature = base64.b64encode(hmac.new(b'test-secret', raw, hashlib.sha256).digest()).decode()
result = commerce.process_callback(c, raw, {'User-Agent': 'PayPlus', 'hash': signature})
assert result['status'] == 'paid'
game = c.execute('SELECT * FROM games WHERE id=10').fetchone()
assert game['max_rounds'] == 30 and game['rounds'] == 30
try:
    commerce.process_callback(c, raw, {'User-Agent': 'attacker', 'hash': signature})
    raise AssertionError('forged callback was accepted')
except commerce.CommerceError as exc:
    assert exc.code == 'invalid_callback_signature'

os.environ.update({'MIPO_COMMERCE_ENABLED':'1','PAYPLUS_API_KEY':'api','PAYPLUS_PAYMENT_PAGE_UID':'page','PUBLIC_BASE_URL':'https://example.test'})
captured = {}
original_post = commerce._provider_post
def fake_post(path, payload):
    captured.update({'path': path, 'payload': payload})
    return {'data': {'page_request_uid': 'checkout-request', 'payment_page_link': 'https://pay.example/checkout'}}
commerce._provider_post = fake_post
checkout = commerce.create_checkout(c, 'one_game', 'checkout-device-001')
assert checkout['amount_cents'] == 799 and checkout['currency'] == 'USD'
assert captured['path'].endswith('/PaymentPages/generateLink')
assert captured['payload']['amount'] == 7.99 and captured['payload']['currency_code'] == 'USD'
assert captured['payload']['sendEmailApproval'] is True
commerce._provider_post = original_post

print('Commerce pricing, trial, entitlement and signed callback checks passed')

# Server-side launch enforcement: a first room is exactly eight questions,
# refresh/access lookup preserves it, a new room cannot repeat it, and paid
# credits cannot exceed their purchased count or question limit.
tmp = tempfile.TemporaryDirectory()
os.environ['DATABASE_PATH'] = str(Path(tmp.name) / 'commerce-http.db')
os.environ['MIPO_COMMERCE_ENABLED'] = '1'
os.environ.pop('DATABASE_URL', None)
os.environ.pop('OPENAI_API_KEY', None)
import kyc_server as k
k.DB = Path(os.environ['DATABASE_PATH']);k.USE_PG = False;k.init()
server = k.ThreadingHTTPServer(('127.0.0.1', 0), k.H)
threading.Thread(target=server.serve_forever, daemon=True).start()
base = 'http://127.0.0.1:' + str(server.server_port)
def request(path, body=None):
    req = Request(base + path, data=json.dumps(body).encode() if body is not None else None,
                  headers={'Content-Type': 'application/json'})
    try:
        with urlopen(req, timeout=5) as response:
            return response.status, json.load(response)
    except HTTPError as exc:
        return exc.code, json.load(exc)

try:
    status, first = request('/api/create', {'name': 'Trial Host', 'client_id': 'http-device-0001', 'rounds': 30})
    assert status == 200
    state = request('/api/state/' + first['code'] + '?token=' + first['token'] + '&host=' + first['host'])[1]
    assert state['access_kind'] == 'trial' and state['total'] == 8 and state['max_rounds'] == 8
    assert request('/api/access?client_id=http-device-0001')[1]['trial_available'] is False
    assert request('/api/create', {'name': 'Again', 'client_id': 'http-device-0001'})[0] == 409
    paid_key = commerce.owner_key('http-paid-device')
    with k.cn() as db:
        db.execute("INSERT INTO commerce_entitlements(id,order_id,owner_key,games_total,games_remaining,created) VALUES('http-ent','http-order',?,1,1,'2026-01-01')", (paid_key,))
    status, paid = request('/api/create', {'name': 'Paid Host', 'client_id': 'http-paid-device', 'rounds': 30})
    assert status == 200
    paid_state = request('/api/state/' + paid['code'] + '?token=' + paid['token'] + '&host=' + paid['host'])[1]
    assert paid_state['access_kind'] == 'paid' and paid_state['total'] == 18 and paid_state['max_rounds'] == 18
    assert request('/api/create', {'name': 'Trial After Credit', 'client_id': 'http-paid-device'})[0] == 200
    assert request('/api/create', {'name': 'No Credit 2', 'client_id': 'http-paid-device'})[0] == 409
finally:
    server.shutdown()
print('Commerce HTTP trial and paid entitlement enforcement passed')
