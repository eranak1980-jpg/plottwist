import json,os,random,secrets,sqlite3,mimetypes
from threading import Thread
from datetime import datetime,timezone
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse,parse_qs
from kyc_questions import GENERAL,TOPICS,SPICY
from kyc_locales import SUPPORTED_LANGUAGES,language_code,other_label,localized_general,callback_text,match_prompt,last_resort_question
from kyc_visuals import generate_many
from kyc_ai import generate_pack
BASE=Path(__file__).parent;DB=Path(os.getenv('DATABASE_PATH',BASE/'kyc.db'));DATABASE_URL=os.getenv('DATABASE_URL','').strip();USE_PG=DATABASE_URL.startswith(('postgres://','postgresql://'));STATIC=BASE/'static';TOTAL=12;PRESENCE_TIMEOUT=12;ADULT_TOPICS={'אינטימיות למבוגרים','Adult / Intimacy (18+)'};THEME_ONLY={'מה היית עושה אם…','דילמות','מביך אבל מצחיק','מי הכי…','סודות והרגלים','נוסטלגיה','טיולים וחופשות','חלומות ופנטזיות','כסף מטורף'}
def now():return datetime.now(timezone.utc).isoformat()
def adult_required(ts,spice=1):return int(spice or 1)>=3 or bool(ADULT_TOPICS.intersection(set(ts or [])))
def recently_seen(p,timeout=PRESENCE_TIMEOUT):
 raw=(p['last_seen'] if 'last_seen' in p.keys() else '') or (p['joined'] if 'joined' in p.keys() else '')
 if not raw:return False
 try:
  dt=datetime.fromisoformat(str(raw).replace('Z','+00:00'));return (datetime.now(timezone.utc)-dt).total_seconds()<=timeout
 except:return False
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
   c.execute("""CREATE TABLE IF NOT EXISTS games(id BIGSERIAL PRIMARY KEY,code TEXT UNIQUE,host TEXT,status TEXT DEFAULT 'lobby',round_no INTEGER DEFAULT 0,answer TEXT DEFAULT '',memory TEXT DEFAULT '[]',topics TEXT DEFAULT '[]',custom_context TEXT DEFAULT '',spice INTEGER DEFAULT 1,custom_questions TEXT DEFAULT '[]',prize TEXT DEFAULT '',rounds INTEGER DEFAULT 12,adults_confirmed INTEGER DEFAULT 0,language TEXT DEFAULT 'he',created TEXT)""")
   c.execute("ALTER TABLE games ADD COLUMN IF NOT EXISTS adults_confirmed INTEGER DEFAULT 0")
   c.execute("ALTER TABLE games ADD COLUMN IF NOT EXISTS language TEXT DEFAULT 'he'")
   c.execute("""CREATE TABLE IF NOT EXISTS players(id BIGSERIAL PRIMARY KEY,game_id BIGINT,name TEXT,token TEXT UNIQUE,score INTEGER DEFAULT 0,joined TEXT,photo_data TEXT DEFAULT '',photo_consent INTEGER DEFAULT 0,active INTEGER DEFAULT 1,last_seen TEXT DEFAULT '',client_id TEXT DEFAULT '')""")
   c.execute("ALTER TABLE players ADD COLUMN IF NOT EXISTS active INTEGER DEFAULT 1")
   c.execute("ALTER TABLE players ADD COLUMN IF NOT EXISTS last_seen TEXT DEFAULT ''")
   c.execute("ALTER TABLE players ADD COLUMN IF NOT EXISTS client_id TEXT DEFAULT ''")
   c.execute("""CREATE TABLE IF NOT EXISTS guesses(game_id BIGINT,round_no INTEGER,player_id BIGINT,guess TEXT,UNIQUE(game_id,round_no,player_id))""")
   c.execute("""CREATE TABLE IF NOT EXISTS hero_scenes(game_id BIGINT,round_no INTEGER,image_data TEXT,created TEXT,UNIQUE(game_id,round_no))""")
   c.execute("""CREATE TABLE IF NOT EXISTS round_scores(game_id BIGINT,round_no INTEGER,created TEXT,UNIQUE(game_id,round_no))""")
   c.execute("""CREATE TABLE IF NOT EXISTS topic_votes(game_id BIGINT,player_id BIGINT,topic TEXT,UNIQUE(game_id,player_id,topic))""")
   c.execute("""CREATE TABLE IF NOT EXISTS question_history(crew_key TEXT,question_key TEXT,question TEXT,used TEXT,UNIQUE(crew_key,question_key))""")
   c.execute("""CREATE TABLE IF NOT EXISTS match_answers(game_id BIGINT,round_no INTEGER,player_id BIGINT,answer TEXT,created TEXT,UNIQUE(game_id,round_no,player_id))""")
   c.execute("""CREATE TABLE IF NOT EXISTS match_scores(game_id BIGINT,round_no INTEGER,matched INTEGER,created TEXT,UNIQUE(game_id,round_no))""")
   c.execute("DELETE FROM players a USING players b WHERE a.game_id=b.game_id AND LOWER(TRIM(a.name))=LOWER(TRIM(b.name)) AND a.id>b.id")
   c.execute("CREATE UNIQUE INDEX IF NOT EXISTS players_game_name_ci ON players(game_id,LOWER(TRIM(name)))")
   c.execute("CREATE UNIQUE INDEX IF NOT EXISTS players_game_client_id ON players(game_id,client_id) WHERE client_id<>''")
  return
 DB.parent.mkdir(parents=True,exist_ok=True)
 with cn() as c:
  c.raw.executescript("""CREATE TABLE IF NOT EXISTS games(id INTEGER PRIMARY KEY,code TEXT UNIQUE,host TEXT,status TEXT DEFAULT 'lobby',round_no INTEGER DEFAULT 0,answer TEXT DEFAULT '',memory TEXT DEFAULT '[]',topics TEXT DEFAULT '[]',custom_context TEXT DEFAULT '',spice INTEGER DEFAULT 1,custom_questions TEXT DEFAULT '[]',prize TEXT DEFAULT '',rounds INTEGER DEFAULT 12,adults_confirmed INTEGER DEFAULT 0,language TEXT DEFAULT 'he',created TEXT);CREATE TABLE IF NOT EXISTS players(id INTEGER PRIMARY KEY,game_id INTEGER,name TEXT,token TEXT UNIQUE,score INTEGER DEFAULT 0,joined TEXT,client_id TEXT DEFAULT '');CREATE TABLE IF NOT EXISTS guesses(game_id INTEGER,round_no INTEGER,player_id INTEGER,guess TEXT,UNIQUE(game_id,round_no,player_id));CREATE TABLE IF NOT EXISTS hero_scenes(game_id INTEGER,round_no INTEGER,image_data TEXT,created TEXT,UNIQUE(game_id,round_no));CREATE TABLE IF NOT EXISTS round_scores(game_id INTEGER,round_no INTEGER,created TEXT,UNIQUE(game_id,round_no));CREATE TABLE IF NOT EXISTS topic_votes(game_id INTEGER,player_id INTEGER,topic TEXT,UNIQUE(game_id,player_id,topic));CREATE TABLE IF NOT EXISTS question_history(crew_key TEXT,question_key TEXT,question TEXT,used TEXT,UNIQUE(crew_key,question_key));CREATE TABLE IF NOT EXISTS match_answers(game_id INTEGER,round_no INTEGER,player_id INTEGER,answer TEXT,created TEXT,UNIQUE(game_id,round_no,player_id));CREATE TABLE IF NOT EXISTS match_scores(game_id INTEGER,round_no INTEGER,matched INTEGER,created TEXT,UNIQUE(game_id,round_no));""")
  gc={r['name'] for r in c.execute('PRAGMA table_info(games)')}
  for n,d in [('topics',"TEXT DEFAULT '[]'"),('custom_context',"TEXT DEFAULT ''"),('spice','INTEGER DEFAULT 1'),('custom_questions',"TEXT DEFAULT '[]'"),('prize',"TEXT DEFAULT ''"),('rounds','INTEGER DEFAULT 12'),('adults_confirmed','INTEGER DEFAULT 0'),('language',"TEXT DEFAULT 'he'")]:
   if n not in gc:c.execute(f'ALTER TABLE games ADD COLUMN {n} {d}')
  pc={r['name'] for r in c.execute('PRAGMA table_info(players)')}
  for n,d in [('photo_data',"TEXT DEFAULT ''"),('photo_consent','INTEGER DEFAULT 0'),('active','INTEGER DEFAULT 1'),('last_seen',"TEXT DEFAULT ''"),('client_id',"TEXT DEFAULT ''")]:
   if n not in pc:c.execute(f'ALTER TABLE players ADD COLUMN {n} {d}')
  c.execute("DELETE FROM players WHERE id NOT IN (SELECT MIN(id) FROM players GROUP BY game_id,LOWER(TRIM(name)))")
  c.execute("CREATE UNIQUE INDEX IF NOT EXISTS players_game_name_ci ON players(game_id,LOWER(TRIM(name)))")
  c.execute("CREATE UNIQUE INDEX IF NOT EXISTS players_game_client_id ON players(game_id,client_id) WHERE client_id<>''")
def game(code):
 with cn() as c:return c.execute('SELECT * FROM games WHERE code=?',(str(code or '').upper(),)).fetchone()
def players(gid):
 with cn() as c:return c.execute('SELECT * FROM players WHERE game_id=? ORDER BY id',(gid,)).fetchall()
def live_players(gid):
 return [p for p in players(gid) if int(p['active'] if p['active'] is not None else 1)==1]
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
 if language_code(g)!='he':
  e=m[-2];sub=next((p for p in ps if p['name']==e.get('subject')),None)
  if not sub:return None
  x=callback_text(g,sub,e.get('answer'))
  return ('callback',x[0],x[1],sub) if x else None
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
def interactive_match_data(g,typ,text,sub):
 if 'callback' not in str(typ) or not sub:return None
 ps=players(g['id']);active=[p for p in ps if int(p['active'] if p['active'] is not None else 1)==1];by_name={p['name']:p for p in active}
 prior=next((e for e in reversed(mem(g)) if e.get('subject')==sub['name'] and e.get('answer') in by_name and e.get('answer')!=sub['name']),None)
 partner=by_name.get(prior.get('answer')) if prior else None
 # Duo has no "who in the room" answers, so the other player is automatically the Match partner.
 if not partner and len(active)==2:
  partner=next((p for p in active if p['id']!=sub['id']),None)
 if not partner or int(sub['active'] if sub['active'] is not None else 1)!=1:return None
 if language_code(g)!='he':
  prompt=match_prompt(g,sub['name'],partner['name'])
  return {'prompt':prompt,'player_ids':[sub['id'],partner['id']],'names':[sub['name'],partner['name']]}
 q=(text or '').lower()
 if any(k in q for k in ['טיול','טיסה','הרפתקה','חופשה','יעד']):
  prompt=f'✈️ {sub["name"]} ו־{partner["name"]}: כל אחד כותב בסוד יעד אחד שהייתם טסים אליו מחר. אם כתבתם אותו יעד — נקודה לשניכם.'
 elif any(k in q for k in ['דייט','קראש','היכרויות']):
  prompt=f'😈 {sub["name"]} ו־{partner["name"]}: כל אחד כותב בסוד מקום אחד לדייט ספונטני. אם יצאתם על אותו רעיון — נקודה לשניכם.'
 elif any(k in q for k in ['50,000','כסף','תקציב','מיליון']):
  prompt=f'💸 {sub["name"]} ו־{partner["name"]}: כל אחד כותב בסוד דבר אחד שהייתם מבזבזים עליו את הכסף. אותה תשובה — נקודה לשניכם.'
 elif any(k in q for k in ['משפחה','חג','ארוחה']):
  prompt=f'🏠 {sub["name"]} ו־{partner["name"]}: כל אחד כותב בסוד פעילות אחת שהייתם בוחרים ליום משפחתי מושלם. אותה תשובה — נקודה לשניכם.'
 else:
  prompt=f'⚡ {sub["name"]} ו־{partner["name"]}: כל אחד כותב בסוד דבר אחד שהייתם בוחרים לעשות יחד בסופ״ש חופשי. אותה תשובה — נקודה לשניכם.'
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
 m=[e for e in mem(g) if e.get('answer') and e.get('answer')!='SKIPPED']
 if len(ps)!=2 or rn<4 or rn not in (4,6,9,12,15) or len(m)<3:return None
 if language_code(g)!='he':
  sub=ps[rn%2];mine=[e for e in reversed(m) if e.get('subject')==sub['name']]
  if not mine:return None
  x=callback_text(g,sub,mine[0].get('answer'))
  return ('duo_callback',x[0],x[1],sub) if x else None
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
 selected=effective_topics(g);focused=[]
 for t in selected:focused+=TOPICS.get(t,[])
 if int(g['spice'] or 1)>=3:focused+=SPICY
 tailored=custom_questions(g)
 themed=len(selected)==1 and selected[0] in THEME_ONLY
 if language_code(g)=='he':base=(tailored+focused) if themed and (tailored or focused) else (tailored+focused+GENERAL if (tailored or focused) else GENERAL)
 else:
  local=localized_general(g);base=(tailored+local) if tailored else local
 if len(ps)==2:
  base=[q for q in base if q[0]!='room' and len(q[2])>=3]
  if not base:base=[q for q in (GENERAL if language_code(g)=='he' else localized_general(g)) if q[0]=='know']
 used={question_key(e.get('question',''),ps) for e in mem(g)}
 used|=past_question_keys(ps)
 seed=sum(ord(ch) for ch in str(g['code']))+rn*7
 chosen=None
 for step in range(len(base)):
  q=base[(seed+step)%len(base)];typ,text,opts=q;formatted=text.format(s=sub['name'])
  if not too_similar(question_key(formatted,ps),used):chosen=(typ,formatted,opts);break
 if chosen is None:
  fallback=[q for q in (GENERAL if language_code(g)=='he' else localized_general(g)) if not (len(ps)==2 and q[0]=='room')]
  for q in fallback:
   typ,text,opts=q;formatted=text.format(s=sub['name'])
   if not too_similar(question_key(formatted,ps),used):chosen=(typ,formatted,opts);break
 if chosen is None:
  # Last-resort variant keeps gameplay moving without repeating the exact prompt.
  typ='know';formatted,opts=last_resort_question(g,sub['name'])
 else:typ,formatted,opts=chosen
 if typ=='room':opts=[p['name'] for p in ps if p['id']!=sub['id']]
 elif typ=='know' and int(g['spice'] or 1)>=3 and other_label(g) not in opts:opts=list(opts)+[other_label(g)]
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
  pack=_clean_pack(generate_pack(ts,ctx,spice,language))
  if not pack:return
  with cn() as c:
   g=c.execute('SELECT status FROM games WHERE id=?',(gid,)).fetchone()
   if g and g['status']=='lobby':c.execute('UPDATE games SET custom_questions=? WHERE id=?',(json.dumps(pack,ensure_ascii=False),gid))
 except Exception as e:print('async pack failed',type(e).__name__,str(e)[:200],flush=True)
def hero_round(rn,total):
 # AI Reveal is a core game mechanic: create one on every round when the spotlight player supplied a photo.
 return 0 <= int(rn) < int(total)
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
  actual=(other_label(g) if str(g['answer']).startswith('OTHER::') else g['answer'])
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
  if p.startswith('/api/hero-image/'):
   a=p.strip('/').split('/')
   if len(a)!=4:return self.send_error(404)
   g=game(a[2])
   if not g:return self.send_error(404)
   try:rn=int(a[3])
   except:return self.send_error(404)
   with cn() as c:row=c.execute('SELECT image_data FROM hero_scenes WHERE game_id=? AND round_no=?',(g['id'],rn)).fetchone()
   if not row or not row['image_data']:return self.send_error(404)
   mime,raw=decode_data_url(row['image_data'])
   if not raw:return self.send_error(404)
   self.send_response(200);self.send_header('Content-Type',mime or 'image/png');self.send_header('Cache-Control','public, max-age=86400, immutable');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw);return
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
   if me:
    try:
     with cn() as c:c.execute('UPDATE players SET last_seen=? WHERE id=?',(now(),me['id']))
    except:pass
   with cn() as c:
    # Never pull multi-megabyte base64 image blobs on every state poll; existence is enough here.
    gs=c.execute('SELECT player_id,guess FROM guesses WHERE game_id=? AND round_no=?',(g['id'],g['round_no'])).fetchall();hero=c.execute('SELECT 1 AS present FROM hero_scenes WHERE game_id=? AND round_no=?',(g['id'],g['round_no'])).fetchone();finalhero=c.execute('SELECT 1 AS present FROM hero_scenes WHERE game_id=? AND round_no=99',(g['id'],)).fetchone();ma=c.execute('SELECT player_id,answer FROM match_answers WHERE game_id=? AND round_no=?',(g['id'],g['round_no'])).fetchall();ms=c.execute('SELECT matched FROM match_scores WHERE game_id=? AND round_no=?',(g['id'],g['round_no'])).fetchone()
   guessed={r['player_id']:r['guess'] for r in gs};active_ids={x['id'] for x in ps if int(x['active'] if x['active'] is not None else 1)==1};need=len([x for x in ps if sub and x['id']!=sub['id'] and x['id'] in active_ids]);ready=bool(g['answer']) and len([pid for pid in guessed if pid in active_ids and (not sub or pid!=sub['id'])])>=need
   if ready and ensure_round_score(g,ps,guessed):
    ps=players(g['id']);me=next((x for x in ps if x['token']==tok),None)
   reveal=ready or g['status']=='finished';myguess=guessed.get(me['id']) if me else None;actual=(other_label(g) if str(g['answer']).startswith('OTHER::') else g['answer']);shown=(str(g['answer'])[7:] if str(g['answer']).startswith('OTHER::') else g['answer']);iscorrect=bool(reveal and myguess is not None and myguess==actual)
   idata=interactive_match_data(g,typ,text,sub) if reveal else None;matchmap={r['player_id']:r['answer'] for r in ma};matchready=bool(idata and all(pid in matchmap for pid in idata['player_ids']));matchmatched=bool(ms['matched']) if ms else (match_equal(matchmap.get(idata['player_ids'][0]),matchmap.get(idata['player_ids'][1])) if matchready else False)
   is_host=bool(host and secrets.compare_digest(host,g['host']));presence={x['id']:(True if me and x['id']==me['id'] else recently_seen(x)) for x in ps}
   return self.J({'code':g['code'],'status':g['status'],'round':g['round_no'],'total':total_rounds(g),'is_host':is_host,'me':{'id':me['id'],'name':me['name'],'score':me['score'],'has_photo':bool(me['photo_data'])} if me else None,'players':[{'id':x['id'],'name':x['name'],'score':x['score'],'active':bool(int(x['active'] if x['active'] is not None else 1)),'connected':bool(presence.get(x['id'])),'can_continue_without':bool(is_host and g['status']=='playing' and int(x['active'] if x['active'] is not None else 1)==1 and (not me or x['id']!=me['id']) and not presence.get(x['id'])),'has_photo':bool(x['photo_data']),'photo_url':('/api/photo/'+g['code']+'/'+str(x['id'])) if x['photo_data'] else ''} for x in ps],'photo_count':sum(1 for x in ps if x['photo_data']),'subject':{'id':sub['id'],'name':sub['name'],'has_photo':bool(sub['photo_data']),'photo_url':('/api/photo/'+g['code']+'/'+str(sub['id'])) if sub and sub['photo_data'] else ''} if sub else None,'type':typ,'question':text,'options':opts,'answer':shown if reveal else None,'interactive':interactive_prompt(g,typ,text,shown,sub) if reveal else '','interactive_match':({'prompt':idata['prompt'],'participants':[{'id':pid,'name':next((p['name'] for p in ps if p['id']==pid),'')} for pid in idata['player_ids']],'my_submitted':bool(me and me['id'] in matchmap),'ready':matchready,'matched':matchmatched if matchready else None,'answers':[{'id':pid,'name':next((p['name'] for p in ps if p['id']==pid),''),'answer':matchmap.get(pid,'')} for pid in idata['player_ids']] if matchready else []} if idata else None),'answered':bool(g['answer']),'my_guess':myguess,'my_correct':iscorrect,'all_guesses':[{'player_id':x['id'],'name':x['name'],'guess':guessed.get(x['id']),'correct':guessed.get(x['id'])==actual,'photo_url':('/api/photo/'+g['code']+'/'+str(x['id'])) if x['photo_data'] else ''} for x in ps if sub and x['id']!=sub['id'] and x['id'] in guessed] if reveal else [],'guessed':bool(me and me['id'] in guessed),'guess_count':len(guessed),'guess_need':need,'waiting_for':[x['name'] for x in ps if sub and x['id']!=sub['id'] and x['id'] in active_ids and x['id'] not in guessed],'reveal':reveal,'hero':('/api/hero-image/'+g['code']+'/'+str(g['round_no'])) if hero and reveal else None,'final_hero':('/api/hero-image/'+g['code']+'/99') if finalhero and g['status']=='finished' else None,'topics':effective_topics(g),'topic_votes':topic_vote_data(g),'my_topic_votes':player_topic_votes(g['id'],me['id'] if me else None),'mode':'duo' if len(ps)==2 else 'group','ai_images_ready':bool(os.getenv('OPENAI_API_KEY','').strip()),'spice':g['spice'],'language':language_code(g),'context':g['custom_context'],'prize':g['prize'],'rounds':total_rounds(g),'can_reopen':bool(g['status']=='playing' and int(g['round_no'])==0 and not mem(g) and not reveal),'history':mem(g)[-4:]})
  return self.J({'error':'not_found'},404)
 def do_POST(self):
  p=urlparse(self.path).path;d=self.B()
  if p=='/api/create':
   name=str(d.get('name','')).strip()[:40]
   if not name:return self.J({'error':'name_required'},400)
   co=code5();ht=secrets.token_urlsafe(16);pt=secrets.token_urlsafe(16);ts=d.get('topics',[]);ts=ts if isinstance(ts,list) else [];ctx=str(d.get('context','')).strip()[:700];sp=max(1,min(3,int(d.get('spice',1) or 1)));prize=str(d.get('prize','')).strip()[:180];rounds=max(6,min(30,int(d.get('rounds',12) or 12)));client_id=str(d.get('client_id','')).strip()[:120];language=str(d.get('language','en'));language=language if language in SUPPORTED_LANGUAGES else 'en'
   adult=adult_required(ts,sp)
   if adult and not d.get('adults_confirmed'):return self.J({'error':'adults_confirmation_required'},400)
   with cn() as c:
    if USE_PG:gid=c.execute('INSERT INTO games(code,host,topics,custom_context,spice,prize,rounds,adults_confirmed,language,created) VALUES(?,?,?,?,?,?,?,?,?,?) RETURNING id',(co,ht,json.dumps(ts,ensure_ascii=False),ctx,sp,prize,rounds,1 if adult else 0,language,now())).fetchone()['id']
    else:gid=c.execute('INSERT INTO games(code,host,topics,custom_context,spice,prize,rounds,adults_confirmed,language,created) VALUES(?,?,?,?,?,?,?,?,?,?)',(co,ht,json.dumps(ts,ensure_ascii=False),ctx,sp,prize,rounds,1 if adult else 0,language,now())).lastrowid
    c.execute('INSERT INTO players(game_id,name,token,joined,active,last_seen,client_id) VALUES(?,?,?,?,1,?,?)',(gid,name,pt,now(),now(),client_id))
   Thread(target=prepare_pack_async,args=(gid,effective_topics(game(co)),ctx,sp,language),daemon=True).start()
   return self.J({'code':co,'host':ht,'token':pt,'name':name})
  if p=='/api/join':
   g=game(d.get('code'));name=str(d.get('name','')).strip()[:40];client_id=str(d.get('client_id','')).strip()[:120]
   if not g:return self.J({'error':'not_found'},404)
   if not name:return self.J({'error':'name_required'},400)
   room_players=players(g['id']);existing=next((x for x in room_players if client_id and (x['client_id'] or '')==client_id),None) or next((x for x in room_players if _norm_name(x['name'])==_norm_name(name)),None)
   if existing:
    if g['status']!='lobby' and int(existing['active'] if existing['active'] is not None else 1)==0:return self.J({'error':'removed_from_game'},409)
    with cn() as c:c.execute("UPDATE players SET active=1,last_seen=?,client_id=CASE WHEN client_id='' THEN ? ELSE client_id END WHERE id=?",(now(),client_id,existing['id']))
    return self.J({'code':g['code'],'token':existing['token'],'name':existing['name'],'recovered':True})
   if g['status']!='lobby':return self.J({'error':'started'},409)
   if len(live_players(g['id']))>=6:return self.J({'error':'full'},409)
   tok=secrets.token_urlsafe(16)
   try:
    with cn() as c:c.execute('INSERT INTO players(game_id,name,token,joined,active,last_seen,client_id) VALUES(?,?,?,?,1,?,?)',(g['id'],name,tok,now(),now(),client_id))
   except Exception:
    existing=next((x for x in players(g['id']) if (client_id and (x['client_id'] or '')==client_id) or _norm_name(x['name'])==_norm_name(name)),None)
    if existing:return self.J({'code':g['code'],'token':existing['token'],'name':existing['name'],'recovered':True})
    raise
   return self.J({'code':g['code'],'token':tok,'name':name})
  a=p.strip('/').split('/')
  if len(a)!=3 or a[0]!='api':return self.J({'error':'not_found'},404)
  g=game(a[1]);act=a[2]
  # Player-token recovery: mobile browsers can keep an older room code in local state.
  # For player actions, the opaque player token is the stronger session identifier.
  if not g and act in ('photo','answer','guess','matchanswer'):
   tok=str(d.get('token',''))
   if tok:
    with cn() as c:
     row=c.execute('SELECT game_id FROM players WHERE token=?',(tok,)).fetchone()
     if row:g=c.execute('SELECT * FROM games WHERE id=?',(row['game_id'],)).fetchone()
  if not g:return self.J({'error':'room_not_found'},404)
  ps=players(g['id']);typ,text,opts,sub=qdata(g,ps)
  if act in ('start','next','hero','finalhero','skip','settings','reopen','drop','replay') and not(d.get('host') and secrets.compare_digest(str(d['host']),g['host'])):return self.J({'error':'forbidden'},403)
  if act=='reopen':
   if g['status']!='playing' or int(g['round_no'])!=0 or mem(g):return self.J({'error':'too_late'},409)
   with cn() as c:
    rgs=c.execute('SELECT player_id FROM guesses WHERE game_id=? AND round_no=?',(g['id'],g['round_no'])).fetchall()
   active_ids={x['id'] for x in ps if int(x['active'] if x['active'] is not None else 1)==1};need=len([x for x in ps if sub and x['id']!=sub['id'] and x['id'] in active_ids]);first_reveal=bool(g['answer']) and len([r for r in rgs if r['player_id'] in active_ids and (not sub or r['player_id']!=sub['id'])])>=need
   if first_reveal:return self.J({'error':'too_late'},409)
   with cn() as c:
    c.execute("UPDATE games SET status='lobby',round_no=0,answer='' WHERE id=?",(g['id'],))
    c.execute('DELETE FROM guesses WHERE game_id=?',(g['id'],));c.execute('DELETE FROM round_scores WHERE game_id=?',(g['id'],));c.execute('DELETE FROM hero_scenes WHERE game_id=?',(g['id'],))
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
  if act=='replay':
   if g['status']!='finished':return self.J({'error':'not_finished'},409)
   with cn() as c:
    c.execute("UPDATE games SET status='lobby',round_no=0,answer='',memory='[]',custom_questions='[]' WHERE id=?",(g['id'],))
    c.execute('UPDATE players SET score=0,active=1,last_seen=? WHERE game_id=?',(now(),g['id']))
    c.execute('DELETE FROM guesses WHERE game_id=?',(g['id'],));c.execute('DELETE FROM hero_scenes WHERE game_id=?',(g['id'],));c.execute('DELETE FROM round_scores WHERE game_id=?',(g['id'],));c.execute('DELETE FROM match_answers WHERE game_id=?',(g['id'],));c.execute('DELETE FROM match_scores WHERE game_id=?',(g['id'],))
   fresh=game(g['code'])
   Thread(target=prepare_pack_async,args=(g['id'],effective_topics(fresh),fresh['custom_context'],int(fresh['spice'] or 1),language_code(fresh)),daemon=True).start()
   return self.J({'ok':True})
  if act=='settings':
   if g['status']!='lobby':return self.J({'error':'already_started'},409)
   ts=d.get('topics',[])
   if not isinstance(ts,list):ts=[]
   ts=[str(x)[:60] for x in ts[:12]]
   ctx=str(d.get('context','')).strip()[:700];prize=str(d.get('prize','')).strip()[:180];rounds=max(6,min(30,int(d.get('rounds',g['rounds']) or 12)))
   try:sp=max(1,min(3,int(d.get('spice',g['spice']) or 1)))
   except:sp=int(g['spice'] or 1)
   adult=adult_required(ts,sp)
   if adult and not d.get('adults_confirmed'):return self.J({'error':'adults_confirmation_required'},400)
   with cn() as c:c.execute('UPDATE games SET topics=?,custom_context=?,spice=?,prize=?,rounds=?,custom_questions=?,adults_confirmed=? WHERE id=?',(json.dumps(ts,ensure_ascii=False),ctx,sp,prize,rounds,'[]',1 if adult else 0,g['id']))
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
   if topic in ADULT_TOPICS and not int(g['adults_confirmed'] or 0):return self.J({'error':'adults_confirmation_required'},409)
   with cn() as c:
    old=c.execute('SELECT 1 FROM topic_votes WHERE game_id=? AND player_id=? AND topic=?',(g['id'],me['id'],topic)).fetchone()
    if old:c.execute('DELETE FROM topic_votes WHERE game_id=? AND player_id=? AND topic=?',(g['id'],me['id'],topic))
    else:
     count=c.execute('SELECT COUNT(*) AS n FROM topic_votes WHERE game_id=? AND player_id=?',(g['id'],me['id'])).fetchone()['n']
     if count>=6:return self.J({'error':'max_topics'},409)
     c.execute('INSERT INTO topic_votes(game_id,player_id,topic) VALUES(?,?,?)',(g['id'],me['id'],topic))
   return self.J({'ok':True})
  if act=='start':
   if len(live_players(g['id']))<2:return self.J({'error':'need_2'},409)
   # Tailored AI questions are prepared while players are in the lobby.
   # Starting the game must be instant; if the pack is not ready, curated questions are used.
   pack=_clean_pack(custom_questions(g))
   with cn() as c:
    c.execute("UPDATE games SET status='playing',round_no=0,answer='',memory='[]',custom_questions=? WHERE id=?",(json.dumps(pack,ensure_ascii=False),g['id']))
    c.execute('DELETE FROM guesses WHERE game_id=?',(g['id'],));c.execute('DELETE FROM hero_scenes WHERE game_id=?',(g['id'],));c.execute('DELETE FROM round_scores WHERE game_id=?',(g['id'],));c.execute('DELETE FROM match_answers WHERE game_id=?',(g['id'],));c.execute('DELETE FROM match_scores WHERE game_id=?',(g['id'],))
   return self.J({'ok':True,'tailored_questions':len(pack)})
  if act=='answer':
   me=next((x for x in ps if x['token']==d.get('token')),None);ans=str(d.get('answer',''))[:160]
   if not me or not sub or me['id']!=sub['id']:return self.J({'error':'subject_only'},403)
   if ans.startswith('OTHER::'):
    custom=ans[7:].strip()
    if other_label(g) not in opts or len(custom)<1:return self.J({'error':'invalid_answer'},400)
    ans='OTHER::'+custom[:120]
   elif ans not in opts:return self.J({'error':'invalid_answer'},400)
   with cn() as c:
    cur=c.execute("UPDATE games SET answer=? WHERE id=? AND answer=''",(ans,g['id']))
    changed=getattr(cur,'rowcount',0)==1
    if not changed:
     old=c.execute('SELECT answer FROM games WHERE id=?',(g['id'],)).fetchone();return self.J({'ok':True,'locked':True,'answer_saved':bool(old and old['answer'])})
   if os.getenv('OPENAI_API_KEY','').strip() and hero_round(int(g['round_no']),total_rounds(g)) and sub['photo_data'] and sub['photo_consent']:
    Thread(target=prepare_hero_async,args=(g['id'],int(g['round_no'])),daemon=True).start()
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
       if r['player_id'] in active_ids and r['guess']==(other_label(g) if str(g['answer']).startswith('OTHER::') else g['answer']):c.execute('UPDATE players SET score=score+1 WHERE id=?',(r['player_id'],))
   fresh=players(g['id'])
   return self.J({'ok':True,'scores':{x['name']:x['score'] for x in fresh}})
  if act=='matchanswer':
   me=next((x for x in ps if x['token']==d.get('token')),None);val=str(d.get('answer','')).strip()[:80];idata=interactive_match_data(g,typ,text,sub)
   if not me or not idata or me['id'] not in idata['player_ids']:return self.J({'error':'not_allowed'},403)
   if not val:return self.J({'error':'answer_required'},400)
   with cn() as c:
    locked=c.execute('SELECT matched FROM match_scores WHERE game_id=? AND round_no=?',(g['id'],g['round_no'])).fetchone()
    if locked:return self.J({'ok':True,'locked':True,'matched':bool(locked['matched'])})
    if USE_PG:c.execute('INSERT INTO match_answers(game_id,round_no,player_id,answer,created) VALUES(?,?,?,?,?) ON CONFLICT(game_id,round_no,player_id) DO NOTHING',(g['id'],g['round_no'],me['id'],val,now()))
    else:c.execute('INSERT OR IGNORE INTO match_answers(game_id,round_no,player_id,answer,created) VALUES(?,?,?,?,?)',(g['id'],g['round_no'],me['id'],val,now()))
    rows=c.execute('SELECT player_id,answer FROM match_answers WHERE game_id=? AND round_no=?',(g['id'],g['round_no'])).fetchall();mp={r['player_id']:r['answer'] for r in rows}
    if all(pid in mp for pid in idata['player_ids']):
     matched=match_equal(mp[idata['player_ids'][0]],mp[idata['player_ids'][1]])
     if USE_PG:claimed=c.execute('INSERT INTO match_scores(game_id,round_no,matched,created) VALUES(?,?,?,?) ON CONFLICT(game_id,round_no) DO NOTHING RETURNING matched',(g['id'],g['round_no'],1 if matched else 0,now())).fetchone()
     else:
      cur=c.execute('INSERT OR IGNORE INTO match_scores(game_id,round_no,matched,created) VALUES(?,?,?,?)',(g['id'],g['round_no'],1 if matched else 0,now()));claimed=True if getattr(cur,'rowcount',0)==1 else None
     if claimed and matched:
      for pid in idata['player_ids']:c.execute('UPDATE players SET score=score+1 WHERE id=?',(pid,))
     final=c.execute('SELECT matched FROM match_scores WHERE game_id=? AND round_no=?',(g['id'],g['round_no'])).fetchone()
     return self.J({'ok':True,'ready':True,'matched':bool(final['matched']) if final else matched})
   return self.J({'ok':True,'ready':False})
  if act=='finalhero':
   with cn() as c:old=c.execute('SELECT image_data FROM hero_scenes WHERE game_id=? AND round_no=99',(g['id'],)).fetchone()
   if old:return self.J({'ok':True,'image':'/api/hero-image/'+g['code']+'/99'})
   available=[p for p in ps if p['photo_data'] and p['photo_consent']]
   if len(available)<2:return self.J({'error':'not_enough_photos'},409)
   ranked=sorted(ps,key=lambda x:x['score'],reverse=True);winner=ranked[0]['name'];summary=', '.join([f"{p['name']} {p['score']} points" for p in ranked])
   items=[(p['name'],p['photo_data']) for p in available]
   prize=g['prize'] or 'bragging rights as the friend who knows the crew best';art=generate_many(items,'Final cinematic ensemble poster for this friend group after a hilarious Know Your Crew game. The winner also receives this playful prize: '+prize,f'Winner: {winner}. Prize: {prize}. Scores: {summary}',winner,'')
   if not art:return self.J({'error':'generation_failed'},502)
   with cn() as c:c.execute('INSERT OR REPLACE INTO hero_scenes(game_id,round_no,image_data,created) VALUES(?,?,?,?)',(g['id'],99,art,now()))
   return self.J({'ok':True,'image':'/api/hero-image/'+g['code']+'/99'})
  if act=='hero':
   if not sub or not sub['photo_data'] or not sub['photo_consent']:return self.J({'error':'no_photo'},409)
   with cn() as c:old=c.execute('SELECT image_data FROM hero_scenes WHERE game_id=? AND round_no=?',(g['id'],g['round_no'])).fetchone()
   if old:return self.J({'ok':True,'image':'/api/hero-image/'+g['code']+'/'+str(g['round_no'])})
   selected=g['answer'] if any(p['name']==g['answer'] for p in ps) else ''
   ordered=[sub]+([p for p in ps if p['name']==selected and p['id']!=sub['id']] if selected else [])+[p for p in ps if p['id']!=sub['id'] and p['name']!=selected]
   items=[(p['name'],p['photo_data']) for p in ordered if p['photo_data'] and p['photo_consent']]
   visual_answer=(str(g['answer'])[7:] if str(g['answer']).startswith('OTHER::') else g['answer'])
   art=generate_many(items,text,visual_answer,sub['name'],selected)
   if not art:return self.J({'error':'generation_failed'},502)
   with cn() as c:c.execute('INSERT OR REPLACE INTO hero_scenes(game_id,round_no,image_data,created) VALUES(?,?,?,?)',(g['id'],g['round_no'],art,now()))
   return self.J({'ok':True,'image':'/api/hero-image/'+g['code']+'/'+str(g['round_no'])})
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
   idata=interactive_match_data(g,typ,text,sub)
   with cn() as c:
    gs=c.execute('SELECT player_id,guess FROM guesses WHERE game_id=? AND round_no=?',(g['id'],g['round_no'])).fetchall()
    active_ids={x['id'] for x in ps if int(x['active'] if x['active'] is not None else 1)==1}
    need=len([x for x in ps if sub and x['id']!=sub['id'] and x['id'] in active_ids])
    if not g['answer'] or len([r for r in gs if r['player_id'] in active_ids])<need:return self.J({'error':'not_ready'},409)
    if idata and not c.execute('SELECT 1 FROM match_scores WHERE game_id=? AND round_no=?',(g['id'],g['round_no'])).fetchone():return self.J({'error':'match_not_ready'},409)
    clean_answer=(str(g['answer'])[7:] if str(g['answer']).startswith('OTHER::') else g['answer']);mm=mem(g);mm.append({'round':g['round_no'],'subject':sub['name'],'question':text,'answer':clean_answer,'type':typ});rn=int(g['round_no'])+1
    c.execute('DELETE FROM players WHERE game_id=? AND active=0',(g['id'],))
    remaining=c.execute('SELECT COUNT(*) AS n FROM players WHERE game_id=?',(g['id'],)).fetchone()['n']
    if rn>=total_rounds(g) or remaining<2:c.execute("UPDATE games SET status='finished',memory=? WHERE id=?",(json.dumps(mm,ensure_ascii=False),g['id']))
    else:c.execute("UPDATE games SET round_no=?,answer='',memory=? WHERE id=?",(rn,json.dumps(mm,ensure_ascii=False),g['id']))
   remember_question(ps,text)
   return self.J({'ok':True})
  return self.J({'error':'not_found'},404)
 def log_message(self,*a):pass
def run():init();ThreadingHTTPServer(('0.0.0.0',int(os.getenv('PORT','5000'))),H).serve_forever()
