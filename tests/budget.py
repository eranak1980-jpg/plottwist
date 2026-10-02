"""No paid API calls. Covers persistent limits, concurrent admissions and retry billing."""
import os,sys,tempfile,json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
tmp=tempfile.TemporaryDirectory();os.environ['DATABASE_PATH']=str(Path(tmp.name)/'budget.db');os.environ.pop('DATABASE_URL',None)
if os.getenv('PLOT_IMAGE_TEST_DATABASE_URL'):os.environ['DATABASE_URL']=os.environ['PLOT_IMAGE_TEST_DATABASE_URL']
import kyc_server as k
import kyc_budget as b
k.init()
# Isolate own singleton in the dedicated test database.
with k.cn() as c:
 c.execute('DELETE FROM budget_calls');c.execute('DELETE FROM budget_active');c.execute('DELETE FROM budget_sessions');c.execute('UPDATE launch_budget SET sessions=0,reserved_micro=0 WHERE id=1')
def admit(gid):
 try:
  with k.cn() as c:return b.admit(c,gid)
 except b.BudgetLimit:return None
with patch.object(b,'CAP',b.SESSION_RESERVE*2):
 with ThreadPoolExecutor(max_workers=8) as pool:results=list(pool.map(admit,range(100,112)))
 assert sum(bool(x) for x in results)==2,results
 with k.cn() as c:gid=c.execute('SELECT game_id FROM budget_active ORDER BY game_id').fetchone()['game_id']
 assert admit(gid),'same game resume consumes no new allowance'
 k.init();assert not admit(999),'restart must not reset budget'
os.environ['OPENAI_API_KEY']='test-only'
with b.scope(k.cn,gid,'image:0'):
 ticket=b.begin('image','gpt-image-2.5-flare')
 b.finish(ticket,{'input_tokens_details':{'text_tokens':1000,'image_tokens':2000},'output_tokens':500})
 b.finish(ticket,{'input_tokens_details':{'text_tokens':1000,'image_tokens':2000},'output_tokens':500})
 for _ in range(2):b.finish(b.begin('image','gpt-image-2.5-flare'),status='unknown_or_failed')
 try:b.begin('image','gpt-image-2.5-flare');raise AssertionError('retry not limited')
 except b.BudgetLimit:pass
with k.cn() as c:
 report=b.report(c,gid);assert report['measured_usd']==.036 and report['unpriced_calls']==2,report
 assert report['estimated_usd']==.336
 assert c.execute('SELECT COUNT(*) AS n FROM budget_calls').fetchone()['n']==3
assert b.pricing(18,1)['total_cents']==799
assert b.pricing(20,2)['total_cents']==1598
for r,g in [(31,1),(7,1),(18,3)]:
 try:b.pricing(r,g);raise AssertionError('invalid quote')
 except ValueError:pass
print('Budget concurrency, persistence, idempotency, retry and pricing checks passed')

import threading
from urllib.request import Request,urlopen
from urllib.error import HTTPError
os.environ.pop('OPENAI_API_KEY',None)
server=k.ThreadingHTTPServer(('127.0.0.1',0),k.H);threading.Thread(target=server.serve_forever,daemon=True).start()
base='http://127.0.0.1:'+str(server.server_port)
def request(path,data=None):
 req=Request(base+path,data=json.dumps(data).encode() if data is not None else None,headers={'Content-Type':'application/json'})
 try:
  with urlopen(req) as r:return r.status,json.load(r)
 except HTTPError as e:return e.code,json.load(e)
_,room=request('/api/create',{'name':'Budget QA','rounds':18})
assert request('/api/pricing?rounds=20&games=2')[1]['total_cents']==1598
assert request('/api/costs/'+room['code'])[0]==403
assert request('/api/costs/'+room['code']+'?host=wrong')[0]==403
assert request('/api/costs/'+room['code']+'?host='+room['host'])[0]==200
os.environ['OPENAI_API_KEY']='test-only'
with patch.object(b,'CAP',0):
 with k.cn() as c:before=c.execute('SELECT COUNT(*) AS n FROM games').fetchone()['n']
 assert request('/api/create',{'name':'Must roll back'})==(429,{'error':'pilot_limit'})
 with k.cn() as c:assert c.execute('SELECT COUNT(*) AS n FROM games').fetchone()['n']==before
server.shutdown();print('Budget HTTP auth, quote and admission rollback passed')
