"""Persistent launch envelope and per-attempt usage ledger. USD estimates, not invoices.
No credentials/photos/prompts are stored. Unknown/failed calls retain their reservation.
"""
import contextvars
import json
import os
import secrets
from contextlib import contextmanager
from datetime import datetime, timezone

ACTIVE = contextvars.ContextVar('plot_budget', default=None)
IMAGE_ALLOWANCE = 150000  # $0.15 per attempt; provisional, measured cost can differ
TEXT_ALLOWANCE = 100000
IMAGE_LIMIT = 60  # 30 rounds + 18 tiebreak rounds + 4 finales + 8 retry slots
TEXT_LIMIT = 3
SESSION_RESERVE = IMAGE_ALLOWANCE * IMAGE_LIMIT + TEXT_ALLOWANCE * TEXT_LIMIT
CAP = 150000000  # $150 for the entire launch pilot; never resets on restart
GAME_LIMIT = 100

class BudgetLimit(Exception):
    pass

def init(c):
    c.execute('CREATE TABLE IF NOT EXISTS launch_budget(id INTEGER PRIMARY KEY,reserved_micro BIGINT NOT NULL DEFAULT 0,sessions INTEGER NOT NULL DEFAULT 0)')
    c.execute('INSERT INTO launch_budget(id) VALUES(1) ON CONFLICT(id) DO NOTHING')
    c.execute('CREATE TABLE IF NOT EXISTS budget_sessions(id TEXT PRIMARY KEY,game_id BIGINT,images INTEGER NOT NULL DEFAULT 0,texts INTEGER NOT NULL DEFAULT 0,created TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS budget_active(game_id BIGINT PRIMARY KEY,session_id TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS budget_calls(id TEXT PRIMARY KEY,session_id TEXT,kind TEXT,operation TEXT,model TEXT,status TEXT,reserved_micro BIGINT,actual_micro BIGINT,usage_json TEXT,created TEXT)')
    c.execute('CREATE INDEX IF NOT EXISTS budget_calls_session ON budget_calls(session_id)')

def admit(c, gid, fresh=False):
    # Shared row lock serializes admissions across processes and PostgreSQL replicas.
    c.execute('UPDATE launch_budget SET sessions=sessions WHERE id=1')
    old=c.execute('SELECT session_id FROM budget_active WHERE game_id=?',(gid,)).fetchone()
    if old and not fresh:return old['session_id']
    row=c.execute('SELECT * FROM launch_budget WHERE id=1').fetchone()
    if row['sessions']>=GAME_LIMIT or row['reserved_micro']+SESSION_RESERVE>CAP:
        raise BudgetLimit('pilot_limit')
    sid=secrets.token_hex(16)
    c.execute('UPDATE launch_budget SET sessions=sessions+1,reserved_micro=reserved_micro+? WHERE id=1',(SESSION_RESERVE,))
    c.execute('INSERT INTO budget_sessions(id,game_id,created) VALUES(?,?,?)',(sid,gid,datetime.now(timezone.utc).isoformat()))
    c.execute('INSERT INTO budget_active(game_id,session_id) VALUES(?,?) ON CONFLICT(game_id) DO UPDATE SET session_id=EXCLUDED.session_id',(gid,sid))
    return sid

@contextmanager
def scope(cn, gid, operation):
    if not os.getenv('OPENAI_API_KEY','').strip():
        yield
        return
    with cn() as c:sid=admit(c,gid)
    token=ACTIVE.set((cn,sid,str(operation)))
    try:yield
    finally:ACTIVE.reset(token)

def begin(kind,model):
    state=ACTIVE.get()
    if state is None:return None  # standalone tests/tools; server calls always use scope
    cn,sid,operation=state
    column,limit,allowance=('images',IMAGE_LIMIT,IMAGE_ALLOWANCE) if kind=='image' else ('texts',TEXT_LIMIT,TEXT_ALLOWANCE)
    with cn() as c:
        c.execute('UPDATE launch_budget SET sessions=sessions WHERE id=1')
        if c.execute('SELECT reserved_micro FROM launch_budget WHERE id=1').fetchone()['reserved_micro']>CAP:
            raise BudgetLimit('pilot_limit')
        s=c.execute('SELECT * FROM budget_sessions WHERE id=?',(sid,)).fetchone()
        if not s or s[column]>=limit:raise BudgetLimit('game_ai_limit')
        count=c.execute('SELECT COUNT(*) AS n FROM budget_calls WHERE session_id=? AND kind=? AND operation=?',(sid,kind,operation)).fetchone()['n']
        if count>=(4 if operation=='image:99' else 3):raise BudgetLimit('retry_limit')
        ident=secrets.token_hex(16)
        c.execute(f'UPDATE budget_sessions SET {column}={column}+1 WHERE id=?',(sid,))
        c.execute('INSERT INTO budget_calls(id,session_id,kind,operation,model,status,reserved_micro,created) VALUES(?,?,?,?,?,?,?,?)',(ident,sid,kind,operation,model,'started',allowance,datetime.now(timezone.utc).isoformat()))
    return (cn,ident)

def finish(ticket,usage=None,status='success'):
    if ticket is None:return
    cn,ident=ticket
    data=usage.model_dump() if hasattr(usage,'model_dump') else usage if isinstance(usage,dict) else None
    with cn() as c:
        c.execute('UPDATE launch_budget SET sessions=sessions WHERE id=1')
        row=c.execute('SELECT * FROM budget_calls WHERE id=?',(ident,)).fetchone()
        if not row or row['status']!='started':return
        actual=None
        if row['kind']=='image' and row['model']=='gpt-image-2.5-flare' and data:
            details=data.get('input_tokens_details') or {}
            if all(k in details for k in ('text_tokens','image_tokens')) and 'output_tokens' in data:
                # Official standard rates: $5 text in, $8 image in, $30 image out / 1M.
                actual=int(details['text_tokens']*5+details['image_tokens']*8+data['output_tokens']*30)
        c.execute('UPDATE budget_calls SET status=?,actual_micro=?,usage_json=? WHERE id=?',(status,actual,json.dumps(data) if data is not None else None,ident))
        # Never release unused reservations automatically. Stop if actual exceeds envelope.
        if actual is not None and actual>row['reserved_micro']:
            c.execute('UPDATE launch_budget SET reserved_micro=reserved_micro+? WHERE id=1',(actual-row['reserved_micro'],))
        print(json.dumps({'event':'ai_cost','call_id':ident,'kind':row['kind'],'status':status,'actual_usd':actual/1e6 if actual is not None else None,'provisional_usd':row['reserved_micro']/1e6}),flush=True)

def report(c,gid):
    active=c.execute('SELECT session_id FROM budget_active WHERE game_id=?',(gid,)).fetchone()
    if not active:return {'calls':0,'measured_usd':0,'unpriced_calls':0,'estimated_usd':0,'provisional':True}
    rows=c.execute('SELECT * FROM budget_calls WHERE session_id=?',(active['session_id'],)).fetchall()
    known=sum(r['actual_micro'] or 0 for r in rows)
    unknown=[r for r in rows if r['actual_micro'] is None]
    return {'calls':len(rows),'measured_usd':round(known/1e6,6),'unpriced_calls':len(unknown),'estimated_usd':round((known+sum(r['reserved_micro'] for r in unknown))/1e6,6),'provisional':True,'image_calls':sum(r['kind']=='image' for r in rows),'text_calls':sum(r['kind']=='text' for r in rows)}

def pricing(rounds=18,games=1):
    if games not in (1,2) or not 8<=rounds<=30:raise ValueError('invalid_quote')
    base=799 if games==1 else 1299
    extra=max(0,rounds-18)*49
    return {'currency':'USD','checkout_enabled':False,'stage':'pilot','single_cents':799,'duo_cents':1299,'included_rounds':18,'extra_question_cents':49,'free_rounds':8,'max_rounds':30,'max_players':6,'games':games,'rounds':rounds,'base_cents':base,'extra_cents':extra,'total_cents':base+extra,'extra_applies_to':'one_game'}
