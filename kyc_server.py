import json,os,random,secrets,sqlite3,mimetypes
from datetime import datetime,timezone
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse,parse_qs
from kyc_questions import GENERAL,TOPICS,SPICY
BASE=Path(__file__).parent;DB=Path(os.getenv('DATABASE_PATH',BASE/'kyc.db'));STATIC=BASE/'static'
TOTAL=12
def now():return datetime.now(timezone.utc).isoformat()
def cn():c=sqlite3.connect(DB,timeout=20);c.row_factory=sqlite3.Row;return c
def init():
 DB.parent.mkdir(parents=True,exist_ok=True)
 with cn() as c:
  c.executescript("""CREATE TABLE IF NOT EXISTS games(id INTEGER PRIMARY KEY,code TEXT UNIQUE,host TEXT,status TEXT DEFAULT 'lobby',round_no INTEGER DEFAULT 0,answer TEXT DEFAULT '',memory TEXT DEFAULT '[]',topics TEXT DEFAULT '[]',custom_context TEXT DEFAULT '',spice INTEGER DEFAULT 1,created TEXT);CREATE TABLE IF NOT EXISTS players(id INTEGER PRIMARY KEY,game_id INTEGER,name TEXT,token TEXT UNIQUE,score INTEGER DEFAULT 0,joined TEXT);CREATE TABLE IF NOT EXISTS guesses(game_id INTEGER,round_no INTEGER,player_id INTEGER,guess TEXT,UNIQUE(game_id,round_no,player_id));""")
  cols={r['name'] for r in c.execute('PRAGMA table_info(games)')}
  for n,d in [('topics',"TEXT DEFAULT '[]'"),('custom_context',"TEXT DEFAULT ''"),('spice','INTEGER DEFAULT 1')]:
   if n not in cols:c.execute(f'ALTER TABLE games ADD COLUMN {n} {d}')
def game(code):
 with cn() as c:return c.execute('SELECT * FROM games WHERE code=?',(str(code or '').upper(),)).fetchone()
def players(gid):
 with cn() as c:return c.execute('SELECT * FROM players WHERE game_id=? ORDER BY id',(gid,)).fetchall()
def code5():
 chars='ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
 while True:
  x=''.join(random.choice(chars) for _ in range(5))
  if not game(x):return x
def mem(g):
 try:
  x=json.loads(g['memory'] or '[]');return x if isinstance(x,list) else []
 except:return []
def topics(g):
 try:t=json.loads(g['topics'] or '[]')
 except:t=[]
 txt=(g['custom_context'] or '').lower()
 hints={'גייז / LGBTQ+':['גיי','gay','להט','lgbt','הומו','queer'],'דייטים':['דייט','dating','טינדר','גריינדר','grindr','tinder'],'זוגיות':['זוג','relationship'],'חיי לילה':['מסיבה','ברים','nightlife','party'],'נסיעות':['טיול','חופשה','travel'],'אינטימיות למבוגרים':['מיניות','סקס','sex','אינטימ']}
 for tag,keys in hints.items():
  if any(k in txt for k in keys) and tag not in t:t.append(tag)
 return t
def pool(g):
 x=list(GENERAL)
 for t in topics(g):x+=TOPICS.get(t,[])
 if int(g['spice'] or 1)>=3:x+=SPICY
 return x
def qdata(g,ps):
 rn=int(g['round_no']);sub=ps[rn%len(ps)] if ps else None;m=mem(g)
 if rn in (6,10) and m:
  ev=m[-min(len(m),3)];old=ev.get('answer','משהו מפתיע');who=ev.get('subject','מישהו')
  text=f'PLOT TWIST: קודם {who} בחר/ה “{old}”. עכשיו זה מסתבך — מי בחבורה {sub["name"]} הכי ירצה/תרצה לידו/ה?'
  return 'callback',text,[p['name'] for p in ps if p['id']!=sub['id']],sub
 x=pool(g);q=x[(rn*3+len(topics(g))*2)%len(x)];typ,text,opts=q;text=text.format(s=sub['name'])
 if typ=='room':opts=[p['name'] for p in ps if p['id']!=sub['id']]
 return typ,text,list(opts),sub
class H(BaseHTTPRequestHandler):
 def J(self,x,s=200):
  b=json.dumps(x,ensure_ascii=False).encode();self.send_response(s);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
 def B(self):
  try:return json.loads(self.rfile.read(int(self.headers.get('Content-Length','0'))) or b'{}')
  except:return {}
 def F(self,p):
  try:b=p.read_bytes()
  except:return self.send_error(404)
  self.send_response(200);self.send_header('Content-Type',mimetypes.guess_type(str(p))[0] or 'text/plain');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
 def do_GET(self):
  u=urlparse(self.path);p=u.path
  if p=='/health':return self.J({'ok':True,'game':'know-your-crew-v2'})
  if p in ('/','/index.html'):return self.F(STATIC/'kyc.html')
  if p.startswith('/static/'):return self.F(STATIC/p[8:])
  if p.startswith('/api/state/'):
   g=game(p.split('/')[-1])
   if not g:return self.J({'error':'not_found'},404)
   ps=players(g['id']);q=parse_qs(u.query);tok=q.get('token',[''])[0];host=q.get('host',[''])[0];me=next((x for x in ps if x['token']==tok),None);typ,text,opts,sub=qdata(g,ps)
   with cn() as c:gs=c.execute('SELECT player_id,guess FROM guesses WHERE game_id=? AND round_no=?',(g['id'],g['round_no'])).fetchall()
   guessed={r['player_id']:r['guess'] for r in gs};need=max(0,len(ps)-1);ready=bool(g['answer']) and len(guessed)>=need;reveal=ready or g['status']=='finished'
   return self.J({'code':g['code'],'status':g['status'],'round':g['round_no'],'total':TOTAL,'is_host':bool(host and secrets.compare_digest(host,g['host'])),'me':{'id':me['id'],'name':me['name'],'score':me['score']} if me else None,'players':[{'id':x['id'],'name':x['name'],'score':x['score']} for x in ps],'subject':{'id':sub['id'],'name':sub['name']} if sub else None,'type':typ,'question':text,'options':opts,'answer':g['answer'] if reveal else None,'answered':bool(g['answer']),'guessed':bool(me and me['id'] in guessed),'guess_count':len(guessed),'guess_need':need,'reveal':reveal,'topics':topics(g),'spice':g['spice'],'context':g['custom_context']})
  return self.J({'error':'not_found'},404)
 def do_POST(self):
  p=urlparse(self.path).path;d=self.B()
  if p=='/api/create':
   name=str(d.get('name','')).strip()[:40]
   if not name:return self.J({'error':'name_required'},400)
   co=code5();ht=secrets.token_urlsafe(16);pt=secrets.token_urlsafe(16);ts=d.get('topics',[]);ts=ts if isinstance(ts,list) else [];ctx=str(d.get('context','')).strip()[:700];sp=max(1,min(3,int(d.get('spice',1) or 1)))
   with cn() as c:cur=c.execute('INSERT INTO games(code,host,topics,custom_context,spice,created) VALUES(?,?,?,?,?,?)',(co,ht,json.dumps(ts,ensure_ascii=False),ctx,sp,now()));c.execute('INSERT INTO players(game_id,name,token,joined) VALUES(?,?,?,?)',(cur.lastrowid,name,pt,now()))
   return self.J({'code':co,'host':ht,'token':pt,'name':name})
  if p=='/api/join':
   g=game(d.get('code'));name=str(d.get('name','')).strip()[:40]
   if not g:return self.J({'error':'not_found'},404)
   if g['status']!='lobby':return self.J({'error':'started'},409)
   if not name:return self.J({'error':'name_required'},400)
   if len(players(g['id']))>=6:return self.J({'error':'full'},409)
   tok=secrets.token_urlsafe(16)
   with cn() as c:c.execute('INSERT INTO players(game_id,name,token,joined) VALUES(?,?,?,?)',(g['id'],name,tok,now()))
   return self.J({'code':g['code'],'token':tok,'name':name})
  a=p.strip('/').split('/')
  if len(a)!=3 or a[0]!='api':return self.J({'error':'not_found'},404)
  g=game(a[1]);act=a[2]
  if not g:return self.J({'error':'not_found'},404)
  ps=players(g['id']);typ,text,opts,sub=qdata(g,ps)
  if act in ('start','next') and not(d.get('host') and secrets.compare_digest(str(d['host']),g['host'])):return self.J({'error':'forbidden'},403)
  if act=='start':
   if len(ps)<3:return self.J({'error':'need_3'},409)
   with cn() as c:c.execute("UPDATE games SET status='playing',round_no=0,answer='',memory='[]' WHERE id=?",(g['id'],));c.execute('DELETE FROM guesses WHERE game_id=?',(g['id'],))
   return self.J({'ok':True})
  if act=='answer':
   me=next((x for x in ps if x['token']==d.get('token')),None);ans=str(d.get('answer',''))[:120]
   if not me or not sub or me['id']!=sub['id']:return self.J({'error':'subject_only'},403)
   if ans not in opts:return self.J({'error':'invalid_answer'},400)
   with cn() as c:c.execute('UPDATE games SET answer=? WHERE id=?',(ans,g['id']))
   return self.J({'ok':True})
  if act=='guess':
   me=next((x for x in ps if x['token']==d.get('token')),None);guess=str(d.get('guess',''))[:120]
   if not me or not sub or me['id']==sub['id']:return self.J({'error':'invalid_player'},403)
   if guess not in opts:return self.J({'error':'invalid_guess'},400)
   with cn() as c:c.execute('INSERT OR REPLACE INTO guesses(game_id,round_no,player_id,guess) VALUES(?,?,?,?)',(g['id'],g['round_no'],me['id'],guess))
   return self.J({'ok':True})
  if act=='next':
   with cn() as c:
    gs=c.execute('SELECT player_id,guess FROM guesses WHERE game_id=? AND round_no=?',(g['id'],g['round_no'])).fetchall()
    if not g['answer'] or len(gs)<len(ps)-1:return self.J({'error':'not_ready'},409)
    for r in gs:
     if r['guess']==g['answer']:c.execute('UPDATE players SET score=score+1 WHERE id=?',(r['player_id'],))
    mm=mem(g);mm.append({'round':g['round_no'],'subject':sub['name'],'question':text,'answer':g['answer'],'type':typ})
    rn=int(g['round_no'])+1
    if rn>=TOTAL:c.execute("UPDATE games SET status='finished',memory=? WHERE id=?",(json.dumps(mm,ensure_ascii=False),g['id']))
    else:c.execute("UPDATE games SET round_no=?,answer='',memory=? WHERE id=?",(rn,json.dumps(mm,ensure_ascii=False),g['id']))
   return self.J({'ok':True})
  return self.J({'error':'not_found'},404)
 def log_message(self,*a):pass
def run():init();ThreadingHTTPServer(('0.0.0.0',int(os.getenv('PORT','5000'))),H).serve_forever()
