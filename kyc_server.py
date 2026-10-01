import json,os,random,secrets,sqlite3,mimetypes
from threading import Thread,Lock,local
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse,parse_qs
from kyc_questions import GENERAL,EVERYDAY_CORE,TOPICS,SPICY,BOLD_COMEDY,SOCIAL_SPARK
from kyc_visuals import generate_many,decode_image,MODEL,warm_image_runtime
import kyc_image_jobs as image_jobs
import kyc_budget as budget
import kyc_instant as instant
from kyc_ai import generate_pack
from kyc_locales import normalize_language,direction,topic_labels,general_pack,spicy_pack,other_label,callback_copy,match_prompt,SUPPORTED_LANGUAGES,TOPIC_LABELS,ui_copy,last_resort
BASE=Path(__file__).parent;DB=Path(os.getenv('DATABASE_PATH',BASE/'kyc.db'));DATABASE_URL=os.getenv('DATABASE_URL','').strip();USE_PG=DATABASE_URL.startswith(('postgres://','postgresql://'));STATIC=BASE/'static';TOTAL=12;PRESENCE_TIMEOUT=40;ADULT_TOPICS={'אינטימיות למבוגרים','Adult / Intimacy (18+)','דייטים','Dating'};THEME_ONLY={'מה היית עושה אם…','דילמות','מביך אבל מצחיק','מי הכי…','סודות והרגלים','נוסטלגיה','טיולים וחופשות','חלומות ופנטזיות','כסף מטורף'};CHAT_REACTIONS=('❤️','😂','😭','😈');VISUAL_POOL=ThreadPoolExecutor(max_workers=1);VISUAL_TASKS=set();VISUAL_TASKS_LOCK=Lock();_DB_LOCAL=local()
def now():return datetime.now(timezone.utc).isoformat()
def adult_required(ts,spice=1):return int(spice or 1)>=3 or bool(ADULT_TOPICS.intersection(set(ts or [])))
def recently_seen(p,timeout=PRESENCE_TIMEOUT):
 raw=(p['last_seen'] if 'last_seen' in p.keys() else '') or (p['joined'] if 'joined' in p.keys() else '')
 if not raw:return False
 try:
  dt=datetime.fromisoformat(str(raw).replace('Z','+00:00'));return (datetime.now(timezone.utc)-dt).total_seconds()<=timeout
 except:return False
class CompatConn:
 def __init__(self,raw,pg=False,borrowed=False):self.raw=raw;self.pg=pg;self.borrowed=borrowed
 def __enter__(self):
  if not self.borrowed:self.raw.__enter__()
  return self
 def __exit__(self,exc_type,exc,tb):
  if self.borrowed:
   # The request scope owns the transaction; nested helpers must not commit a
   # row-locking start/join/reset half way through the operation.
   if exc_type:self.raw.rollback()
   return False
  try:return self.raw.__exit__(exc_type,exc,tb)
  finally:
   # sqlite's connection context manager commits/rolls back but does not close.
   if not self.pg:self.raw.close()
 def execute(self,sql,params=()):
  if self.pg:
   if sql.startswith('INSERT OR REPLACE INTO guesses'):
    sql='INSERT INTO guesses(game_id,round_no,player_id,guess) VALUES(%s,%s,%s,%s) ON CONFLICT(game_id,round_no,player_id) DO UPDATE SET guess=EXCLUDED.guess'
   elif sql.startswith('INSERT OR REPLACE INTO hero_scenes'):
    sql='INSERT INTO hero_scenes(game_id,round_no,image_data,created) VALUES(%s,%s,%s,%s) ON CONFLICT(game_id,round_no) DO UPDATE SET image_data=EXCLUDED.image_data,created=EXCLUDED.created'
   else:sql=sql.replace('?','%s')
  return self.raw.execute(sql,params)
def cn():
 shared=getattr(_DB_LOCAL,'connection',None)
 if shared:return CompatConn(shared[0],shared[1],True)
 if USE_PG:
  import psycopg
  from psycopg.rows import dict_row
  return CompatConn(psycopg.connect(DATABASE_URL,row_factory=dict_row,connect_timeout=10),True)
 c=sqlite3.connect(DB,timeout=30);c.row_factory=sqlite3.Row;c.execute('PRAGMA busy_timeout=30000');return CompatConn(c,False)
class request_connection:
 """Reuse one physical DB connection for all small queries in an HTTP request."""
 def __enter__(self):
  if getattr(_DB_LOCAL,'connection',None):self.owner=False;return self
  self.owner=True
  if USE_PG:
   import psycopg
   from psycopg.rows import dict_row
   raw=psycopg.connect(DATABASE_URL,row_factory=dict_row,connect_timeout=10);pg=True
  else:
   raw=sqlite3.connect(DB,timeout=30);raw.row_factory=sqlite3.Row;raw.execute('PRAGMA busy_timeout=30000');pg=False
  _DB_LOCAL.connection=(raw,pg);return self
 def __exit__(self,*_):
  if self.owner:
   raw,_pg=_DB_LOCAL.connection
   try:
    if _ and _[0]:raw.rollback()
    else:raw.commit()
   finally:
    raw.close();delattr(_DB_LOCAL,'connection')
def init():
 if USE_PG:
  with cn() as c:
   c.execute("""CREATE TABLE IF NOT EXISTS games(id BIGSERIAL PRIMARY KEY,code TEXT UNIQUE,host TEXT,status TEXT DEFAULT 'lobby',round_no INTEGER DEFAULT 0,answer TEXT DEFAULT '',memory TEXT DEFAULT '[]',topics TEXT DEFAULT '[]',custom_context TEXT DEFAULT '',spice INTEGER DEFAULT 1,custom_questions TEXT DEFAULT '[]',prize TEXT DEFAULT '',rounds INTEGER DEFAULT 12,adults_confirmed INTEGER DEFAULT 0,language TEXT DEFAULT 'en',created TEXT)""")
   c.execute("ALTER TABLE games ADD COLUMN IF NOT EXISTS adults_confirmed INTEGER DEFAULT 0")
   c.execute("ALTER TABLE games ADD COLUMN IF NOT EXISTS language TEXT DEFAULT 'he'")
   c.execute("""CREATE TABLE IF NOT EXISTS players(id BIGSERIAL PRIMARY KEY,game_id BIGINT,name TEXT,token TEXT UNIQUE,score INTEGER DEFAULT 0,joined TEXT,photo_data TEXT DEFAULT '',photo_consent INTEGER DEFAULT 0,active INTEGER DEFAULT 1,last_seen TEXT DEFAULT '',client_id TEXT DEFAULT '')""")
   c.execute("ALTER TABLE players ADD COLUMN IF NOT EXISTS adult_confirmed INTEGER DEFAULT 0")
   c.execute("ALTER TABLE players ADD COLUMN IF NOT EXISTS active INTEGER DEFAULT 1")
   c.execute("ALTER TABLE players ADD COLUMN IF NOT EXISTS last_seen TEXT DEFAULT ''")
   c.execute("ALTER TABLE players ADD COLUMN IF NOT EXISTS client_id TEXT DEFAULT ''")
   c.execute("ALTER TABLE players ADD COLUMN IF NOT EXISTS gender TEXT DEFAULT 'unspecified'")
   c.execute("""CREATE TABLE IF NOT EXISTS guesses(game_id BIGINT,round_no INTEGER,player_id BIGINT,guess TEXT,UNIQUE(game_id,round_no,player_id))""")
   c.execute("""CREATE TABLE IF NOT EXISTS hero_scenes(game_id BIGINT,round_no INTEGER,image_data TEXT,created TEXT,UNIQUE(game_id,round_no))""")
   c.execute("""CREATE TABLE IF NOT EXISTS round_scores(game_id BIGINT,round_no INTEGER,created TEXT,UNIQUE(game_id,round_no))""")
   c.execute("""CREATE TABLE IF NOT EXISTS topic_votes(game_id BIGINT,player_id BIGINT,topic TEXT,UNIQUE(game_id,player_id,topic))""")
   c.execute("""CREATE TABLE IF NOT EXISTS question_history(crew_key TEXT,question_key TEXT,question TEXT,used TEXT,UNIQUE(crew_key,question_key))""")
   c.execute("""CREATE TABLE IF NOT EXISTS match_answers(game_id BIGINT,round_no INTEGER,player_id BIGINT,answer TEXT,created TEXT,UNIQUE(game_id,round_no,player_id))""")
   c.execute("""CREATE TABLE IF NOT EXISTS match_scores(game_id BIGINT,round_no INTEGER,matched INTEGER,created TEXT,UNIQUE(game_id,round_no))""")
   c.execute("""CREATE TABLE IF NOT EXISTS chat_messages(id BIGSERIAL PRIMARY KEY,game_id BIGINT,player_id BIGINT,kind TEXT,body TEXT,client_msg_id TEXT DEFAULT '',created TEXT)""")
   c.execute("CREATE INDEX IF NOT EXISTS chat_messages_game_id ON chat_messages(game_id,id)")
   c.execute("CREATE UNIQUE INDEX IF NOT EXISTS chat_messages_idempotency ON chat_messages(game_id,player_id,client_msg_id) WHERE client_msg_id<>''")
   c.execute("DELETE FROM players a USING players b WHERE a.game_id=b.game_id AND LOWER(TRIM(a.name))=LOWER(TRIM(b.name)) AND a.id>b.id")
   c.execute("CREATE UNIQUE INDEX IF NOT EXISTS players_game_name_ci ON players(game_id,LOWER(TRIM(name)))")
   c.execute("CREATE UNIQUE INDEX IF NOT EXISTS players_game_client_id ON players(game_id,client_id) WHERE client_id<>''")
   c.execute("ALTER TABLE games ADD COLUMN IF NOT EXISTS image_run INTEGER DEFAULT 0")
   c.execute("ALTER TABLE games ADD COLUMN IF NOT EXISTS tiebreak TEXT DEFAULT '{}'")
   image_jobs.init_jobs(c);instant.init(c);budget.init(c)
  return
 DB.parent.mkdir(parents=True,exist_ok=True)
 with cn() as c:
  c.raw.executescript("""CREATE TABLE IF NOT EXISTS games(id INTEGER PRIMARY KEY,code TEXT UNIQUE,host TEXT,status TEXT DEFAULT 'lobby',round_no INTEGER DEFAULT 0,answer TEXT DEFAULT '',memory TEXT DEFAULT '[]',topics TEXT DEFAULT '[]',custom_context TEXT DEFAULT '',spice INTEGER DEFAULT 1,custom_questions TEXT DEFAULT '[]',prize TEXT DEFAULT '',rounds INTEGER DEFAULT 12,adults_confirmed INTEGER DEFAULT 0,language TEXT DEFAULT 'en',created TEXT);CREATE TABLE IF NOT EXISTS players(id INTEGER PRIMARY KEY,game_id INTEGER,name TEXT,token TEXT UNIQUE,score INTEGER DEFAULT 0,joined TEXT,client_id TEXT DEFAULT '');CREATE TABLE IF NOT EXISTS guesses(game_id INTEGER,round_no INTEGER,player_id INTEGER,guess TEXT,UNIQUE(game_id,round_no,player_id));CREATE TABLE IF NOT EXISTS hero_scenes(game_id INTEGER,round_no INTEGER,image_data TEXT,created TEXT,UNIQUE(game_id,round_no));CREATE TABLE IF NOT EXISTS round_scores(game_id INTEGER,round_no INTEGER,created TEXT,UNIQUE(game_id,round_no));CREATE TABLE IF NOT EXISTS topic_votes(game_id INTEGER,player_id INTEGER,topic TEXT,UNIQUE(game_id,player_id,topic));CREATE TABLE IF NOT EXISTS question_history(crew_key TEXT,question_key TEXT,question TEXT,used TEXT,UNIQUE(crew_key,question_key));CREATE TABLE IF NOT EXISTS match_answers(game_id INTEGER,round_no INTEGER,player_id INTEGER,answer TEXT,created TEXT,UNIQUE(game_id,round_no,player_id));CREATE TABLE IF NOT EXISTS match_scores(game_id INTEGER,round_no INTEGER,matched INTEGER,created TEXT,UNIQUE(game_id,round_no));CREATE TABLE IF NOT EXISTS chat_messages(id INTEGER PRIMARY KEY,game_id INTEGER,player_id INTEGER,kind TEXT,body TEXT,client_msg_id TEXT DEFAULT '',created TEXT);CREATE INDEX IF NOT EXISTS chat_messages_game_id ON chat_messages(game_id,id);CREATE UNIQUE INDEX IF NOT EXISTS chat_messages_idempotency ON chat_messages(game_id,player_id,client_msg_id) WHERE client_msg_id<>'';""")
  gc={r['name'] for r in c.execute('PRAGMA table_info(games)')}
  for n,d in [('topics',"TEXT DEFAULT '[]'"),('custom_context',"TEXT DEFAULT ''"),('spice','INTEGER DEFAULT 1'),('custom_questions',"TEXT DEFAULT '[]'"),('prize',"TEXT DEFAULT ''"),('rounds','INTEGER DEFAULT 12'),('adults_confirmed','INTEGER DEFAULT 0'),('language',"TEXT DEFAULT 'he'")]:
   if n not in gc:c.execute(f'ALTER TABLE games ADD COLUMN {n} {d}')
  if 'tiebreak' not in gc:c.execute("ALTER TABLE games ADD COLUMN tiebreak TEXT DEFAULT '{}'")
  if 'image_run' not in gc:c.execute('ALTER TABLE games ADD COLUMN image_run INTEGER DEFAULT 0')
  image_jobs.init_jobs(c);instant.init(c);budget.init(c)
  pc={r['name'] for r in c.execute('PRAGMA table_info(players)')}
  for n,d in [('adult_confirmed','INTEGER DEFAULT 0'),('photo_data',"TEXT DEFAULT ''"),('photo_consent','INTEGER DEFAULT 0'),('active','INTEGER DEFAULT 1'),('last_seen',"TEXT DEFAULT ''"),('client_id',"TEXT DEFAULT ''"),('gender',"TEXT DEFAULT 'unspecified'")]:
   if n not in pc:c.execute(f'ALTER TABLE players ADD COLUMN {n} {d}')
  c.execute("DELETE FROM players WHERE id NOT IN (SELECT MIN(id) FROM players GROUP BY game_id,LOWER(TRIM(name)))")
  c.execute("CREATE UNIQUE INDEX IF NOT EXISTS players_game_name_ci ON players(game_id,LOWER(TRIM(name)))")
  c.execute("CREATE UNIQUE INDEX IF NOT EXISTS players_game_client_id ON players(game_id,client_id) WHERE client_id<>''")
def game(code):
 with cn() as c:return c.execute('SELECT * FROM games WHERE code=?',(str(code or '').upper(),)).fetchone()
def _players(c,gid,include_photos=False):
 # State and lobby polling only need photo readiness. Returning a one-byte marker
 # keeps existing boolean callers compatible without copying multi-megabyte blobs.
 photo="photo_data" if include_photos else "CASE WHEN COALESCE(photo_data,'')<>'' AND COALESCE(photo_consent,0)=1 THEN '1' ELSE '' END AS photo_data"
 cols='id,game_id,name,token,score,joined,'+photo+',photo_consent,active,last_seen,client_id,adult_confirmed,gender'
 return c.execute('SELECT '+cols+' FROM players WHERE game_id=? ORDER BY id',(gid,)).fetchall()
def players(gid,include_photos=False):
 with cn() as c:return _players(c,gid,include_photos)
def game_for_token(code,token=''):
 # A valid opaque player token is canonical even if an old, rotated code is
 # someday reused by another room.
 if token:
  with cn() as c:
   g=c.execute('SELECT g.* FROM games g JOIN players p ON p.game_id=g.id WHERE p.token=?',(str(token),)).fetchone()
   if g:return g
 return game(code)
def live_players(gid):
 return [p for p in players(gid) if int(p['active'] if p['active'] is not None else 1)==1]
def normalize_gender(value):
 return value if value in ('male','female','unspecified') else 'unspecified'
def _norm_name(x):
 return ' '.join(str(x or '').strip().lower().split())
def crew_key(ps):
 import hashlib
 names=sorted(_norm_name(p['name']) for p in ps if int(p['active'] if p['active'] is not None else 1)==1)
 return hashlib.sha256('|'.join(names).encode()).hexdigest()[:24] if names else ''
def question_key(text,ps):
 import re
 x=str(text or '').lower()
 for p in ps:
  n=_norm_name(p['name'])
  if n:x=x.replace(n,'{s}')
 x=re.sub(r'[^\w\u0590-\u05ff{}]+',' ',x,flags=re.UNICODE)
 return ' '.join(x.split())
def past_question_keys(ps):
 ck=crew_key(ps)
 if not ck:return set()
 with cn() as c:return {r['question_key'] for r in c.execute('SELECT question_key FROM question_history WHERE crew_key=?',(ck,)).fetchall()}
def too_similar(qk,used):
 if not qk:return True
 # Catch both exact/near-exact repeats and the same underlying prompt with small wording changes.
 # This is intentionally lexical and deterministic so it works without another AI call.
 stop={'מה','מי','אם','של','עם','את','על','או','זה','הכי','כאן','היה','הייתה','היה/תה','עושה','יעשה','תעשה','יכול','יכולה','צריך','צריכה','הוא','היא','לו','לה'}
 def toks(x):
  return {w for w in str(x or '').split() if len(w)>1 and w not in stop and w not in ('{s}','{','s','}')}
 try:
  from difflib import SequenceMatcher
  a=toks(qk)
  for u in used:
   if not u:continue
   if qk==u or SequenceMatcher(None,qk,u).ratio()>=0.84:return True
   b=toks(u)
   if a and b and (len(a&b)>=5 and len(a&b)/max(1,min(len(a),len(b)))>=0.58):return True
  return False
 except:return qk in used
def remember_question(ps,text):
 ck=crew_key(ps);qk=question_key(text,ps)
 if not ck or not qk:return
 with cn() as c:
  if USE_PG:c.execute('INSERT INTO question_history(crew_key,question_key,question,used) VALUES(?,?,?,?) ON CONFLICT(crew_key,question_key) DO UPDATE SET used=EXCLUDED.used',(ck,qk,str(text)[:500],now()))
  else:c.execute('INSERT OR REPLACE INTO question_history(crew_key,question_key,question,used) VALUES(?,?,?,?)',(ck,qk,str(text)[:500],now()))
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
 lang=game_language(g);x=custom_questions(g)
 if lang=='he':
  for t in effective_topics(g):x+=TOPICS.get(t,[])
  if int(g['spice'] or 1)>=3:x+=SPICY
  x+=GENERAL
 else:
  x+=general_pack(lang)
  if int(g['spice'] or 1)>=3:x+=spicy_pack(lang)
 return x
def tie_data(g):
 try:return json.loads(g['tiebreak'] or '{}')
 except (KeyError,IndexError,TypeError,ValueError):return {}
def winners(g,ps):
 ids=tie_data(g).get('contenders',[])
 eligible=[p for p in ps if not ids or p['id'] in ids]
 if not eligible:return []
 top=max(p['score'] for p in eligible)
 return [p for p in eligible if p['score']==top]
def final_image_eligible(g,ps):
 ws=winners(g,ps)
 return bool(ws and all(p['photo_data'] and p['photo_consent'] for p in ws) and sum(bool(p['photo_data'] and p['photo_consent']) for p in ps)<=16)
def can_tiebreak(g,ps):
 ws=winners(g,ps);active=[p for p in ps if p['active']]
 return bool(g['status']=='finished' and len(ws)>1 and len(active)>=2 and
             all(p['active'] for p in ws) and tie_data(g).get('sets',0)<3 and
             total_rounds(g)+len(active)<99)
def total_rounds(g):
 try:return int(tie_data(g).get('end') or max(6,min(30,int(g['rounds'] or 12))))
 except:return 12
def game_language(g):
 try:return normalize_language(g['language'])
 except:return 'en'
def localized_smart_callback(g,ps,rn):
 m=[e for e in mem(g) if e.get('answer') and e.get('answer')!='SKIPPED'];total=total_rounds(g);marks=sorted(set([max(4,total//3),max(6,(total*2)//3),max(7,total-2)]))
 if rn not in marks or len(m)<3:return None
 names=[p['name'] for p in ps]
 room=[e for e in reversed(m) if e.get('answer') in names and e.get('answer')!=e.get('subject')]
 if room:
  e=room[0];sub=next((p for p in ps if p['name']==e.get('subject')),None)
  if sub:
   cb=callback_copy(game_language(g),'friend',sub['name'],friend=e.get('answer'));return (*cb,sub) if cb else None
 e=next((x for x in reversed(m) if x.get('subject')),None)
 if e:
  sub=next((p for p in ps if p['name']==e.get('subject')),None)
  if sub:
   cb=callback_copy(game_language(g),'old',sub['name'],old=e.get('answer',''));return (*cb,sub) if cb else None
 return None
def localized_duo_callback(g,ps,rn):
 m=[e for e in mem(g) if e.get('answer') and e.get('answer')!='SKIPPED']
 if len(ps)!=2 or rn<4 or rn not in (4,6,9,12,15,18,21,24,27) or len(m)<3:return None
 sub=ps[rn%2];mine=next((e for e in reversed(m) if e.get('subject')==sub['name']),None)
 if not mine:return None
 cb=callback_copy(game_language(g),'duo',sub['name'],old=mine.get('answer',''));return (*cb,sub) if cb else None
def novel_callback(cb,g,ps):
 """Allow callbacks to quote old answers while preventing callback-to-callback repeats."""
 if not cb:return None
 # A callback deliberately reuses earlier context, so comparing it with every
 # ordinary question rejects the useful callback itself. Compare it only with
 # callbacks already shown to this crew, including earlier games.
 used={question_key(e.get('question',''),ps) for e in mem(g) if 'callback' in str(e.get('type',''))}
 used|={key for key in past_question_keys(ps) if 'plot twist' in key}
 return None if too_similar(question_key(cb[1],ps),used) else cb
def _callback_source_text(entry):
 """Return compact prior context so a callback is understandable on its own."""
 if 'callback' in str(entry.get('type','')):return None
 question=' '.join(str(entry.get('question') or '').split()).strip()
 answer=' '.join(str(entry.get('answer') or '').split()).strip()
 if not question or not answer or answer=='SKIPPED':return None
 # Callback cards must stay readable on a phone and must not quote malformed data.
 if len(question)>220 or len(answer)>90:return None
 return question,answer
def meaningful_callback(g,ps,rn,duo=False):
 """Build a new social decision from a real earlier choice, never a replay."""
 if game_language(g)!='he' or tie_data(g):return None
 total=total_rounds(g)
 marks=([max(4,total//2)] if total<=8 else [max(4,total//3),max(7,2*total//3)] if total<=12 else [max(4,total//4),max(8,total//2),max(12,3*total//4)])
 if rn not in marks:return None
 history=mem(g)
 if len(history)<3:return None
 used_sources={e.get('callback_source_round') for e in history if e.get('callback_source_round') is not None}
 # The source must give the sequel a specific consequence. Other prior
 # answers are deliberately ignored; generic callbacks were the complaint.
 for e in reversed(history):
  source=_callback_source_text(e)
  if not source or e.get('round') in used_sources:continue
  sub=next((p for p in ps if p['name']==e.get('subject')),None)
  if not sub:continue
  question,answer=source;q=question.lower();name=sub['name']
  if any('callback' in str(prior.get('type','')) and name in str(prior.get('question','')) and answer in str(prior.get('question','')) for prior in history):continue
  friend=answer if answer in [p['name'] for p in ps if p['id']!=sub['id']] else None
  if friend and ('שני מושבים' in q or 'רכב ספורט' in q):
   text=f'⚡ קודם {name} בחר/ה לקחת את {friend} ראשון/ה ברכב החדש. {friend} מעלה תמונה וכותב/ת: “הרכב שלנו!” איך {name} מגיב/ה?'
   options=['זורם/ת עם הבדיחה','מגיב/ה: “שלי, בעצם”','מעלה תמונה לבד עם הרכב','מבקש/ת למחוק את הכיתוב']
  elif friend and ('רפסודה' in q or 'כרישים' in q):
   text=f'⚡ קודם {name} משך/ה את {friend} ראשון/ה מהרפסודה. על החוף {friend} מספר/ת לכולם שהוא/היא הציל/ה את {name}. מה התגובה?'
   options=['נותן/ת לו/לה את הקרדיט','מתקן/ת את הסיפור מול כולם','צוחק/ת ושואל/ת מי הבא בתור','מבקש/ת ממנו/ה לספר שוב']
  elif friend and ('כרטיס זוגי' in q or 'הופעה' in q):
   text=f'⚡ קודם {name} הזמין/ה את {friend} להופעה. {friend} רוצה למכור את הכרטיס שלו/ה ברווח ולהשאיר את {name} לבד. מה {name} עושה?'
   options=['הולך/ת לבד ונהנה/ית','מבקש/ת לבחור אורח/ת אחר/ת','מציע/ה להתחלק ברווח','מנסה לשכנע אותו/ה לבוא']
  elif friend and ('חופשה' in q or 'טיול' in q):
   text=f'⚡ קודם {name} בחר/ה את {friend} לחופשה. ביום הראשון {friend} רוצה להישאר במלון ו־{name} רוצה לצאת. מה {name} מציע/ה?'
   options=['יוצא/ת לבד','נשאר/ת עם החבר/ה','קובע/ת להיפגש בערב','משכנע/ת לעשר דקות בחוץ']
  elif 'תמונה לא מחמיאה' in q and answer in ('צוחק/ת ומגיב/ה','שולח/ת תמונה גרועה יותר','מתעלם/ת'):
   text=f'⚡ קודם {name} בחר/ה להגיב לתמונה הלא מחמיאה ב־“{answer}”. עכשיו מישהו שולח אותה לקבוצת המשפחה. מה עושים?'
   options=['מבקש/ת שימחקו','מעלה תמונה טובה לפיצוי','צוחק/ת עם המשפחה','שואל/ת מי שלח אותה']
  elif 'חשבון משותף' in q and answer in ('מתחלקים שווה','מחכה שמישהו יעלה את זה'):
   text=f'⚡ קודם {name} בחר/ה: “{answer}” בחשבון המסעדה. אחר כך חבר/ה שולח/ת לו/לה בקשה להחזיר כסף. מה התגובה?'
   options=['משלם/ת בלי ויכוח','מבקש/ת לחשב מחדש','שולח/ת צילום של החשבון','מציע/ה לשלם בפעם הבאה']
  else:continue
  cb=('duo_callback' if duo else 'callback',text,options,sub)
  if novel_callback(cb,g,ps):return cb
 return None
def smart_callback(g,ps,rn):
 return meaningful_callback(g,ps,rn)
def interactive_match_data(g,typ,text,sub):
 if tie_data(g) or 'callback' not in str(typ) or not sub:return None
 ps=players(g['id']);active=[p for p in ps if int(p['active'] if p['active'] is not None else 1)==1];by_name={p['name']:p for p in active}
 prior=next((e for e in reversed(mem(g)) if e.get('subject')==sub['name'] and e.get('answer') in by_name and e.get('answer')!=sub['name']),None)
 partner=by_name.get(prior.get('answer')) if prior else None
 # Duo has no "who in the room" answers, so the other player is automatically the Match partner.
 if not partner and len(active)==2:
  partner=next((p for p in active if p['id']!=sub['id']),None)
 if not partner or int(sub['active'] if sub['active'] is not None else 1)!=1:return None
 lang=game_language(g)
 # Pick a different secret prompt for each callback in the same game.  These
 # prompts are not regular questions, so they need their own repeat guard.
 prompt_index=sum(1 for e in mem(g) if 'callback' in str(e.get('type','')))
 if lang!='he':
  a,b=sub['name'],partner['name']
  extra={
   'en':[f'🍿 {a} and {b}: secretly type one snack you would both choose for tonight. Same answer = +1 point each.',f'📵 {a} and {b}: secretly type one thing you would do together on a day without phones. Same answer = +1 point each.'],
   'es':[f'🍿 {a} y {b}: escriban en secreto un snack que elegirían para esta noche. Misma respuesta = +1 punto para cada uno.',f'📵 {a} y {b}: escriban en secreto algo que harían juntos un día sin teléfonos. Misma respuesta = +1 punto para cada uno.'],
   'pt-BR':[f'🍿 {a} e {b}: escrevam em segredo um lanche que escolheriam para hoje. Mesma resposta = +1 ponto para cada um.',f'📵 {a} e {b}: escrevam em segredo algo que fariam juntos num dia sem celular. Mesma resposta = +1 ponto para cada um.'],
   'fr':[f'🍿 {a} et {b} : écrivez en secret un snack que vous choisiriez ce soir. Même réponse = +1 point chacun.',f'📵 {a} et {b} : écrivez en secret une activité à faire ensemble sans téléphone. Même réponse = +1 point chacun.'],
   'ja':[f'🍿 {a}と{b}：今夜2人で選ぶおやつを1つ、秘密で書いてください。同じ答えなら2人に1点。',f'📵 {a}と{b}：スマホなしの日に2人でしたいことを1つ、秘密で書いてください。同じ答えなら2人に1点。']
  }
  prompts=[match_prompt(lang,a,b)]+extra.get(lang,extra['en']);prompt=prompts[prompt_index%len(prompts)]
  return {'prompt':prompt,'player_ids':[sub['id'],partner['id']],'names':[a,b]}
 q=(text or '').lower()
 if any(k in q for k in ['טיול','טיסה','הרפתקה','חופשה','יעד']):
  prompts=[
   f'✈️ {sub["name"]} ו־{partner["name"]}: כל אחד כותב בסוד יעד אחד שהייתם טסים אליו מחר. אם כתבתם אותו יעד — נקודה לשניכם.',
   f'🧳 {sub["name"]} ו־{partner["name"]}: כל אחד כותב בסוד דבר אחד שחייב להיכנס למזוודה המשותפת. אותה תשובה — נקודה לשניכם.',
   f'🏖️ {sub["name"]} ו־{partner["name"]}: כל אחד כותב בסוד את הדבר הראשון שהייתם עושים בחופשה בלי תוכנית. אותה תשובה — נקודה לשניכם.'
  ];prompt=prompts[prompt_index%len(prompts)]
 elif any(k in q for k in ['דייט','קראש','היכרויות']):
  prompts=[
   f'😈 {sub["name"]} ו־{partner["name"]}: כל אחד כותב בסוד מקום אחד לדייט ספונטני. אם יצאתם על אותו רעיון — נקודה לשניכם.',
   f'💬 {sub["name"]} ו־{partner["name"]}: כל אחד כותב בסוד משפט פתיחה אחד שבאמת היה מצחיק את שניכם. אותה תשובה — נקודה לשניכם.',
   f'🍹 {sub["name"]} ו־{partner["name"]}: כל אחד כותב בסוד מה מזמינים קודם בדייט בלי תוכנית. אותה תשובה — נקודה לשניכם.'
  ];prompt=prompts[prompt_index%len(prompts)]
 elif any(k in q for k in ['50,000','כסף','תקציב','מיליון']):
  prompts=[
   f'💸 {sub["name"]} ו־{partner["name"]}: כל אחד כותב בסוד דבר אחד שהייתם מבזבזים עליו את הכסף. אותה תשובה — נקודה לשניכם.',
   f'🎁 {sub["name"]} ו־{partner["name"]}: כל אחד כותב בסוד מתנה מוגזמת אחת שהייתם קונים לקבוצה. אותה תשובה — נקודה לשניכם.',
   f'🎉 {sub["name"]} ו־{partner["name"]}: כל אחד כותב בסוד חוויה אחת ששווה לבזבז עליה הכול. אותה תשובה — נקודה לשניכם.'
  ];prompt=prompts[prompt_index%len(prompts)]
 elif any(k in q for k in ['משפחה','חג','ארוחה']):
  prompts=[
   f'🏠 {sub["name"]} ו־{partner["name"]}: כל אחד כותב בסוד פעילות אחת שהייתם בוחרים ליום משפחתי מושלם. אותה תשובה — נקודה לשניכם.',
   f'🍽️ {sub["name"]} ו־{partner["name"]}: כל אחד כותב בסוד מאכל אחד שחייב להיות בארוחה משפחתית. אותה תשובה — נקודה לשניכם.',
   f'🎲 {sub["name"]} ו־{partner["name"]}: כל אחד כותב בסוד משחק אחד שהמשפחה באמת תסכים לשחק. אותה תשובה — נקודה לשניכם.'
  ];prompt=prompts[prompt_index%len(prompts)]
 else:
  prompts=[
   f'⚡ {sub["name"]} ו־{partner["name"]}: כל אחד כותב בסוד דבר אחד שהייתם בוחרים לעשות יחד בסופ״ש חופשי. אותה תשובה — נקודה לשניכם.',
   f'🍿 {sub["name"]} ו־{partner["name"]}: כל אחד כותב בסוד בילוי אחד שמתאים לשניכם הערב. אותה תשובה — נקודה לשניכם.',
   f'😂 {sub["name"]} ו־{partner["name"]}: כל אחד כותב בסוד דבר אחד שתמיד מצחיק את שניכם. אותה תשובה — נקודה לשניכם.',
   f'📵 {sub["name"]} ו־{partner["name"]}: כל אחד כותב בסוד פעילות אחת שהייתם בוחרים ליום בלי טלפונים. אותה תשובה — נקודה לשניכם.'
  ];prompt=prompts[prompt_index%len(prompts)]
 return {'prompt':prompt,'player_ids':[sub['id'],partner['id']],'names':[sub['name'],partner['name']]}
def interactive_prompt(g,typ,text,answer,sub):
 d=interactive_match_data(g,typ,text,sub)
 return d['prompt'] if d else ''
def match_key(x):
 import re
 return re.sub(r'[^\w\u0590-\u05ff]+','',str(x or '').strip().lower(),flags=re.UNICODE)
def match_equal(a,b):
 ka,kb=match_key(a),match_key(b)
 if not ka or not kb:return False
 if ka==kb:return True
 try:
  from difflib import SequenceMatcher
  return SequenceMatcher(None,ka,kb).ratio()>=0.9
 except:return False
def duo_callback(g,ps,rn):
 return meaningful_callback(g,ps,rn,duo=True) if len(ps)==2 else None
def qdata(g,ps):
 rn=int(g['round_no']);tb=tie_data(g);order=tb.get('order',[])
 sub=next((p for p in ps if p['id']==order[(rn-tb['start'])%len(order)]),None) if order else (ps[rn%len(ps)] if ps else None)
 if not sub:sub=ps[rn%len(ps)] if ps else None
 lang=game_language(g)
 if lang=='he' and not tb:
  cb=duo_callback(g,ps,rn) if len(ps)==2 else smart_callback(g,ps,rn)
  if cb:return cb
 selected=effective_topics(g);tailored=custom_questions(g)
 if lang=='he':
  focused=[]
  for t in selected:focused+=TOPICS.get(t,[])
  def grounded(text):
   # Retire the remaining sketch-comedy fallbacks from live selection. The
   # question should be funny because of a recognizable social moment, not a
   # robot, celebrity, magic object or impossible stunt.
   bad=('רובוט','מלפפון','מיליון','תוכי','קריין','גביע עובד','תפקיד קטן בסרט','פנקייק נחת','אדם מפורסם','כרטיס אשראי בלי הגבלה','דלת בבית שמובילה','שש פיצות','ורוד וזוהר','שלוש דקות למלא עגלה','יום אחד שבו אף החלטה','כפתור שמאפשר לחזור שעה','מוזיקת כניסה של נבל')
   return not any(word in str(text) for word in bad)
  focused=[q for q in focused if grounded(q[1])]
  if int(g['spice'] or 1)==2:
   broad=not selected or any(t in THEME_ONLY for t in selected)
   comic=[('know',text,opts) for topic,text,opts in BOLD_COMEDY if grounded(text) and (broad or topic in selected) and (topic not in ADULT_TOPICS or topic in selected)]
   if comic:focused=comic+focused
  if int(g['spice'] or 1)>=3:focused+=SPICY
  # Ground every game in recognizable daily moments. Topic packs add flavor,
  # but a narrow topic must not force the fallback into abstract or cartoonish
  # prompts when the curated everyday pack is available.
  themed=len(selected)==1 and selected[0] in THEME_ONLY
  general=[q for q in GENERAL if grounded(q[1])]
  base=tailored+focused+EVERYDAY_CORE if (tailored or focused) else EVERYDAY_CORE
 else:
  native=general_pack(lang);spicy=spicy_pack(lang) if int(g['spice'] or 1)>=3 else []
  base=tailored+spicy+native
 if len(ps)==2:
  base=[q for q in base if q[0]!='room' and len(q[2])>=3]
  if not base:base=[q for q in (GENERAL if lang=='he' else general_pack(lang)) if q[0]=='know']
 if lang=='he' and int(g['spice'] or 1)==2 and comic:
  preferred=[q for q in tailored+comic+EVERYDAY_CORE if len(ps)!=2 or q[0]!='room']
  used_now={question_key(e.get('question',''),ps) for e in mem(g)}|past_question_keys(ps)
  if any(not too_similar(question_key(q[1].format(s=sub['name']),ps),used_now) for q in preferred):base=preferred
 used={question_key(e.get('question',''),ps) for e in mem(g)}
 used|=past_question_keys(ps)
 seed=sum(ord(ch) for ch in str(g['code']))+rn*7
 if lang=='he' and len(ps)>2 and not tb and rn%4==2:
  spark=[q for q in SOCIAL_SPARK if not ('רפסודה' in q[1] and any(word in str(g['custom_context'] or '').lower() for word in ('ילדים','children','kids')))]
  for step in range(len(spark)):
   typ,text,opts=spark[(seed//7+step)%len(spark)]
   formatted=text.format(s=sub['name'])
   if not too_similar(question_key(formatted,ps),used):
    return typ,formatted,[p['name'] for p in ps if p['id']!=sub['id']],sub
 chosen=None
 for step in range(len(base)):
  q=base[(seed+step)%len(base)];typ,text,opts=q;formatted=text.format(s=sub['name'])
  if not too_similar(question_key(formatted,ps),used):chosen=(typ,formatted,opts);break
 if chosen is None:
  fallback=[q for q in (general if lang=='he' else general_pack(lang)) if not (len(ps)==2 and q[0]=='room')]
  for q in fallback:
   typ,text,opts=q;formatted=text.format(s=sub['name'])
   if not too_similar(question_key(formatted,ps),used):chosen=(typ,formatted,opts);break
 if chosen is None:
  # Last-resort copy stays in the room language too.
  typ='know';formatted,opts=last_resort(lang,sub['name'],rn)
 else:typ,formatted,opts=chosen
 if typ=='room':opts=[p['name'] for p in ps if p['id']!=sub['id']]
 elif typ=='know':
  opts=[o for o in opts if str(o).strip().removeprefix('✏️').strip().casefold()!=other_label(lang).removeprefix('✏️').strip().casefold()]
  if str(g['answer']).startswith('OTHER::'):opts=list(opts)+[other_label(lang)]
 return typ,formatted,list(opts),sub
def _clean_pack(pack):
 clean=[];seen=set()
 for q in pack or []:
  if not isinstance(q,(list,tuple)) or len(q)!=3:continue
  key=str(q[1]).strip().lower()
  if key and key not in seen:seen.add(key);clean.append(q)
 return clean
def prepare_pack_async(gid,ts,ctx,spice,language='en'):
 try:
  with budget.scope(cn,gid,'questions'):
   pack=_clean_pack(generate_pack(ts,ctx,spice,normalize_language(language)))
  if not pack:return
  with cn() as c:
   g=c.execute('SELECT status FROM games WHERE id=?',(gid,)).fetchone()
   if g and g['status']=='lobby':c.execute('UPDATE games SET custom_questions=? WHERE id=?',(json.dumps(pack,ensure_ascii=False),gid))
 except Exception as e:print('async pack failed',type(e).__name__,str(e)[:200],flush=True)
def hero_round(rn,total):
 # AI Reveal is a core game mechanic: create one on every round when the spotlight player supplied a photo.
 return 0 <= int(rn) < int(total)
def image_url(g,rn):
 return '/api/hero-image/'+g['code']+'/'+str(rn)+'?run='+str(g['image_run'])
def image_payload(g,ps,final=False):
 if final:
  ws=winners(g,ps)
  if not final_image_eligible(g,ps):return None
  winner_ids={p['id'] for p in ws}
  available=ws+[p for p in ps if p['id'] not in winner_ids and p['photo_data'] and p['photo_consent']]
  prize=g['prize'] or 'bragging rights'
  names=[p['name'] for p in ws]
  return dict(items=[(p['name'],p['photo_data']) for p in available],
   question='Final cinematic ensemble winner poster. Prize: '+prize,
   answer=('Joint winners: ' if len(ws)>1 else 'Winner: ')+', '.join(names)+'. Prize for EACH winner: '+prize,
   focus=names[0],winners=names,selected='',final=True)
 typ,text,opts,sub=qdata(g,ps)
 if not sub or not sub['photo_data'] or not sub['photo_consent']:return None
 answer=str(g['answer']);answer=answer[7:] if answer.startswith('OTHER::') else answer
 # Exact selection, or an unambiguous whole-name mention in a free answer.
 import re
 related=[p for p in ps if p['id']!=sub['id'] and
          (p['name']==answer or re.search(r'(?<!\w)'+re.escape(p['name'])+r'(?!\w)',answer,re.I))]
 selected=related[0] if len(related)==1 else None
 cast=[sub]+([selected] if selected and selected['photo_data'] and selected['photo_consent'] else [])
 return dict(items=[(p['name'],p['photo_data']) for p in cast],question=text,answer=answer,
             focus=sub['name'],selected=selected['name'] if selected else '')
def prepare_hero_async(gid,rn,expected_run=None):
 # Reserve and snapshot quickly; only the durable worker performs the slow API call.
 with cn() as c:g=c.execute('SELECT * FROM games WHERE id=?',(gid,)).fetchone()
 if not g or (expected_run is not None and int(g['image_run'])!=int(expected_run)):return 'stale'
 final=int(rn)==99
 if final:
  if g['status']!='finished':return 'not_ready'
 elif g['status']!='playing' or int(g['round_no'])!=int(rn) or not g['answer']:return 'not_ready'
 ps=players(gid,include_photos=True)
 if not final:
  # Start generation as soon as the spotlight player's secret answer exists.
  # Image generation takes tens of seconds, so waiting for every prediction means
  # the Reveal is usually over before the image is ready. Guesses are not needed
  # to build the visual payload and remain private from the image prompt.
  sub=ps[int(rn)%len(ps)] if ps else None
  if not sub:return 'not_ready'
 payload=image_payload(g,ps,final)
 if not payload:return 'no_photo'
 # Queue the final image first. The legacy local preview must not delay the AI
 # request (the current UI deliberately hides that preview).
 result=image_jobs.queue(cn,g,int(rn),payload,generate_many) if os.getenv('OPENAI_API_KEY','').strip() else 'unavailable'
 try:instant.prepare(cn,g,int(rn),payload,ps)
 except Exception as e:print('instant visual failed',type(e).__name__,flush=True)
 return result
def _visual_worker(gid,rn,run,key):
 try:prepare_hero_async(gid,rn,run)
 except Exception as e:print('image scheduling failed',type(e).__name__,flush=True)
 finally:
  with VISUAL_TASKS_LOCK:VISUAL_TASKS.discard(key)
def schedule_image_after_action(gid):
 # Game actions must return immediately. Instant composition and Full AI queueing
 # run off the request thread so a slow image path can never block Join/Guess/State.
 try:
  with cn() as c:g=c.execute('SELECT status,round_no,image_run FROM games WHERE id=?',(gid,)).fetchone()
  if not g:return
  rn=99 if g['status']=='finished' else int(g['round_no']);run=int(g['image_run']);key=(int(gid),run,rn)
  with VISUAL_TASKS_LOCK:
   if key in VISUAL_TASKS:return
   VISUAL_TASKS.add(key)
  VISUAL_POOL.submit(_visual_worker,gid,rn,run,key)
 except Exception as e:print('image scheduling submit failed',type(e).__name__,flush=True)
def _portrait_worker(pid,data):
 try:
  with cn() as c:instant.save_portrait(c,pid,data)
 except Exception as e:print('portrait preprocess failed',type(e).__name__,flush=True)
def ensure_round_score(g,ps,guessed):
 sub=ps[int(g['round_no'])%len(ps)] if ps else None
 active_guessers=[p for p in ps if int(p['active'] if p['active'] is not None else 1)==1 and (not sub or p['id']!=sub['id'])]
 if not g['answer'] or len([p for p in active_guessers if p['id'] in guessed])<len(active_guessers):return False
 with cn() as c:
  if USE_PG:
   claimed=c.execute('INSERT INTO round_scores(game_id,round_no,created) VALUES(?,?,?) ON CONFLICT(game_id,round_no) DO NOTHING RETURNING round_no',(g['id'],g['round_no'],now())).fetchone()
   if not claimed:return False
  else:
   cur=c.execute('INSERT OR IGNORE INTO round_scores(game_id,round_no,created) VALUES(?,?,?)',(g['id'],g['round_no'],now()))
   if getattr(cur,'rowcount',0)!=1:return False
  actual=(other_label(game_language(g)) if str(g['answer']).startswith('OTHER::') else g['answer'])
  for pid,guess in guessed.items():
   if guess==actual:c.execute('UPDATE players SET score=score+1 WHERE id=?',(pid,))
 return True
def decode_data_url(data):
 try:
  import base64
  head,payload=str(data).split(',',1)
  mime=head.split(';')[0].split(':',1)[1]
  return mime,base64.b64decode(payload)
 except:return None,None
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
  if urlparse(self.path).path.startswith('/api/'):
   with request_connection():return self.get_impl()
  return self.get_impl()
 def get_impl(self):
  u=urlparse(self.path);p=u.path
  if p=='/health':return self.J({'ok':True,'game':'know-your-crew-visuals','image_pipeline':'hybrid-v1','release':'pilot-budget-v6','image_model':MODEL,'storage':'postgres' if USE_PG else 'sqlite-ephemeral','ai_images':bool(os.getenv('OPENAI_API_KEY','').strip())})
  if p=='/api/pricing':
   try:return self.J(budget.pricing(int(parse_qs(u.query).get('rounds',['18'])[0]),int(parse_qs(u.query).get('games',['1'])[0])))
   except (ValueError,TypeError):return self.J({'error':'invalid_quote'},400)
  if p.startswith('/api/costs/'):
   g=game(p.rsplit('/',1)[-1]);host=parse_qs(u.query).get('host',[''])[0]
   if not g or not host or not secrets.compare_digest(host,g['host']):return self.J({'error':'forbidden'},403)
   with cn() as c:return self.J(budget.report(c,g['id']))
  if p=='/pricing':return self.F(STATIC/'pricing.html')
  if p=='/play-mipo':return self.F(STATIC/'landing.html')
  if p=='/sw.js':return self.F(STATIC/'sw.js')
  if p in ('/','/index.html'):return self.F(STATIC/'kyc.html')
  if p.startswith('/static/'):return self.F(STATIC/p[8:])
  if p.startswith('/api/photo/'):
   a=p.strip('/').split('/')
   if len(a)!=4:return self.send_error(404)
   g=game(a[2])
   if not g:return self.send_error(404)
   try:pid=int(a[3])
   except:return self.send_error(404)
   with cn() as c:pl=c.execute('SELECT photo_data FROM players WHERE game_id=? AND id=?',(g['id'],pid)).fetchone()
   if not pl or not pl['photo_data']:return self.send_error(404)
   try:
    import base64
    head,data=pl['photo_data'].split(',',1);raw=base64.b64decode(data);mime=head.split(';')[0].split(':',1)[1]
    self.send_response(200);self.send_header('Content-Type',mime);self.send_header('Cache-Control','private, no-cache');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw);return
   except:return self.send_error(404)
  if p.startswith('/api/instant-image/'):
   a=p.strip('/').split('/')
   if len(a)!=4:return self.send_error(404)
   g=game(a[2])
   if not g:return self.send_error(404)
   try:rn=int(a[3]);run=int(parse_qs(u.query).get('run',['-1'])[0])
   except:return self.send_error(404)
   if run!=g['image_run']:return self.send_error(404)
   with cn() as c:row=c.execute('SELECT image_data FROM instant_scenes WHERE game_id=? AND image_run=? AND round_no=?',(g['id'],run,rn)).fetchone()
   if not row:return self.send_error(404)
   mime,raw=decode_data_url(row['image_data'])
   self.send_response(200);self.send_header('Content-Type',mime);self.send_header('Cache-Control','private, max-age=86400, immutable');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw);return
  if p.startswith('/api/hero-image/'):
   a=p.strip('/').split('/')
   if len(a)!=4:return self.send_error(404)
   g=game(a[2])
   if not g:return self.send_error(404)
   try:rn=int(a[3])
   except:return self.send_error(404)
   requested_run=parse_qs(u.query).get('run',[str(g['image_run'])])[0]
   if requested_run!=str(g['image_run']):return self.send_error(404)
   with cn() as c:row=c.execute('SELECT h.image_data FROM hero_scenes h JOIN games g ON g.id=h.game_id WHERE h.game_id=? AND h.round_no=? AND g.image_run=?',(g['id'],rn,g['image_run'])).fetchone()
   if not row or not row['image_data']:return self.send_error(404)
   mime,raw=decode_data_url(row['image_data'])
   if not raw:return self.send_error(404)
   self.send_response(200);self.send_header('Content-Type',mime or 'image/png');self.send_header('Cache-Control','private, no-cache');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw);return
  if p=='/api/meta':
   q=parse_qs(u.query);lang=normalize_language(q.get('lang',['en'])[0]);return self.J({'language':lang,'direction':direction(lang),'languages':SUPPORTED_LANGUAGES,'topics':{k:topic_labels([k],lang)[0] for k in TOPIC_LABELS},'copy':ui_copy(lang)})
  if p.startswith('/api/chat/'):
   a=p.strip('/').split('/');q=parse_qs(u.query);tok=q.get('token',[''])[0]
   if len(a)!=3:return self.J({'error':'not_found'},404)
   g=game_for_token(a[2],tok)
   if not g:return self.J({'error':'room_not_found'},404)
   try:after=max(0,int(q.get('after',['0'])[0]))
   except:return self.J({'error':'invalid_after'},400)
   with cn() as c:
    me=c.execute('SELECT id,last_seen,joined FROM players WHERE game_id=? AND token=? AND active=1',(g['id'],tok)).fetchone()
    if not me:return self.J({'error':'forbidden'},403)
    if not recently_seen(me,5):c.execute('UPDATE players SET last_seen=? WHERE id=?',(now(),me['id']))
    if after:
     rows=c.execute("SELECT m.id,m.player_id,COALESCE(p.name,'') AS name,m.kind,m.body,m.created FROM chat_messages m LEFT JOIN players p ON p.id=m.player_id WHERE m.game_id=? AND m.id>? ORDER BY m.id LIMIT 100",(g['id'],after)).fetchall()
    else:
     rows=c.execute("SELECT m.id,m.player_id,COALESCE(p.name,'') AS name,m.kind,m.body,m.created FROM chat_messages m LEFT JOIN players p ON p.id=m.player_id WHERE m.game_id=? ORDER BY m.id DESC LIMIT 60",(g['id'],)).fetchall()[::-1]
   messages=[{'id':r['id'],'player_id':r['player_id'],'name':r['name'],'kind':r['kind'],'body':r['body'],'created':r['created']} for r in rows]
   return self.J({'code':g['code'],'messages':messages,'latest_id':messages[-1]['id'] if messages else after})
  if p.startswith('/api/state/'):
   q=parse_qs(u.query);tok=q.get('token',[''])[0];host=q.get('host',[''])[0];g=game_for_token(p.split('/')[-1],tok)
   if not g:return self.J({'error':'room_not_found'},404)
   ps=players(g['id']);me=next((x for x in ps if x['token']==tok),None);typ,text,opts,sub=qdata(g,ps)
   if me and not recently_seen(me,5):
    try:
     with cn() as c:c.execute('UPDATE players SET last_seen=? WHERE id=?',(now(),me['id']))
    except:pass
   with cn() as c:
    gs=c.execute('SELECT player_id,guess FROM guesses WHERE game_id=? AND round_no=?',(g['id'],g['round_no'])).fetchall()
    hero_rounds={r['round_no'] for r in c.execute('SELECT round_no FROM hero_scenes WHERE game_id=? AND round_no IN (?,?)',(g['id'],g['round_no'],99)).fetchall()}
    # Expire this run once, then read both current/final statuses together.
    image_jobs.expire_jobs(c,g['id'],g['image_run'])
    jobs={r['round_no']:r['status'] for r in c.execute('SELECT round_no,status FROM image_jobs WHERE game_id=? AND image_run=? AND round_no IN (?,?)',(g['id'],g['image_run'],g['round_no'],99)).fetchall()}
    visuals={r['round_no']:r['category'] for r in c.execute('SELECT round_no,category FROM instant_scenes WHERE game_id=? AND image_run=?',(g['id'],g['image_run'])).fetchall()}
    vote_rows=c.execute('SELECT topic,COUNT(*) AS n FROM topic_votes WHERE game_id=? GROUP BY topic ORDER BY n DESC,topic',(g['id'],)).fetchall();state_votes={r['topic']:r['n'] for r in vote_rows}
    my_votes=[r['topic'] for r in c.execute('SELECT topic FROM topic_votes WHERE game_id=? AND player_id=?',(g['id'],me['id'] if me else -1)).fetchall()] if me else []
   guessed={r['player_id']:r['guess'] for r in gs};active_ids={x['id'] for x in ps if int(x['active'] if x['active'] is not None else 1)==1};need=len([x for x in ps if sub and x['id']!=sub['id'] and x['id'] in active_ids]);ready=bool(g['answer']) and len([pid for pid in guessed if pid in active_ids and (not sub or pid!=sub['id'])])>=need
   if ready and ensure_round_score(g,ps,guessed):
    ps=players(g['id']);me=next((x for x in ps if x['token']==tok),None)
   hero=g['round_no'] in hero_rounds;finalhero=99 in hero_rounds
   hero_status='ready' if hero else jobs.get(g['round_no'],'idle');final_hero_status='ready' if finalhero else jobs.get(99,'idle')
   instant_url=lambda rn:'/api/instant-image/'+g['code']+'/'+str(rn)+'?run='+str(g['image_run']) if rn in visuals else None
   reveal=ready or g['status']=='finished';myguess=guessed.get(me['id']) if me else None;actual=(other_label(game_language(g)) if str(g['answer']).startswith('OTHER::') else g['answer']);shown=(str(g['answer'])[7:] if str(g['answer']).startswith('OTHER::') else g['answer']);iscorrect=bool(reveal and myguess is not None and myguess==actual)
   state_topics=topics(g)
   for topic,_count in sorted(state_votes.items(),key=lambda x:(-x[1],x[0])):
    if topic not in state_topics:state_topics.append(topic)
   state_topics=state_topics[:10]
   is_host=bool(host and secrets.compare_digest(host,g['host']));presence={x['id']:(True if me and x['id']==me['id'] else recently_seen(x)) for x in ps}
   return self.J({
    'code':g['code'],'status':g['status'],'round':g['round_no'],'total':total_rounds(g),'is_host':is_host,
    'adult_required':adult_required(state_topics,g['spice']),'adults_ready':all(x['adult_confirmed'] for x in ps if x['active']),
    'me':{'adult_confirmed':bool(me['adult_confirmed']),'id':me['id'],'name':me['name'],'gender':me['gender'],'score':me['score'],'has_photo':bool(me['photo_data'])} if me else None,
    'players':[{'id':x['id'],'name':x['name'],'gender':x['gender'],'score':x['score'],'active':bool(int(x['active'] if x['active'] is not None else 1)),'connected':bool(presence.get(x['id'])),'can_continue_without':bool(is_host and g['status']=='playing' and int(x['active'] if x['active'] is not None else 1)==1 and (not me or x['id']!=me['id']) and not presence.get(x['id'])),'has_photo':bool(x['photo_data']),'photo_url':('/api/photo/'+g['code']+'/'+str(x['id'])) if x['photo_data'] else ''} for x in ps],
    'photo_count':sum(1 for x in ps if x['photo_data']),
    'subject':{'id':sub['id'],'name':sub['name'],'gender':sub['gender'],'has_photo':bool(sub['photo_data']),'photo_url':('/api/photo/'+g['code']+'/'+str(sub['id'])) if sub and sub['photo_data'] else ''} if sub else None,
    'type':typ,'question':text,'options':opts,'answer':shown if reveal else None,
    # Match Twist secret answers were removed: Reveal chat/reactions are non-blocking.
    'interactive':'','interactive_match':None,
    'answered':bool(g['answer']),'my_guess':myguess,'my_correct':iscorrect,
    'all_guesses':[{'player_id':x['id'],'name':x['name'],'gender':x['gender'],'guess':guessed.get(x['id']),'correct':guessed.get(x['id'])==actual,'photo_url':('/api/photo/'+g['code']+'/'+str(x['id'])) if x['photo_data'] else ''} for x in ps if sub and x['id']!=sub['id'] and x['id'] in guessed] if reveal else [],
    'guessed':bool(me and me['id'] in guessed),'guess_count':len(guessed),'guess_need':need,
    'waiting_for':[x['name'] for x in ps if sub and x['id']!=sub['id'] and x['id'] in active_ids and x['id'] not in guessed],
    'reveal':reveal,'image_run':g['image_run'],'hero_eligible':bool(sub and sub['photo_data'] and sub['photo_consent']),
    'final_image_eligible':final_image_eligible(g,ps),'winner_ids':[p['id'] for p in winners(g,ps)],
    'tiebreak':tie_data(g),'can_tiebreak':can_tiebreak(g,ps),'instant_visual':instant_url(g['round_no']),
    'instant_category':visuals.get(g['round_no']),'final_instant_visual':instant_url(99),
    'hero_status':hero_status,'final_hero_status':final_hero_status,
    'hero':image_url(g,g['round_no']) if hero and reveal else None,
    'final_hero':image_url(g,99) if finalhero and g['status']=='finished' else None,
    'topics':state_topics,'topics_display':topic_labels(state_topics,game_language(g)),'direction':direction(game_language(g)),
    'topic_votes':state_votes,'my_topic_votes':my_votes,'mode':'duo' if len(ps)==2 else 'group',
    'ai_images_ready':bool(os.getenv('OPENAI_API_KEY','').strip()),'spice':g['spice'],'context':g['custom_context'],
    'prize':g['prize'],'rounds':total_rounds(g),'language':game_language(g),
    'can_reopen':bool(g['status']=='playing' and int(g['round_no'])==0 and not mem(g) and not reveal),'history':mem(g)[-4:]
   })
  return self.J({'error':'not_found'},404)
 def do_POST(self):
  try:return self.post_impl()
  except budget.BudgetLimit as e:return self.J({'error':str(e)},429)
 def post_impl(self):
  p=urlparse(self.path).path;d=self.B()
  if p=='/api/create':
   name=str(d.get('name','')).strip()[:40]
   if not name:return self.J({'error':'name_required'},400)
   co=code5();ht=secrets.token_urlsafe(16);pt=secrets.token_urlsafe(16);ts=d.get('topics',[]);ts=ts if isinstance(ts,list) else [];ctx=str(d.get('context','')).strip()[:700];sp=max(1,min(3,int(d.get('spice',1) or 1)));prize=str(d.get('prize','')).strip()[:180];rounds=max(6,min(30,int(d.get('rounds',12) or 12)));client_id=str(d.get('client_id','')).strip()[:120];language=normalize_language(d.get('language','en'))
   adult=adult_required(ts,sp)
   if adult and not d.get('adults_confirmed'):return self.J({'error':'adults_confirmation_required'},400)
   with cn() as c:
    if USE_PG:gid=c.execute('INSERT INTO games(code,host,topics,custom_context,spice,prize,rounds,adults_confirmed,language,created) VALUES(?,?,?,?,?,?,?,?,?,?) RETURNING id',(co,ht,json.dumps(ts,ensure_ascii=False),ctx,sp,prize,rounds,1 if adult else 0,language,now())).fetchone()['id']
    else:gid=c.execute('INSERT INTO games(code,host,topics,custom_context,spice,prize,rounds,adults_confirmed,language,created) VALUES(?,?,?,?,?,?,?,?,?,?)',(co,ht,json.dumps(ts,ensure_ascii=False),ctx,sp,prize,rounds,1 if adult else 0,language,now())).lastrowid
    if os.getenv('OPENAI_API_KEY','').strip():budget.admit(c,gid)
    c.execute('INSERT INTO players(game_id,name,token,joined,active,last_seen,client_id,gender) VALUES(?,?,?,?,1,?,?,?)',(gid,name,pt,now(),now(),client_id,normalize_gender(d.get('gender'))))
   if adult:
    with cn() as c:c.execute('UPDATE players SET adult_confirmed=1 WHERE token=?',(pt,))
   Thread(target=prepare_pack_async,args=(gid,effective_topics(game(co)),ctx,sp,language),daemon=True).start()
   return self.J({'code':co,'host':ht,'token':pt,'name':name,'language':language})
  if p=='/api/join':
   code=str(d.get('code','')).strip().upper();name=str(d.get('name','')).strip()[:40];client_id=str(d.get('client_id','')).strip()[:120]
   if not name:return self.J({'error':'name_required'},400)
   payload=None;status=200
   with cn() as c:
    if not USE_PG:c.execute('BEGIN IMMEDIATE')
    g=c.execute('SELECT * FROM games WHERE code=?'+(' FOR UPDATE' if USE_PG else ''),(code,)).fetchone()
    if not g:payload,status={'error':'not_found'},404
    else:
     room_players=_players(c,g['id']);existing=next((x for x in room_players if client_id and (x['client_id'] or '')==client_id),None) or next((x for x in room_players if _norm_name(x['name'])==_norm_name(name)),None)
     if existing:
      if g['status']!='lobby' and int(existing['active'] if existing['active'] is not None else 1)==0:payload,status={'error':'removed_from_game'},409
      else:
       c.execute("UPDATE players SET active=1,last_seen=?,client_id=CASE WHEN client_id='' THEN ? ELSE client_id END WHERE id=?",(now(),client_id,existing['id']))
       payload={'code':g['code'],'token':existing['token'],'name':existing['name'],'recovered':True}
     elif g['status']!='lobby':payload,status={'error':'started'},409
     elif len([x for x in room_players if int(x['active'] if x['active'] is not None else 1)==1])>=6:payload,status={'error':'full'},409
     else:
      tok=secrets.token_urlsafe(16)
      c.execute('INSERT INTO players(game_id,name,token,joined,active,last_seen,client_id,gender) VALUES(?,?,?,?,1,?,?,?)',(g['id'],name,tok,now(),now(),client_id,normalize_gender(d.get('gender'))))
      payload={'code':g['code'],'token':tok,'name':name}
   return self.J(payload,status)
  a=p.strip('/').split('/')
  if len(a)!=3 or a[0]!='api':return self.J({'error':'not_found'},404)
  act=a[2];tok=str(d.get('token',''))
  player_actions=('photo','answer','guess','chat','profile','topicvote','adultconfirm','matchanswer')
  g=game_for_token(a[1],tok) if act in player_actions else game(a[1])
  if not g:return self.J({'error':'room_not_found'},404)
  ps=players(g['id'])
  if act=='chat':
   me=next((x for x in ps if x['token']==tok and int(x['active'] if x['active'] is not None else 1)==1),None)
   if not me:return self.J({'error':'forbidden'},403)
   kind=str(d.get('kind','text')).strip().lower();body=str(d.get('body',d.get('message',''))).strip();client_msg_id=str(d.get('client_msg_id','')).strip()[:80]
   if not client_msg_id:return self.J({'error':'client_msg_id_required'},400)
   if kind=='reaction':
    if body not in CHAT_REACTIONS:return self.J({'error':'invalid_reaction'},400)
   elif kind=='text':
    if not body:return self.J({'error':'message_required'},400)
    if len(body)>280:return self.J({'error':'message_too_long'},400)
   else:return self.J({'error':'invalid_kind'},400)
   created=now()
   with cn() as c:
    if USE_PG:
     inserted=c.execute('INSERT INTO chat_messages(game_id,player_id,kind,body,client_msg_id,created) VALUES(?,?,?,?,?,?) ON CONFLICT DO NOTHING RETURNING id',(g['id'],me['id'],kind,body,client_msg_id,created)).fetchone()
     mid=inserted['id'] if inserted else None
    else:
     cur=c.execute('INSERT OR IGNORE INTO chat_messages(game_id,player_id,kind,body,client_msg_id,created) VALUES(?,?,?,?,?,?)',(g['id'],me['id'],kind,body,client_msg_id,created));mid=cur.lastrowid if getattr(cur,'rowcount',0)==1 else None
    if not mid:
     existing=c.execute('SELECT id FROM chat_messages WHERE game_id=? AND player_id=? AND client_msg_id=?',(g['id'],me['id'],client_msg_id)).fetchone();mid=existing['id'] if existing else None
    row=c.execute("SELECT m.id,m.player_id,COALESCE(p.name,'') AS name,m.kind,m.body,m.created FROM chat_messages m LEFT JOIN players p ON p.id=m.player_id WHERE m.id=? AND m.game_id=?",(mid,g['id'])).fetchone() if mid else None
   if not row:return self.J({'error':'chat_save_failed'},503)
   return self.J({'ok':True,'code':g['code'],'message':{'id':row['id'],'player_id':row['player_id'],'name':row['name'],'kind':row['kind'],'body':row['body'],'created':row['created']}})
  needs_question=act in ('reopen','drop','tiebreak','answer','guess','hero','finalhero','skip','next')
  typ,text,opts,sub=qdata(g,ps) if needs_question else (None,'',[],None)
  host_actions=('start','next','hero','finalhero','skip','settings','reopen','drop','replay','freshroom','tiebreak')
  if act in host_actions and not(d.get('host') and secrets.compare_digest(str(d['host']),g['host'])):return self.J({'error':'forbidden'},403)
  if act in ('answer','guess','skip','next','hero'):
   if g['status']!='playing':return self.J({'error':'not_playing'},409)
   if d.get('image_run') is not None and str(d['image_run'])!=str(g['image_run']):return self.J({'error':'stale_image_run'},409)
   if d.get('round') is not None and str(d['round'])!=str(g['round_no']):return self.J({'error':'stale_round'},409)
  if act=='finalhero' and g['status']!='finished':return self.J({'error':'not_finished'},409)
  if act=='freshroom':
   old_code=g['code'];new_code=code5()
   with cn() as c:
    if not USE_PG:c.execute('BEGIN IMMEDIATE')
    current=c.execute('SELECT * FROM games WHERE id=?'+(' FOR UPDATE' if USE_PG else ''),(g['id'],)).fetchone()
    if not current or current['code']!=old_code:return self.J({'error':'stale_room'},409)
    if not secrets.compare_digest(str(d.get('host','')),current['host']):return self.J({'error':'forbidden'},403)
    if os.getenv('OPENAI_API_KEY','').strip():budget.admit(c,g['id'],fresh=True)
    # A preserved room means the currently active crew. Players already removed
    # from the run stay removed; photos, tokens, profiles and consents remain.
    c.execute('DELETE FROM players WHERE game_id=? AND active=0',(g['id'],))
    c.execute("UPDATE games SET code=?,status='lobby',round_no=0,answer='',memory='[]',custom_questions='[]',tiebreak='{}',image_run=image_run+1 WHERE id=? AND code=?",(new_code,g['id'],old_code))
    c.execute('UPDATE players SET score=0,last_seen=? WHERE game_id=?',(now(),g['id']))
    for table in ('guesses','round_scores','match_answers','match_scores','image_jobs','hero_scenes','instant_scenes','chat_messages'):
     c.execute('DELETE FROM '+table+' WHERE game_id=?',(g['id'],))
   fresh=game(new_code)
   Thread(target=prepare_pack_async,args=(g['id'],effective_topics(fresh),fresh['custom_context'],int(fresh['spice'] or 1),game_language(fresh)),daemon=True).start()
   return self.J({'ok':True,'code':new_code,'old_code':old_code,'preserved':True})
  if act=='reopen':
   if g['status']!='playing' or int(g['round_no'])!=0 or mem(g):return self.J({'error':'too_late'},409)
   with cn() as c:
    rgs=c.execute('SELECT player_id FROM guesses WHERE game_id=? AND round_no=?',(g['id'],g['round_no'])).fetchall()
   active_ids={x['id'] for x in ps if int(x['active'] if x['active'] is not None else 1)==1};need=len([x for x in ps if sub and x['id']!=sub['id'] and x['id'] in active_ids]);first_reveal=bool(g['answer']) and len([r for r in rgs if r['player_id'] in active_ids and (not sub or r['player_id']!=sub['id'])])>=need
   if first_reveal:return self.J({'error':'too_late'},409)
   with cn() as c:
    c.execute("UPDATE games SET status='lobby',round_no=0,answer='' WHERE id=?",(g['id'],))
    c.execute('DELETE FROM guesses WHERE game_id=?',(g['id'],));c.execute('DELETE FROM round_scores WHERE game_id=?',(g['id'],));c.execute('UPDATE games SET image_run=image_run+1 WHERE id=?',(g['id'],));c.execute('DELETE FROM image_jobs WHERE game_id=?',(g['id'],));c.execute('DELETE FROM hero_scenes WHERE game_id=?',(g['id'],));c.execute('DELETE FROM instant_scenes WHERE game_id=?',(g['id'],))
   return self.J({'ok':True})
  if act=='drop':
   try:pid=int(d.get('player_id',0))
   except:return self.J({'error':'invalid_player'},400)
   target=next((x for x in ps if x['id']==pid),None)
   if not target:return self.J({'error':'player_not_found'},404)
   active=[x for x in ps if int(x['active'] if x['active'] is not None else 1)==1]
   if g['status']=='lobby' and len(active)<=2:return self.J({'error':'need_2'},409)
   if g['status']=='playing' and len(active)<=2:
    with cn() as c:
     c.execute('UPDATE players SET active=0 WHERE id=? AND game_id=?',(pid,g['id']))
     c.execute("UPDATE games SET status='finished',answer='' WHERE id=?",(g['id'],))
    return self.J({'ok':True,'name':target['name'],'finished':True})
   if g['status']=='playing' and sub and target['id']==sub['id'] and not g['answer']:
    mm=mem(g);mm.append({'round':g['round_no'],'subject':sub['name'],'question':text,'answer':'SKIPPED','type':'disconnect_skip'});rn=int(g['round_no'])+1;remember_question(ps,text)
    with cn() as c:
     c.execute('DELETE FROM players WHERE id=? AND game_id=?',(pid,g['id']));c.execute('DELETE FROM guesses WHERE game_id=? AND round_no=?',(g['id'],g['round_no']));c.execute('DELETE FROM match_answers WHERE game_id=? AND round_no=?',(g['id'],g['round_no']));c.execute('DELETE FROM match_scores WHERE game_id=? AND round_no=?',(g['id'],g['round_no']))
     if rn>=total_rounds(g):c.execute("UPDATE games SET status='finished',answer='',memory=? WHERE id=?",(json.dumps(mm,ensure_ascii=False),g['id']))
     else:c.execute("UPDATE games SET round_no=?,answer='',memory=? WHERE id=?",(rn,json.dumps(mm,ensure_ascii=False),g['id']))
    return self.J({'ok':True,'name':target['name'],'advanced':True})
   with cn() as c:
    if g['status']=='lobby':c.execute('DELETE FROM players WHERE id=? AND game_id=?',(pid,g['id']))
    else:c.execute('UPDATE players SET active=0 WHERE id=? AND game_id=?',(pid,g['id']))
   return self.J({'ok':True,'name':target['name']})
  if act=='tiebreak':
   # Serialize host retries and stale clicks. A complete subject cycle gives everyone
   # the same number of guesses; callbacks/bonus points are disabled for this cycle.
   with cn() as c:
    if not USE_PG:c.execute('BEGIN IMMEDIATE')
    g=c.execute('SELECT * FROM games WHERE id=?'+(' FOR UPDATE' if USE_PG else ''),(g['id'],)).fetchone()
    if not can_tiebreak(g,ps):return self.J({'error':'tiebreak_unavailable'},409)
    if str(d.get('image_run'))!=str(g['image_run']):return self.J({'error':'stale_image_run'},409)
    active=[p for p in ps if p['active']];start=total_rounds(g)
    tb={'sets':tie_data(g).get('sets',0)+1,'start':start,'end':start+len(active),
        'order':[p['id'] for p in active],'contenders':[p['id'] for p in winners(g,ps)]}
    c.execute("UPDATE games SET status='playing',round_no=?,answer='',tiebreak=?,image_run=image_run+1 WHERE id=?",(start,json.dumps(tb),g['id']))
    c.execute('DELETE FROM image_jobs WHERE game_id=?',(g['id'],))
    c.execute('DELETE FROM hero_scenes WHERE game_id=?',(g['id'],))
    c.execute('DELETE FROM instant_scenes WHERE game_id=?',(g['id'],))
   return self.J({'ok':True})
  if act=='replay':
   with cn() as c:
    if not USE_PG:c.execute('BEGIN IMMEDIATE')
    current=c.execute('SELECT * FROM games WHERE id=?'+(' FOR UPDATE' if USE_PG else ''),(g['id'],)).fetchone()
    if not current or current['status']!='finished':return self.J({'error':'not_finished'},409)
    if os.getenv('OPENAI_API_KEY','').strip():budget.admit(c,g['id'],fresh=True)
    c.execute("UPDATE games SET status='lobby',round_no=0,answer='',memory='[]',custom_questions='[]',tiebreak='{}',image_run=image_run+1 WHERE id=? AND status='finished'",(g['id'],))
    c.execute('DELETE FROM players WHERE game_id=? AND active=0',(g['id'],));c.execute('UPDATE players SET score=0,last_seen=? WHERE game_id=?',(now(),g['id']))
    for table in ('guesses','image_jobs','hero_scenes','instant_scenes','round_scores','match_answers','match_scores','chat_messages'):
     c.execute('DELETE FROM '+table+' WHERE game_id=?',(g['id'],))
   fresh=game(g['code'])
   Thread(target=prepare_pack_async,args=(g['id'],effective_topics(fresh),fresh['custom_context'],int(fresh['spice'] or 1),game_language(fresh)),daemon=True).start()
   return self.J({'ok':True})
  if act=='settings':
   if g['status']!='lobby':return self.J({'error':'already_started'},409)
   ts=d.get('topics',[])
   if not isinstance(ts,list):ts=[]
   ts=[str(x)[:60] for x in ts[:12]]
   ctx=str(d.get('context','')).strip()[:700];prize=str(d.get('prize','')).strip()[:180];rounds=max(6,min(30,int(d.get('rounds',g['rounds']) or 12)));language=normalize_language(d.get('language',game_language(g)))
   try:sp=max(1,min(3,int(d.get('spice',g['spice']) or 1)))
   except:sp=int(g['spice'] or 1)
   adult=adult_required(ts,sp)
   if adult and not d.get('adults_confirmed'):return self.J({'error':'adults_confirmation_required'},400)
   with cn() as c:c.execute('UPDATE games SET topics=?,custom_context=?,spice=?,prize=?,rounds=?,custom_questions=?,adults_confirmed=?,language=? WHERE id=?',(json.dumps(ts,ensure_ascii=False),ctx,sp,prize,rounds,'[]',1 if adult else 0,language,g['id']))
   fresh=game(g['code']);Thread(target=prepare_pack_async,args=(g['id'],effective_topics(fresh),ctx,sp,language),daemon=True).start();return self.J({'ok':True,'language':language})
  if act=='profile':
   me=next((x for x in ps if x['token']==d.get('token')),None)
   if not me:return self.J({'error':'player_not_found'},404)
   gender=d.get('gender')
   if gender not in ('male','female','unspecified'):return self.J({'error':'invalid_gender'},400)
   with cn() as c:c.execute('UPDATE players SET gender=? WHERE id=?',(gender,me['id']))
   return self.J({'ok':True})
  if act=='photo':
   me=next((x for x in ps if x['token']==d.get('token')),None);data=d.get('data_url','')
   if not me:return self.J({'error':'player_not_found'},404)
   if not d.get('consent'):return self.J({'error':'consent_required'},400)
   if not isinstance(data,str) or not data.startswith('data:image/'):return self.J({'error':'invalid_image'},400)
   if len(data)>5_600_000:return self.J({'error':'image_too_large'},400)
   try:decode_image(data)
   except Exception:return self.J({'error':'invalid_image'},400)
   try:
    # Save the original photo first and respond immediately. Portrait preprocessing
    # is best-effort background work and must never make the lobby or room unavailable.
    with cn() as c:c.execute('UPDATE players SET photo_data=?,photo_consent=1 WHERE id=?',(data,me['id']))
    VISUAL_POOL.submit(_portrait_worker,me['id'],data)
   except Exception as e:
    print('photo save db error',type(e).__name__,flush=True);return self.J({'error':'photo_save_failed'},503)
   return self.J({'ok':True,'bytes':len(data),'photo_ready':True,'has_photo':True,'portrait':'processing'})
  if act=='topicvote':
   me=next((x for x in ps if x['token']==d.get('token')),None);topic=str(d.get('topic','')).strip()[:80]
   if not me or g['status']!='lobby':return self.J({'error':'not_allowed'},403)
   if topic not in TOPICS:return self.J({'error':'invalid_topic'},400)
   if topic in ADULT_TOPICS and not int(g['adults_confirmed'] or 0):return self.J({'error':'adults_confirmation_required'},409)
   with cn() as c:
    old=c.execute('SELECT 1 FROM topic_votes WHERE game_id=? AND player_id=? AND topic=?',(g['id'],me['id'],topic)).fetchone()
    if old:c.execute('DELETE FROM topic_votes WHERE game_id=? AND player_id=? AND topic=?',(g['id'],me['id'],topic))
    else:
     count=c.execute('SELECT COUNT(*) AS n FROM topic_votes WHERE game_id=? AND player_id=?',(g['id'],me['id'])).fetchone()['n']
     if count>=6:return self.J({'error':'max_topics'},409)
     c.execute('INSERT INTO topic_votes(game_id,player_id,topic) VALUES(?,?,?)',(g['id'],me['id'],topic))
   return self.J({'ok':True})
  if act=='adultconfirm':
   me=next((x for x in ps if x['token']==d.get('token')),None)
   if not me:return self.J({'error':'forbidden'},403)
   if d.get('confirmed') is not True:return self.J({'error':'adults_confirmation_required'},400)
   with cn() as c:c.execute('UPDATE players SET adult_confirmed=1 WHERE id=?',(me['id'],))
   return self.J({'ok':True})
  if act=='start':
   with cn() as c:
    if not USE_PG:c.execute('BEGIN IMMEDIATE')
    current=c.execute('SELECT * FROM games WHERE id=?'+(' FOR UPDATE' if USE_PG else ''),(g['id'],)).fetchone()
    if not current or current['status']!='lobby':return self.J({'error':'already_started'},409)
    active=[x for x in _players(c,g['id']) if int(x['active'] if x['active'] is not None else 1)==1]
    if len(active)<2:return self.J({'error':'need_2'},409)
    if any(not x['photo_data'] or not x['photo_consent'] for x in active):return self.J({'error':'photos_required'},409)
    selected=topics(current);vote_rows=c.execute('SELECT topic,COUNT(*) AS n FROM topic_votes WHERE game_id=? GROUP BY topic ORDER BY n DESC,topic',(g['id'],)).fetchall()
    for row in vote_rows:
     if row['topic'] not in selected:selected.append(row['topic'])
    if adult_required(selected[:10],current['spice']) and any(not x['adult_confirmed'] for x in active):return self.J({'error':'adults_confirmation_required'},409)
    # Tailored questions are prepared in the lobby; starting stays a single CAS.
    pack=_clean_pack(custom_questions(current))
    cur=c.execute("UPDATE games SET status='playing',round_no=0,answer='',memory='[]',custom_questions=?,image_run=image_run+1 WHERE id=? AND status='lobby'",(json.dumps(pack,ensure_ascii=False),g['id']))
    if getattr(cur,'rowcount',0)!=1:return self.J({'error':'already_started'},409)
    for table in ('guesses','image_jobs','hero_scenes','instant_scenes','round_scores','match_answers','match_scores'):
     c.execute('DELETE FROM '+table+' WHERE game_id=?',(g['id'],))
   return self.J({'ok':True,'tailored_questions':len(pack)})
  if act=='answer':
   me=next((x for x in ps if x['token']==d.get('token')),None);ans=str(d.get('answer',''))[:160]
   if not me or not sub or me['id']!=sub['id']:return self.J({'error':'subject_only'},403)
   if ans.startswith('OTHER::'):
    custom=ans[7:].strip()
    if other_label(game_language(g)) not in opts or len(custom)<1:return self.J({'error':'invalid_answer'},400)
    ans='OTHER::'+custom[:120]
   elif ans not in opts:return self.J({'error':'invalid_answer'},400)
   with cn() as c:
    cur=c.execute("UPDATE games SET answer=? WHERE id=? AND answer=''",(ans,g['id']))
    changed=getattr(cur,'rowcount',0)==1
    if not changed:
     old=c.execute('SELECT answer FROM games WHERE id=?',(g['id'],)).fetchone();return self.J({'ok':True,'locked':True,'answer_saved':bool(old and old['answer'])})
   schedule_image_after_action(g['id'])
   return self.J({'ok':True})
  if act=='guess':
   me=next((x for x in ps if x['token']==d.get('token')),None);guess=str(d.get('guess',''))[:120]
   if not me or not sub or me['id']==sub['id']:return self.J({'error':'invalid_player'},403)
   if guess not in opts:return self.J({'error':'invalid_guess'},400)
   with cn() as c:
    if USE_PG:c.execute('INSERT INTO guesses(game_id,round_no,player_id,guess) VALUES(?,?,?,?) ON CONFLICT(game_id,round_no,player_id) DO NOTHING',(g['id'],g['round_no'],me['id'],guess))
    else:c.execute('INSERT OR IGNORE INTO guesses(game_id,round_no,player_id,guess) VALUES(?,?,?,?)',(g['id'],g['round_no'],me['id'],guess))
    rows=c.execute('SELECT player_id,guess FROM guesses WHERE game_id=? AND round_no=?',(g['id'],g['round_no'])).fetchall()
    active_ids={x['id'] for x in ps if int(x['active'] if x['active'] is not None else 1)==1}
    need=len([x for x in ps if sub and x['id']!=sub['id'] and x['id'] in active_ids])
    if g['answer'] and len([r for r in rows if r['player_id'] in active_ids])>=need:
     if USE_PG:claimed=c.execute('INSERT INTO round_scores(game_id,round_no,created) VALUES(?,?,?) ON CONFLICT(game_id,round_no) DO NOTHING RETURNING round_no',(g['id'],g['round_no'],now())).fetchone()
     else:
      cur=c.execute('INSERT OR IGNORE INTO round_scores(game_id,round_no,created) VALUES(?,?,?)',(g['id'],g['round_no'],now()));claimed=True if getattr(cur,'rowcount',0)==1 else None
     if claimed:
      for r in rows:
       if r['player_id'] in active_ids and r['guess']==(other_label(game_language(g)) if str(g['answer']).startswith('OTHER::') else g['answer']):c.execute('UPDATE players SET score=score+1 WHERE id=?',(r['player_id'],))
   fresh=players(g['id'])
   return self.J({'ok':True,'scores':{x['name']:x['score'] for x in fresh}})
  if act=='matchanswer':
   return self.J({'error':'not_allowed'},403)
  if act in ('hero','finalhero'):
   rn=99 if act=='finalhero' else int(g['round_no'])
   if d.get('image_run') is not None and str(d['image_run'])!=str(g['image_run']):return self.J({'error':'stale_image_run'},409)
   if act=='hero' and d.get('round') is not None and str(d['round'])!=str(rn):return self.J({'error':'stale_round'},409)
   if d.get('retry'):
    with cn() as c:
     c.execute("DELETE FROM image_jobs WHERE game_id=? AND image_run=? AND round_no=? AND status='failed'",(g['id'],g['image_run'],rn))
   result=prepare_hero_async(g['id'],rn,g['image_run'])
   return self.J({'ok':True,'status':result,'image':image_url(g,rn) if result=='ready' else None},202 if result in ('queued','running') else 200)
  if act=='skip':
   mm=mem(g);mm.append({'round':g['round_no'],'subject':sub['name'] if sub else '','question':text,'answer':'SKIPPED','type':'skip'});rn=int(g['round_no'])+1
   remember_question(ps,text)
   with cn() as c:
    c.execute('DELETE FROM guesses WHERE game_id=? AND round_no=?',(g['id'],g['round_no']))
    c.execute('DELETE FROM players WHERE game_id=? AND active=0',(g['id'],))
    remaining=c.execute('SELECT COUNT(*) AS n FROM players WHERE game_id=?',(g['id'],)).fetchone()['n']
    if rn>=total_rounds(g) or remaining<2:c.execute("UPDATE games SET status='finished',answer='',memory=? WHERE id=?",(json.dumps(mm,ensure_ascii=False),g['id']))
    else:c.execute("UPDATE games SET round_no=?,answer='',memory=? WHERE id=?",(rn,json.dumps(mm,ensure_ascii=False),g['id']))
   return self.J({'ok':True,'skipped':True})
  if act=='next':
   with cn() as c:
    gs=c.execute('SELECT player_id,guess FROM guesses WHERE game_id=? AND round_no=?',(g['id'],g['round_no'])).fetchall()
    active_ids={x['id'] for x in ps if int(x['active'] if x['active'] is not None else 1)==1}
    need=len([x for x in ps if sub and x['id']!=sub['id'] and x['id'] in active_ids])
    if not g['answer'] or len([r for r in gs if r['player_id'] in active_ids])<need:return self.J({'error':'not_ready'},409)
    clean_answer=(str(g['answer'])[7:] if str(g['answer']).startswith('OTHER::') else g['answer']);mm=mem(g);mm.append({'round':g['round_no'],'subject':sub['name'],'question':text,'answer':clean_answer,'type':typ});rn=int(g['round_no'])+1
    c.execute('DELETE FROM players WHERE game_id=? AND active=0',(g['id'],))
    remaining=c.execute('SELECT COUNT(*) AS n FROM players WHERE game_id=?',(g['id'],)).fetchone()['n']
    if rn>=total_rounds(g) or remaining<2:c.execute("UPDATE games SET status='finished',memory=? WHERE id=?",(json.dumps(mm,ensure_ascii=False),g['id']))
    else:c.execute("UPDATE games SET round_no=?,answer='',memory=? WHERE id=?",(rn,json.dumps(mm,ensure_ascii=False),g['id']))
   remember_question(ps,text)
   return self.J({'ok':True})
  return self.J({'error':'not_found'},404)
 def log_message(self,*a):pass
def run():init();instant.warm();warm_image_runtime();image_jobs.recover(cn,generate_many);ThreadingHTTPServer(('0.0.0.0',int(os.getenv('PORT','5000'))),H).serve_forever()
