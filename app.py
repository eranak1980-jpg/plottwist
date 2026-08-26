from __future__ import annotations
import io,json,mimetypes,os,random,secrets,sqlite3
from datetime import datetime,timezone
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs,urlparse
import qrcode
BASE=Path(__file__).resolve().parent;DB_PATH=Path(os.getenv('DATABASE_PATH',str(BASE/'party_game.db')));STATIC=BASE/'static';MIN_PLAYERS=2
def now():return datetime.now(timezone.utc).isoformat()
def db():c=sqlite3.connect(DB_PATH);c.row_factory=sqlite3.Row;return c
def ensure(c,t,n,d):
 if n not in {r['name'] for r in c.execute(f'PRAGMA table_info({t})')}:c.execute(f'ALTER TABLE {t} ADD COLUMN {n} {d}')
def init_db():
 DB_PATH.parent.mkdir(parents=True,exist_ok=True)
 with db() as c:
  c.executescript("""CREATE TABLE IF NOT EXISTS games(id INTEGER PRIMARY KEY,code TEXT UNIQUE,host_token TEXT,theme TEXT,tone TEXT,duration INTEGER,status TEXT DEFAULT 'lobby',round_no INTEGER DEFAULT 0,killer_player_id INTEGER,created_at TEXT);CREATE TABLE IF NOT EXISTS players(id INTEGER PRIMARY KEY,game_id INTEGER,name TEXT,token TEXT UNIQUE,role_name TEXT,secret TEXT,objective TEXT,joined_at TEXT);CREATE TABLE IF NOT EXISTS votes(id INTEGER PRIMARY KEY,game_id INTEGER,round_no INTEGER,voter_player_id INTEGER,accused_player_id INTEGER,created_at TEXT,UNIQUE(game_id,round_no,voter_player_id));CREATE TABLE IF NOT EXISTS gm_events(id INTEGER PRIMARY KEY,game_id INTEGER,round_no INTEGER,prompt TEXT,response TEXT,created_at TEXT);""")
  for n,d in [('group_name',"TEXT DEFAULT ''"),('relationship',"TEXT DEFAULT ''"),('inside_joke',"TEXT DEFAULT ''"),('location',"TEXT DEFAULT ''"),('intensity',"TEXT DEFAULT 'balanced'"),('story_title',"TEXT DEFAULT ''"),('victim_name',"TEXT DEFAULT ''"),('rounds_json',"TEXT DEFAULT ''"),('engine',"TEXT DEFAULT 'local'"),('round_started_at',"TEXT DEFAULT ''"),('round_seconds','INTEGER DEFAULT 600'),('game_type',"TEXT DEFAULT 'murder'")]:ensure(c,'games',n,d)
  ensure(c,'players','private_hint',"TEXT DEFAULT ''")
def make_code():
 chars='ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
 while True:
  x=''.join(random.choice(chars) for _ in range(5))
  with db() as c:
   if not c.execute('SELECT 1 FROM games WHERE code=?',(x,)).fetchone():return x
def game(x):
 with db() as c:return c.execute('SELECT * FROM games WHERE code=?',(x.upper(),)).fetchone()
def players(gid):
 with db() as c:return c.execute('SELECT * FROM players WHERE game_id=? ORDER BY id',(gid,)).fetchall()
def story(g):
 place=g['location'] or 'the living room';joke=g['inside_joke'] or 'an inside detail';mode=g['game_type'] or 'murder'
 if mode=='heist':return f"The Missing Diamond — {g['group_name']}",'the Midnight Diamond',joke
 if mode=='secrets':return f"The Secret of {g['group_name']}",'the secret file',joke
 return f'The Last Glass at {place}','Alex Rosen',joke
def assign(gid):
 with db() as c:g=c.execute('SELECT * FROM games WHERE id=?',(gid,)).fetchone()
 ps=players(gid)
 if len(ps)<MIN_PLAYERS:raise ValueError('need_2_players')
 culprit=random.choice(ps);title,victim,joke=story(g);place=g['location'] or 'the living room';defs=[('The Night Photographer','You captured something in the background of a video before the blackout.','Use what you saw to test the other story.'),('The Secret Keeper',f'{victim} told you they were about to expose someone.','Work out who had the most to lose.'),('The Detail-Obsessed Host',f'You remember exactly who entered and left {place}.','Catch a contradiction.'),('The Missing Friend','You disappeared briefly for an innocent but embarrassing reason.','Protect your alibi unless accused.')];random.shuffle(defs)
 with db() as c:
  c.execute("UPDATE games SET killer_player_id=?,story_title=?,victim_name=?,engine='local' WHERE id=?",(culprit['id'],title,victim,gid))
  for i,p in enumerate(ps):
   others=[x['name'] for x in ps if x['id']!=p['id']]
   if p['id']==culprit['id']:
    other=others[0] if others else 'the other player';role='The Killer' if g['game_type']=='murder' else 'The Culprit';secret=f'You are responsible for what happened to {victim}. {other} almost saw you returning to {place}.';obj=f'Deflect suspicion and make {other} doubt their theory.';hint=f'Private clue: someone remembers seeing you near {place}.'
   else:role,secret,obj=defs[i%len(defs)];hint=f'Private clue: something connected to “{joke[:30]}” matters more than it looks.'
   c.execute('UPDATE players SET role_name=?,secret=?,objective=?,private_hint=? WHERE id=?',(role,secret,obj,hint,p['id']))
def round_prompt(g,n):
 title=g['story_title'] or "Tonight's Mystery";victim=g['victim_name'] or 'the target';place=g['location'] or 'the room';joke=g['inside_joke'] or 'an inside detail';mode=g['game_type']
 if mode=='heist':arr=[f'🚨 {title}. {victim} vanished during a blackout at {place}. Introduce your character but keep your secret hidden.',f'🔎 A clue connects to “{joke[:45]}”. Your private clue is unlocked. Challenge the other timeline.','⚡ Repeat your exact timeline, then answer one sharp follow-up question.','🗳️ Give your final argument, then vote in secret.']
 elif mode=='secrets':arr=[f'📁 {title}. {victim} was leaked at {place}. Introduce your character without revealing your secret.',f'🔎 The first clue links the leak to “{joke[:45]}”. Ask one focused question.','⚡ Each player must state one fact not revealed yet.','🗳️ Who is the saboteur? Give your final defense, then vote.']
 else:arr=[f'🥂 {title}. {victim} is found dead after a blackout at {place}. Introduce your role and alibi but keep your secret hidden.',f'🔎 A torn note reads “{joke[:45]}”. Your private clue is unlocked. Challenge the other story.','⚡ Repeat your alibi in one sentence, then answer one sharp follow-up question.','🗳️ Who did it, and why? Give your final argument, then vote in secret.']
 return arr[n-1] if 1<=n<=4 else 'The game is over.'
def remaining(g):
 if not g['round_started_at'] or g['status']!='playing':return 0
 try:return max(0,int((g['round_seconds'] or 600)-(datetime.now(timezone.utc)-datetime.fromisoformat(g['round_started_at'])).total_seconds()))
 except:return int(g['round_seconds'] or 600)
def twist(summary):
 return random.choice([f'LIVE TWIST — {summary[:150]} Now everyone must repeat their alibi in one sentence. No interruptions.',f'NEW CLUE — {summary[:150]} The person under the most suspicion gets one direct question. They must answer immediately.',f'THE GAME MASTER INTERRUPTS — {summary[:150]} Each player must now reveal one detail they were holding back, but not their full secret.'])
class H(BaseHTTPRequestHandler):
 def j(self,x,s=200):b=json.dumps(x,ensure_ascii=False).encode();self.send_response(s);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
 def body(self):
  try:return json.loads(self.rfile.read(int(self.headers.get('Content-Length','0'))) or b'{}')
  except:return {}
 def f(self,p):
  try:b=p.read_bytes()
  except FileNotFoundError:self.send_error(404);return
  self.send_response(200);self.send_header('Content-Type',mimetypes.guess_type(str(p))[0] or 'application/octet-stream');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
 def do_GET(self):
  u=urlparse(self.path);p=u.path
  if p=='/health':return self.j({'ok':True})
  if p in ('/','/index.html'):return self.f(STATIC/'index.html')
  if p.startswith('/static/'):return self.f(STATIC/p.split('/static/',1)[1])
  if p.startswith('/api/qr/'):
   g=game(p.split('/api/qr/',1)[1]);
   if not g:return self.j({'error':'not_found'},404)
   base=f"{self.headers.get('X-Forwarded-Proto','https')}://{self.headers.get('Host','localhost:5000')}";img=qrcode.make(f"{base}/?code={g['code']}");buf=io.BytesIO();img.save(buf,'PNG');b=buf.getvalue();self.send_response(200);self.send_header('Content-Type','image/png');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b);return
  if p.startswith('/api/game/'):
   g=game(p.rsplit('/',1)[-1]);
   if not g:return self.j({'error':'not_found'},404)
   q=parse_qs(u.query);tok=q.get('token',[''])[0];host=q.get('host',[''])[0]
   with db() as c:me=c.execute('SELECT * FROM players WHERE game_id=? AND token=?',(g['id'],tok)).fetchone() if tok else None;ps=c.execute('SELECT * FROM players WHERE game_id=? ORDER BY id',(g['id'],)).fetchall();ev=c.execute('SELECT * FROM gm_events WHERE game_id=? ORDER BY id DESC LIMIT 1',(g['id'],)).fetchone()
   out={'code':g['code'],'game_type':g['game_type'],'duration':g['duration'],'group_name':g['group_name'],'location':g['location'],'status':g['status'],'round_no':g['round_no'],'story_title':g['story_title'],'engine':g['engine'],'round_prompt':round_prompt(g,g['round_no']) if g['status']=='playing' else None,'remaining_seconds':remaining(g),'latest_gm_event':({'round_no':ev['round_no'],'response':ev['response']} if ev else None),'players':[{'id':x['id'],'name':x['name'],'role_name':x['role_name'] if g['status']=='finished' else None} for x in ps],'is_host':bool(host and secrets.compare_digest(host,g['host_token'])),'me':None,'killer':None,'vote_summary':[],'correct_votes':0,'total_votes':0}
   if me:out['me']={'id':me['id'],'name':me['name'],'role_name':me['role_name'],'secret':me['secret'],'objective':me['objective'],'private_hint':me['private_hint'] if g['status']=='playing' and g['round_no']>=2 else ''}
   if g['status']=='finished':
    k=next((x for x in ps if x['id']==g['killer_player_id']),None);out['killer']={'id':k['id'],'name':k['name']} if k else None
   return self.j(out)
  self.send_error(404)
 def do_POST(self):
  p=urlparse(self.path).path;d=self.body()
  if p=='/api/create':
   co=make_code();ht=secrets.token_urlsafe(18);pt=secrets.token_urlsafe(18)
   with db() as c:cur=c.execute('INSERT INTO games(code,host_token,theme,tone,duration,group_name,relationship,inside_joke,location,intensity,created_at,game_type) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',(co,ht,d.get('theme') or 'Modern mystery',d.get('tone') or 'Funny',int(d.get('duration') or 60),d.get('group_name') or 'The group',d.get('relationship') or 'Friends',d.get('inside_joke') or '',d.get('location') or 'the living room',d.get('intensity') or 'balanced',now(),d.get('game_type') or 'murder'));c.execute('INSERT INTO players(game_id,name,token,joined_at) VALUES(?,?,?,?)',(cur.lastrowid,d.get('name') or 'Host',pt,now()))
   return self.j({'code':co,'host':ht,'token':pt})
  if p=='/api/join':
   g=game((d.get('code') or '').upper());
   if not g:return self.j({'error':'not_found'},404)
   if g['status']!='lobby':return self.j({'error':'already_started'},400)
   tok=secrets.token_urlsafe(18);name=(d.get('name') or '').strip()
   with db() as c:
    if c.execute('SELECT 1 FROM players WHERE game_id=? AND lower(name)=lower(?)',(g['id'],name)).fetchone():return self.j({'error':'name_taken'},400)
    c.execute('INSERT INTO players(game_id,name,token,joined_at) VALUES(?,?,?,?)',(g['id'],name,tok,now()))
   return self.j({'code':g['code'],'token':tok})
  if p.startswith('/api/game/'):
   parts=p.strip('/').split('/');
   if len(parts)!=4:return self.j({'error':'bad_path'},404)
   _,_,co,a=parts;g=game(co)
   if not g:return self.j({'error':'not_found'},404)
   if a in ('start','next','react'):
    if not d.get('host') or not secrets.compare_digest(d['host'],g['host_token']):return self.j({'error':'forbidden'},403)
   if a=='start':
    try:assign(g['id'])
    except ValueError:return self.j({'error':'need_2_players'},400)
    with db() as c:c.execute("UPDATE games SET status='playing',round_no=1,round_started_at=?,round_seconds=? WHERE id=?",(now(),600,g['id']))
    return self.j({'ok':True})
   if a=='next':
    rn=g['round_no']+1;st='finished' if rn>4 else 'playing'
    with db() as c:c.execute('UPDATE games SET status=?,round_no=?,round_started_at=? WHERE id=?',(st,rn,now() if st=='playing' else '',g['id']))
    return self.j({'ok':True})
   if a=='react':
    summary=(d.get('summary') or '').strip()
    if not summary:return self.j({'error':'summary_required'},400)
    response=twist(summary)
    with db() as c:c.execute('INSERT INTO gm_events(game_id,round_no,prompt,response,created_at) VALUES(?,?,?,?,?)',(g['id'],g['round_no'],summary[:500],response,now()))
    return self.j({'ok':True,'response':response})
   if a=='vote':
    with db() as c:v=c.execute('SELECT * FROM players WHERE game_id=? AND token=?',(g['id'],d.get('token',''))).fetchone();acc=c.execute('SELECT * FROM players WHERE game_id=? AND id=?',(g['id'],int(d.get('accused_id',0)))).fetchone()
    if not v or not acc:return self.j({'error':'invalid_vote'},400)
    with db() as c:c.execute('INSERT OR REPLACE INTO votes(game_id,round_no,voter_player_id,accused_player_id,created_at) VALUES(?,?,?,?,?)',(g['id'],g['round_no'],v['id'],acc['id'],now()))
    return self.j({'ok':True})
  return self.j({'error':'not_found'},404)
 def log_message(self,*a):pass
def run():init_db();port=int(os.getenv('PORT','5000'));print(f'PlotTwist running on 0.0.0.0:{port}');ThreadingHTTPServer(('0.0.0.0',port),H).serve_forever()
if __name__=='__main__':run()
