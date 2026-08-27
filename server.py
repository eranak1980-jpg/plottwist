import io,json,mimetypes,os,random,secrets,sqlite3
from datetime import datetime,timezone
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs,urlparse
import qrcode
from server_v2 import ensure_v2,start_case,state_v2,advance_v2,save_photo,next_turn
BASE=Path(__file__).parent;DB=Path(os.getenv('DATABASE_PATH',BASE/'party_game.db'));STATIC=BASE/'static'
def now():return datetime.now(timezone.utc).isoformat()
def cn():c=sqlite3.connect(DB,timeout=10);c.row_factory=sqlite3.Row;return c
def init():
 DB.parent.mkdir(parents=True,exist_ok=True)
 with cn() as c:c.executescript("""CREATE TABLE IF NOT EXISTS games(id INTEGER PRIMARY KEY,code TEXT UNIQUE,host_token TEXT,status TEXT DEFAULT 'lobby',round_no INTEGER DEFAULT 0,killer_player_id INTEGER,group_name TEXT DEFAULT '',location TEXT DEFAULT '',inside_joke TEXT DEFAULT '',game_type TEXT DEFAULT 'murder',story_title TEXT DEFAULT '',victim_name TEXT DEFAULT '',round_started_at TEXT DEFAULT '',round_seconds INTEGER DEFAULT 600,created_at TEXT);CREATE TABLE IF NOT EXISTS players(id INTEGER PRIMARY KEY,game_id INTEGER,name TEXT,token TEXT UNIQUE,role_name TEXT DEFAULT '',secret TEXT DEFAULT '',objective TEXT DEFAULT '',private_hint TEXT DEFAULT '',joined_at TEXT);CREATE TABLE IF NOT EXISTS votes(id INTEGER PRIMARY KEY,game_id INTEGER,round_no INTEGER,voter_player_id INTEGER,accused_player_id INTEGER,created_at TEXT,UNIQUE(game_id,round_no,voter_player_id));""")
 ensure_v2()
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
 def auth(self,g,d):return bool(d.get('host') and secrets.compare_digest(str(d['host']),g['host_token']))
 def do_GET(self):
  u=urlparse(self.path);p=u.path
  if p=='/health':return self.J({'ok':True,'version':'plottwist-2-recovery'})
  if p in ('/','/index.html'):return self.F(STATIC/'index.html')
  if p.startswith('/static/'):return self.F(STATIC/p[8:])
  if p.startswith('/api/qr/'):
   g=game(p[8:]);
   if not g:return self.J({'error':'not_found'},404)
   base=f"{self.headers.get('X-Forwarded-Proto','https')}://{self.headers.get('Host')}";im=qrcode.make(f"{base}/?code={g['code']}");buf=io.BytesIO();im.save(buf,'PNG');b=buf.getvalue();self.send_response(200);self.send_header('Content-Type','image/png');self.send_header('Content-Length',str(len(b)));self.end_headers();return self.wfile.write(b)
  if p.startswith('/api/v2/game/'):
   g=game(p.split('/api/v2/game/',1)[1].split('/')[0]);
   if not g:return self.J({'error':'not_found'},404)
   q=parse_qs(u.query);out=state_v2(g['id'],q.get('token',[''])[0]);out['code']=g['code'];out['is_host']=bool(q.get('host',[''])[0] and secrets.compare_digest(q.get('host',[''])[0],g['host_token']));return self.J(out)
  return self.J({'error':'not_found'},404)
 def do_POST(self):
  p=urlparse(self.path).path;d=self.B()
  if p=='/api/create':
   co=code5();ht=secrets.token_urlsafe(18);pt=secrets.token_urlsafe(18);name=clean(d.get('name'),40) or 'Host'
   with cn() as c:cur=c.execute('INSERT INTO games(code,host_token,group_name,location,inside_joke,game_type,created_at) VALUES(?,?,?,?,?,?,?)',(co,ht,clean(d.get('group_name'),80) or 'The group',clean(d.get('location'),80) or 'the living room',clean(d.get('inside_joke')),clean(d.get('game_type'),20) or 'murder',now()));c.execute('INSERT INTO players(game_id,name,token,joined_at) VALUES(?,?,?,?)',(cur.lastrowid,name,pt,now()))
   return self.J({'code':co,'host':ht,'token':pt,'name':name})
  if p=='/api/join':
   g=game(d.get('code'));name=clean(d.get('name'),40)
   if not g:return self.J({'error':'not_found'},404)
   if not name:return self.J({'error':'name_required'},400)
   # Recovery: the same named player may reclaim their token even after the story starts.
   with cn() as c:existing=c.execute('SELECT * FROM players WHERE game_id=? AND lower(name)=lower(?)',(g['id'],name)).fetchone()
   if existing:return self.J({'code':g['code'],'token':existing['token'],'name':existing['name'],'recovered':True})
   if g['status']!='lobby':return self.J({'error':'game_already_started_use_your_original_name'},400)
   if len(ps(g['id']))>=10:return self.J({'error':'room_full'},400)
   tok=secrets.token_urlsafe(18)
   with cn() as c:c.execute('INSERT INTO players(game_id,name,token,joined_at) VALUES(?,?,?,?)',(g['id'],name,tok,now()))
   return self.J({'code':g['code'],'token':tok,'name':name})
  a=p.strip('/').split('/')
  if len(a)==5 and a[:3]==['api','v2','game']:
   g=game(a[3]);act=a[4]
   if not g:return self.J({'error':'not_found'},404)
   try:
    if act=='photo':return self.J(save_photo(g['id'],d.get('token',''),d.get('data_url',''),bool(d.get('consent'))))
    if act=='start':
     if not self.auth(g,d):return self.J({'error':'forbidden'},403)
     start_case(g['id']);return self.J({'ok':True})
    if act=='turn':
     if not self.auth(g,d):return self.J({'error':'forbidden'},403)
     return self.J(next_turn(g['id']))
    if act=='advance':
     if not self.auth(g,d):return self.J({'error':'forbidden'},403)
     return self.J(advance_v2(g['id']))
   except ValueError as e:return self.J({'error':str(e)},400)
  if len(a)==4 and a[:2]==['api','game'] and a[3]=='vote':
   g=game(a[2]);
   if not g:return self.J({'error':'not_found'},404)
   if g['status']!='playing' or int(g['round_no'])!=4:return self.J({'error':'voting_not_open'},409)
   with cn() as c:
    v=c.execute('SELECT * FROM players WHERE game_id=? AND token=?',(g['id'],d.get('token',''))).fetchone();x=c.execute('SELECT * FROM players WHERE game_id=? AND id=?',(g['id'],int(d.get('accused_id',0)))).fetchone()
    if not v or not x or v['id']==x['id']:return self.J({'error':'invalid_vote'},400)
    c.execute('INSERT OR REPLACE INTO votes(game_id,round_no,voter_player_id,accused_player_id,created_at) VALUES(?,?,?,?,?)',(g['id'],4,v['id'],x['id'],now()))
   return self.J({'ok':True})
  return self.J({'error':'not_found'},404)
 def log_message(self,*a):pass
def run():init();ThreadingHTTPServer(('0.0.0.0',int(os.getenv('PORT','5000'))),H).serve_forever()
