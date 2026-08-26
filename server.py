import io,json,mimetypes,os,random,secrets,sqlite3
from datetime import datetime,timezone
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs,urlparse
import qrcode
BASE=Path(__file__).parent
DB=Path(os.getenv('DATABASE_PATH',BASE/'party_game.db'))
STATIC=BASE/'static'
def now(): return datetime.now(timezone.utc).isoformat()
def cn(): c=sqlite3.connect(DB,timeout=10);c.row_factory=sqlite3.Row;return c
def init():
 DB.parent.mkdir(parents=True,exist_ok=True)
 with cn() as c:c.executescript("""CREATE TABLE IF NOT EXISTS games(id INTEGER PRIMARY KEY,code TEXT UNIQUE,host_token TEXT,status TEXT DEFAULT 'lobby',round_no INTEGER DEFAULT 0,killer_player_id INTEGER,group_name TEXT DEFAULT '',location TEXT DEFAULT '',inside_joke TEXT DEFAULT '',game_type TEXT DEFAULT 'murder',story_title TEXT DEFAULT '',victim_name TEXT DEFAULT '',round_started_at TEXT DEFAULT '',round_seconds INTEGER DEFAULT 600,created_at TEXT);CREATE TABLE IF NOT EXISTS players(id INTEGER PRIMARY KEY,game_id INTEGER,name TEXT,token TEXT UNIQUE,role_name TEXT DEFAULT '',secret TEXT DEFAULT '',objective TEXT DEFAULT '',private_hint TEXT DEFAULT '',joined_at TEXT);CREATE TABLE IF NOT EXISTS gm_events(id INTEGER PRIMARY KEY,game_id INTEGER,round_no INTEGER,response TEXT,created_at TEXT);CREATE TABLE IF NOT EXISTS votes(id INTEGER PRIMARY KEY,game_id INTEGER,round_no INTEGER,voter_player_id INTEGER,accused_player_id INTEGER,created_at TEXT,UNIQUE(game_id,round_no,voter_player_id));""")
def game(code):
 with cn() as c:return c.execute('SELECT * FROM games WHERE code=?',(str(code or '').upper(),)).fetchone()
def ps(gid):
 with cn() as c:return c.execute('SELECT * FROM players WHERE game_id=? ORDER BY id',(gid,)).fetchall()
def clean(x,n=300):return ' '.join(str(x or '').split())[:n]
def code5():
 chars='ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
 while True:
  x=''.join(random.choice(chars) for _ in range(5))
  if not game(x):return x
def story(g):
 p=g['location'] or 'the living room'
 if g['game_type']=='heist':return f'The Missing Diamond at {p}','the Midnight Diamond'
 if g['game_type']=='secrets':return f'The Secret at {p}','the secret file'
 return f'The Last Glass at {p}','Alex Rosen'
def assign(g):
 players=ps(g['id'])
 if len(players)<2:raise ValueError
 killer=random.choice(players);t,v=story(g);place=g['location'] or 'the living room';j=clean(g['inside_joke'])
 roles=[('The Night Photographer','You captured something in a video before the blackout.','Use what you saw to test the others.'),('The Secret Keeper',f'{v} told you they were about to expose someone.','Work out who had the most to lose.'),('The Detail-Obsessed Host',f'You remember who entered and left {place}.','Catch a contradiction.'),('The Missing Friend','You disappeared briefly for an innocent reason.','Protect your alibi unless accused.')]
 random.shuffle(roles)
 with cn() as c:
  c.execute('UPDATE games SET killer_player_id=?,story_title=?,victim_name=? WHERE id=?',(killer['id'],t,v,g['id']))
  for i,p in enumerate(players):
   if p['id']==killer['id']:r='The Killer' if g['game_type']=='murder' else 'The Culprit';s=f'You are responsible for what happened to {v}. Someone almost saw you near {place}.';o='Deflect suspicion and keep your story consistent.';h=f'Private clue: someone remembers seeing you near {place}.'
   else:r,s,o=roles[i%len(roles)];h=f'Private clue: the case references this group memory: "{j}". Ask who would know it and why.' if j else 'Private clue: a small personal detail matters more than it seems.'
   c.execute('UPDATE players SET role_name=?,secret=?,objective=?,private_hint=? WHERE id=?',(r,s,o,h,p['id']))
def prompt(g):
 n=int(g['round_no']);t=g['story_title'] or "Tonight's Mystery";v=g['victim_name'] or 'the target';p=g['location'] or 'the room';j=clean(g['inside_joke'])
 personal=f'A clue references a memory only this group should know: "{j}". Decide who could have planted it and why.' if j else 'A clue contains a personal detail only someone in this group should know.'
 arr=[f'{t}. {v} is found after a blackout at {p}. Introduce your role and alibi, but keep your secret hidden.',f'{personal} Your private clue is now unlocked. Challenge one person’s story.','A new witness statement conflicts with something already said. Give a one-sentence timeline and answer one direct question.','Final accusation. Explain who did it and why, then vote in secret.']
 return arr[n-1] if 1<=n<=4 else 'The game is over.'
def left(g):
 if g['status']!='playing' or not g['round_started_at']:return 0
 try:return max(0,int((g['round_seconds'] or 600)-(datetime.now(timezone.utc)-datetime.fromisoformat(g['round_started_at'])).total_seconds()))
 except:return 600
def stats(g):
 with cn() as c:
  rows=c.execute('SELECT p.id,p.name,COUNT(v.id) n FROM players p LEFT JOIN votes v ON v.accused_player_id=p.id AND v.game_id=? AND v.round_no=4 WHERE p.game_id=? GROUP BY p.id ORDER BY n DESC,p.id',(g['id'],g['id'])).fetchall();total=c.execute('SELECT COUNT(*) n FROM votes WHERE game_id=? AND round_no=4',(g['id'],)).fetchone()['n'];correct=c.execute('SELECT COUNT(*) n FROM votes WHERE game_id=? AND round_no=4 AND accused_player_id=?',(g['id'],g['killer_player_id'])).fetchone()['n']
 return [{'id':r['id'],'name':r['name'],'votes':r['n']} for r in rows],total,correct
class H(BaseHTTPRequestHandler):
 def J(self,x,s=200):
  b=json.dumps(x,ensure_ascii=False).encode();self.send_response(s);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
 def B(self):
  try:return json.loads(self.rfile.read(int(self.headers.get('Content-Length','0'))) or b'{}')
  except:return {}
 def F(self,p):
  try:b=p.read_bytes()
  except:return self.send_error(404)
  self.send_response(200);self.send_header('Content-Type',mimetypes.guess_type(str(p))[0] or 'application/octet-stream');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
 def do_GET(self):
  u=urlparse(self.path);p=u.path
  if p=='/health':return self.J({'ok':True,'version':'split-1'})
  if p in ('/','/index.html'):return self.F(STATIC/'index.html')
  if p.startswith('/static/'):return self.F(STATIC/p[8:])
  if p.startswith('/api/qr/'):
   g=game(p[8:])
   if not g:return self.J({'error':'not_found'},404)
   base=f"{self.headers.get('X-Forwarded-Proto','https')}://{self.headers.get('Host')}";im=qrcode.make(f"{base}/?code={g['code']}");buf=io.BytesIO();im.save(buf,'PNG');b=buf.getvalue();self.send_response(200);self.send_header('Content-Type','image/png');self.send_header('Content-Length',str(len(b)));self.end_headers();return self.wfile.write(b)
  if p.startswith('/api/game/'):
   g=game(p.split('/api/game/',1)[1].split('/')[0])
   if not g:return self.J({'error':'not_found'},404)
   q=parse_qs(u.query);tok=q.get('token',[''])[0];host=q.get('host',[''])[0];players=ps(g['id'])
   with cn() as c:me=c.execute('SELECT * FROM players WHERE game_id=? AND token=?',(g['id'],tok)).fetchone() if tok else None;ev=c.execute('SELECT * FROM gm_events WHERE game_id=? ORDER BY id DESC LIMIT 1',(g['id'],)).fetchone()
   vs,total,correct=stats(g);k=next((x for x in players if x['id']==g['killer_player_id']),None)
   out={'code':g['code'],'group_name':g['group_name'],'location':g['location'],'status':g['status'],'round_no':g['round_no'],'story_title':g['story_title'],'round_prompt':prompt(g) if g['status']=='playing' else None,'remaining_seconds':left(g),'latest_gm_event':({'round_no':ev['round_no'],'response':ev['response']} if ev else None),'players':[{'id':x['id'],'name':x['name'],'role_name':x['role_name'] if g['status']=='finished' else None} for x in players],'is_host':bool(host and secrets.compare_digest(host,g['host_token'])),'me':None,'killer':({'id':k['id'],'name':k['name']} if g['status']=='finished' and k else None),'vote_summary':vs if g['status']=='finished' else [],'total_votes':total,'correct_votes':correct}
   if me:out['me']={'id':me['id'],'name':me['name'],'role_name':me['role_name'],'secret':me['secret'],'objective':me['objective'],'private_hint':me['private_hint'] if g['status']=='playing' and g['round_no']>=2 else ''}
   return self.J(out)
  return self.J({'error':'not_found'},404)
 def do_POST(self):
  p=urlparse(self.path).path;d=self.B()
  if p=='/api/create':
   co=code5();ht=secrets.token_urlsafe(18);pt=secrets.token_urlsafe(18);name=clean(d.get('name'),40) or 'Host'
   with cn() as c:cur=c.execute('INSERT INTO games(code,host_token,group_name,location,inside_joke,game_type,created_at) VALUES(?,?,?,?,?,?,?)',(co,ht,clean(d.get('group_name'),80) or 'The group',clean(d.get('location'),80) or 'the living room',clean(d.get('inside_joke')),clean(d.get('game_type'),20) or 'murder',now()));c.execute('INSERT INTO players(game_id,name,token,joined_at) VALUES(?,?,?,?)',(cur.lastrowid,name,pt,now()))
   return self.J({'code':co,'host':ht,'token':pt})
  if p=='/api/join':
   g=game(d.get('code'));name=clean(d.get('name'),40)
   if not g:return self.J({'error':'not_found'},404)
   if g['status']!='lobby':return self.J({'error':'already_started'},400)
   if not name:return self.J({'error':'name_required'},400)
   tok=secrets.token_urlsafe(18)
   with cn() as c:
    if c.execute('SELECT 1 FROM players WHERE game_id=? AND lower(name)=lower(?)',(g['id'],name)).fetchone():return self.J({'error':'name_taken'},400)
    c.execute('INSERT INTO players(game_id,name,token,joined_at) VALUES(?,?,?,?)',(g['id'],name,tok,now()))
   return self.J({'code':g['code'],'token':tok})
  a=p.strip('/').split('/')
  if len(a)!=4 or a[:2]!=['api','game']:return self.J({'error':'not_found'},404)
  g=game(a[2]);act=a[3]
  if not g:return self.J({'error':'not_found'},404)
  if act in ('start','next','react') and not(d.get('host') and secrets.compare_digest(str(d['host']),g['host_token'])):return self.J({'error':'forbidden'},403)
  if act=='start':
   try:assign(g)
   except ValueError:return self.J({'error':'need_2_players'},400)
   with cn() as c:c.execute("UPDATE games SET status='playing',round_no=1,round_started_at=?,round_seconds=600 WHERE id=?",(now(),g['id']))
   return self.J({'ok':True,'round_no':1,'status':'playing'})
  if act=='next':
   if g['status']!='playing':return self.J({'error':'not_playing'},409)
   rn=int(g['round_no'])+1
   with cn() as c:
    if rn>4:c.execute("UPDATE games SET status='finished',round_started_at='' WHERE id=?",(g['id'],))
    else:c.execute('UPDATE games SET round_no=?,round_started_at=?,round_seconds=600 WHERE id=?',(rn,now(),g['id']))
   return self.J({'ok':True,'round_no':min(rn,4),'status':'finished' if rn>4 else 'playing'})
  if act=='react':
   s=clean(d.get('summary'),500)
   if not s:return self.J({'error':'summary_required'},400)
   r=f'New clue: {s} Everyone must now restate one checkable part of their timeline.'
   with cn() as c:c.execute('INSERT INTO gm_events(game_id,round_no,response,created_at) VALUES(?,?,?,?)',(g['id'],g['round_no'],r,now()))
   return self.J({'ok':True,'response':r})
  if act=='vote':
   if g['status']!='playing' or int(g['round_no'])!=4:return self.J({'error':'voting_not_open'},409)
   with cn() as c:
    v=c.execute('SELECT * FROM players WHERE game_id=? AND token=?',(g['id'],d.get('token',''))).fetchone();x=c.execute('SELECT * FROM players WHERE game_id=? AND id=?',(g['id'],int(d.get('accused_id',0)))).fetchone()
    if not v or not x or v['id']==x['id']:return self.J({'error':'invalid_vote'},400)
    c.execute('INSERT OR REPLACE INTO votes(game_id,round_no,voter_player_id,accused_player_id,created_at) VALUES(?,?,?,?,?)',(g['id'],4,v['id'],x['id'],now()))
   return self.J({'ok':True})
  return self.J({'error':'not_found'},404)
 def log_message(self,*a):pass
def run():init();ThreadingHTTPServer(('0.0.0.0',int(os.getenv('PORT','5000'))),H).serve_forever()
