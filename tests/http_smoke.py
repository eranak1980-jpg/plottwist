import json, os, sys, tempfile, threading
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
tmp = tempfile.TemporaryDirectory()
os.environ['DATABASE_PATH'] = str(Path(tmp.name) / 'http-qa.db')
os.environ.pop('DATABASE_URL', None)
os.environ.pop('OPENAI_API_KEY', None)

import kyc_server as k

k.init()
srv = k.ThreadingHTTPServer(('127.0.0.1', 0), k.H)
thread = threading.Thread(target=srv.serve_forever, daemon=True)
thread.start()
BASE = f'http://127.0.0.1:{srv.server_port}'


def request(path, body=None, expected=200):
    data = None if body is None else json.dumps(body, ensure_ascii=False).encode()
    req = Request(
        BASE + path,
        data=data,
        method='GET' if body is None else 'POST',
        headers={'Content-Type': 'application/json'},
    )
    try:
        with urlopen(req, timeout=5) as r:
            status = r.status
            payload = json.loads(r.read().decode())
    except HTTPError as e:
        status = e.code
        payload = json.loads(e.read().decode())
    assert status == expected, (path, status, payload)
    return payload


try:
    # Device-aware duplicate join: retry/reopen must recover the same Player.
    c = request('/api/create', {
        'name': 'Eran', 'topics': [], 'spice': 1, 'rounds': 6,
        'client_id': 'device-host',
    })
    code, host_token, eran_token = c['code'], c['host'], c['token']
    j1 = request('/api/join', {'code': code, 'name': 'Shai', 'client_id': 'device-shai'})
    j2 = request('/api/join', {'code': code, 'name': 'Shai', 'client_id': 'device-shai'})
    assert j2['recovered'] and j2['token'] == j1['token']
    g = k.game(code)
    assert len(k.players(g['id'])) == 2
    print('HTTP_DUPLICATE_RECONNECT_OK')

    # Reconnect from a persisted token returns the current player/game state.
    st = request(f"/api/state/{code}?token={j1['token']}")
    assert st['me']['name'] == 'Shai' and st['code'] == code
    assert st['language'] == 'en'
    print('HTTP_TOKEN_RECONNECT_OK')
    print('HTTP_DEFAULT_ENGLISH_OK')

    # Explicit room language persists server-side and is inherited by joiners.
    jp = request('/api/create', {
        'name': 'Yuki', 'topics': [], 'spice': 1, 'rounds': 6,
        'client_id': 'jp-host', 'language': 'ja',
    })
    jp_guest = request('/api/join', {'code': jp['code'], 'name': 'Hana', 'client_id': 'jp-guest'})
    jp_state = request(f"/api/state/{jp['code']}?token={jp_guest['token']}")
    assert jp_state['language'] == 'ja'
    print('HTTP_ROOM_LANGUAGE_PERSISTS_OK')

    # Start is immediate. First secret answer / prediction is locked server-side.
    request(f'/api/{code}/start', {'host': host_token})
    st_host = request(f'/api/state/{code}?token={eran_token}&host={host_token}')
    assert st_host['mode'] == 'duo' and len(st_host['options']) >= 3
    assert st_host['subject']['name'] == 'Eran'
    correct = st_host['options'][0]
    wrong = st_host['options'][1]
    request(f'/api/{code}/answer', {'token': eran_token, 'answer': correct})
    request(f'/api/{code}/answer', {'token': eran_token, 'answer': wrong})
    request(f'/api/{code}/guess', {'token': j1['token'], 'guess': correct})
    request(f'/api/{code}/guess', {'token': j1['token'], 'guess': wrong})
    st_shai = request(f"/api/state/{code}?token={j1['token']}")
    shai = next(p for p in st_shai['players'] if p['name'] == 'Shai')
    assert st_shai['reveal'] and st_shai['my_guess'] == correct and shai['score'] == 1
    print('HTTP_IDEMPOTENT_SCORE_AND_SUBMIT_OK')

    # Once the first reveal has happened, rollback to lobby is intentionally closed.
    locked = request(f'/api/{code}/reopen', {'host': host_token}, expected=409)
    assert locked['error'] == 'too_late'
    print('HTTP_REOPEN_AFTER_REVEAL_BLOCKED_OK')

    # Before the first reveal, host may return to lobby.
    c2 = request('/api/create', {'name': 'Host2', 'topics': [], 'spice': 1, 'rounds': 6, 'client_id': 'h2'})
    j = request('/api/join', {'code': c2['code'], 'name': 'Guest2', 'client_id': 'g2'})
    request(f"/api/{c2['code']}/start", {'host': c2['host']})
    request(f"/api/{c2['code']}/reopen", {'host': c2['host']})
    back = request(f"/api/state/{c2['code']}?token={c2['token']}&host={c2['host']}")
    assert back['status'] == 'lobby'
    print('HTTP_FIRST_ROUND_REOPEN_OK')

    # An actually stale/disconnected player becomes removable; Duo no longer blocks forever.
    request(f"/api/{c2['code']}/start", {'host': c2['host']})
    g2 = k.game(c2['code'])
    guest = next(p for p in k.players(g2['id']) if p['name'] == 'Guest2')
    with k.cn() as db:
        db.execute("UPDATE players SET last_seen='2000-01-01T00:00:00+00:00' WHERE id=?", (guest['id'],))
    stale = request(f"/api/state/{c2['code']}?token={c2['token']}&host={c2['host']}")
    gp = next(p for p in stale['players'] if p['id'] == guest['id'])
    assert not gp['connected'] and gp['can_continue_without']
    dropped = request(f"/api/{c2['code']}/drop", {'host': c2['host'], 'player_id': guest['id']})
    assert dropped.get('finished')
    ended = request(f"/api/state/{c2['code']}?token={c2['token']}&host={c2['host']}")
    assert ended['status'] == 'finished'
    print('HTTP_DISCONNECT_DOES_NOT_BLOCK_DUO_OK')

    # Final round completes into the final screen state.
    c3 = request('/api/create', {'name': 'A', 'topics': [], 'spice': 1, 'rounds': 6, 'client_id': 'a3'})
    b3 = request('/api/join', {'code': c3['code'], 'name': 'B', 'client_id': 'b3'})
    request(f"/api/{c3['code']}/start", {'host': c3['host']})
    g3 = k.game(c3['code'])
    with k.cn() as db:
        db.execute("UPDATE games SET round_no=5,answer='',memory='[]' WHERE id=?", (g3['id'],))
        db.execute("DELETE FROM guesses WHERE game_id=?", (g3['id'],))
        db.execute("DELETE FROM round_scores WHERE game_id=?", (g3['id'],))
    sg = request(f"/api/state/{c3['code']}?token={b3['token']}")
    assert sg['subject']['name'] == 'B'
    a = sg['options'][0]
    request(f"/api/{c3['code']}/answer", {'token': b3['token'], 'answer': a})
    request(f"/api/{c3['code']}/guess", {'token': c3['token'], 'guess': a})
    reveal = request(f"/api/state/{c3['code']}?token={c3['token']}&host={c3['host']}")
    assert reveal['reveal'] and reveal['round'] == 5
    request(f"/api/{c3['code']}/next", {'host': c3['host']})
    final = request(f"/api/state/{c3['code']}?token={c3['token']}&host={c3['host']}")
    assert final['status'] == 'finished'
    print('HTTP_FINAL_ROUND_OK')

    # Play Again keeps the crew but resets run state and scores; question history remains external.
    old_question = reveal['question']
    old_key = k.question_key(old_question, k.players(g3['id']))
    assert old_key in k.past_question_keys(k.players(g3['id']))
    request(f"/api/{c3['code']}/replay", {'host': c3['host']})
    replay = request(f"/api/state/{c3['code']}?token={c3['token']}&host={c3['host']}")
    assert replay['status'] == 'lobby' and len(replay['players']) == 2
    assert all(p['score'] == 0 for p in replay['players']) and replay['history'] == []
    request(f"/api/{c3['code']}/start", {'host': c3['host']})
    fresh = request(f"/api/state/{c3['code']}?token={c3['token']}&host={c3['host']}")
    assert not k.too_similar(k.question_key(fresh['question'], k.players(g3['id'])), {old_key})
    print('HTTP_PLAY_AGAIN_NEW_QUESTIONS_OK')

    # Adult intimacy is 18+ even when the room is not No Filter.
    adult = request('/api/create', {
        'name': 'AdultHost', 'topics': ['אינטימיות למבוגרים'], 'spice': 1,
        'rounds': 6, 'client_id': 'adult-device',
    }, expected=400)
    assert adult['error'] == 'adults_confirmation_required'
    adult_ok = request('/api/create', {
        'name': 'AdultHost', 'topics': ['אינטימיות למבוגרים'], 'spice': 1,
        'rounds': 6, 'client_id': 'adult-device', 'adults_confirmed': True,
    })
    assert adult_ok['code']
    print('HTTP_ADULT_TOPIC_GATE_OK')

    print('HTTP_SMOKE_OK')
finally:
    srv.shutdown()
    srv.server_close()
    thread.join(timeout=2)
    tmp.cleanup()
