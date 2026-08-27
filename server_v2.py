import base64,io,json,os,sqlite3
from datetime import datetime,timezone
from pathlib import Path
from game_engine import build_case,public_round
BASE=Path(__file__).parent;DB=Path(os.getenv('DATABASE_PATH',BASE/'party_game.db'))
def now():return datetime.now(timezone.utc).isoformat()
def cn():c=sqlite3.connect(DB,timeout=20);c.row_factory=sqlite3.Row;return c
def ensure_v2():
 with cn() as c:
  cols={r['name'] for r in c.execute('PRAGMA table_info(games)')}
  for name,decl in [('case_json',"TEXT DEFAULT ''"),('phase_started_at',"TEXT DEFAULT ''"),('turn_index','INTEGER DEFAULT 0')]:
   if name not in cols:c.execute(f'ALTER TABLE games ADD COLUMN {name} {decl}')
  pcols={r['name'] for r in c.execute('PRAGMA table_info(players)')}
  for name,decl in [('photo_data',"TEXT DEFAULT ''"),('photo_consent','INTEGER DEFAULT 0'),('ai_art_data',"TEXT DEFAULT ''")]:
   if name not in pcols:c.execute(f'ALTER TABLE players ADD COLUMN {name} {decl}')
def portrait_prompt(role,mode,location):
 mood={'The Culprit':'tense, enigmatic, morally ambiguous suspect','The Witness':'alert eyewitness who has seen something important','The Secret Keeper':'mysterious confidant protecting a dangerous secret'}.get(role,'mysterious participant')
 genre={'murder':'modern cinematic murder mystery','heist':'stylish contemporary heist thriller','secrets':'prestige psychological mystery'}.get(mode,'cinematic mystery')
 return f'''Transform the provided real person's photo into a premium fictional role-card portrait for a private party game. Preserve the person's recognizable identity, facial structure, age, skin tone, hairstyle and key facial features with high fidelity. They are playing {role}: {mood}. Genre: {genre}. Setting inspired by {location or 'an elegant interior'}. Photorealistic cinematic editorial portrait, dramatic practical lighting, shallow depth of field, sophisticated dark atmosphere, premium streaming-series key art, chest-up composition. Keep the face clearly visible and unobstructed. Change clothing/background/lighting to fit the role. No text, no letters, no logos, no captions, no weapons, no blood, no injury, no gore.'''
def generate_portrait(data_url,role,mode,location):
 key=os.getenv('OPENAI_API_KEY','').strip()
 if not key or not data_url:return ''
 try:
  from openai import OpenAI
  head,b64=data_url.split(',',1);raw=base64.b64decode(b64);ext='png' if 'png' in head else ('webp' if 'webp' in head else 'jpg');f=io.BytesIO(raw);f.name='player.'+ext
  client=OpenAI(api_key=key,timeout=90.0);res=client.images.edit(model='gpt-image-1',image=f,prompt=portrait_prompt(role,mode,location),size='1024x1024',quality='medium',input_fidelity='high')
  out=res.data[0].b64_json
  return 'data:image/png;base64,'+out if out else ''
 except Exception as e:
  print('AI portrait generation failed:',type(e).__name__,str(e)[:300],flush=True);return ''
def start_case(game_id):
 with cn() as c:g=c.execute('SELECT * FROM games WHERE id=?',(game_id,)).fetchone();players=c.execute('SELECT * FROM players WHERE game_id=? ORDER BY id',(game_id,)).fetchall()
 if len(players)<2:raise ValueError('need_2_players')
 case=build_case([{'id':p['id'],'name':p['name']} for p in players],g['location'],g['inside_joke'],g['game_type']);culprit=next(p for p in players if p['name']==case['culprit'])
 with cn() as c:
  c.execute('DELETE FROM votes WHERE game_id=?',(game_id,));c.execute("UPDATE games SET status='playing',round_no=1,turn_index=0,killer_player_id=?,story_title=?,victim_name=?,case_json=?,phase_started_at=? WHERE id=?",(culprit['id'],case['title'],case['victim'],json.dumps(case,ensure_ascii=False),now(),game_id))
  for p in players:
   r=case['roles'][p['name']];c.execute('UPDATE players SET role_name=?,secret=?,objective=?,private_hint=? WHERE id=?',(r['role'],r['secret'],r['objective'],' '.join(r['knows']),p['id']))
 # Generate after the game is committed. A failed/limited image API never blocks gameplay.
 for p in players:
  if not p['photo_data'] or not p['photo_consent']:continue
  role=case['roles'][p['name']]['role'];art=generate_portrait(p['photo_data'],role,g['game_type'],g['location'])
  if art:
   with cn() as c:c.execute('UPDATE players SET ai_art_data=? WHERE id=?',(art,p['id']))
 return case
def vote_snapshot(c,game_id,me_id=None):
 rows=c.execute('SELECT p.id,p.name,COUNT(v.id) votes FROM players p LEFT JOIN votes v ON v.game_id=? AND v.round_no=4 AND v.accused_player_id=p.id WHERE p.game_id=? GROUP BY p.id ORDER BY p.id',(game_id,game_id)).fetchall();total=c.execute('SELECT COUNT(*) n FROM votes WHERE game_id=? AND round_no=4',(game_id,)).fetchone()['n'];my=None
 if me_id:
  r=c.execute('SELECT accused_player_id FROM votes WHERE game_id=? AND round_no=4 AND voter_player_id=?',(game_id,me_id)).fetchone();my=r['accused_player_id'] if r else None
 return [{'id':r['id'],'name':r['name'],'votes':r['votes']} for r in rows],total,my
def state_v2(game_id,token=''):
 with cn() as c:
  g=c.execute('SELECT * FROM games WHERE id=?',(game_id,)).fetchone();players=c.execute('SELECT * FROM players WHERE game_id=? ORDER BY id',(game_id,)).fetchall();me=c.execute('SELECT * FROM players WHERE game_id=? AND token=?',(game_id,token)).fetchone() if token else None;results,vote_count,my_vote=vote_snapshot(c,game_id,me['id'] if me else None)
 case=json.loads(g['case_json']) if g['case_json'] else None;out={'status':g['status'],'round_no':g['round_no'],'turn_index':int(g['turn_index'] or 0),'title':g['story_title'],'vote_count':vote_count,'votes_needed':len(players),'my_vote':my_vote,'players':[{'id':p['id'],'name':p['name'],'has_photo':bool(p['photo_data']),'has_ai_art':bool(p['ai_art_data'])} for p in players]}
 if me:out['me']={'id':me['id'],'name':me['name'],'has_photo':bool(me['photo_data']),'photo_data':me['photo_data'],'ai_art_data':me['ai_art_data']}
 if case and g['status']=='playing':out['round']=public_round(case,int(g['round_no']))
 if case and me:out['me'].update({'role':me['role_name'],'secret':me['secret'],'objective':me['objective'],'private_hint':me['private_hint']})
 if case and g['status']=='finished':out['reveal']=case['reveal'];out['results']=results;out['correct_votes']=sum(r['votes'] for r in results if r['id']==g['killer_player_id']);out['culprit_id']=g['killer_player_id']
 return out
def next_turn(game_id):
 with cn() as c:
  g=c.execute('SELECT * FROM games WHERE id=?',(game_id,)).fetchone();case=json.loads(g['case_json']) if g['case_json'] else None
  if not case or g['status']!='playing':raise ValueError('game_not_playing')
  total=len(case['rounds'][int(g['round_no'])-1].get('turns',[]));n=min(int(g['turn_index'] or 0)+1,total);c.execute('UPDATE games SET turn_index=? WHERE id=?',(n,game_id));return {'ok':True,'turn_index':n,'total':total}
def advance_v2(game_id):
 with cn() as c:
  g=c.execute('SELECT * FROM games WHERE id=?',(game_id,)).fetchone();case=json.loads(g['case_json']) if g['case_json'] else None;total=len(case['rounds'][int(g['round_no'])-1].get('turns',[])) if case else 0
  if int(g['turn_index'] or 0)<total:raise ValueError('finish_player_turns_first')
  if int(g['round_no'])==4:
   players=c.execute('SELECT COUNT(*) n FROM players WHERE game_id=?',(game_id,)).fetchone()['n'];votes=c.execute('SELECT COUNT(*) n FROM votes WHERE game_id=? AND round_no=4',(game_id,)).fetchone()['n']
   if votes<players:raise ValueError('waiting_for_all_votes')
  n=int(g['round_no'])+1
  if n>4:c.execute("UPDATE games SET status='finished',phase_started_at=? WHERE id=?",(now(),game_id));return {'status':'finished'}
  c.execute('UPDATE games SET round_no=?,turn_index=0,phase_started_at=? WHERE id=?',(n,now(),game_id));return {'status':'playing','round_no':n}
def save_photo(game_id,token,data_url,consent):
 if not consent:raise ValueError('consent_required')
 if not isinstance(data_url,str) or not data_url.startswith('data:image/'):raise ValueError('invalid_image')
 if len(data_url)>1_500_000:raise ValueError('image_too_large')
 with cn() as c:
  p=c.execute('SELECT id FROM players WHERE game_id=? AND token=?',(game_id,token)).fetchone()
  if not p:raise ValueError('player_not_found')
  c.execute("UPDATE players SET photo_data=?,photo_consent=1,ai_art_data='' WHERE id=?",(data_url,p['id']))
 return {'ok':True,'saved':True}
