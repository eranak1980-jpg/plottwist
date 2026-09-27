"""Tie fairness, prize cast, bounded continuation and persisted sessions through real HTTP."""
import json, os, sys, tempfile, threading
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
tmp=tempfile.TemporaryDirectory();os.environ['DATABASE_PATH']=str(Path(tmp.name)/'qa.db');os.environ.pop('DATABASE_URL',None);os.environ.pop('OPENAI_API_KEY',None)
import kyc_server as k
from kyc_visuals import prompt_for
k.init();k.schedule_image_after_action=lambda *_:None
server=k.ThreadingHTTPServer(('127.0.0.1',0),k.H);threading.Thread(target=server.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{server.server_port}'
def req(path,body=None,expected=200):
 try:
  r=urlopen(Request(base+path,data=json.dumps(body).encode() if body is not None else None,headers={'Content-Type':'application/json'}));status=r.status;data=json.load(r)
 except HTTPError as e:status=e.code;data=json.load(e)
 assert status==expected,(path,status,data)
 return data
def room(n):
 host=req('/api/create',{'name':'Host','rounds':8,'language':'he','client_id':'host-'+str(n)})
 sessions=[host]+[req('/api/join',{'code':host['code'],'name':'Player '+str(i),'client_id':str(n)+'-'+str(i)}) for i in range(1,n)]
 with k.cn() as c:c.execute("UPDATE players SET photo_data='test-reference',photo_consent=1 WHERE game_id=?",(k.game(host['code'])['id'],))
 req('/api/'+host['code']+'/start',{'host':host['host']})
 g=k.game(host['code'])
 with k.cn() as c:
  c.execute("UPDATE games SET status='finished',round_no=7,prize='wearing a dress' WHERE id=?",(g['id'],))
  c.execute('UPDATE players SET score=3 WHERE game_id=?',(g['id'],))
 return host,sessions
try:
 for n in (2,3,5):
  host,sessions=room(n);code=host['code'];g=k.game(code);ps=k.players(g['id'])
  state=lambda:req('/api/state/'+code+'?token='+host['token']+'&host='+host['host'])
  st=state();assert len(st['winner_ids'])==n and st['can_tiebreak']
  photos=[dict(p,photo_data='same-reference',photo_consent=1) for p in ps]
  payload=k.image_payload(g,photos,True);assert payload['winners']==[p['name'] for p in ps]
  assert len(payload['items'])==n
  prompt=prompt_for(payload['question'],payload['answer'],[p['name'] for p in ps],payload['focus'],final=True,winners=payload['winners'])
  assert 'EVERY joint winner' in prompt and 'never merge or omit' in prompt
  photos[-1]['photo_consent']=0;assert k.image_payload(g,photos,True) is None
  # Only the host may start, and stale/double clicks cannot add extra cycles.
  req('/api/'+code+'/tiebreak',{'host':'wrong','image_run':st['image_run']},403)
  req('/api/'+code+'/tiebreak',{'host':host['host'],'image_run':-1},409)
  token_by_id={p['id']:s['token'] for p,s in zip(ps,sessions)}
  for cycle in range(1,4):
   st=state();run=st['image_run']
   req('/api/'+code+'/tiebreak',{'host':host['host'],'image_run':run})
   req('/api/'+code+'/tiebreak',{'host':host['host'],'image_run':run},409)
   subjects=[];counts={p['id']:0 for p in ps}
   for turn in range(n):
    st=state();assert st['status']=='playing';assert not st['interactive_match']
    subject=st['subject']['id'];subjects.append(subject);answer=st['options'][0]
    req('/api/'+code+'/answer',{'token':token_by_id[subject],'answer':answer})
    for p in ps:
     if p['id']!=subject:req('/api/'+code+'/guess',{'token':token_by_id[p['id']],'guess':answer});counts[p['id']]+=1
    req('/api/'+code+'/next',{'host':host['host']})
   assert len(set(subjects))==n and set(counts.values())=={n-1}
   st=state();assert st['status']=='finished' and len(st['winner_ids'])==n
   assert st['can_tiebreak']==(cycle<3)
  req('/api/'+code+'/tiebreak',{'host':host['host'],'image_run':st['image_run']},409)
  # A newly opened HTTP session retains identity, score and host rights.
  assert state()['me']['id']==ps[0]['id'] and len(state()['players'])==n
  req('/api/'+code+'/replay',{'host':host['host']});st=state()
  assert st['tiebreak']=={} and st['total']==8 and all(p['score']==0 for p in st['players'])
 print('TIES_2_3_5_ALL_WINNERS_PRIZE_REFERENCES_FAIR_CYCLES_CAP_AUTH_REPLAY_OK')
 # One winner after a complete two-player cycle, never after the first turn.
 host,sessions=room(2);code=host['code'];g=k.game(code);ps=k.players(g['id'])
 st=req('/api/state/'+code+'?token='+host['token'])
 req('/api/'+code+'/tiebreak',{'host':host['host'],'image_run':st['image_run']})
 for i in range(2):
  st=req('/api/state/'+code+'?token='+host['token']);sub=st['subject']['id'];si=next(j for j,p in enumerate(ps) if p['id']==sub);other=1-si
  req('/api/'+code+'/answer',{'token':sessions[si]['token'],'answer':st['options'][0]})
  req('/api/'+code+'/guess',{'token':sessions[other]['token'],'guess':st['options'][0 if i==0 else 1]})
  req('/api/'+code+'/next',{'host':host['host']})
  result=req('/api/state/'+code+'?token='+host['token'])
  assert result['status']==('playing' if i==0 else 'finished')
 assert len(result['winner_ids'])==1 and not result['can_tiebreak']
 print('DUO_NO_PREMATURE_WINNER_OK')
finally:server.shutdown();server.server_close();tmp.cleanup()
