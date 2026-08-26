import json,os,secrets,sqlite3
from datetime import datetime,timezone
from pathlib import Path
from game_engine import build_case,public_round
BASE=Path(__file__).parent
DB=Path(os.getenv('DATABASE_PATH',BASE/'party_game.db'))
def now():return datetime.now(timezone.utc).isoformat()
def cn():c=sqlite3.connect(DB,timeout=10);c.row_factory=sqlite3.Row;return c
def ensure_v2():
 with cn() as c:
  cols={r['name'] for r in c.execute('PRAGMA table_info(games)')}
  for name,decl in [('case_json',"TEXT DEFAULT ''"),('phase_started_at',"TEXT DEFAULT ''")]:
   if name not in cols:c.execute(f'ALTER TABLE games ADD COLUMN {name} {decl}')
  pcols={r['name'] for r in c.execute('PRAGMA table_info(players)')}
  for name,decl in [('photo_data',"TEXT DEFAULT ''"),('photo_consent','INTEGER DEFAULT 0')]:
   if name not in pcols:c.execute(f'ALTER TABLE players ADD COLUMN {name} {decl}')
def start_case(game_id):
 with cn() as c:g=c.execute('SELECT * FROM games WHERE id=?',(game_id,)).fetchone();players=c.execute('SELECT * FROM players WHERE game_id=? ORDER BY id',(game_id,)).fetchall()
 if len(players)<2:raise ValueError('need_2_players')
 case=build_case([{'id':p['id'],'name':p['name']} for p in players],g['location'],g['inside_joke'],g['game_type'])
 culprit=next(p for p in players if p['name']==case['culprit'])
 with cn() as c:
  c.execute("UPDATE games SET status='playing',round_no=1,killer_player_id=?,story_title=?,victim_name=?,case_json=?,phase_started_at=? WHERE id=?",(culprit['id'],case['title'],case['victim'],json.dumps(case,ensure_ascii=False),now(),game_id))
  for p in players:
   r=case['roles'][p['name']];c.execute('UPDATE players SET role_name=?,secret=?,objective=?,private_hint=? WHERE id=?',(r['role'],r['secret'],r['objective'],' '.join(r['knows']),p['id']))
 return case
def state_v2(game_id,token=''):
 with cn() as c:g=c.execute('SELECT * FROM games WHERE id=?',(game_id,)).fetchone();players=c.execute('SELECT * FROM players WHERE game_id=? ORDER BY id',(game_id,)).fetchall();me=c.execute('SELECT * FROM players WHERE game_id=? AND token=?',(game_id,token)).fetchone() if token else None
 case=json.loads(g['case_json']) if g['case_json'] else None
 out={'status':g['status'],'round_no':g['round_no'],'title':g['story_title'],'players':[{'id':p['id'],'name':p['name'],'has_photo':bool(p['photo_data'])} for p in players]}
 if case and g['status']=='playing':out['round']=public_round(case,int(g['round_no']))
 if case and me:out['me']={'role':me['role_name'],'secret':me['secret'],'objective':me['objective'],'private_hint':me['private_hint'],'photo_data':me['photo_data']}
 if case and g['status']=='finished':out['reveal']=case['reveal']
 return out
def advance_v2(game_id):
 with cn() as c:g=c.execute('SELECT * FROM games WHERE id=?',(game_id,)).fetchone();n=int(g['round_no'])+1
 with cn() as c:
  if n>4:c.execute("UPDATE games SET status='finished',phase_started_at=? WHERE id=?",(now(),game_id));return {'status':'finished'}
  c.execute('UPDATE games SET round_no=?,phase_started_at=? WHERE id=?',(n,now(),game_id));return {'status':'playing','round_no':n}
def save_photo(game_id,token,data_url,consent):
 if not consent:raise ValueError('consent_required')
 if not isinstance(data_url,str) or not data_url.startswith('data:image/'):raise ValueError('invalid_image')
 if len(data_url)>1_500_000:raise ValueError('image_too_large')
 with cn() as c:
  p=c.execute('SELECT id FROM players WHERE game_id=? AND token=?',(game_id,token)).fetchone()
  if not p:raise ValueError('player_not_found')
  c.execute('UPDATE players SET photo_data=?,photo_consent=1 WHERE id=?',(data_url,p['id']))
 return {'ok':True}
