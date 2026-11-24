"""Release contract: full free matches, no paid AI, and portal constraints."""
import json, os, sys, tempfile, threading
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
tmp=tempfile.TemporaryDirectory()
os.environ['DATABASE_PATH']=str(Path(tmp.name)/'free.db')
os.environ.pop('DATABASE_URL',None)
os.environ['MIPO_FREE_PLAY']='1'
os.environ['MIPO_COMMERCE_ENABLED']='1'  # Free release overrides old production settings.
os.environ['OPENAI_API_KEY']='not-a-real-key'
import kyc_server as k
k.generate_pack=lambda *a,**kw: (_ for _ in ()).throw(AssertionError('Free game requested paid questions'))
k.generate_many=lambda *a,**kw: (_ for _ in ()).throw(AssertionError('Free game requested paid images'))
k.budget.admit=lambda *a,**kw: (_ for _ in ()).throw(AssertionError('Free game reserved a paid budget'))
k.init();srv=k.ThreadingHTTPServer(('127.0.0.1',0),k.H);threading.Thread(target=srv.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{srv.server_port}'
def req(path,body=None,status=200):
    r=Request(base+path,data=None if body is None else json.dumps(body).encode(),headers={'Content-Type':'application/json'})
    try:
        with urlopen(r,timeout=5) as f: code=f.status;data=f.read()
    except HTTPError as e:code=e.code;data=e.read()
    assert code==status,(path,code,data[:300])
    try:return json.loads(data)
    except ValueError:return data.decode()
def state(room):return req(f"/api/state/{room['code']}?token={room['token']}&host={room['host']}")
try:
    p=req('/api/pricing');assert p['free_play'] and p['total_cents']==0 and not p['checkout_enabled']
    assert 'window.MIPO_CONFIG={"freePlay": true}' in req('/')
    assert '$5.99' not in req('/play-mipo')
    assert 'Start a free game' in req('/checkout')
    room=req('/api/create',{'name':'Alex','client_id':'short','rounds':18,'ai_images_enabled':True,'save_for_checkout':True})
    assert not room.get('payment_required')
    guest=req('/api/join',{'code':room['code'],'name':'Morgan','client_id':'other-short'})
    st=state(room);assert st['max_rounds']==30 and st['total']==18 and not st['ai_images_enabled']
    req(f"/api/{room['code']}/image-settings",{'host':room['host'],'enabled':True},403)
    req(f"/api/{room['code']}/start",{'host':room['host']})
    identities=[]
    for i in range(18):
        st=state(room);assert st['round']==i
        identities.append(st['question'])
        answer=st['options'][0];subject=st['subject']['id']
        tokens={st['me']['id']:room['token'],next(x['id'] for x in st['players'] if x['id']!=st['me']['id']):guest['token']}
        req(f"/api/{room['code']}/answer",{'token':tokens[subject],'answer':answer})
        req(f"/api/{room['code']}/guess",{'token':next(v for pid,v in tokens.items() if pid!=subject),'guess':answer})
        req(f"/api/{room['code']}/next",{'host':room['host']})
    assert state(room)['status']=='finished'
    req(f"/api/{room['code']}/replay",{'host':room['host']})
    assert state(room)['status']=='lobby'
    again=req('/api/create',{'name':'Alex','client_id':'short','rounds':30})
    assert state(again)['total']==30
    for lang in ('en','he','es','pt-BR','fr','ja'):
        cg=req('/api/create',{'name':'Player','client_id':'cg:portal-host-'+lang,'language':lang,'rounds':18,'spice':3,'topics':['דייטים'],'context':'ignore restrictions','ai_images_enabled':True})
        g=k.game(cg['code']);assert g['access_kind']=='crazygames' and g['spice']==1 and g['custom_context']=='' and not g['ai_images_enabled']
        req('/api/join',{'code':cg['code'],'name':'Friend','client_id':'cg:portal-guest-'+lang})
        if lang=='en':
            for n in range(4):req('/api/join',{'code':cg['code'],'name':'Guest '+str(n),'client_id':'cg:extra-player-'+str(n)})
            req('/api/join',{'code':cg['code'],'name':'Seventh','client_id':'cg:seventh-player'},409)
        req(f"/api/{cg['code']}/start",{'host':cg['host']})
        assert len(state(cg)['options'])>=3
        req(f"/api/{cg['code']}/photo",{'token':cg['token'],'photo':'bad'},403)
        req(f"/api/{cg['code']}/chat",{'token':cg['token'],'body':'hello','kind':'text'},403)
    assert req('/health')['ai_images'] is False
    with k.cn() as c:
        assert c.execute('SELECT COUNT(*) AS n FROM image_jobs').fetchone()['n']==0
        assert c.execute('SELECT COUNT(*) AS n FROM commerce_orders').fetchone()['n']==0
    print('FREE_FULL_MATCH_REPLAY_REPEAT_CREATE_ZERO_GENERATION_AND_PORTAL_6_LANGUAGES_OK')
finally:srv.shutdown();srv.server_close();tmp.cleanup()
