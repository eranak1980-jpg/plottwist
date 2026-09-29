import base64, io, json, os, sys, tempfile, threading
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
    if path.endswith('/start') and expected==200:
        with k.cn() as c:c.execute("UPDATE players SET photo_data='test-reference',photo_consent=1,adult_confirmed=1 WHERE game_id=?",(k.game(path.split('/')[2])['id'],))
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
        'client_id': 'device-host', 'gender':'male',
    })
    code, host_token, eran_token = c['code'], c['host'], c['token']
    j1 = request('/api/join', {'code': code, 'name': 'Shai', 'client_id': 'device-shai', 'gender':'female'})
    j2 = request('/api/join', {'code': code, 'name': 'Shai', 'client_id': 'device-shai'})
    assert j2['recovered'] and j2['token'] == j1['token']
    g = k.game(code)
    assert len(k.players(g['id'])) == 2
    print('HTTP_DUPLICATE_RECONNECT_OK')

    # Reconnect from a persisted token returns the current player/game state.
    st = request(f"/api/state/{code}?token={j1['token']}")
    assert st['me']['name'] == 'Shai' and st['code'] == code
    print('HTTP_TOKEN_RECONNECT_OK')
    assert st['me']['gender']=='female'  # reconnect without gender must preserve it
    assert next(p for p in st['players'] if p['name']=='Eran')['gender']=='male'
    request(f'/api/{code}/profile', {'token':'invalid','gender':'male'}, expected=404)
    request(f'/api/{code}/profile', {'token':j1['token'],'gender':'invalid'}, expected=400)
    request(f'/api/{code}/profile', {'token':j1['token'],'gender':'unspecified'})
    assert request(f"/api/state/{code}?token={j1['token']}")['me']['gender']=='unspecified'
    print('HTTP_OPTIONAL_GENDER_PERSISTENCE_AND_AUTH_OK')

    # Room chat is private to active members, idempotent on retry, and bounded.
    request(f'/api/chat/{code}', expected=403)
    first_chat = request(f'/api/{code}/chat', {
        'token': eran_token, 'kind': 'text', 'body': 'Ready?', 'client_msg_id': 'host-1',
    })['message']
    duplicate_chat = request(f'/api/{code}/chat', {
        'token': eran_token, 'kind': 'text', 'body': 'must not replace', 'client_msg_id': 'host-1',
    })['message']
    assert duplicate_chat['id'] == first_chat['id'] and duplicate_chat['body'] == 'Ready?'
    reaction = request(f'/api/{code}/chat', {
        'token': j1['token'], 'kind': 'reaction', 'body': '😂', 'client_msg_id': 'guest-1',
    })['message']
    assert reaction['kind'] == 'reaction'
    chat = request(f'/api/chat/{code}?token={eran_token}')
    assert [m['body'] for m in chat['messages']] == ['Ready?', '😂']
    newer = request(f"/api/chat/{code}?token={eran_token}&after={first_chat['id']}")
    assert [m['id'] for m in newer['messages']] == [reaction['id']]
    request(f'/api/{code}/chat', {'token': eran_token, 'kind': 'reaction', 'body': '👍', 'client_msg_id': 'bad-reaction'}, expected=400)
    request(f'/api/{code}/chat', {'token': eran_token, 'kind': 'text', 'body': 'x'*281, 'client_msg_id': 'too-long'}, expected=400)
    print('HTTP_AUTHENTICATED_CHAT_OK')

    # Photo acknowledgement reflects the durable save, independently of a later state refresh.
    from PIL import Image
    photo_bytes = io.BytesIO(); Image.new('RGB', (32, 32), 'purple').save(photo_bytes, format='PNG')
    photo_url = 'data:image/png;base64,' + base64.b64encode(photo_bytes.getvalue()).decode()
    photo_saved = request(f'/api/{code}/photo', {'token': eran_token, 'data_url': photo_url, 'consent': True})
    assert photo_saved['photo_ready'] and photo_saved['has_photo']
    assert request(f'/api/state/{code}?token={eran_token}')['me']['has_photo']
    print('HTTP_PHOTO_DURABLE_ACK_OK')


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
    assert st_shai['interactive'] == '' and st_shai['interactive_match'] is None
    request(f'/api/{code}/matchanswer', {'token': j1['token'], 'answer': 'legacy'}, expected=403)
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
    # New rounds have no generic catch-all, while legacy submitted custom rounds survive.
    from kyc_locales import other_label
    for lang in ['he','en','es','pt-BR','fr','ja']:
        with k.cn() as db:
            db.execute('UPDATE games SET language=?,spice=3,round_no=0,answer=\'\' WHERE id=?',(lang,g3['id']))
        test_game=k.game(c3['code'])
        assert other_label(lang) not in k.qdata(test_game,k.players(g3['id']))[2]
    print('HTTP_NO_GENERIC_OTHER_OPTION_ALL_LANGUAGES_OK')

    # A preserved new room rotates the code and resets only run data. Active
    # player sessions/photos/settings survive; previously dropped players do not.
    keep = request('/api/create', {
        'name': 'KeepHost', 'topics': ['נוסטלגיה'], 'context': 'old friends',
        'prize': 'Coffee machine', 'spice': 1, 'rounds': 8, 'client_id': 'keep-host',
    })
    keep_guest = request('/api/join', {'code': keep['code'], 'name': 'KeepGuest', 'client_id': 'keep-guest'})
    removed = request('/api/join', {'code': keep['code'], 'name': 'Removed', 'client_id': 'removed-device'})
    request(f"/api/{keep['code']}/start", {'host': keep['host']})
    keep_game = k.game(keep['code'])
    with k.cn() as db:
        db.execute("UPDATE games SET round_no=3,answer='old',memory='[{}]' WHERE id=?", (keep_game['id'],))
        db.execute("UPDATE players SET score=7 WHERE game_id=?", (keep_game['id'],))
        db.execute("UPDATE players SET active=0 WHERE token=?", (removed['token'],))
    request(f"/api/{keep['code']}/chat", {'token': keep['token'], 'kind': 'text', 'body': 'old run', 'client_msg_id': 'old-run'})
    old_code = keep['code']
    rotated = request(f'/api/{old_code}/freshroom', {'host': keep['host']})
    assert rotated['preserved'] and rotated['code'] != old_code
    new_code = rotated['code']
    assert k.game(old_code) is None
    recovered = request(f"/api/state/{old_code}?token={keep_guest['token']}&host={keep['host']}")
    assert recovered['code'] == new_code and recovered['status'] == 'lobby' and recovered['history'] == []
    assert {p['name'] for p in recovered['players']} == {'KeepHost', 'KeepGuest'}
    assert all(p['score'] == 0 and p['has_photo'] for p in recovered['players'])
    assert recovered['topics'] == ['נוסטלגיה'] and recovered['context'] == 'old friends' and recovered['prize'] == 'Coffee machine'
    assert request(f"/api/chat/{old_code}?token={keep_guest['token']}")['messages'] == []
    moved_chat = request(f'/api/{old_code}/chat', {'token': keep_guest['token'], 'kind': 'reaction', 'body': '❤️', 'client_msg_id': 'new-run'})
    assert moved_chat['code'] == new_code
    request(f"/api/state/{old_code}?token={removed['token']}", expected=404)
    request(f'/api/{new_code}/start', {'host': keep['host']})
    request(f'/api/{new_code}/start', {'host': keep['host']}, expected=409)
    request('/api/join', {'code': new_code, 'name': 'TooLate', 'client_id': 'too-late'}, expected=409)
    with k.cn() as db:db.execute("UPDATE games SET status='finished' WHERE id=?", (keep_game['id'],))
    request(f'/api/{new_code}/replay', {'host': keep['host']})
    request(f'/api/{new_code}/replay', {'host': keep['host']}, expected=409)
    print('HTTP_FRESH_ROOM_PRESERVES_ACTIVE_CREW_OK')

    # Callback rounds advance without the removed Match Twist secret-answer gate.
    no_match = request('/api/create', {'name': 'Dana', 'topics': [], 'spice': 1, 'rounds': 8, 'client_id': 'no-match-a'})
    no_match_b = request('/api/join', {'code': no_match['code'], 'name': 'Noa', 'client_id': 'no-match-b'})
    request(f"/api/{no_match['code']}/start", {'host': no_match['host']})
    no_match_game = k.game(no_match['code'])
    callback_memory = [
        {'round': 0, 'subject': 'Dana', 'question': 'Q0', 'answer': 'טיסה', 'type': 'know'},
        {'round': 1, 'subject': 'Noa', 'question': 'Q1', 'answer': 'בית', 'type': 'know'},
        {'round': 2, 'subject': 'Dana', 'question': 'Q2', 'answer': 'ספונטני', 'type': 'know'},
    ]
    with k.cn() as db:
        db.execute("UPDATE games SET round_no=4,answer='',memory=? WHERE id=?", (json.dumps(callback_memory, ensure_ascii=False), no_match_game['id']))
        db.execute('DELETE FROM guesses WHERE game_id=?', (no_match_game['id'],))
    callback_state = request(f"/api/state/{no_match['code']}?token={no_match['token']}")
    assert 'callback' in callback_state['type'] and callback_state['interactive_match'] is None
    subject_token = no_match['token'] if callback_state['subject']['name'] == 'Dana' else no_match_b['token']
    guess_token = no_match_b['token'] if subject_token == no_match['token'] else no_match['token']
    callback_answer = callback_state['options'][0]
    request(f"/api/{no_match['code']}/answer", {'token': subject_token, 'answer': callback_answer})
    request(f"/api/{no_match['code']}/guess", {'token': guess_token, 'guess': callback_answer})
    request(f"/api/{no_match['code']}/next", {'host': no_match['host']})
    print('HTTP_MATCH_TWIST_GATE_REMOVED_OK')


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
