"""Create/join/play at the AI ceiling, without provider calls or real payments."""
import json
import os
import sys
import tempfile
import threading
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
tmp = tempfile.TemporaryDirectory()
os.environ.update(DATABASE_PATH=str(Path(tmp.name) / 'invite.db'),
                  MIPO_COMMERCE_ENABLED='1', MIPO_OWNER_HASH_SECRET='test-owner')
os.environ.pop('DATABASE_URL', None)
if os.getenv('PLOT_IMAGE_TEST_DATABASE_URL'):
    os.environ['DATABASE_URL'] = os.environ['PLOT_IMAGE_TEST_DATABASE_URL']
os.environ.pop('OPENAI_API_KEY', None)
import kyc_server as k
import mipo_commerce as commerce

k.init()
os.environ['OPENAI_API_KEY'] = 'test-only'
k.budget.CAP = 0
pack_calls = []
k.prepare_pack_async = lambda *args: pack_calls.append(args)

def forbidden_provider(*args, **kwargs):
    raise AssertionError('No external provider call is allowed')

k.generate_many = forbidden_provider
commerce._provider_post = forbidden_provider
server = k.ThreadingHTTPServer(('127.0.0.1', 0), k.H)
threading.Thread(target=server.serve_forever, daemon=True).start()

def request(path, body=None, expected=200):
    data = json.dumps(body).encode() if body is not None else None
    req = Request(f'http://127.0.0.1:{server.server_port}' + path,
                  data=data, headers={'Content-Type': 'application/json'})
    try:
        with urlopen(req, timeout=5) as response:
            status, result = response.status, json.load(response)
    except HTTPError as error:
        status, result = error.code, json.load(error)
    assert status == expected, (path, status, result)
    return result

try:
    # Use a unique identity even when run after the PostgreSQL image suite.
    client = 'invite-capacity-' + os.urandom(8).hex()
    body = {'name': 'Host', 'client_id': client, 'language': 'en', 'rounds': 8,
            'ai_images_enabled': True, 'spice': 3, 'adults_confirmed': True}
    with k.cn() as db:
        before = db.execute('SELECT COUNT(*) AS n FROM budget_sessions').fetchone()['n']
    assert request('/api/create', body, 429)['error'] == 'pilot_limit'
    assert request('/api/create', {**body, 'allow_ai_fallback': 'true'}, 429)['error'] == 'pilot_limit'
    access = request('/api/access?client_id=' + client)
    assert access['trial_available'], 'failed admission must not consume the trial'

    room = request('/api/create', {**body, 'allow_ai_fallback': True})
    assert room['ai_fallback_used'] is True
    path = '/api/' + room['code']
    state_url = '/api/state/' + room['code'] + '?token=' + room['token'] + '&host=' + room['host']
    state = request(state_url)
    assert state['status'] == 'lobby' and state['ai_images_enabled'] is False
    assert state['adult_required'] and state['me']['adult_confirmed']
    assert not request('/api/access?client_id=' + client)['trial_available']
    assert pack_calls == [], 'fallback must not schedule a paid question pack'
    with k.cn() as db:
        assert db.execute('SELECT COUNT(*) AS n FROM budget_sessions').fetchone()['n'] == before
    request(path + '/image-settings', {'host': room['host'], 'enabled': True}, 429)
    assert request(state_url)['ai_images_enabled'] is False

    # The public invite still joins the same room and all eight rounds work.
    tokens = {state['me']['id']: room['token']}
    for index in range(3):
        guest = request('/api/join', {'code': room['code'], 'name': 'Guest ' + str(index)})
        request(path + '/adultconfirm', {'token': guest['token'], 'confirmed': True})
        guest_state = request('/api/state/' + room['code'] + '?token=' + guest['token'])
        tokens[guest_state['me']['id']] = guest['token']
    request(path + '/start', {'host': room['host']})
    for round_no in range(8):
        state = request(state_url)
        assert state['round'] == round_no and len(state['options']) >= 2
        subject = state['subject']['id']
        answer = state['options'][0]
        request(path + '/answer', {'token': tokens[subject], 'answer': answer})
        for player_id, token in tokens.items():
            if player_id != subject:
                request(path + '/guess', {'token': token, 'guess': answer})
        assert request(state_url)['reveal']
        request(path + '/next', {'host': room['host']})
    assert request(state_url)['status'] == 'finished'
    assert pack_calls == []

    # A failed attempt also preserves a previously purchased game credit.
    paid_client = client + '-paid'
    entitlement = 'ent-' + os.urandom(8).hex()
    with k.cn() as db:
        db.execute('INSERT INTO commerce_entitlements(id,order_id,owner_key,games_total,games_remaining,created) VALUES(?,?,?,?,?,?)',
                   (entitlement, entitlement, commerce.owner_key(paid_client), 2, 2, k.now()))
        db.execute('INSERT INTO budget_order_holds(order_id,slots_remaining,created) VALUES(?,?,?)',
                   (entitlement, 2, k.now()))
    paid_body = {**body, 'client_id': paid_client}
    request('/api/create', paid_body, 429)
    assert request('/api/access?client_id=' + paid_client)['paid_games'] == 2
    with k.cn() as db:
        assert db.execute('SELECT slots_remaining FROM budget_order_holds WHERE order_id=?', (entitlement,)).fetchone()['slots_remaining'] == 2
    paid_room = request('/api/create', {**paid_body, 'allow_ai_fallback': True})
    assert paid_room['ai_fallback_used']
    assert request('/api/access?client_id=' + paid_client)['paid_games'] == 1
    with k.cn() as db:
        assert db.execute('SELECT slots_remaining FROM budget_order_holds WHERE order_id=?', (entitlement,)).fetchone()['slots_remaining'] == 1
    assert pack_calls == []
    print('INVITE_CAPACITY_EXPLICIT_FALLBACK_TRIAL_PAID_CREDIT_JOIN_8_ROUNDS_NO_PROVIDER_OK')
finally:
    server.shutdown()
    server.server_close()
    k.VISUAL_POOL.shutdown(wait=True)
    tmp.cleanup()
