"""Persistent $150 launch liability ledger (estimates, not provider invoices).

Live games and payable checkout links hold capacity. Completed games release
unused round capacity; known/unknown call costs and final-image retries remain.
No rollover, budget reset, external charge, or change to AI generation settings.
"""
import contextvars
import json
import os
import secrets
from contextlib import contextmanager
from datetime import datetime, timezone

ACTIVE = contextvars.ContextVar('plot_budget', default=None)
IMAGE_ALLOWANCE = 150000
TEXT_ALLOWANCE = 100000
IMAGE_LIMIT = 60  # 30 rounds + 18 tiebreak rounds + 4 finales + 8 retries
TRIAL_IMAGE_LIMIT = 20  # 8 trial rounds + 4 finales + 8 retries; no tiebreak
TEXT_LIMIT = 3
SESSION_RESERVE = IMAGE_ALLOWANCE * IMAGE_LIMIT + TEXT_ALLOWANCE * TEXT_LIMIT
TRIAL_RESERVE = IMAGE_ALLOWANCE * TRIAL_IMAGE_LIMIT + TEXT_ALLOWANCE * TEXT_LIMIT
CAP = 150000000  # $150 lifetime launch ceiling, never reset automatically
GAME_LIMIT = 100  # historical constant; admissions now use the money ceiling

class BudgetLimit(Exception):
    pass

def _exists(c, table):
    if getattr(c, 'pg', False):
        return bool(c.execute('SELECT to_regclass(?) AS name', (table,)).fetchone()['name'])
    return bool(c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)).fetchone())

def _lock(c):
    # All admissions, checkout holds and call accounting share this PG row lock.
    c.execute('UPDATE launch_budget SET sessions=sessions WHERE id=1')

def _costs(c, sid):
    row = c.execute('SELECT COALESCE(SUM(CASE WHEN actual_micro IS NULL THEN reserved_micro ELSE actual_micro END),0) AS n FROM budget_calls WHERE session_id=?', (sid,)).fetchone()
    return int(row['n'])

def _final_hold(c, sid):
    n = c.execute("SELECT COUNT(*) AS n FROM budget_calls WHERE session_id=? AND operation='image:99' AND kind='image'", (sid,)).fetchone()['n']
    return max(0, 4-int(n)) * IMAGE_ALLOWANCE

def _refresh(c):
    # capacity is a total envelope, inclusive of costs already recorded in it.
    total = int(c.execute('''SELECT COALESCE(SUM(CASE WHEN COALESCE(cost.n,0)>a.capacity_micro
        THEN cost.n ELSE a.capacity_micro END),0) AS n FROM budget_allocations a
        LEFT JOIN (SELECT session_id,SUM(CASE WHEN actual_micro IS NULL THEN reserved_micro
        ELSE actual_micro END) AS n FROM budget_calls GROUP BY session_id) cost
        ON cost.session_id=a.session_id''').fetchone()['n'])
    total += int(c.execute('SELECT COALESCE(SUM(slots_remaining),0) AS n FROM budget_order_holds').fetchone()['n']) * SESSION_RESERVE
    c.execute('UPDATE launch_budget SET reserved_micro=? WHERE id=1', (total,))
    return total

def _profile(c, gid, access_kind=None):
    if access_kind is None and _exists(c, 'games'):
        cols = c.execute('SELECT * FROM games WHERE id=?', (gid,)).fetchone()
        access_kind = cols['access_kind'] if cols and 'access_kind' in cols.keys() else None
    trial = access_kind in ('trial', 'qa')
    return ('trial' if trial else 'paid', TRIAL_RESERVE if trial else SESSION_RESERVE, TRIAL_IMAGE_LIMIT if trial else IMAGE_LIMIT)

def init(c):
    c.execute('CREATE TABLE IF NOT EXISTS launch_budget(id INTEGER PRIMARY KEY,reserved_micro BIGINT NOT NULL DEFAULT 0,sessions INTEGER NOT NULL DEFAULT 0)')
    c.execute('INSERT INTO launch_budget(id) VALUES(1) ON CONFLICT(id) DO NOTHING')
    c.execute('CREATE TABLE IF NOT EXISTS budget_sessions(id TEXT PRIMARY KEY,game_id BIGINT,images INTEGER NOT NULL DEFAULT 0,texts INTEGER NOT NULL DEFAULT 0,created TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS budget_active(game_id BIGINT PRIMARY KEY,session_id TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS budget_calls(id TEXT PRIMARY KEY,session_id TEXT,kind TEXT,operation TEXT,model TEXT,status TEXT,reserved_micro BIGINT,actual_micro BIGINT,usage_json TEXT,created TEXT)')
    c.execute('CREATE INDEX IF NOT EXISTS budget_calls_session ON budget_calls(session_id)')
    c.execute('''CREATE TABLE IF NOT EXISTS budget_allocations(session_id TEXT PRIMARY KEY,
        kind TEXT NOT NULL,capacity_micro BIGINT NOT NULL,image_limit INTEGER NOT NULL,closed INTEGER NOT NULL DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS budget_order_holds(order_id TEXT PRIMARY KEY,
        slots_remaining INTEGER NOT NULL DEFAULT 0,created TEXT NOT NULL)''')
    _lock(c)
    # Idempotent migration: retain every historical call and counter. Never
    # reconstruct already-consumed order slots or discard unknown charges.
    for s in c.execute('SELECT * FROM budget_sessions').fetchall():
        kind, capacity, limit = _profile(c, s['game_id'])
        c.execute('INSERT INTO budget_allocations(session_id,kind,capacity_micro,image_limit) VALUES(?,?,?,?) ON CONFLICT(session_id) DO NOTHING', (s['id'],kind,max(capacity,_costs(c,s['id'])),limit))
    if _exists(c, 'commerce_orders') and _exists(c, 'commerce_entitlements'):
        for o in c.execute('SELECT * FROM commerce_orders').fetchall():
            if o['product'] == 'extension': slots = 0
            elif o['status'] == 'refunded': slots = 0
            elif o['status'] == 'paid':
                ent = c.execute('SELECT games_remaining FROM commerce_entitlements WHERE order_id=?', (o['id'],)).fetchone()
                slots = int(ent['games_remaining']) if ent else 0
            else:
                # Static links remain payable even after a declined attempt;
                # retain their hold rather than overbook on a late approval.
                slots = 2 if o['product'] == 'two_games' else 1
            c.execute('INSERT INTO budget_order_holds(order_id,slots_remaining,created) VALUES(?,?,?) ON CONFLICT(order_id) DO NOTHING', (o['id'],slots,o['created']))
    if _exists(c, 'games'):
        for r in c.execute("SELECT a.game_id FROM budget_active a JOIN games g ON g.id=a.game_id WHERE g.status='finished'").fetchall():
            complete(c,r['game_id'])
    _refresh(c)

def complete(c, gid):
    """Release unused rounds, keeping incurred charges + four final attempts."""
    _lock(c)
    active = c.execute('SELECT session_id FROM budget_active WHERE game_id=?', (gid,)).fetchone()
    if active:
        sid=active['session_id']
        c.execute('UPDATE budget_allocations SET closed=1,capacity_micro=? WHERE session_id=?', (_costs(c,sid)+_final_hold(c,sid),sid))
    _refresh(c)

def resume(c, gid):
    """Reacquire the existing envelope before an optional tiebreak starts."""
    _lock(c)
    a=c.execute('SELECT s.* FROM budget_allocations s JOIN budget_active a ON a.session_id=s.session_id WHERE a.game_id=?',(gid,)).fetchone()
    if not a or not a['closed']:return
    capacity=max(TRIAL_RESERVE if a['kind']=='trial' else SESSION_RESERVE,_costs(c,a['session_id']))
    if _refresh(c)+capacity-int(a['capacity_micro'])>CAP:raise BudgetLimit('pilot_limit')
    c.execute('UPDATE budget_allocations SET capacity_micro=?,closed=0 WHERE session_id=?',(capacity,a['session_id']))
    _refresh(c)

def hold_checkout(c, order_id, product, target_game=None):
    _lock(c)
    if c.execute('SELECT 1 FROM budget_order_holds WHERE order_id=?',(order_id,)).fetchone():return
    slots=2 if product=='two_games' else 0 if product=='extension' else 1
    if product=='extension':
        # Paid sessions already reserve the unchanged 30-round + tie envelope.
        a=c.execute('SELECT s.* FROM budget_allocations s JOIN budget_active a ON a.session_id=s.session_id WHERE a.game_id=?',(target_game['id'],)).fetchone() if target_game else None
        if not a or a['closed'] or a['kind']!='paid':raise BudgetLimit('pilot_limit')
    if _refresh(c)+slots*SESSION_RESERVE>CAP:raise BudgetLimit('pilot_limit')
    c.execute('INSERT INTO budget_order_holds(order_id,slots_remaining,created) VALUES(?,?,?)',(order_id,slots,datetime.now(timezone.utc).isoformat()))
    _refresh(c)

def release_refund(c, order_id):
    _lock(c)
    c.execute('UPDATE budget_order_holds SET slots_remaining=0 WHERE order_id=?',(order_id,))
    _refresh(c)

def admit(c, gid, fresh=False, access_kind=None, entitlement_id=None):
    _lock(c)
    old=c.execute('SELECT session_id FROM budget_active WHERE game_id=?',(gid,)).fetchone()
    if old and not fresh:return old['session_id']
    kind,capacity,limit=_profile(c,gid,access_kind)
    # Transfer a prepaid checkout slot, atomically with consuming its entitlement.
    if entitlement_id is None and _exists(c,'games'):
        g=c.execute('SELECT * FROM games WHERE id=?',(gid,)).fetchone()
        entitlement_id=g['entitlement_id'] if g and 'entitlement_id' in g.keys() else None
    order_id=None
    if kind=='paid' and entitlement_id and _exists(c,'commerce_entitlements'):
        ent=c.execute('SELECT order_id FROM commerce_entitlements WHERE id=?',(entitlement_id,)).fetchone()
        hold=c.execute('SELECT * FROM budget_order_holds WHERE order_id=?',(ent['order_id'],)).fetchone() if ent else None
        if hold and int(hold['slots_remaining'])>0:order_id=ent['order_id']
    needed=capacity-(SESSION_RESERVE if order_id else 0)
    if _refresh(c)+needed>CAP:raise BudgetLimit('pilot_limit')
    # fresh replay ends the old run; its historical charges remain forever.
    if old:complete(c,gid)
    sid=secrets.token_hex(16)
    if order_id:c.execute('UPDATE budget_order_holds SET slots_remaining=slots_remaining-1 WHERE order_id=? AND slots_remaining>0',(order_id,))
    c.execute('UPDATE launch_budget SET sessions=sessions+1 WHERE id=1')
    c.execute('INSERT INTO budget_sessions(id,game_id,created) VALUES(?,?,?)',(sid,gid,datetime.now(timezone.utc).isoformat()))
    c.execute('INSERT INTO budget_allocations(session_id,kind,capacity_micro,image_limit) VALUES(?,?,?,?)',(sid,kind,capacity,limit))
    c.execute('INSERT INTO budget_active(game_id,session_id) VALUES(?,?) ON CONFLICT(game_id) DO UPDATE SET session_id=EXCLUDED.session_id',(gid,sid))
    _refresh(c)
    return sid

@contextmanager
def scope(cn,gid,operation):
    if not os.getenv('OPENAI_API_KEY','').strip():
        yield
        return
    with cn() as c:sid=admit(c,gid)
    token=ACTIVE.set((cn,sid,str(operation)))
    try:yield
    finally:ACTIVE.reset(token)

def begin(kind,model):
    state=ACTIVE.get()
    if state is None:return None
    cn,sid,operation=state
    column,allowance=('images',IMAGE_ALLOWANCE) if kind=='image' else ('texts',TEXT_ALLOWANCE)
    with cn() as c:
        _lock(c)
        s=c.execute('SELECT b.*,a.image_limit,a.capacity_micro,a.closed FROM budget_sessions b JOIN budget_allocations a ON a.session_id=b.id WHERE b.id=?',(sid,)).fetchone()
        if not s or s[column]>=(s['image_limit'] if kind=='image' else TEXT_LIMIT):raise BudgetLimit('game_ai_limit')
        if s['closed'] and operation!='image:99':raise BudgetLimit('game_ai_limit')
        count=c.execute('SELECT COUNT(*) AS n FROM budget_calls WHERE session_id=? AND kind=? AND operation=?',(sid,kind,operation)).fetchone()['n']
        if count>=(4 if operation=='image:99' else 3):raise BudgetLimit('retry_limit')
        extra=max(0,_costs(c,sid)+allowance-int(s['capacity_micro']))
        if _refresh(c)+extra>CAP:raise BudgetLimit('pilot_limit')
        if extra:c.execute('UPDATE budget_allocations SET capacity_micro=capacity_micro+? WHERE session_id=?',(extra,sid))
        ident=secrets.token_hex(16)
        c.execute(f'UPDATE budget_sessions SET {column}={column}+1 WHERE id=?',(sid,))
        c.execute('INSERT INTO budget_calls(id,session_id,kind,operation,model,status,reserved_micro,created) VALUES(?,?,?,?,?,?,?,?)',(ident,sid,kind,operation,model,'started',allowance,datetime.now(timezone.utc).isoformat()))
        _refresh(c)
    return (cn,ident)

def finish(ticket,usage=None,status='success'):
    if ticket is None:return
    cn,ident=ticket
    data=usage.model_dump() if hasattr(usage,'model_dump') else usage if isinstance(usage,dict) else None
    with cn() as c:
        _lock(c)
        row=c.execute('SELECT * FROM budget_calls WHERE id=?',(ident,)).fetchone()
        if not row or row['status']!='started':return
        actual=None
        if row['kind']=='image' and row['model']=='gpt-image-2.5-flare' and data:
            details=data.get('input_tokens_details') or {}
            if all(k in details for k in ('text_tokens','image_tokens')) and 'output_tokens' in data:
                # Existing estimate only; unknown models/text retain allowance.
                actual=int(details['text_tokens']*5+details['image_tokens']*8+data['output_tokens']*30)
        c.execute('UPDATE budget_calls SET status=?,actual_micro=?,usage_json=? WHERE id=?',(status,actual,json.dumps(data) if data is not None else None,ident))
        a=c.execute('SELECT * FROM budget_allocations WHERE session_id=?',(row['session_id'],)).fetchone()
        if a and a['closed']:
            c.execute('UPDATE budget_allocations SET capacity_micro=? WHERE session_id=?',(_costs(c,row['session_id'])+_final_hold(c,row['session_id']),row['session_id']))
        total=_refresh(c)
        print(json.dumps({'event':'ai_cost','call_id':ident,'kind':row['kind'],'status':status,'actual_usd':actual/1e6 if actual is not None else None,'provisional_usd':row['reserved_micro']/1e6,'launch_liability_usd':total/1e6,'launch_warning':total>=CAP*.8}),flush=True)

def report(c,gid):
    active=c.execute('SELECT session_id FROM budget_active WHERE game_id=?',(gid,)).fetchone()
    if not active:return {'calls':0,'measured_usd':0,'unpriced_calls':0,'estimated_usd':0,'provisional':True}
    rows=c.execute('SELECT * FROM budget_calls WHERE session_id=?',(active['session_id'],)).fetchall()
    known=sum(r['actual_micro'] or 0 for r in rows)
    unknown=[r for r in rows if r['actual_micro'] is None]
    return {'calls':len(rows),'measured_usd':round(known/1e6,6),'unpriced_calls':len(unknown),'estimated_usd':round((known+sum(r['reserved_micro'] for r in unknown))/1e6,6),'provisional':True,'image_calls':sum(r['kind']=='image' for r in rows),'text_calls':sum(r['kind']=='text' for r in rows)}

def pricing(rounds=18,games=1):
    from mipo_commerce import quote
    return quote(rounds,games)
