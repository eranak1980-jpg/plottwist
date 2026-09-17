import base64,io,json,mimetypes,os,random,secrets,sqlite3
from datetime import datetime,timezone
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs,urlparse
import qrcode

BASE=Path(__file__).parent
DB=Path(os.getenv('DATABASE_PATH',BASE/'party_game.db'))
STATIC=BASE/'static'

def now(): return datetime.now(timezone.utc).isoformat()
def cn():
 c=sqlite3.connect(DB,timeout=20);c.row_factory=sqlite3.Row;return c

def init():
 DB.parent.mkdir(parents=True,exist_ok=True)
 with cn() as c:
  c.executescript("""CREATE TABLE IF NOT EXISTS games(id INTEGER PRIMARY KEY,code TEXT UNIQUE,host_token TEXT,status TEXT DEFAULT 'lobby',round_no INTEGER DEFAULT 0,killer_player_id INTEGER,group_name TEXT DEFAULT '',location TEXT DEFAULT '',inside_joke TEXT DEFAULT '',game_type TEXT DEFAULT 'murder',story_title TEXT DEFAULT '',victim_name TEXT DEFAULT '',round_started_at TEXT DEFAULT '',round_seconds INTEGER DEFAULT 600,created_at TEXT);CREATE TABLE IF NOT EXISTS players(id INTEGER PRIMARY KEY,game_id INTEGER,name TEXT,token TEXT UNIQUE,role_name TEXT DEFAULT '',secret TEXT DEFAULT '',objective TEXT DEFAULT '',private_hint TEXT DEFAULT '',joined_at TEXT);CREATE TABLE IF NOT EXISTS gm_events(id INTEGER PRIMARY KEY,game_id INTEGER,round_no INTEGER,response TEXT,created_at TEXT);CREATE TABLE IF NOT EXISTS votes(id INTEGER PRIMARY KEY,game_id INTEGER,round_no INTEGER,voter_player_id INTEGER,accused_player_id INTEGER,created_at TEXT,UNIQUE(game_id,round_no,voter_player_id));""")
  pcols={r['name'] for r in c.execute('PRAGMA table_info(players)')}
  for name,decl in [('photo_data',"TEXT DEFAULT ''"),('photo_consent','INTEGER DEFAULT 0'),('ai_art_data',"TEXT DEFAULT ''")]:
   if name not in pcols:c.execute(f'ALTER TABLE players ADD COLUMN {name} {decl}')

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
 p=g['location'] or 'הסלון'
 if g['game_type']=='heist':return f'היהלום שנעלם ב{p}','יהלום חצות'
 if g['game_type']=='secrets':return f'הסוד של {p}','התיק הסודי'
 return f'הכוס האחרונה ב{p}','אלכס רוזן'

def portrait_prompt(role,mode,location):
 return f"Transform the provided real person's photo into a premium cinematic fictional role-card portrait for a private party mystery. Preserve recognizable identity and facial features. Role: {role}. Setting inspired by {location or 'an elegant interior'}. Photorealistic, dramatic lighting, chest-up composition. No text, logos, blood, injury or gore."

def generate_portrait(data_url,role,mode,location):
 key=os.getenv('OPENAI_API_KEY','').strip()
 if not key or not data_url:return ''
 try:
  from openai import OpenAI
  head,b64=data_url.split(',',1);raw=base64.b64decode(b64);f=io.BytesIO(raw);f.name='player.png'
  res=OpenAI(api_key=key,timeout=90.0).images.edit(model='gpt-image-1',image=f,prompt=portrait_prompt(role,mode,location),size='1024x1024',quality='medium',input_fidelity='high')
  out=res.data[0].b64_json
  return 'data:image/png;base64,'+out if out else ''
 except Exception as e:
  print('AI portrait generation failed:',type(e).__name__,str(e)[:300],flush=True);return ''

def assign(g):
 players=ps(g['id'])
 if len(players)<2:raise ValueError
 killer=random.choice(players);t,v=story(g);place=g['location'] or 'הסלון';j=clean(g['inside_joke'])
 roles=[('צלם הלילה','צילמת משהו רגע לפני שהאורות כבו.','השתמש במה שראית כדי לבדוק את הסיפורים של האחרים.'),('שומר הסוד',f'{v} סיפר לך שהוא עומד לחשוף מישהו.','גלה למי היה הכי הרבה מה להפסיד.'),('המארח חד־העין',f'אתה זוכר מי נכנס ומי יצא מ{place}.','חפש סתירות בסיפורים של האחרים.'),('החבר שנעלם','נעלמת לזמן קצר מסיבה תמימה.','שמור על האליבי שלך, אלא אם מישהו מאשים אותך.')]
 random.shuffle(roles)
 with cn() as c:
  c.execute('UPDATE games SET killer_player_id=?,story_title=?,victim_name=? WHERE id=?',(killer['id'],t,v,g['id']))
  for i,p in enumerate(players):
   if p['id']==killer['id']:
    r='הרוצח' if g['game_type']=='murder' else 'האשם';s=f'אתה אחראי למה שקרה ל{v}. מישהו כמעט ראה אותך ליד {place}.';o='הסט את החשד ממך ושמור על סיפור עקבי.';h=f'רמז פרטי: מישהו זוכר שראה אותך ליד {place}.'
   else:
    r,s,o=roles[i%len(roles)];h=f'רמז פרטי: המקרה כולל זיכרון שרק החבורה מכירה: "{j}". נסה להבין מי יכול היה להשתמש בו ולמה.' if j else 'רמז פרטי: פרט אישי קטן חשוב יותר ממה שנראה.'
   c.execute('UPDATE players SET role_name=?,secret=?,objective=?,private_hint=? WHERE id=?',(r,s,o,h,p['id']))
 for p in ps(g['id']):
  if p['photo_data'] and p['photo_consent']:
   art=generate_portrait(p['photo_data'],p['role_name'],g['game_type'],g['location'])
   if art:
    with cn() as c:c.execute('UPDATE players SET ai_art_data=? WHERE id=?',(art,p['id']))

def prompt(g):
 n=int(g['round_no']);t=g['story_title'] or 'התעלומה של הערב';v=g['victim_name'] or 'הקורבן';p=g['location'] or 'החדר';j=clean(g['inside_joke'])
 personal=f'רמז חדש מזכיר זיכרון שרק החבורה שלכם מכירה: "{j}". מי יכול היה להשתמש בפרט הזה ולמה?' if j else 'ברמז החדש מופיע פרט אישי שרק מישהו מהחבורה אמור להכיר.'
 arr=[f'{t}. אחרי הפסקת חשמל ב{p}, {v} נמצא ללא רוח חיים. כל אחד מציג את הדמות והאליבי שלו — אבל שומר את הסוד לעצמו.',f'{personal} הרמז הפרטי שלך פתוח עכשיו. בחר שחקן אחד ואתגר פרט בסיפור שלו.','עדות חדשה סותרת משהו שכבר נאמר. כל אחד מציג במשפט אחד את ציר הזמן שלו ועונה על שאלה ישירה משחקן אחר.','הגיע הזמן להאשמה הסופית. אמרו מי לדעתכם אחראי, הסבירו למה, ואז כל אחד מצביע בסוד.']
 return arr[n-1] if 1<=n<=4 else 'המשחק הסתיים.'

def left(g):
 if g['status']!='playing' or not g['round_started_at']:return 0
 try:return max(0,int((g['round_seconds'] or 600)-(datetime.now(timezone.utc)-datetime.fromisoformat(g['round_started_at'])).total_seconds()))
 except:return 600

def stats(g):
 with cn() as c:
  rows=c.execute('SELECT p.id,p.name,COUNT(v.id) n FROM players p LEFT JOIN votes v ON v.accused_player_id=p.id AND v.game_id=? AND v.round_no=4 WHERE p.game_id=? GROUP BY p.id ORDER BY n DESC,p.id',(g['id'],g['id'])).fetchall()
  total=c.execute('SELECT COUNT(*) n FROM votes WHERE game_id=? AND round_no=4',(g['id'],)).fetchone()['n']
  correct=c.execute('SELECT COUNT(*) n FROM votes WHERE game_id=? AND round_no=4 AND accused_player_id=?',(g['id'],g['killer_player_id'])).fetchone()['n']
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
  if p=='/health':return self.J({'ok':True,'version':'hebrew-playtest-complete'})
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
   with cn() as c:
    me=c.execute('SELECT * FROM players WHERE game_id=? AND token=?',(g['id'],tok)).fetchone() if tok else None
    ev=c.execute('SELECT * FROM gm_events WHERE game_id=? ORDER BY id DESC LIMIT 1',(g['id'],)).fetchone()
   vs,total,correct=stats(g);k=next((x for x in players if x['id']==g['killer_player_id']),None)
   out={'code':g['code'],'group_name':g['group_name'],'location':g['location'],'status':g['status'],'round_no':g['round_no'],'story_title':g['story_title'],'round_prompt':prompt(g) if g['status']=='playing' else None,'remaining_seconds':left(g),'latest_gm_event':({'round_no':ev['round_no'],'response':ev['response']} if ev else None),'players':[{'id':x['id'],'name':x['name'],'role_name':x['role_name'] if g['status']=='finished' else None,'has_photo':bool(x['photo_data']),'has_ai_art':bool(x['ai_art_data'])} for x in players],'is_host':bool(host and secrets.compare_digest(host,g['host_token'])),'me':None,'killer':({'id':k['id'],'name':k['name']} if g['status']=='finished' and k else None),'vote_summary':vs if g['status']=='finished' else [],'total_votes':total,'correct_votes':correct}
   if me:out['me']={'id':me['id'],'name':me['name'],'role_name':me['role_name'],'secret':me['secret'],'objective':me['objective'],'private_hint':me['private_hint'] if g['status']=='playing' and g['round_no']>=2 else '','has_photo':bool(me['photo_data']),'photo_data':me['photo_data'],'ai_art_data':me['ai_art_data']}
   return self.J(out)
  return self.J({'error':'not_found'},404)
 def do_POST(self):
  p=urlparse(self.path).path;d=self.B()
  if p=='/api/create':
   co=code5();ht=secrets.token_urlsafe(18);pt=secrets.token_urlsafe(18);name=clean(d.get('name'),40) or 'מארח'
   with cn() as c:
    cur=c.execute('INSERT INTO games(code,host_token,group_name,location,inside_joke,game_type,created_at) VALUES(?,?,?,?,?,?,?)',(co,ht,clean(d.get('group_name'),80) or 'החבורה',clean(d.get('location'),80) or 'הסלון',clean(d.get('inside_joke')),clean(d.get('game_type'),20) or 'murder',now()))
    c.execute('INSERT INTO players(game_id,name,token,joined_at) VALUES(?,?,?,?)',(cur.lastrowid,name,pt,now()))
   return self.J({'code':co,'host':ht,'token':pt,'name':name})
  if p=='/api/join':
   g=game(d.get('code'));name=clean(d.get('name'),40)
   if not g:return self.J({'error':'not_found'},404)
   if not name:return self.J({'error':'name_required'},400)
   with cn() as c:existing=c.execute('SELECT * FROM players WHERE game_id=? AND lower(name)=lower(?)',(g['id'],name)).fetchone()
   if existing:return self.J({'code':g['code'],'token':existing['token'],'name':existing['name'],'recovered':True})
   if g['status']!='lobby':return self.J({'error':'already_started'},400)
   tok=secrets.token_urlsafe(18)
   with cn() as c:c.execute('INSERT INTO players(game_id,name,token,joined_at) VALUES(?,?,?,?)',(g['id'],name,tok,now()))
   return self.J({'code':g['code'],'token':tok,'name':name})
  a=p.strip('/').split('/')
  if len(a)!=4 or a[:2]!=['api','game']:return self.J({'error':'not_found'},404)
  g=game(a[2]);act=a[3]
  if not g:return self.J({'error':'not_found'},404)
  if act in ('start','next') and not(d.get('host') and secrets.compare_digest(str(d['host']),g['host_token'])):return self.J({'error':'forbidden'},403)
  if act=='photo':
   data=d.get('data_url','')
   if not d.get('consent'):return self.J({'error':'consent_required'},400)
   if not isinstance(data,str) or not data.startswith('data:image/'):return self.J({'error':'invalid_image'},400)
   if len(data)>5_600_000:return self.J({'error':'image_too_large'},400)
   with cn() as c:
    me=c.execute('SELECT id FROM players WHERE game_id=? AND token=?',(g['id'],d.get('token',''))).fetchone()
    if not me:return self.J({'error':'player_not_found'},400)
    c.execute("UPDATE players SET photo_data=?,photo_consent=1,ai_art_data='' WHERE id=?",(data,me['id']))
   return self.J({'ok':True,'saved':True})
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
   s=clean(d.get('summary'),500);tok=d.get('token','')
   if not s:return self.J({'error':'summary_required'},400)
   with cn() as c:me=c.execute('SELECT * FROM players WHERE game_id=? AND token=?',(g['id'],tok)).fetchone()
   if not me:return self.J({'error':'forbidden'},403)
   r=f'{me["name"]} שם לב: {s}. עכשיו כל אחד צריך לחזור על פרט אחד בציר הזמן שלו שאפשר לבדוק.'
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

def run():
 init();ThreadingHTTPServer(('0.0.0.0',int(os.getenv('PORT','5000'))),H).serve_forever()
