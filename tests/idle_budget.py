"""Release abandoned reservations, then create real HTTP AI jobs for trial/paid rooms."""
import base64
import io
import json
import os
import secrets
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
tmp = tempfile.TemporaryDirectory()
os.environ.update(DATABASE_PATH=str(Path(tmp.name) / 'idle.db'),
                  MIPO_COMMERCE_ENABLED='1', MIPO_OWNER_HASH_SECRET='test-idle-owner')
os.environ.pop('DATABASE_URL', None)
if os.getenv('PLOT_IMAGE_TEST_DATABASE_URL'):
    os.environ['DATABASE_URL'] = os.environ['PLOT_IMAGE_TEST_DATABASE_URL']
os.environ.pop('OPENAI_API_KEY', None)
import kyc_server as k
import kyc_budget as b
import mipo_commerce as commerce

k.init()
old = (datetime.now(timezone.utc) - timedelta(hours=26)).isoformat()

def reset_budget():
    with k.cn() as db:
        for table in ('budget_calls', 'budget_active', 'budget_sessions', 'budget_allocations', 'budget_order_holds'):
            db.execute('DELETE FROM ' + table)
        db.execute('UPDATE launch_budget SET reserved_micro=0,sessions=0 WHERE id=1')

def liability():
    with k.cn() as db:
        return db.execute('SELECT reserved_micro FROM launch_budget WHERE id=1').fetchone()['reserved_micro']

def allocation(sid):
    with k.cn() as db:
        return dict(db.execute('SELECT * FROM budget_allocations WHERE session_id=?', (sid,)).fetchone())

def fixture():
    code = secrets.token_hex(6)
    with k.cn() as db:
        db.execute('INSERT INTO games(code,status,access_kind,created) VALUES(?,?,?,?)', (code, 'lobby', 'trial', k.now()))
        gid = db.execute('SELECT id FROM games WHERE code=?', (code,)).fetchone()['id']
        db.execute('INSERT INTO players(game_id,name,joined,last_seen) VALUES(?,?,?,?)', (gid, 'Test', k.now(), k.now()))
        sid = b.admit(db, gid)
    return gid, sid

reset_budget()
# Upgrade the old table shape before populating leases, in both DB backends.
with k.cn() as db:
    db.execute('ALTER TABLE budget_allocations DROP COLUMN parked')
k.init()
rooms = [fixture() for _ in range(7)]
with k.cn() as db:
    for gid, sid in rooms[:6]:
        db.execute('UPDATE budget_sessions SET created=? WHERE id=?', (old, sid))
        db.execute('UPDATE players SET joined=?,last_seen=? WHERE game_id=?', (old, old, gid))
    # Three idle rooms release. A returning player, recent call and live job retain full capacity.
    db.execute('UPDATE players SET last_seen=? WHERE game_id=?', (k.now(), rooms[2][0]))
    for sid, created, actual in [(rooms[1][1], old, 25000), (rooms[1][1], old, None), (rooms[3][1], k.now(), None)]:
        db.execute('INSERT INTO budget_calls(id,session_id,kind,operation,status,reserved_micro,actual_micro,created) VALUES(?,?,?,?,?,?,?,?)',
                   (secrets.token_hex(8), sid, 'image', 'image:0', 'success' if actual else 'unknown_or_failed', b.IMAGE_ALLOWANCE, actual, created))
    db.execute('UPDATE budget_sessions SET images=2 WHERE id=?', (rooms[1][1],))
    for index, deadline in [(4, time.time() + 300), (5, time.time() - 10)]:
        db.execute('INSERT INTO image_jobs(game_id,image_run,round_no,status,deadline) VALUES(?,?,?,?,?)',
                   (rooms[index][0], 0, 0, 'running', deadline))
    db.execute('INSERT INTO budget_order_holds(order_id,slots_remaining,created) VALUES(?,?,?)', ('idle-test-held-order', 1, old))
    b._refresh(db)
before = liability()
with patch.object(b, 'CAP', before):
    fixture()  # A new admission succeeds by reclaiming unused old allowances.
for index in (0, 1, 5):
    assert allocation(rooms[index][1])['parked'] == 1
for index in (2, 3, 4, 6):
    assert allocation(rooms[index][1])['capacity_micro'] == b.TRIAL_RESERVE
assert allocation(rooms[1][1])['capacity_micro'] == 175000, 'retain measured and unknown costs'
with k.cn() as db:
    assert db.execute('SELECT slots_remaining FROM budget_order_holds WHERE order_id=?', ('idle-test-held-order',)).fetchone()['slots_remaining'] == 1

# A parked room cannot make a provider call without reacquiring capacity.
os.environ['OPENAI_API_KEY'] = 'test-only'
with patch.object(b, 'CAP', liability()):
    try:
        with b.scope(k.cn, rooms[1][0], 'image:1'):
            raise AssertionError('Provider work must not start at capacity')
    except b.BudgetLimit:
        pass
assert allocation(rooms[1][1])['parked'] == 1

def resume_room(_):
    with k.cn() as db:
        return b.admit(db, rooms[1][0])

before = liability()
with ThreadPoolExecutor(max_workers=6) as pool:
    assert set(pool.map(resume_room, range(6))) == {rooms[1][1]}
assert liability() == before + b.TRIAL_RESERVE - 175000
with k.cn() as db:
    assert db.execute('SELECT images FROM budget_sessions WHERE id=?', (rooms[1][1],)).fetchone()['images'] == 2
    db.execute('UPDATE players SET last_seen=? WHERE game_id=?', (k.now(), rooms[1][0]))
k.init()
assert allocation(rooms[1][1])['parked'] == 0
assert allocation(rooms[0][1])['parked'] == 1, 'restart preserves idle leases'
print('IDLE_LEASE_MIGRATION_COSTS_ACTIVE_ROOMS_JOBS_CHECKOUT_HOLDS_ATOMIC_REACQUIRE_OK')

# End-to-end opt-in through HTTP with a controlled image provider, no external calls.
reset_budget()
buffer = io.BytesIO()
Image.new('RGB', (128, 128), '#8877cc').save(buffer, format='JPEG')
art = 'data:image/jpeg;base64,' + base64.b64encode(buffer.getvalue()).decode()
generated = []
def generate(**payload):
    generated.append(payload)
    return art
k.generate_many = generate
k.prepare_pack_async = lambda *args: None
server = k.ThreadingHTTPServer(('127.0.0.1', 0), k.H)
threading.Thread(target=server.serve_forever, daemon=True).start()

def request(path, body=None, raw=False):
    req = Request(f'http://127.0.0.1:{server.server_port}' + path,
                  data=json.dumps(body).encode() if body is not None else None,
                  headers={'Content-Type': 'application/json'})
    with urlopen(req, timeout=5) as response:
        return response.read() if raw else json.load(response)

def verify_image(room):
    path = '/api/' + room['code']
    state_url = '/api/state/' + room['code'] + '?token=' + room['token']
    guest = request('/api/join', {'code': room['code'], 'name': 'Guest'})
    request(path + '/photo', {'token': room['token'], 'data_url': art, 'consent': True})
    request(path + '/start', {'host': room['host']})
    state = request(state_url)
    assert state['ai_images_enabled'] is True and state['hero_eligible']
    answer = state['options'][0]
    request(path + '/answer', {'token': room['token'], 'answer': answer})
    request(path + '/guess', {'token': guest['token'], 'guess': answer})
    for _ in range(100):
        state = request(state_url)
        if state['hero']:
            assert request(state['hero'], raw=True) == buffer.getvalue()
            return
        time.sleep(.02)
    raise AssertionError('Selected AI images did not reach Reveal')

try:
    abandoned = fixture()
    with k.cn() as db:
        db.execute('UPDATE budget_sessions SET created=? WHERE id=?', (old, abandoned[1]))
        db.execute('UPDATE players SET joined=?,last_seen=? WHERE game_id=?', (old, old, abandoned[0]))
    with patch.object(b, 'CAP', liability()):
        trial = request('/api/create', {'name': 'Host', 'client_id': 'idle-trial-' + secrets.token_hex(8), 'rounds': 8, 'ai_images_enabled': True})
        assert trial['ai_fallback_used'] is False
        verify_image(trial)
    paid_client = 'idle-paid-' + secrets.token_hex(8)
    entitlement = secrets.token_hex(12)
    with k.cn() as db:
        db.execute('INSERT INTO commerce_entitlements(id,order_id,owner_key,games_total,games_remaining,created) VALUES(?,?,?,?,?,?)',
                   (entitlement, entitlement, commerce.owner_key(paid_client), 1, 1, k.now()))
        db.execute('INSERT INTO budget_order_holds(order_id,slots_remaining,created) VALUES(?,?,?)', (entitlement, 1, k.now()))
        b._refresh(db)
    with patch.object(b, 'CAP', liability()):
        paid = request('/api/create', {'name': 'Host', 'client_id': paid_client, 'rounds': 18, 'ai_images_enabled': True})
        assert paid['ai_fallback_used'] is False
        verify_image(paid)
    assert len(generated) == 2
    print('TRIAL_AND_PAID_AI_OPT_IN_CREATE_PHOTO_ANSWER_GENERATE_DOWNLOAD_AT_CAPACITY_OK')
finally:
    server.shutdown()
    server.server_close()
    k.VISUAL_POOL.shutdown(wait=True)
    k.image_jobs.POOL.shutdown(wait=True)
    tmp.cleanup()
