import json,os,random,secrets,sqlite3,mimetypes
from threading import Thread
from datetime import datetime,timezone
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse,parse_qs
from kyc_questions import GENERAL,TOPICS,SPICY
from kyc_visuals import generate_many
from kyc_ai import generate_pack
BASE=Path(__file__).parent;DB=Path(os.getenv('DATABASE_PATH',BASE/'kyc.db'));DATABASE_URL=os.getenv('DATABASE_URL','').strip();USE_PG=DATABASE_URL.startswith(('postgres://','postgresql://'));STATIC=BASE/'static';TOTAL=12
def now():return datetime.now(timezone.utc).isoformat()
class CompatConn:
 def __init__(self,raw,pg=False):self.raw=raw;self.pg=pg
 def __enter__(self):self.raw.__enter__();return self
 def __exit__(self,*a):return self.raw.__exit__(*a)
 def execute(self,sql,params=()):
  if self.pg:
   if sql.startswith('INSERT OR REPLACE INTO guesses'):
    sql='INSERT INTO guesses(game_id,round_no,player_id,guess) VALUES(%s,%s,%s,%s) ON CONFLICT(game_id,round_no,player_id) DO UPDATE SET guess=EXCLUDED.guess'
   elif sql.startswith('INSERT OR REPLACE INTO hero_scenes'):
    sql='INSERT INTO hero_scenes(game_id,round_no,image_data,created) VALUES(%s,%s,%s,%s) ON CONFLICT(game_id,round_no) DO UPDATE SET image_data=EXCLUDED.image_data,created=EXCLUDED.created'
   else:sql=sql.replace('?','%s')
  return self.raw.execute(sql,params)
def cn():
 if USE_PG:
  import psycopg
  from psycopg.rows import dict_row
  return CompatConn(psycopg.connect(DATABASE_URL,row_factory=dict_row,connect_timeout=10),True)
 c=sqlite3.connect(DB,timeout=30);c.row_factory=sqlite3.Row;c.execute('PRAGMA busy_timeout=30000');return CompatConn(c,False)
def init():
 if USE_PG:
  with cn() as c:
   c.execute("""CREATE TABLE IF NOT EXISTS games(id BIGSERIAL PRIMARY KEY,code TEXT UNIQUE,host TEXT,status TEXT DEFAULT 'lobby',round_no INTEGER DEFAULT 0,answer TEXT DEFAULT '',memory TEXT DEFAULT '[]',topics TEXT DEFAULT '[]',custom_context TEXT DEFAULT '',spice INTEGER DEFAULT 1,custom_questions TEXT DEFAULT '[]',prize TEXT DEFAULT '',rounds INTEGER DEFAULT 12,created TEXT)""")
   c.execute("""CREATE TABLE IF NOT EXISTS players(id BIGSERIAL PRIMARY KEY,game_id BIGINT,name TEXT,token TEXT UNIQUE,score INTEGER DEFAULT 0,joined TEXT,photo_data TEXT DEFAULT '',photo_consent INTEGER DEFAULT 0)""")
   c.execute("""CREATE TABLE IF NOT EXISTS guesses(game_id BIGINT,round_no INTEGER,player_id BIGINT,guess TEXT,UNIQUE(game_id,round_no,player_id))""")
   c.execute("""CREATE TABLE IF NOT EXISTS hero_scenes(game_id BIGINT,round_no INTEGER,image_data TEXT,created TEXT,UNIQUE(game_id,round_no))""")
   c.execute("""CREATE TABLE IF NOT EXISTS round_scores(game_id BIGINT,round_no INTEGER,created TEXT,UNIQUE(game_id,round_no))""")
   c.execute("""CREATE TABLE IF NOT EXISTS topic_votes(game_id BIGINT,player_id BIGINT,topic TEXT,UNIQUE(game_id,player_id,topic))""")
  return
 DB.parent.mkdir(parents=True,exist_ok=True)
 with cn() as c:
  c.raw.executescript("""CREATE TABLE IF NOT EXISTS games(id INTEGER PRIMARY KEY,code TEXT UNIQUE,host TEXT,status TEXT DEFAULT 'lobby',round_no INTEGER DEFAULT 0,answer TEXT DEFAULT '',memory TEXT DEFAULT '[]',topics TEXT DEFAULT '[]',custom_context TEXT DEFAULT '',spice INTEGER DEFAULT 1,custom_questions TEXT DEFAULT '[]',prize TEXT DEFAULT '',rounds INTEGER DEFAULT 12,created TEXT);CREATE TABLE IF NOT EXISTS players(id INTEGER PRIMARY KEY,game_id INTEGER,name TEXT,token TEXT UNIQUE,score INTEGER DEFAULT 0,joined TEXT);CREATE TABLE IF NOT EXISTS guesses(game_id INTEGER,round_no INTEGER,player_id INTEGER,guess TEXT,UNIQUE(game_id,round_no,player_id));CREATE TABLE IF NOT EXISTS hero_scenes(game_id INTEGER,round_no INTEGER,image_data TEXT,created TEXT,UNIQUE(game_id,round_no));CREATE TABLE IF NOT EXISTS round_scores(game_id INTEGER,round_no INTEGER,created TEXT,UNIQUE(game_id,round_no));CREATE TABLE IF NOT EXISTS topic_votes(game_id INTEGER,player_id INTEGER,topic TEXT,UNIQUE(game_id,player_id,topic));""")
  gc={r['name'] for r in c.execute('PRAGMA table_info(games)')}
  for n,d in [('topics',"TEXT DEFAULT '[]'"),('custom_context',"TEXT DEFAULT ''"),('spice','INTEGER DEFAULT 1'),('custom_questions',"TEXT DEFAULT '[]'"),('prize',"TEXT DEFAULT ''"),('rounds','INTEGER DEFAULT 12')]:
   if n not in gc:c.execute(f'ALTER TABLE games ADD COLUMN {n} {d}')
  pc={r['name'] for r in c.execute('PRAGMA table_info(players)')}
  for n,d in [('photo_data',"TEXT DEFAULT ''"),('photo_consent','INTEGER DEFAULT 0')]:
   if n not in pc:c.execute(f'ALTER TABLE players ADD COLUMN {n} {d}')
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
 txt=(g['custom_context'] or '').lower();h={'גייז / LGBTQ+':['גיי','gay','להט','lgbt','הומו','queer'],'דייטים':['דייט','dating','טינדר','גריינדר','grindr','tinder'],'זוגיות':['זוג','relationship'],'חיי לילה':['מסיבה','ברים','nightlife','party'],'נסיעות':['טיול','חופשה','travel'],'אינטימיות למבוגרים':['מיניות','סקס','sex','אינטימ']}
 for tag,keys in h.items():
  if any(k in txt for k in keys) and tag not in t:t.append(tag)
 return t
def topic_vote_data(g):
 with cn() as c:rows=c.execute('SELECT topic,COUNT(*) AS n FROM topic_votes WHERE game_id=? GROUP BY topic ORDER BY n DESC,topic',(g['id'],)).fetchall()
 return {r['topic']:r['n'] for r in rows}
def effective_topics(g):
 base=topics(g);votes=topic_vote_data(g)
 for t,n in sorted(votes.items(),key=lambda x:(-x[1],x[0])):
  if t not in base:base.append(t)
 return base[:10]
def player_topic_votes(gid,pid):
 if not pid:return []
 with cn() as c:return [r['topic'] for r in c.execute('SELECT topic FROM topic_votes WHERE game_id=? AND player_id=?',(gid,pid)).fetchall()]
def custom_questions(g):
 try:
  raw=json.loads(g['custom_questions'] or '[]')
  return [(x[0],x[1],x[2]) for x in raw if isinstance(x,list) and len(x)==3]
 except:return []
def pool(g):
 x=custom_questions(g)
 for t in effective_topics(g):x+=TOPICS.get(t,[])
 if int(g['spice'] or 1)>=3:x+=SPICY
 x+=GENERAL
 return x
def total_rounds(g):
 try:return max(6,min(30,int(g['rounds'] or 12)))
 except:return 12
def smart_callback(g,ps,rn):
 m=[e for e in mem(g) if e.get('answer') and e.get('answer')!='SKIPPED'];total=total_rounds(g);marks=sorted(set([max(4,total//3),max(6,(total*2)//3),max(7,total-2)]))
 if rn not in marks or len(m)<3:return None
 names=[p['name'] for p in ps]
 room=[e for e in m if e.get('answer') in names and e.get('answer')!=e.get('subject')]
 if room:
  e=room[-1];sub=next((p for p in ps if p['name']==e.get('subject')),None);friend=e.get('answer');q=(e.get('question') or '').lower()
  if sub:
   if any(k in q for k in ['טיול','חופשה','אי בודד','טיסה','מדינה']):
    text=f'⚡ PLOT TWIST: {sub["name"]} כבר בחר/ה ב־{friend} כשותף/ה להרפתקה. הטיסה יוצאת בעוד שעתיים ואין שום תוכנית. מה {sub["name"]} חושב/ת ש־{friend} יעשה/תעשה ראשון?'
    opts=['אומר/ת “יאללה, מזמינים”','פותח/ת מיד מפות ומלונות','נלחץ/ת ומתחיל/ה לשאול שאלות','דואג/ת קודם לדרינק ואז נראה']
   elif any(k in q for k in ['דייט','גריינדר','היכרויות','crush']):
    text=f'⚡ PLOT TWIST: קודם {sub["name"]} בחר/ה ב־{friend}. עכשיו מגיע דייט שנראה כמו צרות מהשנייה הראשונה. איזו עצה {sub["name"]} חושב/ת ש־{friend} ייתן/תיתן?'
    opts=['לך/י על זה — חיים פעם אחת','תברח/י עכשיו','תן/י לזה דרינק אחד','שלח/י לי לייב מה קורה']
   elif any(k in q for k in ['עסק','50%','כסף','תקציב']):
    text=f'⚡ PLOT TWIST: {sub["name"]} כבר שם/ה את האמון ב־{friend}. עכשיו נוחתים עליכם 50,000 ₪ שחייבים להוציא יחד עד חצות. על מה {sub["name"]} חושב/ת ש־{friend} ישרוף/תשרוף אותם?'
    opts=['טיסה ברגע האחרון','מסיבה מוגזמת','משהו יוקרתי ומיותר','חוויה לכל החבורה']
   else:
    text=f'⚡ PLOT TWIST: קודם {sub["name"]} בחר/ה ב־{friend}. עכשיו שניהם תקועים יחד בסיטואציה שלא תכננו. מי {sub["name"]} חושב/ת שייקח/תיקח פיקוד ראשון?'
    opts=[sub['name'],friend]
   return 'callback',text,opts,sub
 e=m[-2];sub=next((p for p in ps if p['name']==e.get('subject')),None)
 if sub:
  old=e.get('answer')
  text=f'⚡ PLOT TWIST: קודם {sub["name"]} בחר/ה “{old}”. עכשיו הבחירה הזאת חוזרת אליו/ה בזמן הכי לא מתאים. מה {sub["name"]} יעשה/תעשה?'
  return 'callback',text,['זורם/ת עד הסוף','מתחרט/ת ברגע האחרון','גורר/ת חבר איתו/ה','מאלתר/ת משהו אחר'],sub
 return None
def interactive_prompt(g,typ,text,answer,sub):
 if not str(typ).startswith('callback') or not sub:return ''
 names={p['name'] for p in players(g['id'])}
 prior=next((e for e in reversed(mem(g)) if e.get('subject')==sub['name'] and e.get('answer') in names and e.get('answer')!=sub['name']),None)
 partner=prior.get('answer') if prior else ''
 if not partner:return ''
 q=(text or '').lower()
 if any(k in q for k in ['טיול','טיסה','הרפתקה','חופשה']):
  return f'⚡ עכשיו באמת: {sub["name"]} ו־{partner} — יש לכם 20 שניות להסכים על יעד אחד שהייתם טסים אליו מחר. בלי לפתוח גוגל.'
 if 'דייט' in q:
  return f'😈 עכשיו באמת: {sub["name"]} ו־{partner} — 15 שניות להמציא יחד את הודעת הפתיחה הכי גרועה שאפשר לשלוח בדייטינג.'
 if any(k in q for k in ['50,000','כסף']):
  return f'💸 עכשיו באמת: {sub["name"]} ו־{partner} — 20 שניות להסכים על דבר אחד שהייתם מבזבזים עליו את הכסף.'
 return ''
def duo_callback(g,ps,rn):
 m=[e for e in mem(g) if e.get('answer') and e.get('answer')!='SKIPPED']
 if len(ps)!=2 or rn<4 or rn not in (4,6,9,12,15) or len(m)<3:return None
 sub=ps[rn%2];mine=[e for e in reversed(m) if e.get('subject')==sub['name']]
 if not mine:return None
 used={e.get('question','') for e in m}
 variants=[
  ('⚡ PLOT TWIST: קודם {name} בחר/ה “{old}”. מחר הבחירה הזאת הופכת למציאות בלי אפשרות לבטל. מה הכי סביר ש־{name} יעשה/תעשה ראשון?',['זורם/ת מיד','מחפש/ת דרך לשדרג','נלחץ/ת אבל ממשיך/ה','מנסה לצרף מישהו']),
  ('⚡ PLOT TWIST: זוכרים ש־{name} בחר/ה “{old}”? עכשיו זה קורה באמת — אבל יש טוויסט: צריך להחליט תוך 30 שניות. מה {name} עושה?',['אומר/ת כן לפני שחושב/ת','מבקש/ת עוד פרטים','משנה את הבחירה','הולך/ת על משהו אפילו יותר קיצוני']),
  ('⚡ PLOT TWIST: הבחירה של {name} — “{old}” — חזרה אליו/ה כבומרנג. מה החלק שהכי סביר שיגרום לו/לה להגיד “רגע, לא לזה התכוונתי”?',['המחיר','הספונטניות','מי שמצטרף','זה שזה באמת קורה']),
  ('⚡ PLOT TWIST: קודם “{old}” נשמע ל־{name} כמו רעיון טוב. עכשיו כל החבורה אומרת: יאללה, עושים את זה. מה התגובה?',['אני בפנים','רגע, צחקתי','רק אם משנים פרט אחד','מעלה את הרף עוד יותר'])
 ]
 seed=(rn+sum(ord(x) for x in str(g['code'])))%len(variants)
 for off in range(len(variants)):
  template,opts=variants[(seed+off)%len(variants)];text=template.format(name=sub['name'],old=mine[0].get('answer'))
  if text not in used:return 'duo_callback',text,opts,sub
 return None
def qdata(g,ps):
 rn=int(g['round_no']);sub=ps[rn%len(ps)] if ps else None
 if len(ps)==2:
  cb=duo_callback(g,ps,rn)
  if cb:return cb
 else:
  cb=smart_callback(g,ps,rn)
  if cb:return cb
 focused=[]
 for t in effective_topics(g):focused+=TOPICS.get(t,[])
 if int(g['spice'] or 1)>=3:focused+=SPICY
 tailored=custom_questions(g);base=tailored+focused+GENERAL if (tailored or focused) else GENERAL
 if len(ps)==2:
  base=[q for q in base if q[0]!='room' and len(q[2])>=3]
  if not base:base=[q for q in GENERAL if q[0]=='know']
 used={e.get('question','') for e in mem(g)}
 seed=sum(ord(ch) for ch in str(g['code']))+rn*7
 chosen=None
 for step in range(len(base)):
  q=base[(seed+step)%len(base)];typ,text,opts=q;formatted=text.format(s=sub['name'])
  if formatted not in used:chosen=(typ,formatted,opts);break
 if chosen is None:
  fallback=[q for q in GENERAL if not (len(ps)==2 and q[0]=='room')]
  for q in fallback:
   typ,text,opts=q;formatted=text.format(s=sub['name'])
   if formatted not in used:chosen=(typ,formatted,opts);break
 if chosen is None:
  # Last-resort variant keeps gameplay moving without repeating the exact prompt.
  typ='know';formatted=f'מה הכי יפתיע את מי שחושב שהוא מכיר את {sub["name"]} טוב?';opts=['בחירה ספונטנית','בחירה בטוחה','משהו שאף אחד לא מצפה לו','תלוי במצב']
 else:typ,formatted,opts=chosen
 if typ=='room':opts=[p['name'] for p in ps if p['id']!=sub['id']]
 elif typ=='know' and int(g['spice'] or 1)>=3 and '✏️ משהו אחר' not in opts:opts=list(opts)+['✏️ משהו אחר']
 return typ,formatted,list(opts),sub
def _clean_pack(pack):
 clean=[];seen=set()
 for q in pack or []:
  if not isinstance(q,(list,tuple)) or len(q)!=3:continue
  key=str(q[1]).strip().lower()
  if key and key not in seen:seen.add(key);clean.append(q)
 return clean
def prepare_pack_async(gid,ts,ctx,spice):
 try:
  pack=_clean_pack(generate_pack(ts,ctx,spice))
  if not pack:return
  with cn() as c:
   g=c.execute('SELECT status FROM games WHERE id=?',(gid,)).fetchone()
   if g and g['status']=='lobby':c.execute('UPDATE games SET custom_questions=? WHERE id=?',(json.dumps(pack,ensure_ascii=False),gid))
 except Exception as e:print('async pack failed',type(e).__name__,str(e)[:200],flush=True)
def hero_round(rn,total):
 return rn in ([0,3,6] if total<=8 else [0,3,6,9,12,15])
def prepare_hero_async(gid,rn):
 try:
  with cn() as c:
   g=c.execute('SELECT * FROM games WHERE id=?',(gid,)).fetchone()
   if not g or int(g['round_no'])!=int(rn):return
   old=c.execute('SELECT image_data FROM hero_scenes WHERE game_id=? AND round_no=?',(gid,rn)).fetchone()
   if old:return
  ps=players(gid);typ,text,opts,sub=qdata(g,ps)
  if not sub or not sub['photo_data'] or not sub['photo_consent']:return
  selected=g['answer'] if any(p['name']==g['answer'] for p in ps) else ''
  ordered=[sub]+([p for p in ps if p['name']==selected and p['id']!=sub['id']] if selected else [])+[p for p in ps if p['id']!=sub['id'] and p['name']!=selected]
  items=[(p['name'],p['photo_data']) for p in ordered if p['photo_data'] and p['photo_consent']]
  visual_answer=(str(g['answer'])[7:] if str(g['answer']).startswith('OTHER::') else g['answer'])
  art=generate_many(items,text,visual_answer,sub['name'],selected)
  if art:
   with cn() as c:c.execute('INSERT OR REPLACE INTO hero_scenes(game_id,round_no,image_data,created) VALUES(?,?,?,?)',(gid,rn,art,now()))
 except Exception as e:print('async hero failed',type(e).__name__,str(e)[:250],flush=True)
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
  if p=='/health':return self.J({'ok':True,'game':'know-your-crew-visuals','storage':'postgres' if USE_PG else 'sqlite-ephemeral','ai_images':bool(os.getenv('OPENAI_API_KEY','').strip())})
  if p in ('/','/index.html'):return self.F(STATIC/'kyc.html')
  if p.startswith('/static/'):return self.F(STATIC/p[8:])
  if p.startswith('/api/photo/'):
   a=p.strip('/').split('/')
   if len(a)!=4:return self.send_error(404)
   g=game(a[2])
   if not g:return self.send_error(404)
   try:pid=int(a[3])
   except:return self.send_error(404)
   pl=next((x for x in players(g['id']) if x['id']==pid),None)
   if not pl or not pl['photo_data']:return self.send_error(404)
   try:
    import base64
    head,data=pl['photo_data'].split(',',1);raw=base64.b64decode(data);mime=head.split(';')[0].split(':',1)[1]
    self.send_response(200);self.send_header('Content-Type',mime);self.send_header('Cache-Control','private, max-age=3600');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw);return
   except:return self.send_error(404)
  if p.startswith('/api/state/'):
   q=parse_qs(u.query);tok=q.get('token',[''])[0];host=q.get('host',[''])[0];g=game(p.split('/')[-1])
   # Recover the canonical room from the opaque player token if the browser URL/local state
   # carries a stale or malformed room code. This is especially important in mobile webviews.
   if not g and tok:
    with cn() as c:
     row=c.execute('SELECT game_id FROM players WHERE token=?',(tok,)).fetchone()
     if row:g=c.execute('SELECT * FROM games WHERE id=?',(row['game_id'],)).fetchone()
   if not g:return self.J({'error':'room_not_found'},404)
   ps=players(g['id']);me=next((x for x in ps if x['token']==tok),None);typ,text,opts,sub=qdata(g,ps)
   with cn() as c:
    gs=c.execute('SELECT player_id,guess FROM guesses WHERE game_id=? AND round_no=?',(g['id'],g['round_no'])).fetchall();hero=c.execute('SELECT image_data FROM hero_scenes WHERE game_id=? AND round_no=?',(g['id'],g['round_no'])).fetchone();finalhero=c.execute('SELECT image_data FROM hero_scenes WHERE game_id=? AND round_no=99',(g['id'],)).fetchone()
   guessed={r['player_id']:r['guess'] for r in gs};need=max(0,len(ps)-1);ready=bool(g['answer']) and len(guessed)>=need;reveal=ready or g['status']=='finished';myguess=guessed.get(me['id']) if me else None;actual=('✏️ משהו אחר' if str(g['answer']).startswith('OTHER::') else g['answer']);shown=(str(g['answer'])[7:] if str(g['answer']).startswith('OTHER::') else g['answer']);iscorrect=bool(reveal and myguess is not None and myguess==actual)
   return self.J({'code':g['code'],'status':g['status'],'round':g['round_no'],'total':total_rounds(g),'is_host':bool(host and secrets.compare_digest(host,g['host'])),'me':{'id':me['id'],'name':me['name'],'score':me['score'],'has_photo':bool(me['photo_data'])} if me else None,'players':[{'id':x['id'],'name':x['name'],'score':x['score'],'has_photo':bool(x['photo_data']),'photo_url':('/api/photo/'+g['code']+'/'+str(x['id'])) if x['photo_data'] else ''} for x in ps],'photo_count':sum(1 for x in ps if x['photo_data']),'subject':{'id':sub['id'],'name':sub['name'],'has_photo':bool(sub['photo_data']),'photo_url':('/api/photo/'+g['code']+'/'+str(sub['id'])) if sub and sub['photo_data'] else ''} if sub else None,'type':typ,'question':text,'options':opts,'answer':shown if reveal else None,'interactive':interactive_prompt(g,typ,text,shown,sub) if reveal else '','answered':bool(g['answer']),'my_guess':myguess,'my_correct':iscorrect,'all_guesses':[{'player_id':x['id'],'name':x['name'],'guess':guessed.get(x['id']),'correct':guessed.get(x['id'])==actual,'photo_url':('/api/photo/'+g['code']+'/'+str(x['id'])) if x['photo_data'] else ''} for x in ps if sub and x['id']!=sub['id'] and x['id'] in guessed] if reveal else [],'guessed':bool(me and me['id'] in guessed),'guess_count':len(guessed),'guess_need':need,'waiting_for':[x['name'] for x in ps if sub and x['id']!=sub['id'] and x['id'] not in guessed],'reveal':reveal,'hero':hero['image_data'] if hero and reveal else None,'final_hero':finalhero['image_data'] if finalhero and g['status']=='finished' else None,'topics':effective_topics(g),'topic_votes':topic_vote_data(g),'my_topic_votes':player_topic_votes(g['id'],me['id'] if me else None),'mode':'duo' if len(ps)==2 else 'group','ai_images_ready':bool(os.getenv('OPENAI_API_KEY','').strip()),'spice':g['spice'],'context':g['custom_context'],'prize':g['prize'],'rounds':total_rounds(g),'history':mem(g)[-4:]})
  return self.J({'error':'not_found'},404)
 def do_POST(self):
  p=urlparse(self.path).path;d=self.B()
  if p=='/api/create':
   name=str(d.get('name','')).strip()[:40]
   if not name:return self.J({'error':'name_required'},400)
   co=code5();ht=secrets.token_urlsafe(16);pt=secrets.token_urlsafe(16);ts=d.get('topics',[]);ts=ts if isinstance(ts,list) else [];ctx=str(d.get('context','')).strip()[:700];sp=max(1,min(3,int(d.get('spice',1) or 1)));prize=str(d.get('prize','')).strip()[:180];rounds=max(6,min(30,int(d.get('rounds',12) or 12)))
   if sp==3 and not d.get('adults_confirmed'):return self.J({'error':'adults_confirmation_required'},400)
   with cn() as c:
    if USE_PG:gid=c.execute('INSERT INTO games(code,host,topics,custom_context,spice,prize,rounds,created) VALUES(?,?,?,?,?,?,?,?) RETURNING id',(co,ht,json.dumps(ts,ensure_ascii=False),ctx,sp,prize,rounds,now())).fetchone()['id']
    else:gid=c.execute('INSERT INTO games(code,host,topics,custom_context,spice,prize,rounds,created) VALUES(?,?,?,?,?,?,?,?)',(co,ht,json.dumps(ts,ensure_ascii=False),ctx,sp,prize,rounds,now())).lastrowid
    c.execute('INSERT INTO players(game_id,name,token,joined) VALUES(?,?,?,?)',(gid,name,pt,now()))
   Thread(target=prepare_pack_async,args=(gid,effective_topics(game(co)),ctx,sp),daemon=True).start()
   return self.J({'code':co,'host':ht,'token':pt,'name':name})
  if p=='/api/join':
   g=game(d.get('code'));name=str(d.get('name','')).strip()[:40]
   if not g:return self.J({'error':'not_found'},404)
   if not name:return self.J({'error':'name_required'},400)
   existing=next((x for x in players(g['id']) if x['name'].strip().lower()==name.lower()),None)
   if existing:return self.J({'code':g['code'],'token':existing['token'],'name':existing['name'],'recovered':True})
   if g['status']!='lobby':return self.J({'error':'started'},409)
   if len(players(g['id']))>=6:return self.J({'error':'full'},409)
   tok=secrets.token_urlsafe(16)
   with cn() as c:c.execute('INSERT INTO players(game_id,name,token,joined) VALUES(?,?,?,?)',(g['id'],name,tok,now()))
   return self.J({'code':g['code'],'token':tok,'name':name})
  a=p.strip('/').split('/')
  if len(a)!=3 or a[0]!='api':return self.J({'error':'not_found'},404)
  g=game(a[1]);act=a[2]
  # Player-token recovery: mobile browsers can keep an older room code in local state.
  # For player actions, the opaque player token is the stronger session identifier.
  if not g and act in ('photo','answer','guess'):
   tok=str(d.get('token',''))
   if tok:
    with cn() as c:
     row=c.execute('SELECT game_id FROM players WHERE token=?',(tok,)).fetchone()
     if row:g=c.execute('SELECT * FROM games WHERE id=?',(row['game_id'],)).fetchone()
  if not g:return self.J({'error':'room_not_found'},404)
  ps=players(g['id']);typ,text,opts,sub=qdata(g,ps)
  if act in ('start','next','hero','finalhero','skip','settings') and not(d.get('host') and secrets.compare_digest(str(d['host']),g['host'])):return self.J({'error':'forbidden'},403)
  if act=='settings':
   if g['status']!='lobby':return self.J({'error':'already_started'},409)
   ts=d.get('topics',[])
   if not isinstance(ts,list):ts=[]
   ts=[str(x)[:60] for x in ts[:12]]
   ctx=str(d.get('context','')).strip()[:700];prize=str(d.get('prize','')).strip()[:180];rounds=max(6,min(30,int(d.get('rounds',g['rounds']) or 12)))
   try:sp=max(1,min(3,int(d.get('spice',g['spice']) or 1)))
   except:sp=int(g['spice'] or 1)
   if sp==3 and not d.get('adults_confirmed'):return self.J({'error':'adults_confirmation_required'},400)
   with cn() as c:c.execute('UPDATE games SET topics=?,custom_context=?,spice=?,prize=?,rounds=?,custom_questions=? WHERE id=?',(json.dumps(ts,ensure_ascii=False),ctx,sp,prize,rounds,'[]',g['id']))
   return self.J({'ok':True})
  if act=='photo':
   me=next((x for x in ps if x['token']==d.get('token')),None);data=d.get('data_url','')
   if not me:return self.J({'error':'player_not_found'},404)
   if not d.get('consent'):return self.J({'error':'consent_required'},400)
   if not isinstance(data,str) or not data.startswith('data:image/'):return self.J({'error':'invalid_image'},400)
   if len(data)>5_600_000:return self.J({'error':'image_too_large'},400)
   try:
    with cn() as c:c.execute('UPDATE players SET photo_data=?,photo_consent=1 WHERE id=?',(data,me['id']))
   except sqlite3.Error as e:
    print('photo save db error',type(e).__name__,str(e)[:200],flush=True);return self.J({'error':'photo_save_failed'},503)
   return self.J({'ok':True,'bytes':len(data)})
  if act=='topicvote':
   me=next((x for x in ps if x['token']==d.get('token')),None);topic=str(d.get('topic','')).strip()[:80]
   if not me or g['status']!='lobby':return self.J({'error':'not_allowed'},403)
   if topic not in TOPICS:return self.J({'error':'invalid_topic'},400)
   with cn() as c:
    old=c.execute('SELECT 1 FROM topic_votes WHERE game_id=? AND player_id=? AND topic=?',(g['id'],me['id'],topic)).fetchone()
    if old:c.execute('DELETE FROM topic_votes WHERE game_id=? AND player_id=? AND topic=?',(g['id'],me['id'],topic))
    else:
     count=c.execute('SELECT COUNT(*) AS n FROM topic_votes WHERE game_id=? AND player_id=?',(g['id'],me['id'])).fetchone()['n']
     if count>=6:return self.J({'error':'max_topics'},409)
     c.execute('INSERT INTO topic_votes(game_id,player_id,topic) VALUES(?,?,?)',(g['id'],me['id'],topic))
   return self.J({'ok':True})
  if act=='start':
   if len(ps)<2:return self.J({'error':'need_2'},409)
   # Tailored AI questions are prepared while players are in the lobby.
   # Starting the game must be instant; if the pack is not ready, curated questions are used.
   pack=_clean_pack(custom_questions(g))
   with cn() as c:
    c.execute("UPDATE games SET status='playing',round_no=0,answer='',memory='[]',custom_questions=? WHERE id=?",(json.dumps(pack,ensure_ascii=False),g['id']))
    c.execute('DELETE FROM guesses WHERE game_id=?',(g['id'],));c.execute('DELETE FROM hero_scenes WHERE game_id=?',(g['id'],));c.execute('DELETE FROM round_scores WHERE game_id=?',(g['id'],))
   return self.J({'ok':True,'tailored_questions':len(pack)})
  if act=='answer':
   me=next((x for x in ps if x['token']==d.get('token')),None);ans=str(d.get('answer',''))[:160]
   if not me or not sub or me['id']!=sub['id']:return self.J({'error':'subject_only'},403)
   if ans.startswith('OTHER::'):
    custom=ans[7:].strip()
    if '✏️ משהו אחר' not in opts or len(custom)<1:return self.J({'error':'invalid_answer'},400)
    ans='OTHER::'+custom[:120]
   elif ans not in opts:return self.J({'error':'invalid_answer'},400)
   with cn() as c:c.execute('UPDATE games SET answer=? WHERE id=?',(ans,g['id']))
   if os.getenv('OPENAI_API_KEY','').strip() and hero_round(int(g['round_no']),total_rounds(g)) and sub['photo_data'] and sub['photo_consent']:
    Thread(target=prepare_hero_async,args=(g['id'],int(g['round_no'])),daemon=True).start()
   return self.J({'ok':True})
  if act=='guess':
   me=next((x for x in ps if x['token']==d.get('token')),None);guess=str(d.get('guess',''))[:120]
   if not me or not sub or me['id']==sub['id']:return self.J({'error':'invalid_player'},403)
   if guess not in opts:return self.J({'error':'invalid_guess'},400)
   with cn() as c:
    c.execute('INSERT OR REPLACE INTO guesses(game_id,round_no,player_id,guess) VALUES(?,?,?,?)',(g['id'],g['round_no'],me['id'],guess))
    rows=c.execute('SELECT player_id,guess FROM guesses WHERE game_id=? AND round_no=?',(g['id'],g['round_no'])).fetchall()
    if g['answer'] and len(rows)>=len(ps)-1:
     already=c.execute('SELECT 1 FROM round_scores WHERE game_id=? AND round_no=?',(g['id'],g['round_no'])).fetchone()
     if not already:
      for r in rows:
       if r['guess']==('✏️ משהו אחר' if str(g['answer']).startswith('OTHER::') else g['answer']):c.execute('UPDATE players SET score=score+1 WHERE id=?',(r['player_id'],))
      c.execute('INSERT INTO round_scores(game_id,round_no,created) VALUES(?,?,?)',(g['id'],g['round_no'],now()))
   fresh=players(g['id'])
   return self.J({'ok':True,'scores':{x['name']:x['score'] for x in fresh}})
  if act=='finalhero':
   with cn() as c:old=c.execute('SELECT image_data FROM hero_scenes WHERE game_id=? AND round_no=99',(g['id'],)).fetchone()
   if old:return self.J({'ok':True,'image':old['image_data']})
   available=[p for p in ps if p['photo_data'] and p['photo_consent']]
   if len(available)<2:return self.J({'error':'not_enough_photos'},409)
   ranked=sorted(ps,key=lambda x:x['score'],reverse=True);winner=ranked[0]['name'];summary=', '.join([f"{p['name']} {p['score']} points" for p in ranked])
   items=[(p['name'],p['photo_data']) for p in available]
   prize=g['prize'] or 'bragging rights as the friend who knows the crew best';art=generate_many(items,'Final cinematic ensemble poster for this friend group after a hilarious Know Your Crew game. The winner also receives this playful prize: '+prize,f'Winner: {winner}. Prize: {prize}. Scores: {summary}',winner,'')
   if not art:return self.J({'error':'generation_failed'},502)
   with cn() as c:c.execute('INSERT OR REPLACE INTO hero_scenes(game_id,round_no,image_data,created) VALUES(?,?,?,?)',(g['id'],99,art,now()))
   return self.J({'ok':True,'image':art})
  if act=='hero':
   if not sub or not sub['photo_data'] or not sub['photo_consent']:return self.J({'error':'no_photo'},409)
   with cn() as c:old=c.execute('SELECT image_data FROM hero_scenes WHERE game_id=? AND round_no=?',(g['id'],g['round_no'])).fetchone()
   if old:return self.J({'ok':True,'image':old['image_data']})
   selected=g['answer'] if any(p['name']==g['answer'] for p in ps) else ''
   ordered=[sub]+([p for p in ps if p['name']==selected and p['id']!=sub['id']] if selected else [])+[p for p in ps if p['id']!=sub['id'] and p['name']!=selected]
   items=[(p['name'],p['photo_data']) for p in ordered if p['photo_data'] and p['photo_consent']]
   visual_answer=(str(g['answer'])[7:] if str(g['answer']).startswith('OTHER::') else g['answer'])
   art=generate_many(items,text,visual_answer,sub['name'],selected)
   if not art:return self.J({'error':'generation_failed'},502)
   with cn() as c:c.execute('INSERT OR REPLACE INTO hero_scenes(game_id,round_no,image_data,created) VALUES(?,?,?,?)',(g['id'],g['round_no'],art,now()))
   return self.J({'ok':True,'image':art})
  if act=='skip':
   mm=mem(g);mm.append({'round':g['round_no'],'subject':sub['name'] if sub else '','question':text,'answer':'SKIPPED','type':'skip'});rn=int(g['round_no'])+1
   with cn() as c:
    c.execute('DELETE FROM guesses WHERE game_id=? AND round_no=?',(g['id'],g['round_no']))
    if rn>=total_rounds(g):c.execute("UPDATE games SET status='finished',answer='',memory=? WHERE id=?",(json.dumps(mm,ensure_ascii=False),g['id']))
    else:c.execute("UPDATE games SET round_no=?,answer='',memory=? WHERE id=?",(rn,json.dumps(mm,ensure_ascii=False),g['id']))
   return self.J({'ok':True,'skipped':True})
  if act=='next':
   with cn() as c:
    gs=c.execute('SELECT player_id,guess FROM guesses WHERE game_id=? AND round_no=?',(g['id'],g['round_no'])).fetchall()
    if not g['answer'] or len(gs)<len(ps)-1:return self.J({'error':'not_ready'},409)
    clean_answer=(str(g['answer'])[7:] if str(g['answer']).startswith('OTHER::') else g['answer']);mm=mem(g);mm.append({'round':g['round_no'],'subject':sub['name'],'question':text,'answer':clean_answer,'type':typ});rn=int(g['round_no'])+1
    if rn>=total_rounds(g):c.execute("UPDATE games SET status='finished',memory=? WHERE id=?",(json.dumps(mm,ensure_ascii=False),g['id']))
    else:c.execute("UPDATE games SET round_no=?,answer='',memory=? WHERE id=?",(rn,json.dumps(mm,ensure_ascii=False),g['id']))
   return self.J({'ok':True})
  return self.J({'error':'not_found'},404)
 def log_message(self,*a):pass
def run():init();ThreadingHTTPServer(('0.0.0.0',int(os.getenv('PORT','5000'))),H).serve_forever()
