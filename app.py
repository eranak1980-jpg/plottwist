from __future__ import annotations

import json
import mimetypes
import os
import urllib.request
import urllib.error
import io
import qrcode
import random
import secrets
import sqlite3
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "party_game.db"
STATIC_DIR = BASE_DIR / "static"


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_column(conn, table, name, decl):
    cols = {r["name"] for r in conn.execute(f"PRAGMA table_info({table})")}
    if name not in cols:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {name} {decl}")


def init_db():
    with db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS games (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          code TEXT UNIQUE NOT NULL,
          host_token TEXT NOT NULL,
          theme TEXT NOT NULL,
          tone TEXT NOT NULL,
          duration INTEGER NOT NULL,
          status TEXT NOT NULL DEFAULT 'lobby',
          round_no INTEGER NOT NULL DEFAULT 0,
          killer_player_id INTEGER,
          created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS players (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          game_id INTEGER NOT NULL,
          name TEXT NOT NULL,
          token TEXT UNIQUE NOT NULL,
          role_name TEXT,
          secret TEXT,
          objective TEXT,
          joined_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS votes (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          game_id INTEGER NOT NULL,
          round_no INTEGER NOT NULL,
          voter_player_id INTEGER NOT NULL,
          accused_player_id INTEGER NOT NULL,
          created_at TEXT NOT NULL,
          UNIQUE(game_id, round_no, voter_player_id)
        );
        CREATE TABLE IF NOT EXISTS gm_events (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          game_id INTEGER NOT NULL,
          round_no INTEGER NOT NULL,
          prompt TEXT NOT NULL,
          response TEXT NOT NULL,
          created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS feedback (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          game_id INTEGER NOT NULL,
          player_id INTEGER NOT NULL,
          fun_score INTEGER NOT NULL,
          clarity_score INTEGER NOT NULL,
          replay INTEGER NOT NULL,
          note TEXT DEFAULT '',
          created_at TEXT NOT NULL,
          UNIQUE(game_id, player_id)
        );
        """)
        for name, decl in [
            ("group_name", "TEXT DEFAULT ''"),
            ("relationship", "TEXT DEFAULT ''"),
            ("inside_joke", "TEXT DEFAULT ''"),
            ("location", "TEXT DEFAULT ''"),
            ("intensity", "TEXT DEFAULT 'balanced'"),
            ("story_title", "TEXT DEFAULT ''"),
            ("victim_name", "TEXT DEFAULT ''"),
            ("rounds_json", "TEXT DEFAULT ''"),
            ("engine", "TEXT DEFAULT 'local'"),
            ("round_started_at", "TEXT DEFAULT ''"),
            ("round_seconds", "INTEGER DEFAULT 600"),
            ("game_type", "TEXT DEFAULT 'murder'"),
        ]:
            ensure_column(conn, "games", name, decl)
        for name, decl in [
            ("private_hint", "TEXT DEFAULT ''"),
        ]:
            ensure_column(conn, "players", name, decl)



def ai_enabled():
    return bool(os.getenv("OPENAI_API_KEY"))

def generate_ai_case(game, players):
    """Optional real-AI case generation. Falls back safely to the local engine."""
    key=os.getenv("OPENAI_API_KEY")
    if not key:
        return None
    names=[p["name"] for p in players]
    prompt=f"""Create a coherent Hebrew social party mystery game for {len(names)} adults. Game mode: {game['game_type']}.
If mode is murder, use a classic non-graphic murder mystery. If mode is heist, use a stolen-object caper with a hidden mastermind and no killing. If mode is secrets, use a scandal/secret-leak mystery with one hidden saboteur and no killing.
Players: {', '.join(names)}. Group: {game['group_name']}. Relationship: {game['relationship']}.
Location: {game['location']}. Theme: {game['theme']}. Tone: {game['tone']}. Inside joke/detail: {game['inside_joke']}.
Return ONLY valid JSON with keys: title, victim, killer_name, roles, rounds.
roles must be an array with one item per player: name, role_name, secret, objective, private_hint. Exactly one role must be the killer.
private_hint is a short additional clue revealed privately from round 2 onward; it must be consistent with the mystery and must not directly reveal the killer.
rounds must be exactly 4 Hebrew strings. Build one solvable mystery: clues must be consistent, round 4 must ask for final vote, and do not reveal killer before the end.
Avoid graphic violence, sexual content, or humiliating personal claims. Treat supplied personal details as playful fictional inspiration only."""
    body={"model":os.getenv("OPENAI_MODEL","gpt-4.1-mini"),"input":prompt}
    req=urllib.request.Request("https://api.openai.com/v1/responses", data=json.dumps(body).encode(), headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=35) as r:
            payload=json.loads(r.read().decode())
        text=payload.get("output_text")
        if not text:
            chunks=[]
            for item in payload.get("output",[]):
                for c in item.get("content",[]):
                    if c.get("type") in ("output_text","text") and c.get("text"): chunks.append(c["text"])
            text="".join(chunks)
        if not text: return None
        text=text.strip().removeprefix("```json").removesuffix("```").strip()
        data=json.loads(text)
        if len(data.get("roles",[]))!=len(players) or len(data.get("rounds",[]))!=4: return None
        return data
    except Exception as e:
        print("AI generation fallback:", e)
        return None

def make_code():
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    while True:
        code = "".join(random.choice(alphabet) for _ in range(5))
        with db() as conn:
            if not conn.execute("SELECT 1 FROM games WHERE code=?", (code,)).fetchone():
                return code


def get_game(code):
    with db() as conn:
        return conn.execute("SELECT * FROM games WHERE code=?", (code.upper(),)).fetchone()


def get_players(game_id):
    with db() as conn:
        return conn.execute("SELECT * FROM players WHERE game_id=? ORDER BY id", (game_id,)).fetchall()


def build_story(game, players):
    place = game["location"] or "הסלון"
    joke = game["inside_joke"] or "הבדיחה שרק אתם מבינים"
    mode = game["game_type"] or "murder"
    if mode == "heist":
        return f"היהלום שנעלם אצל {game['group_name']}", "יהלום הלילה", joke
    if mode == "secrets":
        return f"הסוד של {game['group_name']}", "הקובץ הסודי", joke
    return f"הכוס האחרונה ב{place}", "אלכס רוזן", joke

def assign_roles(game_id):
    game = None
    with db() as conn:
        game = conn.execute("SELECT * FROM games WHERE id=?", (game_id,)).fetchone()
    players = get_players(game_id)
    if len(players) < 4:
        raise ValueError("need_4_players")

    ai_case = generate_ai_case(game, players)
    if ai_case:
        by_name={r.get("name"):r for r in ai_case["roles"]}
        killer_name=ai_case.get("killer_name")
        killer=next((p for p in players if p["name"]==killer_name), None)
        if killer and all(p["name"] in by_name for p in players):
            with db() as conn:
                conn.execute("UPDATE games SET killer_player_id=?, story_title=?, victim_name=?, rounds_json=?, engine='ai' WHERE id=?",
                             (killer["id"], ai_case.get("title","תעלומת הלילה"), ai_case.get("victim","הקורבן"), json.dumps(ai_case["rounds"],ensure_ascii=False), game_id))
                for p in players:
                    r=by_name[p["name"]]
                    conn.execute("UPDATE players SET role_name=?, secret=?, objective=?, private_hint=? WHERE id=?",
                                 (r.get("role_name","חשוד/ה"), r.get("secret",""), r.get("objective",""), r.get("private_hint",""), p["id"]))
            return

    killer = random.choice(players)
    title, victim, joke = build_story(game, players)
    names = [p["name"] for p in players]
    place = game["location"] or "הסלון"
    intensity = game["intensity"] or "balanced"

    role_defs = [
        ("הצלם/ת של הערב", "צילמת בטעות משהו ברקע של סרטון רגע לפני כיבוי האורות.", "לגרום לשני שחקנים למסור ציר זמן לפני שתחשוף/י מה ראית."),
        ("שומר/ת הסוד", f"{victim} סיפר/ה לך מוקדם יותר שהוא/היא עומד/ת לחשוף סוד על אחד מהנוכחים.", "לגלות למי היה הכי הרבה מה להפסיד, בלי לחשוף מיד את כל מה שנאמר לך."),
        ("המארח/ת האובססיבי/ת", f"את/ה זוכר/ת בדיוק מי נכנס ויצא מ{place} לאורך הערב.", "לתפוס לפחות סתירה אחת בין שני סיפורים."),
        ("החבר/ה שנעלם/ה", "נעדרת לכמה דקות בדיוק לפני האירוע, ויש לך סיבה תמימה — אבל מביכה — לכך.", "להגן על האליבי שלך בלי לחשוף את הסיבה עד שמישהו מאשים אותך ישירות."),
        ("האספן/ית", "מצאת חפץ קטן שלא שייך לך. הוא יכול להפיל מישהו — או להציל אותו.", "לגלות למי החפץ שייך לפני סוף הסיבוב השלישי."),
        ("החשדן/ית", "כבר מתחילת הערב הרגשת שמשהו לא בסדר, אבל אף אחד לא לקח אותך ברצינות.", "לשאול שלוש שאלות חדות ולהכריח מישהו לשנות גרסה."),
        ("האקס/ית מהעבר", f"קיבלת מ-{victim} הודעה מסתורית: 'הלילה זה נגמר'.", "להבין למה ההודעה התכוונה בלי להפוך לחשוד/ה המרכזי/ת."),
        ("העד/ה הלא אמין/ה", "ראית חלק מהאירוע דרך השתקפות בחלון, אבל ייתכן שפירשת אותו לא נכון.", "לשתף את הרמז שלך רק אחרי ששמעת שתי תיאוריות שונות."),
        ("המתווך/ת", "את/ה יודע/ת ששני אנשים בחדר רבו מוקדם יותר, אבל שניהם ביקשו ממך לשמור על זה בסוד.", "להחליט איזה סוד לחשוף ומתי, כדי למנוע מהקבוצה להאשים אדם חף מפשע."),
    ]
    random.shuffle(role_defs)

    with db() as conn:
        conn.execute("UPDATE games SET killer_player_id=?, story_title=?, victim_name=?, rounds_json='', engine='local' WHERE id=?", (killer["id"], title, victim, game_id))
        idx = 0
        for p in players:
            other_names = [n for n in names if n != p["name"]]
            random.shuffle(other_names)
            if p["id"] == killer["id"]:
                framed = other_names[0] if other_names else "שחקן אחר"
                secret_text = f"את/ה אחראי/ת למה שקרה ל-{victim}. כיבוי האורות נתן לך חלון של 8 שניות. פרט מסוכן: {framed} כמעט ראה אותך חוזר/ת ל{place}."
                objective = f"להרחיק חשד מעצמך ולגרום לפחות לאדם אחד לחשוד ב-{framed}. אל תמציא/י עובדות חדשות שלא הופיעו במשחק."
                hint = f"רמז פרטי: מישהו זוכר שראה אותך ליד {place} לפני כיבוי האורות. אם ישאלו — כדאי שתהיה לך גרסה עקבית."
                conn.execute("UPDATE players SET role_name=?, secret=?, objective=?, private_hint=? WHERE id=?", ("הרוצח/ת", secret_text, objective, hint, p["id"]))
            else:
                role, secret_text, objective = role_defs[idx % len(role_defs)]
                idx += 1
                if intensity == "wild":
                    objective += " מותר לך להיות דרמטי/ת במיוחד."
                hint_pool = [
                    f"רמז פרטי: פרט קטן ששמעת קודם מתחבר ל-{victim}; אל תחשוף/י אותו לפני שמישהו מציג אליבי.",
                    f"רמז פרטי: יש סתירה קטנה בין מה שנאמר על {place} לבין מה שראית בעצמך.",
                    "רמז פרטי: אחד השחקנים בטוח מדי בגרסה שלו. נסה/י לשאול אותו שאלה מאוד ספציפית.",
                    f"רמז פרטי: משהו שקשור ל-{joke[:28]} כנראה חשוב יותר ממה שנראה.",
                ]
                conn.execute("UPDATE players SET role_name=?, secret=?, objective=?, private_hint=? WHERE id=?", (role, secret_text, objective, random.choice(hint_pool), p["id"]))


def round_prompt(game, n):
    if game["rounds_json"]:
        try:
            rounds=json.loads(game["rounds_json"])
            if 1 <= n <= len(rounds): return rounds[n-1]
        except Exception: pass
    title=game["story_title"] or "תעלומת הלילה"
    victim=game["victim_name"] or "הקורבן"
    place=game["location"] or "החדר"
    joke=game["inside_joke"] or "פרט פנימי"
    mode=game["game_type"] or "murder"
    if mode=="heist":
        prompts={
            1:f"🚨 {title}. {victim} נעלם בזמן כיבוי אורות קצר ב{place}. לכל אחד יש סוד ומניע אפשרי. הציגו את הדמות שלכם — אבל לא את הסוד.",
            2:f"🔎 ליד המקום שבו נשמר {victim} הופיע סימן שקשור ל״{joke[:45]}״. לכל שחקן נפתח עכשיו רמז פרטי. חקרו זה את זה.",
            3:"⚡ מישהו שינה פרט באליבי שלו. עברו אחד־אחד: איפה הייתם בזמן כיבוי האורות, ומי יכול לאשר את זה?",
            4:"🗳️ הגיע הזמן להאשים. לכל אחד 20 שניות לטיעון אחרון, ואז הצבעה סודית."
        }
    elif mode=="secrets":
        prompts={
            1:f"📁 {title}. {victim} הודלף באמצע הערב ב{place}. מישהו כאן עשה את זה בכוונה. הציגו את הדמות שלכם בלי לחשוף את הסוד.",
            2:f"🔎 הרמז הראשון מחבר את ההדלפה ל״{joke[:45]}״. לכל שחקן נפתח רמז פרטי. התחילו לשאול שאלות ממוקדות.",
            3:"⚡ צצה סתירה חדשה. כל אחד חייב לספר דבר אחד אמיתי ודבר אחד שאולי אינו אמיתי.",
            4:"🗳️ מי החבלן? הצבעה סופית. לפני כן: 20 שניות לכל שחקן להסביר למה הוא חף מפשע."
        }
    else:
        prompts={
            1:f"🥂 {title}. {victim} נמצא ללא רוח חיים אחרי שכיבוי אורות קצר קטע את הערב ב{place}. כולם חשודים. הציגו את הדמות ומה עשיתם לפני כיבוי האורות — אבל שמרו את הסוד.",
            2:f"🔎 ליד הזירה נמצא פתק קרוע עם המילים ״{joke[:45]}״. לכל שחקן נפתח עכשיו רמז פרטי. חקרו לפחות שני אנשים.",
            3:"⚡ אחד האליבים שנאמרו בחדר אינו יכול להיות נכון. עברו אחד־אחד וחזרו על האליבי במשפט אחד. אחרי כל אליבי מותרת שאלה חדה אחת.",
            4:"🗳️ זמן ההכרעה. לכל שחקן 20 שניות: מי עשה את זה ומה המניע? לאחר מכן הצביעו בסוד."
        }
    return prompts.get(n,"המשחק הסתיים.")

def calc_round_seconds(game):
    # Keep the experience moving even if the host selected a long total duration.
    total = int(game["duration"] or 60) * 60
    return max(300, min(900, total // 4))

def remaining_seconds(game):
    raw = game["round_started_at"]
    if not raw or game["status"] != "playing":
        return 0
    try:
        started = datetime.fromisoformat(raw)
        elapsed = (datetime.now(timezone.utc) - started).total_seconds()
        return max(0, int((game["round_seconds"] or 600) - elapsed))
    except Exception:
        return int(game["round_seconds"] or 600)

def generate_gm_reaction(game, summary):
    summary = (summary or "").strip()[:500]
    if not summary:
        return "ה־Game Master מחכה לעדכון קצר על מה שקרה בחדר."
    key = os.getenv("OPENAI_API_KEY")
    if key:
        prompt = f"""You are the live Game Master of a Hebrew murder-mystery party game.
Title: {game['story_title']}. Round: {game['round_no']}. Tone: {game['tone']}.
The host reports this just happened in the room: {summary}
Write ONE short Hebrew intervention (max 55 words) that reacts to the group and advances tension without revealing the killer or inventing a contradiction with established facts. It may introduce a neutral clue, force a choice, or ask one pointed question."""
        body={"model":os.getenv("OPENAI_MODEL","gpt-4.1-mini"),"input":prompt}
        req=urllib.request.Request("https://api.openai.com/v1/responses", data=json.dumps(body).encode(), headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                payload=json.loads(r.read().decode())
            text=payload.get("output_text")
            if not text:
                chunks=[]
                for item in payload.get("output",[]):
                    for c in item.get("content",[]):
                        if c.get("text"): chunks.append(c["text"])
                text="".join(chunks)
            if text:
                return text.strip()[:650]
        except Exception as e:
            print("GM reaction fallback:", e)
    templates = [
        f"ה־Game Master עוצר את כולם: בעקבות מה שקרה — {summary[:150]} — כל אחד חייב עכשיו לתת תשובה אחת בלי להתחמק: מה הפרט הכי חשוד ששמעת עד עכשיו?",
        f"טוויסט חי: {summary[:140]}. עכשיו בחרו אדם אחד שיצטרך לחזור על האליבי שלו מהתחלה, בלי שמישהו יפריע לו.",
        f"החדר נהיה שקט. {summary[:140]}. ה־Game Master מכריז: מי ששמר פרט לעצמו עד עכשיו חייב לחשוף לפחות חצי ממנו.",
    ]
    return random.choice(templates)

def vote_summary(game_id, killer_id):
    with db() as conn:
        rows = conn.execute("""
            SELECT p.name, COUNT(v.id) votes
            FROM players p LEFT JOIN votes v ON v.accused_player_id=p.id AND v.game_id=?
            WHERE p.game_id=? GROUP BY p.id ORDER BY votes DESC, p.id
        """, (game_id, game_id)).fetchall()
        correct = conn.execute("SELECT COUNT(*) c FROM votes WHERE game_id=? AND accused_player_id=?", (game_id, killer_id)).fetchone()["c"]
        total = conn.execute("SELECT COUNT(*) c FROM votes WHERE game_id=?", (game_id,)).fetchone()["c"]
    return [{"name": r["name"], "votes": r["votes"]} for r in rows], correct, total


class Handler(BaseHTTPRequestHandler):
    def _json(self, payload, status=200):
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _body_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        return json.loads(raw.decode("utf-8") or "{}")

    def _serve_file(self, path: Path):
        if not path.exists() or not path.is_file():
            self.send_error(404); return
        data = path.read_bytes()
        ctype = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers(); self.wfile.write(data)

    def do_GET(self):
        u = urlparse(self.path); path = u.path; q = parse_qs(u.query)
        if path == "/": return self._serve_file(STATIC_DIR / "index.html")
        if path == "/health":
            return self._json({"ok": True})
        if path.startswith("/static/"):
            return self._serve_file(STATIC_DIR / path.split("/static/", 1)[1])
        if path.startswith("/api/qr/"):
            code = path.split("/api/qr/", 1)[1].upper()
            game = get_game(code)
            if not game: return self._json({"error":"not_found"},404)
            if APP_BASE_URL:
                join_url = f"{APP_BASE_URL}/?code={code}"
            else:
                scheme = self.headers.get("X-Forwarded-Proto","http")
                host = self.headers.get("Host","localhost:5000")
                join_url = f"{scheme}://{host}/?code={code}"
            img = qrcode.make(join_url)
            buf = io.BytesIO(); img.save(buf, format="PNG"); data = buf.getvalue()
            self.send_response(200)
            self.send_header("Content-Type","image/png")
            self.send_header("Cache-Control","no-store")
            self.send_header("Content-Length",str(len(data)))
            self.end_headers(); self.wfile.write(data); return
        if path.startswith("/api/game/"):
            code = path.split("/api/game/", 1)[1].upper(); game = get_game(code)
            if not game: return self._json({"error": "not_found"}, 404)
            token = q.get("token", [""])[0]; host_token = q.get("host", [""])[0]
            with db() as conn:
                player = conn.execute("SELECT * FROM players WHERE token=? AND game_id=?", (token, game["id"])).fetchone()
                players = conn.execute("SELECT * FROM players WHERE game_id=? ORDER BY id", (game["id"],)).fetchall()
                latest_event = conn.execute("SELECT * FROM gm_events WHERE game_id=? ORDER BY id DESC LIMIT 1", (game["id"],)).fetchone()
            payload = {
                "code": game["code"], "theme": game["theme"], "tone": game["tone"], "game_type": game["game_type"], "duration": game["duration"],
                "group_name": game["group_name"], "location": game["location"], "relationship": game["relationship"],
                "status": game["status"], "round_no": game["round_no"], "story_title": game["story_title"], "victim_name": game["victim_name"], "engine": game["engine"],
                "round_prompt": round_prompt(game, game["round_no"]) if game["status"] == "playing" else None,
                "round_seconds": int(game["round_seconds"] or 600), "remaining_seconds": remaining_seconds(game),
                "latest_gm_event": ({"round_no":latest_event["round_no"],"response":latest_event["response"]} if latest_event else None),
                "players": [{"id": p["id"], "name": p["name"], "role_name": p["role_name"] if game["status"] == "finished" else None} for p in players],
                "is_host": bool(host_token and secrets.compare_digest(host_token, game["host_token"])),
                "me": None, "killer": None, "vote_summary": [], "correct_votes": 0, "total_votes": 0,
            }
            if player:
                payload["me"] = {k: player[k] for k in ("id", "name", "role_name", "secret", "objective")}
                payload["me"]["private_hint"] = player["private_hint"] if game["status"]=="playing" and game["round_no"]>=2 else "" 
            if game["status"] == "finished":
                killer = next((p for p in players if p["id"] == game["killer_player_id"]), None)
                if killer: payload["killer"] = {"id": killer["id"], "name": killer["name"]}
                summary, correct, total = vote_summary(game["id"], game["killer_player_id"])
                payload["vote_summary"], payload["correct_votes"], payload["total_votes"] = summary, correct, total
            return self._json(payload)
        self.send_error(404)

    def do_POST(self):
        path = urlparse(self.path).path; data = self._body_json()
        if path == "/api/create":
            code = make_code(); host_token = secrets.token_urlsafe(18); player_token = secrets.token_urlsafe(18)
            with db() as conn:
                cur = conn.execute("""
                    INSERT INTO games(code,host_token,theme,tone,duration,group_name,relationship,inside_joke,location,intensity,created_at)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?)
                """, (
                    code, host_token, (data.get("theme") or "מסתורין מודרני").strip(), (data.get("tone") or "מצחיק ומותח").strip(),
                    int(data.get("duration") or 60), (data.get("group_name") or "החבורה").strip(), (data.get("relationship") or "חברים").strip(),
                    (data.get("inside_joke") or "").strip(), (data.get("location") or "הסלון").strip(), (data.get("intensity") or "balanced").strip(), now_iso()
                ))
                gid = cur.lastrowid
                conn.execute("INSERT INTO players(game_id,name,token,joined_at) VALUES(?,?,?,?)", (gid, (data.get("name") or "Host").strip(), player_token, now_iso()))
            return self._json({"code": code, "host": host_token, "token": player_token})

        if path == "/api/join":
            game = get_game((data.get("code") or "").upper())
            if not game: return self._json({"error": "not_found"}, 404)
            if game["status"] != "lobby": return self._json({"error": "already_started"}, 400)
            name = (data.get("name") or "Guest").strip()
            if not name: return self._json({"error": "name_required"}, 400)
            token = secrets.token_urlsafe(18)
            with db() as conn:
                if conn.execute("SELECT 1 FROM players WHERE game_id=? AND lower(name)=lower(?)", (game["id"], name)).fetchone():
                    return self._json({"error": "name_taken"}, 400)
                conn.execute("INSERT INTO players(game_id,name,token,joined_at) VALUES(?,?,?,?)", (game["id"], name, token, now_iso()))
            return self._json({"code": game["code"], "token": token})

        if path.startswith("/api/game/"):
            parts = path.strip("/").split("/")
            if len(parts) != 4: return self._json({"error": "bad_path"}, 404)
            _, _, code, action = parts; game = get_game(code)
            if not game: return self._json({"error": "not_found"}, 404)

            if action in {"start", "next"}:
                if not data.get("host") or not secrets.compare_digest(data.get("host"), game["host_token"]):
                    return self._json({"error": "forbidden"}, 403)
                if action == "start":
                    try: assign_roles(game["id"])
                    except ValueError: return self._json({"error": "need_4_players"}, 400)
                    with db() as conn:
                        seconds=calc_round_seconds(game)
                        conn.execute("UPDATE games SET status='playing', round_no=1, round_started_at=?, round_seconds=? WHERE id=?", (now_iso(), seconds, game["id"]))
                    return self._json({"ok": True, "round_no": 1, "status": "playing"})
                next_no = game["round_no"] + 1
                status = "finished" if next_no > 4 else "playing"
                with db() as conn:
                    conn.execute("UPDATE games SET status=?, round_no=?, round_started_at=? WHERE id=?", (status, next_no, now_iso() if status=="playing" else "", game["id"]))
                return self._json({"ok": True, "round_no": next_no, "status": status})

            if action == "react":
                if not data.get("host") or not secrets.compare_digest(data.get("host"), game["host_token"]):
                    return self._json({"error":"forbidden"},403)
                if game["status"] != "playing":
                    return self._json({"error":"not_playing"},400)
                summary=(data.get("summary") or "").strip()
                if not summary: return self._json({"error":"summary_required"},400)
                response=generate_gm_reaction(game,summary)
                with db() as conn:
                    conn.execute("INSERT INTO gm_events(game_id,round_no,prompt,response,created_at) VALUES(?,?,?,?,?)",(game["id"],game["round_no"],summary[:500],response,now_iso()))
                return self._json({"ok":True,"response":response})

            if action == "feedback":
                token = data.get("token")
                with db() as conn:
                    player = conn.execute(
                        "SELECT * FROM players WHERE game_id=? AND token=?",
                        (game["id"], token)
                    ).fetchone() if token else None
                if not player:
                    return self._json({"error": "forbidden"}, 403)
                try:
                    fun = max(1, min(5, int(data.get("fun_score", 0))))
                    clarity = max(1, min(5, int(data.get("clarity_score", 0))))
                except Exception:
                    return self._json({"error": "bad_feedback"}, 400)
                replay = 1 if bool(data.get("replay")) else 0
                note = (data.get("note") or "").strip()[:1000]
                with db() as conn:
                    conn.execute(
                        '''INSERT INTO feedback(game_id,player_id,fun_score,clarity_score,replay,note,created_at)
                           VALUES(?,?,?,?,?,?,?)
                           ON CONFLICT(game_id,player_id) DO UPDATE SET
                             fun_score=excluded.fun_score,
                             clarity_score=excluded.clarity_score,
                             replay=excluded.replay,
                             note=excluded.note,
                             created_at=excluded.created_at''',
                        (game["id"], player["id"], fun, clarity, replay, note, now_iso())
                    )
                return self._json({"ok": True})

            if action == "vote":
                if game["status"] != "playing" or game["round_no"] < 4:
                    return self._json({"error": "voting_closed"}, 400)
                with db() as conn:
                    voter = conn.execute("SELECT * FROM players WHERE token=? AND game_id=?", (data.get("token", ""), game["id"])).fetchone()
                    accused = conn.execute("SELECT * FROM players WHERE id=? AND game_id=?", (int(data.get("accused_id", 0)), game["id"])).fetchone()
                    if not voter or not accused or voter["id"] == accused["id"]: return self._json({"error": "invalid_vote"}, 400)
                    conn.execute("INSERT OR REPLACE INTO votes(game_id,round_no,voter_player_id,accused_player_id,created_at) VALUES(?,?,?,?,?)", (game["id"], game["round_no"], voter["id"], accused["id"], now_iso()))
                return self._json({"ok": True})

        self.send_error(404)

    def log_message(self, fmt, *args):
        return


def run(host="0.0.0.0", port=5000):
    init_db(); print(f"PlotTwist running on http://localhost:{port}")
    ThreadingHTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    run()
