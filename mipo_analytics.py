"""Minimal first-party launch funnel events; no dashboard and no raw identifiers."""
import hashlib
import json
from datetime import datetime, timezone

EVENTS = {
    'landing_page_view', 'click_play_mipo', 'click_free_trial', 'game_started',
    'trial_completed', 'checkout_started', 'purchase_completed', 'game_completed',
}


def init(c):
    ident = 'BIGSERIAL PRIMARY KEY' if getattr(c, 'pg', False) else 'INTEGER PRIMARY KEY'
    c.execute('''CREATE TABLE IF NOT EXISTS analytics_events(
        id ''' + ident + ''', event TEXT NOT NULL, subject_hash TEXT DEFAULT '',
        game_id BIGINT, metadata TEXT DEFAULT '{}', created TEXT NOT NULL)''')
    c.execute('CREATE INDEX IF NOT EXISTS analytics_events_name_created ON analytics_events(event,created)')


def record(c, event, subject='', game_id=None, metadata=None):
    if event not in EVENTS:
        return False
    digest = hashlib.sha256(str(subject or '').encode()).hexdigest()[:24] if subject else ''
    data = json.dumps(metadata or {}, separators=(',', ':'), ensure_ascii=False)[:2000]
    c.execute('INSERT INTO analytics_events(event,subject_hash,game_id,metadata,created) VALUES(?,?,?,?,?)',
              (event, digest, game_id, data, datetime.now(timezone.utc).isoformat()))
    return True
