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
Return ONLY JSON with keys title, victim, killer_name, roles, rounds. roles must have one object per player with name, role_name, secret, objective, private_hint. Exactly one player is the hidden culprit. rounds must contain exactly 4 English strings and form a solvable mystery. In heist mode nobody dies; in secrets mode use a hidden saboteur. Avoid graphic violence, sexual content, or humiliating claims.'''
    body={'model':os.getenv('OPENAI_MODEL','gpt-4.1-mini'),'input':prompt}
    req=urllib.request.Request('https://api.openai.com/v1/responses',data=json.dumps(body).encode(),headers={'Authorization':f'Bearer {key}','Content-Type':'application/json'},method='POST')
    try:
        with urllib.request.urlopen(req,timeout=30) as r: out=json.loads(r.read().decode())
        text=out.get('output_text','')
        if not text: text=''.join(c.get('text','') for item in out.get('output',[]) for c in item.get('content',[]))
        data=json.loads(text.strip().removeprefix('```json').removesuffix('```').strip())
        return data if len(data.get('roles',[]))==len(ps) and len(data.get('rounds',[]))==4 else None
    except Exception as e:
        print('AI fallback:',e); return None

def local_story(g):
    place=g['location'] or 'the living room'; joke=g['inside_joke'] or 'the inside joke only your group understands'; mode=g['game_type'] or 'murder'
    if mode=='heist': return f"The Missing Diamond — {g['group_name']}",'the Midnight Diamond',joke
    if mode=='secrets': return f"The Secret of {g['group_name']}",'the secret file',joke
    return f'The Last Glass at {place}','Alex Rosen',joke

def assign(gid):
    with db() as c: g=c.execute('SELECT * FROM games WHERE id=?',(gid,)).fetchone()
    ps=players(gid)
    if len(ps)<4: raise ValueError('need_4_players')
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
    defs=[
      ('The Night Photographer','You accidentally captured something in the background of a video moments before the lights went out.','Get two players to give their timelines before you reveal what you saw.'),
      ('The Secret Keeper',f'{victim} told you earlier that they were about to expose someone in the room.','Figure out who had the most to lose without revealing everything too early.'),
      ('The Detail-Obsessed Host',f'You remember exactly who entered and left {place}.','Catch at least one contradiction between two stories.'),
      ('The Missing Friend','You disappeared for a few minutes just before the incident for an innocent but embarrassing reason.','Protect your alibi unless someone accuses you directly.'),
      ('The Collector','You found a small object that does not belong to you. It could condemn someone — or clear them.','Discover who the object belongs to before round three ends.'),
      ('The Suspicious One','You felt something was wrong from the beginning, but nobody took you seriously.','Ask three sharp questions and force someone to clarify their story.'),
      ('The Ex from the Past',f"You received a cryptic message from {victim}: 'Tonight it ends.'",'Work out what the message meant without becoming the main suspect.'),
      ('The Unreliable Witness','You saw part of the incident in a window reflection, but you may have misread it.','Share your clue only after hearing two different theories.'),
      ('The Mediator','You know two people argued earlier, and both asked you to keep it secret.','Choose what to reveal and when, to prevent a false accusation.')]
    random.shuffle(defs)
    with db() as c:
        c.execute("UPDATE games SET killer_player_id=?,story_title=?,victim_name=?,rounds_json='',engine='local' WHERE id=?",(culprit['id'],title,victim,gid))
        for i,p in enumerate(ps):
            others=[x['name'] for x in ps if x['id']!=p['id']]; random.shuffle(others)
            if p['id']==culprit['id']:
                framed=others[0] if others else 'another player'
                secret=f'You are responsible for what happened to {victim}. The blackout gave you an 8-second window. {framed} almost saw you returning to {place}.'
                obj=f'Deflect suspicion and get at least one player to suspect {framed}. Keep your story consistent.'
                hint=f'Private clue: someone remembers seeing you near {place} before the blackout.'
                c.execute('UPDATE players SET role_name=?,secret=?,objective=?,private_hint=? WHERE id=?',('The Killer' if g['game_type']=='murder' else 'The Culprit',secret,obj,hint,p['id']))
            else:
                role,secret,obj=defs[i%len(defs)]
                hints=[f'Private clue: a small detail you heard earlier connects to {victim}.',f'Private clue: there is a small contradiction between what was said about {place} and what you saw.','Private clue: one player seems far too confident. Ask one very specific question.',f'Private clue: something connected to “{joke[:30]}” matters more than it looks.']
                c.execute('UPDATE players SET role_name=?,secret=?,objective=?,private_hint=? WHERE id=?',(role,secret,obj,random.choice(hints),p['id']))

def round_text(g,n):
    if g['rounds_json']:
        try: return json.loads(g['rounds_json'])[n-1]
        except Exception: pass
    title=g['story_title'] or 'Tonight’s Mystery'; victim=g['victim_name'] or 'the target'; place=g['location'] or 'the room'; joke=g['inside_joke'] or 'an inside detail'; mode=g['game_type']
    if mode=='heist': arr=[f'🚨 {title}. {victim} vanished during a brief blackout at {place}. Introduce your character — but keep your secret hidden.',f'🔎 A clue near the scene connects to “{joke[:45]}”. Everyone now has a private clue. Start interrogating each other.','⚡ Someone changed a detail in their alibi. Go around the room: where were you during the blackout, and who can confirm it?','🗳️ Time to accuse. Everyone gets 20 seconds for a final argument, then vote in secret.']
    elif mode=='secrets': arr=[f'📁 {title}. {victim} was leaked during the night at {place}. Someone here did it deliberately. Introduce your character without revealing your secret.',f'🔎 The first clue links the leak to “{joke[:45]}”. Everyone now has a private clue. Ask focused questions.','⚡ A new contradiction appears. Everyone must tell one true thing and one thing that may not be true.','🗳️ Who is the saboteur? Final vote. First, everyone gets 20 seconds to explain why they are innocent.']
    else: arr=[f'🥂 {title}. {victim} is found dead after a brief blackout at {place}. Everyone is a suspect. Introduce your role and say what you were doing before the lights went out — but keep your secret hidden.',f'🔎 A torn note is found with the words “{joke[:45]}”. Everyone now has a private clue. Question at least two people.','⚡ One alibi in the room cannot be true. Repeat your alibi in one sentence. After each one, another player may ask one sharp follow-up question.','🗳️ Time to decide. Everyone gets 20 seconds: who did it, and why? Then vote in secret.']
    return arr[n-1] if 1<=n<=4 else 'The game is over.'

def remaining(g):
    if not g['round_started_at'] or g['status']!='playing': return 0
    try: return max(0,int((g['round_seconds'] or 600)-(datetime.now(timezone.utc)-datetime.fromisoformat(g['round_started_at'])).total_seconds()))
    except Exception: return int(g['round_seconds'] or 600)

def gm_reaction(g,summary):
    key=os.getenv('OPENAI_API_KEY')
    if key:
        prompt=f"You are the live Game Master for an English party mystery. Title: {g['story_title']}. Round: {g['round_no']}. The host says: {summary}. Reply with one tense intervention under 55 words. Never reveal the culprit."
        body={'model':os.getenv('OPENAI_MODEL','gpt-4.1-mini'),'input':prompt}
        try:
            req=urllib.request.Request('https://api.openai.com/v1/responses',data=json.dumps(body).encode(),headers={'Authorization':f'Bearer {key}','Content-Type':'application/json'},method='POST')
            with urllib.request.urlopen(req,timeout=25) as r: out=json.loads(r.read().decode())
            text=out.get('output_text','') or ''.join(c.get('text','') for x in out.get('output',[]) for c in x.get('content',[]))
            if text: return text.strip()[:650]
        except Exception as e: print('GM fallback:',e)
    return random.choice([f'Live twist: {summary[:120]}. Pick one player to repeat their alibi from the beginning without interruption.',f'The room goes quiet. {summary[:120]}. Anyone holding back a detail must reveal at least half of it now.',f'After that development — {summary[:120]} — everyone must name the most suspicious detail they have heard so far.'])

def votes(gid,kid):
    with db() as c:
        rows=c.execute('SELECT p.name,COUNT(v.id) votes FROM players p LEFT JOIN votes v ON p.id=v.accused_player_id WHERE p.game_id=? GROUP BY p.id ORDER BY votes DESC',(gid,)).fetchall(); total=c.execute('SELECT COUNT(*) n FROM votes WHERE game_id=?',(gid,)).fetchone()['n']; correct=c.execute('SELECT COUNT(*) n FROM votes WHERE game_id=? AND accused_player_id=?',(gid,kid)).fetchone()['n']
    return [{'name':r['name'],'votes':r['votes']} for r in rows],correct,total

class Handler(BaseHTTPRequestHandler):
    def j(self,x,status=200):
        b=json.dumps(x,ensure_ascii=False).encode(); self.send_response(status); self.send_header('Content-Type','application/json; charset=utf-8'); self.send_header('Cache-Control','no-store'); self.send_header('X-Content-Type-Options','nosniff'); self.send_header('Content-Length',str(len(b))); self.end_headers(); self.wfile.write(b)
    def body(self):
        try: return json.loads(self.rfile.read(int(self.headers.get('Content-Length','0'))) or b'{}')
        except Exception: return {}
    def file(self,p):
        try: b=p.read_bytes()
        except FileNotFoundError: self.send_error(404); return
        self.send_response(200); self.send_header('Content-Type',mimetypes.guess_type(str(p))[0] or 'application/octet-stream'); self.send_header('Content-Length',str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        u=urlparse(self.path); path=u.path
        if path=='/health': return self.j({'ok':True})
        if path=='/' or path=='/index.html': return self.file(STATIC/'index.html')
        if path.startswith('/static/'): return self.file(STATIC/path.split('/static/',1)[1])
        if path.startswith('/api/qr/'):
            g=game(path.split('/api/qr/',1)[1])
            if not g: return self.j({'error':'not_found'},404)
            base=APP_BASE_URL or f"{self.headers.get('X-Forwarded-Proto','http')}://{self.headers.get('Host','localhost:5000')}"
            img=qrcode.make(f'{base}/?code={g["code"]}'); buf=io.BytesIO(); img.save(buf,'PNG'); b=buf.getvalue(); self.send_response(200); self.send_header('Content-Type','image/png'); self.send_header('Content-Length',str(len(b))); self.end_headers(); self.wfile.write(b); return
        if path.startswith('/api/game/'):
            g=game(path.rsplit('/',1)[-1])
            if not g: return self.j({'error':'not_found'},404)
            q=parse_qs(u.query); token=q.get('token',[''])[0]; host=q.get('host',[''])[0]
            with db() as c:
                me=c.execute('SELECT * FROM players WHERE game_id=? AND token=?',(g['id'],token)).fetchone() if token else None; ps=c.execute('SELECT * FROM players WHERE game_id=? ORDER BY id',(g['id'],)).fetchall(); event=c.execute('SELECT * FROM gm_events WHERE game_id=? ORDER BY id DESC LIMIT 1',(g['id'],)).fetchone()
            out={'code':g['code'],'theme':g['theme'],'tone':g['tone'],'game_type':g['game_type'],'duration':g['duration'],'group_name':g['group_name'],'location':g['location'],'relationship':g['relationship'],'status':g['status'],'round_no':g['round_no'],'story_title':g['story_title'],'victim_name':g['victim_name'],'engine':g['engine'],'round_prompt':round_text(g,g['round_no']) if g['status']=='playing' else None,'round_seconds':g['round_seconds'] or 600,'remaining_seconds':remaining(g),'latest_gm_event':({'round_no':event['round_no'],'response':event['response']} if event else None),'players':[{'id':p['id'],'name':p['name'],'role_name':p['role_name'] if g['status']=='finished' else None} for p in ps],'is_host':bool(host and secrets.compare_digest(host,g['host_token'])),'me':None,'killer':None,'vote_summary':[],'correct_votes':0,'total_votes':0,'feedback_done':False}
            if me:
                out['me']={k:me[k] for k in ('id','name','role_name','secret','objective')}; out['me']['private_hint']=me['private_hint'] if g['status']=='playing' and g['round_no']>=2 else ''
                with db() as c: out['feedback_done']=bool(c.execute('SELECT 1 FROM feedback WHERE game_id=? AND player_id=?',(g['id'],me['id'])).fetchone())
            if g['status']=='finished':
                culprit=next((p for p in ps if p['id']==g['killer_player_id']),None); out['killer']={'id':culprit['id'],'name':culprit['name']} if culprit else None; out['vote_summary'],out['correct_votes'],out['total_votes']=votes(g['id'],g['killer_player_id'])
            return self.j(out)
        self.send_error(404)
    def do_POST(self):
        path=urlparse(self.path).path; d=self.body()
        if path=='/api/create':
            co=code(); ht=secrets.token_urlsafe(18); pt=secrets.token_urlsafe(18)
            with db() as c:
                cur=c.execute('INSERT INTO games(code,host_token,theme,tone,duration,group_name,relationship,inside_joke,location,intensity,created_at,game_type) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',(co,ht,(d.get('theme') or 'Modern mystery').strip(),(d.get('tone') or 'Funny & suspenseful').strip(),int(d.get('duration') or 60),(d.get('group_name') or 'The group').strip(),(d.get('relationship') or 'Friends').strip(),(d.get('inside_joke') or '').strip(),(d.get('location') or 'the living room').strip(),(d.get('intensity') or 'balanced').strip(),now(),(d.get('game_type') or 'murder').strip())); gid=cur.lastrowid; c.execute('INSERT INTO players(game_id,name,token,joined_at) VALUES(?,?,?,?)',(gid,(d.get('name') or 'Host').strip(),pt,now()))
            return self.j({'code':co,'host':ht,'token':pt})
        if path=='/api/join':
            g=game((d.get('code') or '').upper())
            if not g: return self.j({'error':'not_found'},404)
            if g['status']!='lobby': return self.j({'error':'already_started'},400)
            name=(d.get('name') or '').strip()
            if not name: return self.j({'error':'name_required'},400)
            tok=secrets.token_urlsafe(18)
            with db() as c:
                if c.execute('SELECT 1 FROM players WHERE game_id=? AND lower(name)=lower(?)',(g['id'],name)).fetchone(): return self.j({'error':'name_taken'},400)
                c.execute('INSERT INTO players(game_id,name,token,joined_at) VALUES(?,?,?,?)',(g['id'],name,tok,now()))
            return self.j({'code':g['code'],'token':tok})
        if path.startswith('/api/game/'):
            parts=path.strip('/').split('/')
            if len(parts)!=4: return self.j({'error':'bad_path'},404)
            _,_,co,action=parts; g=game(co)
            if not g: return self.j({'error':'not_found'},404)
            if action in ('start','next'):
                if not d.get('host') or not secrets.compare_digest(d['host'],g['host_token']): return self.j({'error':'forbidden'},403)
                if action=='start':
                    try: assign(g['id'])
                    except ValueError: return self.j({'error':'need_4_players'},400)
                    seconds=max(300,min(900,int(g['duration'] or 60)*60//4))
                    with db() as c: c.execute("UPDATE games SET status='playing',round_no=1,round_started_at=?,round_seconds=? WHERE id=?",(now(),seconds,g['id']))
                    return self.j({'ok':True})
                rn=g['round_no']+1; status='finished' if rn>4 else 'playing'
                with db() as c: c.execute('UPDATE games SET status=?,round_no=?,round_started_at=? WHERE id=?',(status,rn,now() if status=='playing' else '',g['id']))
                return self.j({'ok':True})
            if action=='react':
                if not d.get('host') or not secrets.compare_digest(d['host'],g['host_token']): return self.j({'error':'forbidden'},403)
                summary=(d.get('summary') or '').strip()
                if not summary: return self.j({'error':'summary_required'},400)
                response=gm_reaction(g,summary)
                with db() as c: c.execute('INSERT INTO gm_events(game_id,round_no,prompt,response,created_at) VALUES(?,?,?,?,?)',(g['id'],g['round_no'],summary[:500],response,now()))
                return self.j({'ok':True,'response':response})
            if action=='vote':
                if g['status']!='playing' or g['round_no']<4: return self.j({'error':'voting_closed'},400)
                with db() as c:
                    voter=c.execute('SELECT * FROM players WHERE game_id=? AND token=?',(g['id'],d.get('token',''))).fetchone(); accused=c.execute('SELECT * FROM players WHERE game_id=? AND id=?',(g['id'],int(d.get('accused_id',0)))).fetchone()
                    if not voter or not accused or voter['id']==accused['id']: return self.j({'error':'invalid_vote'},400)
                    c.execute('INSERT OR REPLACE INTO votes(game_id,round_no,voter_player_id,accused_player_id,created_at) VALUES(?,?,?,?,?)',(g['id'],g['round_no'],voter['id'],accused['id'],now()))
                return self.j({'ok':True})
            if action=='feedback':
                with db() as c: me=c.execute('SELECT * FROM players WHERE game_id=? AND token=?',(g['id'],d.get('token',''))).fetchone()
                if not me: return self.j({'error':'forbidden'},403)
                try: fun=max(1,min(5,int(d.get('fun_score',0)))); clarity=max(1,min(5,int(d.get('clarity_score',0))))
                except Exception: return self.j({'error':'bad_feedback'},400)
                with db() as c: c.execute('INSERT OR REPLACE INTO feedback(game_id,player_id,fun_score,clarity_score,replay,note,created_at) VALUES(?,?,?,?,?,?,?)',(g['id'],me['id'],fun,clarity,1 if d.get('replay') else 0,(d.get('note') or '')[:1000],now()))
                return self.j({'ok':True})
        return self.j({'error':'not_found'},404)
    def log_message(self,*args): pass

def run():
    init_db(); port=int(os.getenv('PORT','5000')); print(f'PlotTwist running on 0.0.0.0:{port}'); ThreadingHTTPServer(('0.0.0.0',port),Handler).serve_forever()
if __name__=='__main__': run()
