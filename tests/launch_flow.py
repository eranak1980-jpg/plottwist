"""Local HTTP launch flow. Fake payments; no external API calls or charges."""
import os, sys, tempfile, threading, json, base64, hashlib, hmac
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
tmp = tempfile.TemporaryDirectory()
os.environ.update(DATABASE_PATH=str(Path(tmp.name)/'launch.db'), MIPO_COMMERCE_ENABLED='1', PAYPLUS_API_KEY='test', PAYPLUS_SECRET_KEY='test-secret', PAYPLUS_PAYMENT_PAGE_UID='test-page', PUBLIC_BASE_URL='https://example.test', MIPO_OWNER_HASH_SECRET='test-owner')
os.environ.pop('DATABASE_URL', None)
os.environ.pop('OPENAI_API_KEY', None)
import kyc_server as k
import mipo_commerce as commerce
k.init()
def provider(path, payload):
    assert payload['currency_code']=='USD'
    assert payload['amount'] in (5.99,9.99,2.99)
    return {'data': {'page_request_uid':'req-'+payload['more_info'], 'payment_page_link':'https://example.test/checkout'}}
commerce._provider_post=provider
srv=k.ThreadingHTTPServer(('127.0.0.1',0),k.H)
threading.Thread(target=srv.serve_forever,daemon=True).start()
base='http://127.0.0.1:'+str(srv.server_port)
def req(path, body=None, expected=200, headers=None):
    data=body if isinstance(body,bytes) else json.dumps(body).encode() if body is not None else None
    r=Request(base+path,data=data,headers={'Content-Type':'application/json',**(headers or {})})
    try:
        with urlopen(r,timeout=10) as response: status,payload=response.status,json.load(response)
    except HTTPError as error: status,payload=error.code,json.load(error)
    assert status==expected,(path,status,payload)
    return payload
def purchase(device, product, amount, room=None):
    order=req('/api/checkout',{'product':product,'client_id':device,**(room or {})},201)
    assert order['amount_cents']==amount
    with k.cn() as db: row=db.execute('SELECT * FROM commerce_orders WHERE id=?',(order['order_id'],)).fetchone()
    raw=json.dumps({'status':'approved','transaction_uid':'tx-'+row['id'],'payment_request_uid':row['provider_request_uid'],'more_info':row['id'],'amount':amount/100,'currency_code':'USD'},separators=(',',':')).encode()
    sig=base64.b64encode(hmac.new(b'test-secret',raw,hashlib.sha256).digest()).decode()
    for _ in range(2): assert req('/api/payplus/callback',raw,headers={'User-Agent':'PayPlus','hash':sig})['status']=='paid'
def play(device, expected_rounds, count, extension=False):
    room=req('/api/create',{'name':'Host','client_id':device,'rounds':30})
    code=room['code']; tokens=[room['token']]
    for n in range(1,count):tokens.append(req('/api/join',{'code':code,'name':'Guest'+str(n),'client_id':device+'-guest'+str(n)})['token'])
    # Exercise the public flow with no photos, using real HTTP state and actions.
    if extension:purchase(device,'extension',299,{'code':code,'host':room['host']})
    def state(token=room['token']):return req('/api/state/'+code+'?token='+token+'&host='+room['host'])
    assert state()['total']==expected_rounds
    req('/api/'+code+'/start',{'host':room['host']})
    for rn in range(expected_rounds):
        s=state(); assert s['round']==rn and s['status']=='playing'
        ps=k.players(k.game(code)['id']); subject=next(p for p in ps if p['id']==s['subject']['id'])
        answer=s['options'][0]
        req('/api/'+code+'/answer',{'token':subject['token'],'answer':answer})
        for p in ps:
            if p['id']!=subject['id']:req('/api/'+code+'/guess',{'token':p['token'],'guess':answer})
        assert state()['reveal']
        req('/api/'+code+'/next',{'host':room['host']})
    final=state();assert final['status']=='finished'
    assert final['relationships'] and all(x['correct']==x['attempts'] for x in final['relationships']),final['relationships']
    print('FULL_FLOW_OK',expected_rounds,'rounds',count,'players')
try:
    play('trial-device-launch',8,4)
    req('/api/create',{'name':'Repeat','client_id':'trial-device-launch'},409)
    purchase('single-device-launch','one_game',599)
    play('single-device-launch',18,4)
    purchase('duo-device-launch','two_games',999)
    play('duo-device-launch',18,2)
    play('duo-device-launch',30,2,extension=True)
    with k.cn() as db:
        ent=db.execute('SELECT * FROM commerce_entitlements WHERE owner_key=?',(commerce.owner_key('duo-device-launch'),)).fetchone()
        assert ent['games_total']==2 and ent['games_remaining']==0
    print('LAUNCH_FLOW_ALL_PASSED; external API calls=0, real charges=0')
finally:srv.shutdown()
