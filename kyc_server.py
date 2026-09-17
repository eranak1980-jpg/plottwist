import json,os,random,secrets,sqlite3,mimetypes
from datetime import datetime,timezone
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse,parse_qs
BASE=Path(__file__).parent; DB=Path(os.getenv('DATABASE_PATH',BASE/'kyc.db')); STATIC=BASE/'static'
QUESTIONS=[
('know','{s} מקבל/ת עכשיו 100,000 ₪ שחייבים לבזבז ב־24 שעות. לאן רוב הכסף הולך?',['טיסה וחופשה מטורפת','קניות ופינוקים','מתנות לאנשים קרובים','חוויה חד־פעמית']),
('know','אם {s} יכול/ה למחוק מחר התחייבות אחת מהחיים — מה נעלם?',['עבודה','סידורים ובירוקרטיה','דאגות כסף','מחויבויות חברתיות']),
('room','עם מי מהחבורה {s} היה/תה בוחר/ת להיות חודש על אי בודד?',[]),
('know','{s} מקבל/ת שבוע חופש בהפתעה. מה הכי סביר שיקרה?',['טיסה ברגע האחרון','שבוע של בית ומנוחה','טיול בארץ','תכנון פרויקט חדש']),
('room','למי בחבורה {s} היה/תה מתקשר/ת ראשון אם הסתבך/ה ב־3 בלילה?',[]),
('know','אם {s} נהיה/ת מפורסם/ת מחר — בגלל מה זה יקרה?',['עסק מצליח','ריאליטי','סרטון ויראלי','כישרון שאף אחד לא ציפה לו']),
('callback','לפני כמה סיבובים למדנו ש־{s} בחר/ה: “{m}”. עכשיו זה קורה באמת — מי בחבורה הכי סביר שיצטרף/תצטרף אליו/ה?',[]),
('room','עם מי מהחבורה {s} היה/תה מוכן/ה לפתוח עסק ולחלוק 50% מהחברה?',[]),
('know','אם {s} חייב/ת לגור שנה במדינה אחרת החל ממחר — מה הוא/היא בוחר/ת?',['תאילנד','ארה״ב','יוון / קפריסין','מדינה אירופית גדולה']),
('predict','מי בחבורה יקבל הכי הרבה קולות לשאלה: מי הכי בלתי צפוי?',[]),
('callback','PlotTwist: קודם {s} בחר/ה “{m}”. עכשיו הכול השתבש. מי בחבורה הוא/היא הכי ירצה/תרצה לידו/ה?',[]),
('know','אם הערב הזה הופך לסרט על החבורה — איזה תפקיד {s} מקבל/ת?',['הגיבור/ה','הכאוס','המוח מאחורי הכול','זה שמפתיע בסוף'])]
def now():return datetime.now(timezone.utc).isoformat()
def cn():c=sqlite3.connect(DB,timeout=20);c.row_factory=sqlite3.Row;return c
def init():
 DB.parent.mkdir(parents=True,exist_ok=True)
 with cn() as c:c.executescript("""CREATE TABLE IF NOT EXISTS games(id INTEGER PRIMARY KEY,code TEXT UNIQUE,host TEXT,status TEXT DEFAULT 'lobby',round_no INTEGER DEFAULT 0,answer TEXT DEFAULT '',memory TEXT DEFAULT '{}',created TEXT);CREATE TABLE IF NOT EXISTS players(id INTEGER PRIMARY KEY,game_id INTEGER,name TEXT,token TEXT UNIQUE,score INTEGER DEFAULT 0,joined TEXT);CREATE TABLE IF NOT EXISTS guesses(game_id INTEGER,round_no INTEGER,player_id INTEGER,guess TEXT,UNIQUE(game_id,round_no,player_id));""")
def game(code):
 with cn() as c:return c.execute('SELECT * FROM games WHERE code=?',(str(code or '').upper(),)).fetchone()
def players(gid):
 with cn() as c:return c.execute('SELECT * FROM players WHERE game_id=? ORDER BY id',(gid,)).fetchall()
def code5():
 chars='ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
 while True:
  x=''.join(random.choice(chars) for _ in range(5))
  if not game(x):return x
def qdata(g,ps):
 rn=int(g['round_no']);typ,text,opts=QUESTIONS[rn%len(QUESTIONS)];sub=ps[rn%len(ps)] if ps else None;mem=json.loads(g['memory'] or '{}');m=mem.get(str(sub['id']),'משהו מפתיע') if sub else 'משהו מפתיע';text=text.format(s=sub['name'] if sub else 'השחקן',m=m)
 if typ in ('room','predict','callback'):opts=[p['name'] for p in ps if not sub or p['id']!=sub['id']]
 return typ,text,opts,sub
class H(BaseHTTPRequestHandler):
 def J(self,x,s=200):
  b=json.dumps(x,ensure_ascii=False).encode();self.send_response(s);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
 def B(self):
  try:return json.loads(self.rfile.read(int(self.headers.get('Content-Length','0'))) or b'{}')
  except:return {}
 def F(self,p):
  try:b=p.read_bytes()
  except:return self.send_error(404)
  self.send_response(200);self.send_header('Content-Type',mimetypes.guess_type(str(p))[0] or 'text/plain');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
 def do_GET(self):
  u=urlparse(self.path);p=u.path
  if p=='/health':return self.J({'ok':True,'game':'know-your-crew'})
  if p in ('/','/index.html'):return self.F(STATIC/'kyc.html')
  if p.startswith('/static/'):return self.F(STATIC/p[8:])
  if p.startswith('/api/state/'):
   g=game(p.split('/')[-1])
   if not g:return self.J({'error':'not_found'},404)
   ps=players(g['id']);q=parse_qs(u.query);tok=q.get('token',[''])[0];host=q.get('host',[''])[0];me=next((x for x in ps if x['token']==tok),None);typ,text,opts,sub=qdata(g,ps)
   with cn() as c:gs=c.execute('SELECT player_id,guess FROM guesses WHERE game_id=? AND round_no=?',(g['id'],g['round_no'])).fetchall()
   guessed={r['player_id']:r['guess'] for r in gs};need=max(0,len(ps)-1);ready=bool(g['answer']) and len(guessed)>=need;reveal=ready or g['status']=='finished'
   return self.J({'code':g['code'],'status':g['status'],'round':g['round_no'],'total':len(QUESTIONS),'is_host':bool(host and secrets.compare_digest(host,g['host'])),'me':{'id':me['id'],'name':me['name'],'score':me['score']} if me else None,'players':[{'id':x['id'],'name':x['name'],'score':x['score']} for x in ps],'subject':{'id':sub['id'],'name':sub['name']} if sub else None,'type':typ,'question':text,'options':opts,'answer':g['answer'] if reveal else None,'answered':bool(g['answer']),'guessed':bool(me and me['id'] in guessed),'guess_count':len(guessed),'guess_need':need,'reveal':reveal})
  return self.J({'error':'not_found'},404)
 def do_POST(self):
  p=urlparse(self.path).path;d=self.B()
  if p=='/api/create':
   name=str(d.get('name','')).strip()[:40]
   if not name:return self.J({'error':'name_required'},400)
   co=code5();ht=secrets.token_urlsafe(16);pt=secrets.token_urlsafe(16)
   with cn() as c:cur=c.execute('INSERT INTO games(code,host,created) VALUES(?,?,?)',(co,ht,now()));c.execute('INSERT INTO players(game_id,name,token,joined) VALUES(?,?,?,?)',(cur.lastrowid,name,pt,now()))
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
   with cn() as c:c.execute("UPDATE games SET status='playing',round_no=0,answer='',memory='{}' WHERE id=?",(g['id'],));c.execute('DELETE FROM guesses WHERE game_id=?',(g['id'],))
   return self.J({'ok':True})
  if act=='answer':
   me=next((x for x in ps if x['token']==d.get('token')),None);ans=str(d.get('answer',''))[:120]
   if not me or not sub or me['id']!=sub['id']:return self.J({'error':'subject_only'},403)
   if ans not in opts:return self.J({'error':'invalid_answer'},400)
   mem=json.loads(g['memory'] or '{}');mem[str(me['id'])]=ans
   with cn() as c:c.execute('UPDATE games SET answer=?,memory=? WHERE id=?',(ans,json.dumps(mem,ensure_ascii=False),g['id']))
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
    rn=int(g['round_no'])+1
    if rn>=len(QUESTIONS):c.execute("UPDATE games SET status='finished' WHERE id=?",(g['id'],))
    else:c.execute("UPDATE games SET round_no=?,answer='' WHERE id=?",(rn,g['id']))
   return self.J({'ok':True})
  return self.J({'error':'not_found'},404)
 def log_message(self,*a):pass
def run():init();ThreadingHTTPServer(('0.0.0.0',int(os.getenv('PORT','5000'))),H).serve_forever()
