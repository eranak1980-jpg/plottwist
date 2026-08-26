from __future__ import annotations
import io,json,mimetypes,os,random,re,secrets,sqlite3
from datetime import datetime,timezone
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs,urlparse
import qrcode
BASE=Path(__file__).resolve().parent;DB_PATH=Path(os.getenv('DATABASE_PATH',str(BASE/'party_game.db')));STATIC=BASE/'static';MIN_PLAYERS=2
def now():return datetime.now(timezone.utc).isoformat()
def db():c=sqlite3.connect(DB_PATH,timeout=10);c.row_factory=sqlite3.Row;return c
def ensure(c,t,n,d):
 if n not in {r['name'] for r in c.execute(f'PRAGMA table_info({t})')}:c.execute(f'ALTER TABLE {t} ADD COLUMN {n} {d}')
def init_db():
 DB_PATH.parent.mkdir(parents=True,exist_ok=True)
 with db() as c:
  c.executescript("""CREATE TABLE IF NOT EXISTS games(id INTEGER PRIMARY KEY,code TEXT UNIQUE,host_token TEXT,theme TEXT,tone TEXT,duration INTEGER,status TEXT DEFAULT 'lobby',round_no INTEGER DEFAULT 0,killer_player_id INTEGER,created_at TEXT);CREATE TABLE IF NOT EXISTS players(id INTEGER PRIMARY KEY,game_id INTEGER,name TEXT,token TEXT UNIQUE,role_name TEXT,secret TEXT,objective TEXT,joined_at TEXT);CREATE TABLE IF NOT EXISTS votes(id INTEGER PRIMARY KEY,game_id INTEGER,round_no INTEGER,voter_player_id INTEGER,accused_player_id INTEGER,created_at TEXT,UNIQUE(game_id,round_no,voter_player_id));CREATE TABLE IF NOT EXISTS gm_events(id INTEGER PRIMARY KEY,game_id INTEGER,round_no INTEGER,prompt TEXT,response TEXT,created_at TEXT);""")
  for n,d in [('group_name',"TEXT DEFAULT ''"),('relationship',"TEXT DEFAULT ''"),('inside_joke',"TEXT DEFAULT ''"),('location',"TEXT DEFAULT ''"),('intensity',"TEXT DEFAULT 'balanced'"),('story_title',"TEXT DEFAULT ''"),('victim_name',"TEXT DEFAULT ''"),('round_started_at',"TEXT DEFAULT ''"),('round_seconds','INTEGER DEFAULT 600'),('game_type',"TEXT DEFAULT 'murder'")]:ensure(c,'games',n,d)
  ensure(c,'players','private_hint',"TEXT DEFAULT ''")
def make_code():
 chars='ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
 while True:
  x=''.join(random.choice(chars) for _ in range(5))
  with db() as c:
   if not c.execute('SELECT 1 FROM games WHERE code=?',(x,)).fetchone():return x
def game(x):
 with db() as c:return c.execute('SELECT * FROM games WHERE code=?',(str(x or '').upper(),)).fetchone()
def players(gid):
 with db() as c:return c.execute('SELECT * FROM players WHERE game_id=? ORDER BY id',(gid,)).fetchall()
def clean(s,n=500):return re.sub(r'\s+',' ',str(s or '')).strip()[:n]
def story(g):
 place=g['location'] or 'the living room';mode=g['game_type'] or 'murder'
 if mode=='heist':return f'The Missing Diamond at {place}','the Midnight Diamond'
 if mode=='secrets':return f'The Secret at {place}','the secret file'
 return f'The Last Glass at {place}','Alex Rosen'
def assign(gid):
 with db() as c:g=c.execute('SELECT * FROM games WHERE id=?',(gid,)).fetchone()
 ps=players(gid)
 if len(ps)<MIN_PLAYERS:raise ValueError('need_2_players')
 culprit=random.choice(ps);title,victim=story(g);place=g['location'] or 'the living room';joke=clean(g['inside_joke'],300)
 defs=[('The Night Photographer','You captured something in the background of a video before the blackout.','Use what you saw to test the other stories.'),('The Secret Keeper',f'{victim} told you they were about to expose someone.','Work out who had the most to lose.'),('The Detail-Obsessed Host',f'You remember exactly who entered and left {place}.','Catch a contradiction.'),('The Missing Friend','You disappeared briefly for an innocent but embarrassing reason.','Protect your alibi unless accused.'),('The Observer','You noticed a detail everyone else missed.','Wait for the right moment to reveal it.')];random.shuffle(defs)
 with db() as c:
  c.execute('UPDATE games SET killer_player_id=?,story_title=?,victim_name=? WHERE id=?',(culprit['id'],title,victim,gid))
  for i,p in enumerate(ps):
   others=[x['name'] for x in ps if x['id']!=p['id']]
   if p['id']==culprit['id']:
    other=others[0] if others else 'the other player';role='The Killer' if g['game_type']=='murder' else 'The Culprit';secret=f'You are responsible for what happened to {victim}. {other} almost saw you returning to {place}.';obj='Deflect suspicion and keep your story consistent.';hint=f'Someone remembers seeing you near {place}.'
   else:
    role,secret,obj=defs[i%len(defs)];hint=f'The case references a familiar group memory: “{joke}”. Ask who would know it and why.' if joke else 'A small personal detail matters more than it first appears.'
   c.execute('UPDATE players SET role_name=?,secret=?,objective=?,private_hint=? WHERE id=?',(role,secret,obj,hint,p['id']))
def round_prompt(g,n):
 title=g['story_title'] or "Tonight's Mystery";victim=g['victim_name'] or 'the target';place=g['location'] or 'the room';joke=clean(g['inside_joke'],300)
 personal=f'A clue deliberately references a memory only this group should recognize: “{joke}”. Decide who could have planted it and why.' if joke else 'A clue contains a personal detail only someone in this group should know.'
 arr=[f'{title}. {victim} is found after a blackout at {place}. Introduce your role and alibi, but keep your secret hidden.',f'{personal} Your private clue is now unlocked. Challenge one person’s story.','A new witness statement conflicts with something already said. Each player gives a one-sentence timeline and answers one direct question.','Final accusation. Explain who did it and why, then vote in secret.']
 return arr[n-1] if 1<=n<=4 else 'The game is over.'
def remaining(g):
 if not g['round_started_at'] or g['status']!='playing':return 0
 try:return max(0,int((g['round_seconds'] or 600)-(datetime.now(timezone.utc)-datetime.fromisoformat(g['round_started_at'])).total_seconds()))
 except:return int(g['round_seconds'] or 600)
def twist(summary):
 s=clean(summary,300);return random.choice([f'New development: {s} Everyone must restate one checkable part of their timeline.',f'New clue: based on what just happened — {s} — the most questioned player must answer one direct question.',f'The Game Master interrupts: {s} Each player must reveal one previously withheld detail without revealing their full secret.'])
def vote_stats(g):
 with db() as c:
  rows=c.execute('SELECT p.id,p.name,COUNT(v.id) n FROM players p LEFT JOIN votes v ON v.accused_player_id=p.id AND v.game_id=? WHERE p.game_id=? GROUP BY p.id ORDER BY n DESC,p.id',(g['id'],g['id'])).fetchall();total=c.execute('SELECT COUNT(*) n FROM votes WHERE game_id=? AND round_no=4',(g['id'],)).fetchone()['n'];correct=c.execute('SELECT COUNT(*) n FROM votes WHERE game_id=? AND round_no=4 AND accused_player_id=?',(g['id'],g['killer_player_id'])).fetchone()['n']
 return [{'id':r['id'],'name':r['name'],'votes':r['n']} for r in rows],total,correct
class H(BaseHTTPRequestHandler):
 def j(self,x,s=200):
  b=json.dumps(x,ensure_ascii=False).encode();self.send_response(s);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
 def body(self):
  try:return json.loads(self.rfile.read(int(self.headers.get('Content-Length','0'))) or b'{}')
  except:return {}
 def f(self,p):
  try:b=p.read_bytes()
  except FileNotFoundError:return self.j({'error':'not_found'},404)
  self.send_response(200);self.send_header('Content-Type',mimetypes.guess_type(str(p))[0] or 'application/octet-stream');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
 def do_GET(self):
  u=urlparse(self.path);p=u.path
  if p=='/health':return self.j({'ok':True,'version':'qa-flow-2'})
  if p in ('/','/index.html'):return self.f(STATIC/'index.html')
  if p.startswith('/static/'):return self.f(STATIC/p.split('/static/',1)[1])
  if p.startswith('/api/qr/'):
   g=game(p.split('/api/qr/',1)[1])
   if not g:return self.j({'error':'not_found'},404)
   base=f"{self.headers.get('X-Forwarded-Proto','https')}://{self.headers.get('Host','localhost:5000')}";img=qrcode.make(f"{base}/?code={g['code']}");buf=io.BytesIO();img.save(buf,'PNG');b=buf.getvalue();self.send_response(200);self.send_header('Content-Type','image/png');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b);return
  if p.startswith('/api/game/'):
   g=game(p.split('/api/game/',1)[1].split('/')[0])
   if not g:return self.j({'error':'not_found'},404)
   q=parse_qs(u.query);tok=q.get('token',[''])[0];host=q.get('host',[''])[0]
   with db() as c:me=c.execute('SELECT * FROM players WHERE game_id=? AND token=?',(g['id'],tok)).fetchone() if tok else None;ps=c.execute('SELECT * FROM players WHERE game_id=? ORDER BY id',(g['id'],)).fetchall();ev=c.execute('SELECT * FROM gm_events WHERE game_id=? ORDER BY id DESC LIMIT 1',(g['id'],)).fetchone()
   summary,total,correct=vote_stats(g);k=next((x for x in ps if x['id']==g['killer_player_id']),None)
   out={'code':g['code'],'game_type':g['game_type'],'duration':g['duration'],'group_name':g['group_name'],'location':g['location'],'status':g['status'],'round_no':g['round_no'],'story_title':g['story_title'],'round_prompt':round_prompt(g,g['round_no']) if g['status']=='playing' else None,'remaining_seconds':remaining(g),'latest_gm_event':({'round_no':ev['round_no'],'response':ev['response']} if ev else None),'players':[{'id':x['id'],'name':x['name'],'role_name':x['role_name'] if g['status']=='finished' else None} for x in ps],'is_host':bool(host and secrets.compare_digest(host,g['host_token'])),'me':None,'killer':({'id':k['id'],'name':k['name']} if g['status']=='finished' and k else None),'vote_summary':summary if g['status']=='finished' else [],'correct_votes':correct if g['status']=='finished' else 0,'total_votes':total}
   if me:out['me']={'id':me['id'],'name':me['name'],'role_name':me['role_name'],'secret':me['secret'],'objective':me['objective'],'private_hint':me['private_hint'] if g['status']=='playing' and g['round_no']>=2 else ''}
   return self.j(out)
  return self.j({'error':'not_found'},404)
 def do_POST(self):
  p=urlparse(self.path).path;d=self.body()
  if p=='/api/create':
   co=make_code();ht=secrets.token_urlsafe(18);pt=secrets.token_urlsafe(18);name=clean(d.get('name'),40) or 'Host'
   with db() as c:cur=c.execute('INSERT INTO games(code,host_token,theme,tone,duration,group_name,relationship,inside_joke,location,intensity,created_at,game_type) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',(co,ht,clean(d.get('theme'),80) or 'Modern mystery',clean(d.get('tone'),80) or 'Funny',int(d.get('duration') or 60),clean(d.get('group_name'),80) or 'The group',clean(d.get('relationship'),80) or 'Friends',clean(d.get('inside_joke'),300),clean(d.get('location'),80) or 'the living room','balanced',now(),clean(d.get('game_type'),20) or 'murder'));c.execute('INSERT INTO players(game_id,name,token,joined_at) VALUES(?,?,?,?)',(cur.lastrowid,name,pt,now()))
   return self.j({'code':co,'host':ht,'token':pt})
  if p=='/api/join':
   g=game(d.get('code'))
   if not g:return self.j({'error':'not_found'},404)
   if g['status']!='lobby':return self.j({'error':'already_started'},400)
   name=clean(d.get('name'),40)
   if not name:return self.j({'error':'name_required'},400)
   if len(players(g['id']))>=10:return self.j({'error':'room_full'},400)
   tok=secrets.token_urlsafe(18)
   with db() as c:
    if c.execute('SELECT 1 FROM players WHERE game_id=? AND lower(name)=lower(?)',(g['id'],name)).fetchone():return self.j({'error':'name_taken'},400)
    c.execute('INSERT INTO players(game_id,name,token,joined_at) VALUES(?,?,?,?)',(g['id'],name,tok,now()))
   return self.j({'code':g['code'],'token':tok})
  if p.startswith('/api/game/'):
   parts=p.strip('/').split('/')
   if len(parts)!=4:return self.j({'error':'bad_path'},404)
   co,a=parts[2],parts[3];g=game(co)
   if not g:return self.j({'error':'not_found'},404)
   if a in ('start','next','react') and (not d.get('host') or not secrets.compare_digest(str(d['host']),g['host_token'])):return self.j({'error':'forbidden'},403)
   if a=='start':
    if g['status']!='lobby':return self.j({'error':'already_started'},409)
    try:assign(g['id'])
    except ValueError:return self.j({'error':'need_2_players'},400)
    with db() as c:c.execute("UPDATE games SET status='playing',round_no=1,round_started_at=?,round_seconds=600 WHERE id=?",(now(),g['id']))
    return self.j({'ok':True,'round_no':1,'status':'playing'})
   if a=='next':
    if g['status']!='playing':return self.j({'error':'not_playing'},409)
    current=int(g['round_no'] or 1);rn=current+1
    if rn>4:
     with db() as c:c.execute("UPDATE games SET status='finished',round_started_at='' WHERE id=?",(g['id'],))
     return self.j({'ok':True,'round_no':current,'status':'finished'})
    with db() as c:c.execute("UPDATE games SET round_no=?,round_started_at=?,round_seconds=600 WHERE id=?",(rn,now(),g['id']))
    return self.j({'ok':True,'round_no':rn,'status':'playing'})
   if a=='react':
    if g['status']!='playing':return self.j({'error':'not_playing'},409)
    summary=clean(d.get('summary'),500)
    if not summary:return self.j({'error':'summary_required'},400)
    response=twist(summary)
    with db() as c:c.execute('INSERT INTO gm_events(game_id,round_no,prompt,response,created_at) VALUES(?,?,?,?,?)',(g['id'],g['round_no'],summary,response,now()))
    return self.j({'ok':True,'response':response})
   if a=='vote':
    if g['status']!='playing' or int(g['round_no'])!=4:return self.j({'error':'voting_not_open'},409)
    with db() as c:v=c.execute('SELECT * FROM players WHERE game_id=? AND token=?',(g['id'],d