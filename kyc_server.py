import json,os,random,secrets,sqlite3,mimetypes
from datetime import datetime,timezone
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse,parse_qs
from kyc_questions import GENERAL,TOPICS,SPICY
from kyc_visuals import generate_many
from kyc_ai import generate_pack
BASE=Path(__file__).parent;DB=Path(os.getenv('DATABASE_PATH',BASE/'kyc.db'));STATIC=BASE/'static';TOTAL=12
def now():return datetime.now(timezone.utc).isoformat()
def cn():c=sqlite3.connect(DB,timeout=20);c.row_factory=sqlite3.Row;return c
def init():
 DB.parent.mkdir(parents=True,exist_ok=True)
 with cn() as c:
  c.executescript("""CREATE TABLE IF NOT EXISTS games(id INTEGER PRIMARY KEY,code TEXT UNIQUE,host TEXT,status TEXT DEFAULT 'lobby',round_no INTEGER DEFAULT 0,answer TEXT DEFAULT '',memory TEXT DEFAULT '[]',topics TEXT DEFAULT '[]',custom_context TEXT DEFAULT '',spice INTEGER DEFAULT 1,custom_questions TEXT DEFAULT '[]',prize TEXT DEFAULT '',created TEXT);CREATE TABLE IF NOT EXISTS players(id INTEGER PRIMARY KEY,game_id INTEGER,name TEXT,token TEXT UNIQUE,score INTEGER DEFAULT 0,joined TEXT);CREATE TABLE IF NOT EXISTS guesses(game_id INTEGER,round_no INTEGER,player_id INTEGER,guess TEXT,UNIQUE(game_id,round_no,player_id));CREATE TABLE IF NOT EXISTS hero_scenes(game_id INTEGER,round_no INTEGER,image_data TEXT,created TEXT,UNIQUE(game_id,round_no));CREATE TABLE IF NOT EXISTS round_scores(game_id INTEGER,round_no INTEGER,created TEXT,UNIQUE(game_id,round_no));""")
  gc={r['name'] for r in c.execute('PRAGMA table_info(games)')}
  for n,d in [('topics',"TEXT DEFAULT '[]'"),('custom_context',"TEXT DEFAULT ''"),('spice','INTEGER DEFAULT 1'),('custom_questions',"TEXT DEFAULT '[]'"),('prize',"TEXT DEFAULT ''")]:
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
def custom_questions(g):
 try:
  raw=json.loads(g['custom_questions'] or '[]')
  return [(x[0],x[1],x[2]) for x in raw if isinstance(x,list) and len(x)==3]
 except:return []
def pool(g):
 x=custom_questions(g)
 for t in topics(g):x+=TOPICS.get(t,[])
 if int(g['spice'] or 1)>=3:x+=SPICY
 x+=GENERAL
 return x
def smart_callback(g,ps,rn):
 m=mem(g)
 if rn not in (5,8,10) or len(m)<3:return None
 names=[p['name'] for p in ps];room=[e for e in m if e.get('answer') in names]
 if rn==10 and len(m)>=6:
  for e1 in reversed(m):
   for e2 in reversed(m):
    if e1 is not e2 and e1.get('subject')==e2.get('subject'):
     sub=next((p for p in ps if p['name']==e1.get('subject')),None);friend=e1.get('answer')
     if sub and friend in names and friend!=sub['name']:
      text=f'⚡ DOUBLE PLOT TWIST: קודם {sub["name"]} בחר/ה ב־{friend}, ובסיבוב אחר בחר/ה “{e2.get("answer")}”. עכשיו שני הדברים מתנגשים: למי בחבורה {sub["name"]} הכי סביר שיפנה/תפנה כדי להציל את המצב?'
      return 'callback2',text,[p['name'] for p in ps if p['id']!=sub['id']],sub
 if room:
  e=room[-1];sub=next((p for p in ps if p['name']==e.get('subject')),None);friend=e.get('answer')
  if sub and friend!=sub['name']:
   text=f'⚡ PLOT TWIST: קודם {sub["name"]} בחר/ה ב־{friend}. עכשיו התוכנית מסתבכת ברגע הכי לא מתאים. מי מהם {sub["name"]} חושב/ת שיישאר רגוע יותר?'
   return 'callback',text,[sub['name'],friend],sub
 e=m[-2];sub=next((p for p in ps if p['name']==e.get('subject')),None)
 if sub:
  text=f'⚡ PLOT TWIST: קודם {sub["name"]} בחר/ה “{e.get("answer")}”. עכשיו זה באמת קורה. מי מהחבורה {sub["name"]} הכי ירצה/תרצה לצרף אליו/ה?'
  return 'callback',text,[p['name'] for p in ps if p['id']!=sub['id']],sub
 return None
def qdata(g,ps):
 rn=int(g['round_no']);sub=ps[rn%len(ps)] if ps else None
 cb=smart_callback(g,ps,rn)
 if cb:return cb
 focused=[]
 for t in topics(g):focused+=TOPICS.get(t,[])
 if int(g['spice'] or 1)>=3:focused+=SPICY
 tailored=custom_questions(g);base=tailored+focused+GENERAL if (tailored or focused) else GENERAL
 used={e.get('question','') for e in mem(g)}
 seed=sum(ord(ch) for ch in str(g['code']))+rn*7
 for step in range(len(base)):
  q=base[(seed+step)%len(base)];typ,text,opts=q;formatted=text.format(s=sub['name'])
  if formatted not in used:break
 if typ=='room':opts=[p['name'] for p in ps if p['id']!=sub['id']]
 elif typ=='know' and int(g['spice'] or 1)>=3 and '✏️ משהו אחר' not in opts:opts=list(opts)+['✏️ משהו אחר']
 return typ,formatted,list(opts),sub
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
  if p=='/health':return self.J({'ok':True,'game':'know-your-crew-visuals'})
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
   g=game(p.split('/')[-1])
   if not g:return self.J({'error':'not_found'},404)
   ps=players(g['id']);q=parse_qs(u.query);tok=q.get('token',[''])[0];host=q.get('host',[''])[0];me=next((x for x in ps if x['token']==tok),None);typ,text,opts,sub=qdata(g,ps)
   with cn() as c:
    gs=c.execute('SELECT player_id,guess FROM guesses WHERE game_id=? AND round_no=?',(g['id'],g['round_no'])).fetchall();hero=c.execute('SELECT image_data FROM hero_scenes WHERE game_id=? AND round_no=?',(g['id'],g['round_no'])).fetchone();finalhero=c.execute('SELECT image_data FROM hero_scenes WHERE game_id=? AND round_no=99',(g['id'],)).fetchone()
   guessed={r['player_id']:r['guess'] for r in gs};need=max(0,len(ps)-1);ready=bool(g['answer']) and len(guessed)>=need;reveal=ready or g['status']=='finished';myguess=guessed.get(me['id']) if me else None;actual=('✏️ משהו אחר' if str(g['answer']).startswith('OTHER::') else g['answer']);shown=(str(g['answer'])[7:] if str(g['answer']).startswith('OTHER::') else g['answer']);iscorrect=bool(reveal and myguess is not None and myguess==actual)
   return self.J({'code':g['code'],'status':g['status'],'round':g['round_no'],'total':TOTAL,'is_host':bool(host and secrets.compare_digest(host,g['host'])),'me':{'id':me['id'],'name':me['name'],'score':me['score'],'has_photo':bool(me['photo_data'])} if me else None,'players':[{'id':x['id'],'name':x['name'],'score':x['score'],'has_photo':bool(x['photo_data']),'photo_url':('/api/photo/'+g['code']+'/'+str(x['id'])) if x['photo_data'] else ''} for x in ps],'photo_count':sum(1 for x in ps if x['photo_data']),'subject':{'id':sub['id'],'name':sub['name'],'has_photo':bool(sub['photo_data']),'photo_url':('/api/photo/'+g['code']+'/'+str(sub['id'])) if sub and sub['photo_data'] else ''} if sub else None,'type':typ,'question':text,'options':opts,'answer':shown if reveal else None,'answered':bool(g['answer']),'my_guess':myguess,'my_correct':iscorrect,'all_guesses':[{'player_id':x['id'],'name':x['name'],'guess':guessed.get(x['id']),'correct':guessed.get(x['id'])==actual,'photo_url':('/api/photo/'+g['code']+'/'+str(x['id'])) if x['photo_data'] else ''} for x in ps if sub and x['id']!=sub['id'] and x['id'] in guessed] if reveal else [],'guessed':bool(me and me['id'] in guessed),'guess_count':len(guessed),'guess_need':need,'reveal':reveal,'hero':hero['image_data'] if hero and reveal else None,'final_hero':finalhero['image_data'] if finalhero and g['status']=='finished' else None,'topics':topics(g),'spice':g['spice'],'context':g['custom_context'],'prize':g['prize'],'history':mem(g)[-4:]})
  return self.J({'error':'not_found'},404)
 def do_POST(self):
  p=urlparse(self.path).path;d=self.B()
  if p=='/api/create':
   name=str(d.get('name','')).strip()[:40]
   if not name:return self.J({'error':'name_required'},400)
   co=code5();ht=secrets.token_urlsafe(16);pt=secrets.token_urlsafe(16);ts=d.get('topics',[]);ts=ts if isinstance(ts,list) else [];ctx=str(d.get('context','')).strip()[:700];sp=max(1,min(3,int(d.get('spice',1) or 1)));prize=str(d.get('prize','')).strip()[:180]
   if sp==3 and not d.get('adults_confirmed'):return self.J({'error':'adults_confirmation_required'},400)
   with cn() as c:cur=c.execute('INSERT INTO games(code,host,topics,custom_context,spice,prize,created) VALUES(?,?,?,?,?,?,?)',(co,ht,json.dumps(ts,ensure_ascii=False),ctx,sp,prize,now()));c.execute('INSERT INTO players(game_id,name,token,joined) VALUES(?,?,?,?)',(cur.lastrowid,name,pt,now()))
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
  if not g:return self.J({'error':'not_found'},404)
  ps=players(g['id']);typ,text,opts,sub=qdata(g,ps)
  if act in ('start','next','hero','finalhero','skip','settings') and not(d.get('host') and secrets.compare_digest(str(d['host']),g['host'])):return self.J({'error':'forbidden'},403)
  if act=='settings':
   if g['status']!='lobby':return self.J({'error':'already_started'},409)
   ts=d.get('topics',[])
   if not isinstance(ts,list):ts=[]
   ts=[str(x)[:60] for x in ts[:12]]
   ctx=str(d.get('context','')).strip()[:700];prize=str(d.get('prize','')).strip()[:180]
   try:sp=max(1,min(3,int(d.get('spice',g['spice']) or 1)))
   except:sp=int(g['spice'] or 1)
   if sp==3 and not d.get('adults_confirmed'):return self.J({'error':'adults_confirmation_required'},400)
   with cn() as c:c.execute('UPDATE games SET topics=?,custom_context=?,spice=?,prize=?,custom_questions=? WHERE id=?',(json.dumps(ts,ensure_ascii=False),ctx,sp,prize,'[]',g['id']))
   return self.J({'ok':True})
  if act=='photo':
   me=next((x for x in ps if x['token']==d.get('token')),None);data=d.get('data_url','')
   if not me:return self.J({'error':'player_not_found'},404)
   if not d.get('consent'):return self.J({'error':'consent_required'},400)
   if not isinstance(data,str) or not data.startswith('data:image/'):return self.J({'error':'invalid_image'},400)
   if len(data)>5_600_000:return self.J({'error':'image_too_large'},400)
   with cn() as c:c.execute('UPDATE players SET photo_data=?,photo_consent=1 WHERE id=?',(data,me['id']))
   return self.J({'ok':True})
  if act=='start':
   if len(ps)<3:return self.J({'error':'need_3'},409)
   pack=custom_questions(g)
   if not pack:
    pack=generate_pack(topics(g),g['custom_context'],g['spice'])
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
   return self.J({'ok':True})
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
    if rn>=TOTAL:c.execute("UPDATE games SET status='finished',answer='',memory=? WHERE id=?",(json.dumps(mm,ensure_ascii=False),g['id']))
    else:c.execute("UPDATE games SET round_no=?,answer='',memory=? WHERE id=?",(rn,json.dumps(mm,ensure_ascii=False),g['id']))
   return self.J({'ok':True,'skipped':True})
  if act=='next':
   with cn() as c:
    gs=c.execute('SELECT player_id,guess FROM guesses WHERE game_id=? AND round_no=?',(g['id'],g['round_no'])).fetchall()
    if not g['answer'] or len(gs)<len(ps)-1:return self.J({'error':'not_ready'},409)
    clean_answer=(str(g['answer'])[7:] if str(g['answer']).startswith('OTHER::') else g['answer']);mm=mem(g);mm.append({'round':g['round_no'],'subject':sub['name'],'question':text,'answer':clean_answer,'type':typ});rn=int(g['round_no'])+1
    if rn>=TOTAL:c.execute("UPDATE games SET status='finished',memory=? WHERE id=?",(json.dumps(mm,ensure_ascii=False),g['id']))
    else:c.execute("UPDATE games SET round_no=?,answer='',memory=? WHERE id=?",(rn,json.dumps(mm,ensure_ascii=False),g['id']))
   return self.J({'ok':True})
  return self.J({'error':'not_found'},404)
 def log_message(self,*a):pass
def run():init();ThreadingHTTPServer(('0.0.0.0',int(os.getenv('PORT','5000'))),H).serve_forever()
