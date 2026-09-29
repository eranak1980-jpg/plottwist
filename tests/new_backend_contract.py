"""Focused HTTP contract tests for chat, preserved-room reset, and lean state.

This file intentionally runs against the real request handler and a temporary
SQLite database.  It avoids image generation and external API calls.
"""

import json
import os
import sys
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

tmp = tempfile.TemporaryDirectory()
os.environ["DATABASE_PATH"] = str(Path(tmp.name) / "new-backend-contract.db")
os.environ.pop("DATABASE_URL", None)
os.environ.pop("OPENAI_API_KEY", None)

import kyc_server as k  # noqa: E402


# Keep this integration test deterministic and offline.  The contracts under
# test do not depend on either question-pack preparation or image generation.
k.prepare_pack_async = lambda *_args, **_kwargs: None
k.schedule_image_after_action = lambda *_args, **_kwargs: None
k.init()

server = k.ThreadingHTTPServer(("127.0.0.1", 0), k.H)
server_thread = threading.Thread(target=server.serve_forever, daemon=True)
server_thread.start()
BASE = f"http://127.0.0.1:{server.server_port}"


def call(path, body=None):
    encoded = None if body is None else json.dumps(body, ensure_ascii=False).encode()
    request = Request(
        BASE + path,
        data=encoded,
        method="GET" if body is None else "POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urlopen(request, timeout=10) as response:
            status = response.status
            raw = response.read()
    except HTTPError as error:
        status = error.code
        raw = error.read()
    return status, json.loads(raw.decode()), raw


def expect(path, body=None, status=200):
    actual, payload, raw = call(path, body)
    assert actual == status, (path, actual, payload)
    return payload, raw


def state_path(code, token, host=""):
    query = {"token": token}
    if host:
        query["host"] = host
    return f"/api/state/{code}?{urlencode(query)}"


try:
    # A room with realistic settings and three identities, one of which is
    # marked inactive before the preserved-room reset.
    created, _ = expect(
        "/api/create",
        {
            "name": "Host",
            "client_id": "device-host",
            "gender": "male",
            "topics": ["טיולים וחופשות", "מוזיקה"],
            "context": "Friends from a long trip",
            "spice": 2,
            "prize": "Coffee machine",
            "rounds": 9,
            "language": "fr",
        },
    )
    old_code = created["code"]
    guest, _ = expect(
        "/api/join",
        {
            "code": old_code,
            "name": "Guest",
            "client_id": "device-guest",
            "gender": "female",
        },
    )
    removed, _ = expect(
        "/api/join",
        {
            "code": old_code,
            "name": "Removed",
            "client_id": "device-removed",
        },
    )
    game = k.game(old_code)
    original_run = int(game["image_run"])
    player_rows = k.players(game["id"])
    player_by_name = {player["name"]: player for player in player_rows}

    # Deliberately large stored photos prove that polling state returns URLs and
    # readiness flags rather than copying blobs into every response.
    host_photo = "data:image/jpeg;base64," + ("QUJD" * 600_000)
    guest_photo = "data:image/jpeg;base64," + ("REVG" * 600_000)
    removed_photo = "data:image/jpeg;base64," + ("R0hJ" * 50_000)
    with k.cn() as db:
        db.execute(
            "UPDATE players SET photo_data=?,photo_consent=1,adult_confirmed=1,score=7 "
            "WHERE id=?",
            (host_photo, player_by_name["Host"]["id"]),
        )
        db.execute(
            "UPDATE players SET photo_data=?,photo_consent=1,adult_confirmed=1,score=5 "
            "WHERE id=?",
            (guest_photo, player_by_name["Guest"]["id"]),
        )
        db.execute(
            "UPDATE players SET photo_data=?,photo_consent=1,active=0,score=99 WHERE id=?",
            (removed_photo, player_by_name["Removed"]["id"]),
        )
        db.execute(
            "INSERT INTO topic_votes(game_id,player_id,topic) VALUES(?,?,?)",
            (game["id"], player_by_name["Guest"]["id"], "אוכל"),
        )

    lean_state, lean_raw = expect(
        state_path(old_code, created["token"], created["host"])
    )
    assert len(lean_raw) < 100_000, len(lean_raw)
    assert b"data:image" not in lean_raw and b"QUJDQUJDQUJD" not in lean_raw
    assert lean_state["me"]["has_photo"] is True
    assert all("photo_data" not in player for player in lean_state["players"])
    assert all(
        player["photo_url"].startswith(f"/api/photo/{old_code}/")
        for player in lean_state["players"]
        if player["has_photo"]
    )
    print("STATE_MULTI_MEGABYTE_PHOTOS_STAY_LEAN_OK")

    # Chat requires an active room identity for both reads and writes.
    expect(f"/api/chat/{old_code}", status=403)
    expect(
        f"/api/{old_code}/chat",
        {"token": "not-a-player", "kind": "text", "body": "hello", "client_msg_id": "x"},
        status=403,
    )
    expect(
        f"/api/{old_code}/chat",
        {"token": created["token"], "kind": "text", "body": "hello"},
        status=400,
    )
    expect(
        f"/api/{old_code}/chat",
        {
            "token": created["token"],
            "kind": "reaction",
            "body": "👍",
            "client_msg_id": "bad-reaction",
        },
        status=400,
    )
    expect(
        f"/api/{old_code}/chat",
        {
            "token": created["token"],
            "kind": "text",
            "body": "x" * 281,
            "client_msg_id": "too-long",
        },
        status=400,
    )

    first, _ = expect(
        f"/api/{old_code}/chat",
        {
            "token": created["token"],
            "kind": "text",
            "body": "Ready to play?",
            "client_msg_id": "host-1",
        },
    )
    second, _ = expect(
        f"/api/{old_code}/chat",
        {
            "token": guest["token"],
            "kind": "reaction",
            "body": "😂",
            "client_msg_id": "guest-1",
        },
    )
    third, _ = expect(
        f"/api/{old_code}/chat",
        {
            "token": created["token"],
            "kind": "text",
            "body": "Let's go",
            "client_msg_id": "host-2",
        },
    )
    duplicate, _ = expect(
        f"/api/{old_code}/chat",
        {
            "token": created["token"],
            "kind": "text",
            "body": "this retry must not overwrite the first body",
            "client_msg_id": "host-1",
        },
    )
    assert duplicate["message"]["id"] == first["message"]["id"]
    assert duplicate["message"]["body"] == "Ready to play?"

    all_chat, _ = expect(f"/api/chat/{old_code}?{urlencode({'token': guest['token']})}")
    all_ids = [message["id"] for message in all_chat["messages"]]
    assert all_ids == sorted(all_ids)
    assert all_ids == [
        first["message"]["id"],
        second["message"]["id"],
        third["message"]["id"],
    ]
    delta, _ = expect(
        f"/api/chat/{old_code}?{urlencode({'token': guest['token'], 'after': all_ids[0]})}"
    )
    assert [message["id"] for message in delta["messages"]] == all_ids[1:]
    expect(
        f"/api/chat/{old_code}?{urlencode({'token': guest['token'], 'after': 'nope'})}",
        status=400,
    )
    with k.cn() as db:
        count = db.execute(
            "SELECT COUNT(*) AS n FROM chat_messages WHERE game_id=?", (game["id"],)
        ).fetchone()["n"]
    assert count == 3
    print("CHAT_AUTH_VALIDATION_IDEMPOTENCY_AND_DELTA_ORDERING_OK")

    # Seed every per-run table so freshroom has to clear real state, while game
    # settings and the active players' identities/photos must survive.
    seeded_memory = json.dumps(
        [{"round": 0, "subject": "Host", "question": "Old?", "answer": "Yes", "type": "know"}]
    )
    with k.cn() as db:
        db.execute(
            "UPDATE games SET status='playing',round_no=3,answer='Yes',memory=?,"
            "custom_questions=?,tiebreak=?,image_run=? WHERE id=?",
            (
                seeded_memory,
                json.dumps([["know", "Old generated question", ["Yes", "No"]]]),
                json.dumps({"sets": 1}),
                original_run + 4,
                game["id"],
            ),
        )
        db.execute(
            "INSERT INTO guesses(game_id,round_no,player_id,guess) VALUES(?,?,?,?)",
            (game["id"], 3, player_by_name["Guest"]["id"], "Yes"),
        )
        db.execute(
            "INSERT INTO round_scores(game_id,round_no,created) VALUES(?,?,?)",
            (game["id"], 3, k.now()),
        )
        db.execute(
            "INSERT INTO match_answers(game_id,round_no,player_id,answer,created) VALUES(?,?,?,?,?)",
            (game["id"], 3, player_by_name["Host"]["id"], "legacy", k.now()),
        )
        db.execute(
            "INSERT INTO match_scores(game_id,round_no,matched,created) VALUES(?,?,?,?)",
            (game["id"], 3, 1, k.now()),
        )
        db.execute(
            "INSERT INTO image_jobs(game_id,image_run,round_no,job_id,status,payload,created,deadline,error) "
            "VALUES(?,?,?,?,?,?,?,?,?)",
            (game["id"], original_run + 4, 3, "job", "ready", "{}", 1.0, 2.0, ""),
        )
        db.execute(
            "INSERT INTO hero_scenes(game_id,round_no,image_data,created) VALUES(?,?,?,?)",
            (game["id"], 3, "data:image/jpeg;base64,old", k.now()),
        )
        db.execute(
            "INSERT INTO instant_scenes(game_id,image_run,round_no,category,image_data,seconds) "
            "VALUES(?,?,?,?,?,?)",
            (game["id"], original_run + 4, 3, "travel", "data:image/jpeg;base64,old", 0.1),
        )

    expect(
        f"/api/{old_code}/freshroom", {"host": "wrong-host"}, status=403
    )
    assert k.game(old_code) is not None
    reset, _ = expect(
        f"/api/{old_code}/freshroom", {"host": created["host"]}
    )
    new_code = reset["code"]
    assert reset == {
        "ok": True,
        "code": new_code,
        "old_code": old_code,
        "preserved": True,
    }
    assert new_code != old_code and k.game(old_code) is None

    fresh = k.game(new_code)
    assert fresh["id"] == game["id"]
    assert fresh["status"] == "lobby" and fresh["round_no"] == 0
    assert fresh["answer"] == "" and json.loads(fresh["memory"]) == []
    assert json.loads(fresh["custom_questions"]) == []
    assert json.loads(fresh["tiebreak"]) == {}
    assert fresh["image_run"] == original_run + 5
    assert json.loads(fresh["topics"]) == ["טיולים וחופשות", "מוזיקה"]
    assert fresh["custom_context"] == "Friends from a long trip"
    assert fresh["spice"] == 2 and fresh["prize"] == "Coffee machine"
    assert fresh["rounds"] == 9 and fresh["language"] == "fr"

    survivors = k.players(fresh["id"], include_photos=True)
    assert [player["name"] for player in survivors] == ["Host", "Guest"]
    expected_sessions = {
        "Host": (created["token"], host_photo, "device-host", "male"),
        "Guest": (guest["token"], guest_photo, "device-guest", "female"),
    }
    for player in survivors:
        token, photo, client_id, gender = expected_sessions[player["name"]]
        assert player["token"] == token and player["photo_data"] == photo
        assert player["photo_consent"] == 1 and player["adult_confirmed"] == 1
        assert player["client_id"] == client_id and player["gender"] == gender
        assert player["active"] == 1 and player["score"] == 0
    with k.cn() as db:
        assert not db.execute(
            "SELECT 1 FROM players WHERE token=?", (removed["token"],)
        ).fetchone()
        for table in (
            "guesses",
            "round_scores",
            "match_answers",
            "match_scores",
            "image_jobs",
            "hero_scenes",
            "instant_scenes",
            "chat_messages",
        ):
            remaining = db.execute(
                f"SELECT COUNT(*) AS n FROM {table} WHERE game_id=?", (fresh["id"],)
            ).fetchone()["n"]
            assert remaining == 0, (table, remaining)
        vote = db.execute(
            "SELECT topic FROM topic_votes WHERE game_id=? AND player_id=?",
            (fresh["id"], player_by_name["Guest"]["id"]),
        ).fetchone()
        assert vote and vote["topic"] == "אוכל"

    stale_state, _ = expect(
        state_path(old_code, created["token"], created["host"])
    )
    assert stale_state["code"] == new_code and stale_state["me"]["name"] == "Host"
    stale_chat, _ = expect(
        f"/api/chat/{old_code}?{urlencode({'token': guest['token']})}"
    )
    assert stale_chat["code"] == new_code and stale_chat["messages"] == []
    recovered_post, _ = expect(
        f"/api/{old_code}/chat",
        {
            "token": guest["token"],
            "kind": "reaction",
            "body": "❤️",
            "client_msg_id": "after-reset",
        },
    )
    assert recovered_post["code"] == new_code
    print("FRESHROOM_PRESERVES_CREW_SETTINGS_AND_RECOVERS_STALE_LINK_OK")

    # Host auth and the transaction/CAS around start guarantee that a double tap
    # or concurrent retry starts exactly once.
    expect(f"/api/{new_code}/start", {"host": "wrong-host"}, status=403)
    barrier = threading.Barrier(3)

    def race_start():
        barrier.wait()
        return call(f"/api/{new_code}/start", {"host": created["host"]})

    with ThreadPoolExecutor(max_workers=2) as pool:
        attempts = [pool.submit(race_start) for _ in range(2)]
        barrier.wait()
        race_results = [attempt.result(timeout=15) for attempt in attempts]
    race_statuses = sorted(result[0] for result in race_results)
    assert race_statuses == [200, 409], race_results
    rejected = next(result[1] for result in race_results if result[0] == 409)
    assert rejected["error"] == "already_started"
    expect(
        f"/api/{new_code}/start", {"host": created["host"]}, status=409
    )
    print("START_DOUBLE_CALL_AND_RACE_REJECTED_OK")

    # Match Twist is no longer part of state and cannot block moving on from a
    # fully revealed round.  The legacy submission route is closed.
    playing, _ = expect(
        state_path(new_code, created["token"], created["host"])
    )
    assert playing["interactive"] == "" and playing["interactive_match"] is None
    expect(
        f"/api/{new_code}/matchanswer",
        {"token": created["token"], "answer": "legacy"},
        status=403,
    )
    token_by_player_id = {
        player_by_name["Host"]["id"]: created["token"],
        player_by_name["Guest"]["id"]: guest["token"],
    }
    subject_id = playing["subject"]["id"]
    guesser_id = next(player_id for player_id in token_by_player_id if player_id != subject_id)
    answer = playing["options"][0]
    expect(
        f"/api/{new_code}/answer",
        {
            "token": token_by_player_id[subject_id],
            "answer": answer,
            "image_run": int(playing["image_run"]) - 1,
            "round": playing["round"],
        },
        status=409,
    )
    expect(
        f"/api/{new_code}/answer",
        {
            "token": token_by_player_id[subject_id],
            "answer": answer,
            "image_run": playing["image_run"],
            "round": playing["round"] + 1,
        },
        status=409,
    )
    expect(
        f"/api/{new_code}/answer",
        {
            "token": token_by_player_id[subject_id],
            "answer": answer,
            "image_run": playing["image_run"],
            "round": playing["round"],
        },
    )
    expect(
        f"/api/{new_code}/guess",
        {"token": token_by_player_id[guesser_id], "guess": answer},
    )
    reveal, _ = expect(
        state_path(new_code, created["token"], created["host"])
    )
    assert reveal["reveal"] is True
    assert reveal["interactive"] == "" and reveal["interactive_match"] is None
    expect(
        f"/api/{new_code}/next",
        {
            "host": created["host"],
            "image_run": reveal["image_run"],
            "round": reveal["round"],
        },
    )
    advanced, _ = expect(
        state_path(new_code, created["token"], created["host"])
    )
    assert advanced["round"] == 1 and advanced["status"] == "playing"
    print("STALE_RUN_ROUND_REJECTED_AND_MATCH_TWIST_NONBLOCKING_OK")

    print("NEW_BACKEND_CONTRACT_OK")
finally:
    server.shutdown()
    server.server_close()
    server_thread.join(timeout=2)
    tmp.cleanup()
