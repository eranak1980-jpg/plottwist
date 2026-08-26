from __future__ import annotations
import io, json, mimetypes, os, qrcode, random, secrets, sqlite3, urllib.request
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

BASE=Path(__file__).resolve().parent
DB_PATH=Path(os.getenv('DATABASE_PATH', str(BASE/'party_game.db')))
STATIC=BASE/'static'
APP_BASE_URL=os.getenv('APP_BASE_URL','').rstrip('/')
MIN_PLAYERS=2

def now(): return datetime.now(timezone.utc).isoformat()
def db():
    c=sqlite3.connect(DB_PATH); c.row_factory=sqlite3.Row; return c

def ensure(c,t,n,d):
    if n not in {r['name'] for r in c.execute(f'PRAGMA table_info({t})')}: c.execute(f'ALTER TABLE {t} ADD COLUMN {n} {d}')

def init_db():
    DB_PATH.parent.mkdir(parents=True,exist_ok=True)
    with db() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS games(id INTEGER PRIMARY KEY,code TEXT UNIQUE,host_token TEXT,theme TEXT,tone TEXT,duration INTEGER,status TEXT DEFAULT 'lobby',round_no INTEGER DEFAULT 0,killer_player_id INTEGER,created_at TEXT);
        CREATE TABLE IF NOT EXISTS players(id INTEGER PRIMARY KEY,game_id INTEGER,name TEXT,token TEXT UNIQUE,role_name TEXT,secret TEXT,objective TEXT,joined_at TEXT);
        CREATE TABLE IF NOT EXISTS votes(id INTEGER PRIMARY KEY,game_id INTEGER,round_no INTEGER,voter_player_id INTEGER,accused_player_id INTEGER,created_at TEXT,UNIQUE(game_id,round_no,voter_player_id));
        CREATE TABLE IF NOT EXISTS gm_events(id INTEGER PRIMARY KEY,game_id INTEGER,round_no INTEGER,prompt TEXT,response TEXT,created_at TEXT);
        CREATE TABLE IF NOT EXISTS feedback(id INTEGER PRIMARY KEY,game_id INTEGER,player_id INTEGER,fun_score INTEGER,clarity_score INTEGER,replay INTEGER,note TEXT,created_at TEXT,UNIQUE(game_id,player_id));
        ''')
        for n,d in [('group_name',"TEXT DEFAULT ''"),('relationship',"TEXT DEFAULT ''"),('inside_joke',"TEXT DEFAULT ''"),('location',"TEXT DEFAULT ''"),('intensity',"TEXT DEFAULT 'balanced'"),('story_title',"TEXT DEFAULT ''"),('victim_name',"TEXT DEFAULT ''"),('rounds_json',"TEXT DEFAULT ''"),('engine',"TEXT DEFAULT 'local'"),('round_started_at',"TEXT DEFAULT ''"),('round_seconds','INTEGER DEFAULT 600'),('game_type',"TEXT DEFAULT 'murder'")]: ensure(c,'games',n,d)
        ensure(c,'players','private_hint',"TEXT DEFAULT ''")

def code():
    chars='ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    while True:
        x=''.join(random.choice(chars) for _ in range(5))
        with db() as c:
            if not c.execute('SELECT 1 FROM games WHERE code=?',(x,)).fetchone(): return x

def game(x):
    with db() as c: return c.execute('SELECT * FROM games WHERE code=?',(x.upper(),)).fetchone()
def players(gid):
    with db() as c: return c.execute('SELECT * FROM players WHERE game_id=? ORDER BY id',(gid,)).fetchall()

def ai_case(g,ps):
    key=os.getenv('OPENAI_API_KEY')
    if not key: return None
    names=[p['name'] for p in ps]
    prompt=f'''Create a coherent English social party mystery for {len(names)} adults. Mode: {g['game_type']}.
Players: {', '.join(names)}. Group: {g['group_name']}. Relationship: {g['relationship']}. Location: {g['location']}. Theme: {g['theme']}. Tone: {g['tone']}. Inside detail: {g['inside_joke']}.
For exactly 2 players, design a tight head-to-head mystery where both have meaningful private information and one is the hidden culprit; avoid mechanics that require questioning multiple other people. For 3+ players, use normal group deduction.
Return ONLY JSON with keys title, victim, killer_name, roles, rounds. roles must have one object per player with name, role_name, secret, objective, private_hint. Exactly one player is the hidden culprit. rounds must contain exactly 4 English strings and form a solvable mystery. In heist mode nobody dies; in secrets mode use a hidden saboteur. Avoid graphic violence, sexual content, or humiliating claims.'''
    body={'model':os.getenv('OPENAI_MODEL','gpt-4.1-mini'),'input':prompt}
    req=urllib.request.Request('https://api.openai.com/v1/responses',data=json.dumps(body).encode(),headers={'Authorization':f'Bearer {key}','Content-Type':'application/json'},method='POST')
    try:
        with urllib.request.urlopen(req,timeout=30) as r: out=json.loads(r.read().decode())
        text=out.get('output_text','') or ''.join(c.get('text','') for item in out.get('output',[]) for c in item.get('content',[]))
        data=json.loads(text.strip().removeprefix('```json').removesuffix('```').strip())
        return data if len(data.get('roles',[]))==len(ps) and len(data.get('rounds',[]))==4 else None
    except Exception as e: print('AI fallback:',e); return None

def local_story(g):
    place=g['location'] or 'the living room'; joke=g['inside_joke'] or 'the inside joke only your group understands'; mode=g['game_type'] or 'murder'
    if mode=='heist': return f"The Missing Diamond — {g['group_name']}",'the Midnight Diamond',joke
    if mode=='secrets': return f"The Secret of {g['group_name']}",'the secret file',joke
    return f'The Last Glass at {place}','Alex Rosen',joke

def assign(gid):
    with db() as c: g=c.execute('SELECT * FROM games WHERE id=?',(gid,)).fetchone()
    ps=players(gid)
    if len(ps)<MIN_PLAYERS: raise ValueError('need_2_players')
    case=ai_case(g,ps)
    if case:
        roles={r.get('name'):r for r in case['roles']}; culprit=next((p for p in ps if p['name']==case.get('killer_name')),None)
        if culprit and all(p['name'] in roles for p in ps):
            with db() as c:
                c.execute("UPDATE games SET killer_player_id=?,story_title=?,victim_name=?,rounds_json=?,engine='ai' WHERE id=?",(culprit['id'],case.get('title','Tonight’s Mystery'),case.get('victim','the target'),json.dumps(case['rounds']),gid))
                for p in ps:
                    r=roles[p['name']]; c.execute('UPDATE players SET role_name=?,secret=?,objective=?,private_hint=? WHERE id=?',(r.get('role_name','Suspect'),r.get('secret',''),r.get('objective',''),r.get('private_hint',''),p['id']))
            return
    culprit=random.choice(ps); title,victim,joke=local_story(g); place=g['location'] or 'the living room'
    defs=[('The Night Photographer','You accidentally captured something in the background of a video moments before the lights went out.','Use what you saw to test the other player’s story.'),('The Secret Keeper',f'{victim} told you earlier that they were about to expose someone.','Work out who had the most to lose without revealing everything too early.'),('The Detail-Obsessed Host',f'You remember exactly who entered and left {place}.','Catch a contradiction in the other player’s story.'),('The Missing Friend','You disappeared for a few minutes just before the incident for an innocent but embarrassing reason.','Protect your alibi unless accused directly.'),('The Collector','You found a small object that does not belong to you.','Work out who it belongs to before round three ends.')]
    random.shuffle(defs)
    with db() as c:
        c.execute("UPDATE games SET killer_player_id=?,story_title=?,victim_name=?,rounds_json='',engine='local' WHERE id=?",(culprit['id'],title,victim,gid))
        for i,p in enumerate(ps):
            others=[x['name'] for x in ps if x['id']!=p['id']]; random.shuffle(others)
            if p['id']==culprit['id']:
                framed=others[0] if others else 'the other player'; secret=f'You are responsible for what happened to {victim}. The blackout gave you an 8-second window. {framed} almost saw you returning to {place}.'; obj=f'Deflect suspicion and make {framed} doubt their own theory. Keep your story consistent.'; hint=f'Private clue: someone remembers seeing you near {place} before the blackout.'; role='The Killer' if g['game_type']=='murder' else 'The Culprit'
            else:
                role,secret,obj=defs[i%len(defs)]; hint=random.choice([f'Private clue: a detail connects directly to {victim}.',f'Private clue: something said about {place} does not match what you saw.',f'Private clue: something connected to “{joke[:30]}” matters more than it looks.'])
            c.execute('UPDATE players SET role_name=?,secret=?,objective=?,private_hint=? WHERE id=?',(role,secret,obj,hint,p['id']))

def round_text(g,n):
    if g['rounds_json']:
        try: return json.loads(g['rounds_json'])[n-1]
        except Exception: pass
    title=g['story_title'] or 'Tonight’s Mystery'; victim=g['victim_name'] or 'the target'; place=g['location'] or 'the room'; joke=g['inside_joke'] or 'an inside detail'; mode=g['game_type']
    if mode=='heist': arr=[f'🚨 {title}. {victim} vanished during a brief blackout at {place}. Introduce your character — but keep your secret hidden.',f'🔎 A clue connects to “{joke[:45]}”. Your private clue is now unlocked. Challenge the other player’s timeline.','⚡ Something in the stories does not add up. Each player must repeat their exact timeline, then answer one sharp follow-up question.','🗳️ Time to accuse. Give your final argument, then vote in secret.']
    elif mode=='secrets': arr=[f'📁 {title}. {victim} was leaked during the night at {place}. Someone did it deliberately. Introduce your character without revealing your secret.',f'🔎 The first clue links the leak to “{joke[:45]}”. Your private clue is now unlocked. Ask one focused question.','⚡ A contradiction appears. Each player must state one fact they have not revealed yet.','🗳️ Who is the saboteur? Give your final defense, then vote.']
    else: arr=[f'🥂 {title}. {victim} is found dead after a brief blackout at {place}. Introduce your role and say what you were doing before the lights went out — keep your secret hidden.',f'🔎 A torn note reads “{joke[:45]}”. Your private clue is now unlocked. Challenge the other player’s story.','⚡ One detail cannot be true. Repeat your alibi in one sentence, then answer one sharp follow-up question.','🗳️ Time to decide. Who did it, and why? Give your final argument, then vote in secret.']
    return arr[n-1] if 1<=n<=4 else 'The game is over.'

def remaining(g):
    if not g['round_started_at'] or g['status']!='playing': return 0
    try: return max(0,int((g['round_seconds'] or 600)-(datetime.now(timezone.utc)-datetime.fromisoformat(g['round_started_at'])).total_seconds()))
    except Exception: return int(g['round_seconds'] or 600)

def gm_reaction(g,summary):
    key=os.getenv('OPENAI_API_KEY')
    if key:
        prompt=f"You are the live Game Master for an English party mystery. Title: {g['story_title']}. Round: {g['round_no']}. The host says: {summary}. Reply with one tense intervention under 55 words. Never reveal the culprit."
        try:
            body={'model':os.getenv('OPENAI_MODEL','gpt-4.1-mini'),'input':prompt}; req=urllib.request.Request('https://api.openai.com/v1/responses',data=json.dumps(body).encode(),headers={'Authorization':f'Bearer {key}','Content-Type':'application/json'},method='POST')
            with urllib.request.urlopen(req,timeout=25) as r: out=json.loads(r.read().decode())
            text=out.get('output_text','') or ''.join(c.get('text','') for x in out.get('output',[]) for c in x.get('content',[]))
            if text:return text.strip()[:650]
        except Exception as e:print('GM fallback:',e)
    return random.choice([f'Live twist: {summary[:120]}. Repeat your alibis from the beginning.',f'The room goes quiet. {summary[:120]}. Anyone holding back a detail must reveal part of it now.',f'After that development — {summary[:120]} — name the most suspicious detail you have heard.'])

def votes(gid,kid):
    with db() as c:
        rows=c.execute('SELECT p.name,COUNT(v.id) votes FROM players p LEFT JOIN votes v ON p.id=v.accused_player_id WHERE p.game_id=? GROUP BY p.id ORDER BY votes DESC',(gid,)).fetchall();total=c.execute('SELECT COUNT(*) n FROM votes WHERE game_id=?',(gid,)).fetchone()['n'];correct=c.execute('SELECT COUNT(*) n FROM votes WHERE game_id=? AND accused_player_id=?',(gid,kid)).fetchone()['n']
    return [{'name':r['name'],'votes':r['votes']} for r in rows],correct,total

class Handler(BaseHTTPRequestHandler):
    def j(self,x,status=200):
        b=json.dumps(x,ensure_ascii=False).encode();self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
    def body(self):
        try:return json.loads(self.rfile.read(int(self.headers.get('Content-Length','0'))) or b'{}')
        except:return {}
    def file(self,p):
        try:b=p.read_bytes()
        except FileNotFoundError:self.send_error(404);return
        self.send_response(200);self.send_header('Content-Type',mimetypes.guess_type(str(p))[0] or 'application/octet-stream');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
    def do_GET(self):
        u=urlparse(self.path);path=u.path
        if path=='/health':return self.j({'ok':True})
        if path in ('/','/index.html'):return self.file(STATIC/'index.html')
        if path.startswith('/static/'):return self.file(STATIC/path.split('/static/',1)[1])
        if path.startswith('/api/qr/'):
            g=game(path.split('/api/qr/',1)[1]);base=APP_BASE_URL or f"{self.headers.get('X-Forwarded-Proto','http')}://{self.headers.get('Host','localhost:5000')}"
            if not g:return self.j({'error':'not_found'},404)
            img=qrcode.make(f'{base}/?code={g["code"]}');buf=io.BytesIO();img.save(buf,'PNG');b=buf.getvalue();self.send_response(200);self.send_header('Content-Type','image/png');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b);return
        if path.startswith('/api/game/'):
            g=game(path.rsplit('/',1)[-1]);
            if not g:return self.j({'error':'not_found'},404)
            q=parse_qs(u.query);token=q.get('token',[''])[0];host=q.get('host',[''])[0]
            with db() as c:me=c.execute('SELECT * FROM players WHERE game_id=? AND token=?',(g['id'],token)).fetchone() if token else None;ps=c.execute('SELECT * FROM players WHERE game_id=? ORDER BY id',(g['id'],)).fetchall();event=c.execute('SELECT * FROM gm_events WHERE game_id=? ORDER BY id DESC LIMIT 1',(g['id'],)).fetchone()
            out={'code':g['code'],'game_type':g['game_type'],'duration':g['duration'],'group_name':g['group_name'],'location':g['location'],'status':g['status'],'round_no':g['round_no'],'story_title':g['story_title'],'engine':g['engine'],'round_prompt':round_text(g,g['round_no']) if g['status']=='