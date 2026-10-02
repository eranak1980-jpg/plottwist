"""Server-side checkout, entitlements and trial enforcement for MIPO.

PayPlus credentials are read only from the environment.  A hosted payment page
keeps card data outside MIPO.  Entitlements are granted only by a verified
PayPlus callback; redirects never unlock a purchase.
"""
import base64
import hashlib
import hmac
import json
import os
import secrets
import urllib.error
import urllib.request
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation


PRODUCTS = {
    'one_game': {'name': 'MIPO — One Game', 'amount_cents': 799, 'games': 1, 'extension': False},
    'two_games': {'name': 'MIPO — Two Games', 'amount_cents': 1299, 'games': 2, 'extension': False},
    'extension': {'name': 'MIPO — Game Extension (18 to 30 Questions)', 'amount_cents': 299, 'games': 0, 'extension': True},
}
PAYPLUS_PROD = 'https://restapi.payplus.co.il/api/v1.0'
PAYPLUS_TEST = 'https://restapidev.payplus.co.il/api/v1.0'


class CommerceError(Exception):
    def __init__(self, code, status=400):
        super().__init__(code)
        self.code, self.status = code, status


def utcnow():
    return datetime.now(timezone.utc).isoformat()


def enabled(use_pg=False):
    value = os.getenv('MIPO_COMMERCE_ENABLED', '').strip().lower()
    if value:
        return value in ('1', 'true', 'yes', 'on')
    # Launch enforcement is a deliberate switch. Keeping it off until PayPlus
    # credentials and production callbacks are verified avoids locking pilot
    # testers out while paid access is still impossible.
    return False


def checkout_configured():
    return all(os.getenv(k, '').strip() for k in ('PAYPLUS_API_KEY', 'PAYPLUS_SECRET_KEY', 'PAYPLUS_PAYMENT_PAGE_UID', 'PUBLIC_BASE_URL'))


def init(c):
    c.execute('''CREATE TABLE IF NOT EXISTS commerce_orders(
        id TEXT PRIMARY KEY, owner_key TEXT NOT NULL, product TEXT NOT NULL,
        amount_cents INTEGER NOT NULL, currency TEXT NOT NULL DEFAULT 'USD',
        status TEXT NOT NULL DEFAULT 'created', provider_request_uid TEXT UNIQUE,
        provider_transaction_uid TEXT, target_game_id BIGINT, checkout_url TEXT,
        created TEXT NOT NULL, updated TEXT NOT NULL, raw_callback TEXT DEFAULT '')''')
    c.execute('CREATE INDEX IF NOT EXISTS commerce_orders_owner ON commerce_orders(owner_key,created)')
    c.execute('''CREATE TABLE IF NOT EXISTS commerce_entitlements(
        id TEXT PRIMARY KEY, order_id TEXT UNIQUE NOT NULL, owner_key TEXT NOT NULL,
        games_total INTEGER NOT NULL DEFAULT 0, games_remaining INTEGER NOT NULL DEFAULT 0,
        created TEXT NOT NULL)''')
    c.execute('CREATE INDEX IF NOT EXISTS commerce_entitlements_owner ON commerce_entitlements(owner_key,created)')
    c.execute('''CREATE TABLE IF NOT EXISTS trial_claims(
        owner_key TEXT PRIMARY KEY, game_id BIGINT UNIQUE, claimed TEXT NOT NULL)''')


def owner_key(client_id):
    value = str(client_id or '').strip()
    if len(value) < 12 or len(value) > 160:
        raise CommerceError('device_identity_required', 400)
    salt = os.getenv('MIPO_OWNER_HASH_SECRET', os.getenv('PAYPLUS_SECRET_KEY', 'mipo-local-owner-key'))
    return hmac.new(salt.encode(), value.encode(), hashlib.sha256).hexdigest()


def price(product):
    try:
        return PRODUCTS[str(product)]
    except KeyError:
        raise CommerceError('invalid_product', 400)


def pricing_payload():
    active = enabled()
    return {
        'currency': 'USD', 'checkout_enabled': bool(active and checkout_configured()), 'commerce_enabled': active,
        'stage': 'launch' if active and checkout_configured() else 'configuration_required',
        'single_cents': 799, 'duo_cents': 1299, 'extension_cents': 299,
        'included_rounds': 18, 'free_rounds': 8, 'extended_rounds': 30,
        'max_players': 6, 'extension_applies_to': 'one_game',
    }


def quote(rounds=18, games=1):
    rounds, games = int(rounds), int(games)
    if games not in (1, 2) or rounds not in range(8, 31):
        raise ValueError('invalid_quote')
    base = 799 if games == 1 else 1299
    extension = 299 if rounds > 18 else 0
    return dict(pricing_payload(), games=games, rounds=rounds, base_cents=base,
                extra_cents=extension, total_cents=base + extension)


def claim_trial(c, key, game_id):
    try:
        c.execute('INSERT INTO trial_claims(owner_key,game_id,claimed) VALUES(?,?,?)', (key, game_id, utcnow()))
    except Exception as exc:
        # The unique owner key makes refresh, a direct URL and a new room unable
        # to silently create another trial for the same browser identity.
        raise CommerceError('trial_already_used', 409) from exc


def _paid_credit(c, key):
    row = c.execute('SELECT * FROM commerce_entitlements WHERE owner_key=? AND games_remaining>0 ORDER BY created,id LIMIT 1', (key,)).fetchone()
    if not row:
        raise CommerceError('payment_required', 402)
    changed = c.execute('UPDATE commerce_entitlements SET games_remaining=games_remaining-1 WHERE id=? AND games_remaining>0', (row['id'],))
    if getattr(changed, 'rowcount', 0) != 1:
        raise CommerceError('payment_required', 402)
    return row['id']


def allocate_new_game(c, client_id, requested_access, game_id):
    key = owner_key(client_id)
    if str(requested_access or '').lower() == 'trial':
        claim_trial(c, key, game_id)
        return {'owner_key': key, 'access_kind': 'trial', 'max_rounds': 8, 'entitlement_id': ''}
    try:
        entitlement_id = _paid_credit(c, key)
    except CommerceError as exc:
        # A first-time host who presses Play MIPO receives the public trial.
        # Once claimed, subsequent rooms require a verified paid entitlement.
        if exc.code != 'payment_required':
            raise
        claim_trial(c, key, game_id)
        return {'owner_key': key, 'access_kind': 'trial', 'max_rounds': 8, 'entitlement_id': ''}
    return {'owner_key': key, 'access_kind': 'paid', 'max_rounds': 18, 'entitlement_id': entitlement_id}


def allocate_replay(c, owner):
    return _paid_credit(c, str(owner or ''))


def available(c, client_id):
    try:
        key = owner_key(client_id)
    except CommerceError:
        return {'trial_available': False, 'paid_games': 0}
    trial = c.execute('SELECT 1 FROM trial_claims WHERE owner_key=?', (key,)).fetchone()
    paid = c.execute('SELECT COALESCE(SUM(games_remaining),0) AS n FROM commerce_entitlements WHERE owner_key=?', (key,)).fetchone()
    return {'trial_available': not bool(trial), 'paid_games': int(paid['n'] or 0)}


def _public_url(path):
    return os.environ['PUBLIC_BASE_URL'].rstrip('/') + path


def _provider_post(path, payload):
    base = os.getenv('PAYPLUS_API_BASE', '').strip() or (PAYPLUS_TEST if os.getenv('PAYPLUS_ENV', '').lower() in ('test', 'staging', 'sandbox') else PAYPLUS_PROD)
    body = json.dumps(payload, separators=(',', ':'), ensure_ascii=False).encode()
    request = urllib.request.Request(base.rstrip('/') + path, data=body, method='POST', headers={
        'Content-Type': 'application/json', 'Accept': 'application/json',
        'api-key': os.environ['PAYPLUS_API_KEY'], 'secret-key': os.environ['PAYPLUS_SECRET_KEY'],
    })
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            raw = response.read();headers = response.headers
    except urllib.error.HTTPError as exc:
        # PayPlus returns useful validation details for rejected requests. Log a
        # small, sanitized diagnostic (never credentials or the submitted body)
        # and expose only a stable category to the browser.
        provider_code = None
        description = ''
        try:
            provider_error = json.loads(exc.read())
            results = provider_error.get('results') or {}
            provider_code = results.get('code')
            description = str(results.get('description') or '')[:240]
        except Exception:
            pass
        print(json.dumps({
            'event': 'payplus_checkout_http_error',
            'http_status': exc.code,
            'provider_code': provider_code,
            'description': description,
        }, ensure_ascii=False), flush=True)
        if exc.code in (401, 403):
            code = 'checkout_provider_auth_or_api_access'
        elif exc.code == 422:
            code = 'checkout_provider_request_rejected'
        else:
            code = 'checkout_provider_http_error'
        raise CommerceError(code, 503) from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        print(json.dumps({
            'event': 'payplus_checkout_network_error',
            'error_type': type(exc).__name__,
        }), flush=True)
        raise CommerceError('checkout_provider_unavailable', 503) from exc
    supplied = str(headers.get('hash', ''))
    expected = base64.b64encode(hmac.new(os.environ['PAYPLUS_SECRET_KEY'].encode(), raw, hashlib.sha256).digest()).decode()
    if str(headers.get('user-agent', '')) != 'PayPlus' or not supplied or not hmac.compare_digest(supplied, expected):
        raise CommerceError('checkout_provider_unverified_response', 502)
    try:
        return json.loads(raw)
    except Exception as exc:
        raise CommerceError('checkout_provider_invalid_response', 502) from exc


def create_checkout(c, product, client_id, target_game=None):
    if not enabled() or not checkout_configured():
        raise CommerceError('checkout_not_configured', 503)
    item, key = price(product), owner_key(client_id)
    target_id = None
    if item['extension']:
        if not target_game or target_game['status'] not in ('lobby', 'playing') or target_game['access_kind'] != 'paid':
            raise CommerceError('extension_requires_paid_game', 409)
        if int(target_game['max_rounds'] or 18) >= 30:
            raise CommerceError('extension_already_active', 409)
        target_id = target_game['id']
    order_id, stamp = secrets.token_urlsafe(18), utcnow()
    c.execute('INSERT INTO commerce_orders(id,owner_key,product,amount_cents,currency,status,target_game_id,created,updated) VALUES(?,?,?,?,?,?,?,?,?)',
              (order_id, key, product, item['amount_cents'], 'USD', 'created', target_id, stamp, stamp))
    payload = {
        'payment_page_uid': os.environ['PAYPLUS_PAYMENT_PAGE_UID'], 'charge_method': 1,
        'amount': item['amount_cents'] / 100, 'currency_code': 'USD',
        'sendEmailApproval': True, 'sendEmailFailure': False, 'send_failure_callback': True,
        'refURL_success': _public_url('/checkout/success?order=' + order_id),
        'refURL_failure': _public_url('/checkout/failure?order=' + order_id),
        'refURL_cancel': _public_url('/checkout/cancel?order=' + order_id),
        'refURL_callback': _public_url('/api/payplus/callback'),
        'more_info': order_id, 'more_info_1': product,
        'items': [{'name': item['name'], 'quantity': 1, 'price': item['amount_cents'] / 100}],
    }
    if os.getenv('PAYPLUS_INITIAL_INVOICE', '').strip().lower() in ('1', 'true', 'yes', 'on'):
        payload['initial_invoice'] = True
    response = _provider_post('/PaymentPages/generateLink', payload)
    data = response.get('data') or {}
    link = data.get('payment_page_link') or data.get('url')
    request_uid = data.get('page_request_uid') or data.get('payment_request_uid')
    if not link or not request_uid:
        raise CommerceError('checkout_provider_invalid_response', 502)
    c.execute("UPDATE commerce_orders SET status='pending',provider_request_uid=?,checkout_url=?,updated=? WHERE id=?",
              (str(request_uid), str(link), utcnow(), order_id))
    return {'order_id': order_id, 'checkout_url': link, 'amount_cents': item['amount_cents'], 'currency': 'USD'}


def verified_callback(raw, headers):
    agent = str(headers.get('User-Agent', headers.get('user-agent', '')))
    supplied = str(headers.get('hash', headers.get('Hash', '')))
    if agent != 'PayPlus' or not supplied or not os.getenv('PAYPLUS_SECRET_KEY', ''):
        return False
    expected = base64.b64encode(hmac.new(os.environ['PAYPLUS_SECRET_KEY'].encode(), raw, hashlib.sha256).digest()).decode()
    return hmac.compare_digest(supplied, expected)


def _walk(payload, *keys):
    if not isinstance(payload, dict):
        return None
    for key in keys:
        if key in payload and payload[key] not in (None, ''):
            return payload[key]
    for value in payload.values():
        found = _walk(value, *keys)
        if found not in (None, ''):
            return found
    return None


def _callback_success(payload):
    # PayPlus callback schemas vary by payment-page configuration. Accept only
    # explicit success indicators; an ambiguous callback never unlocks access.
    status = str(_walk(payload, 'status', 'transaction_status', 'status_code') or '').strip().lower()
    code = str(_walk(payload, 'code', 'result_code') or '').strip().lower()
    approval = _walk(payload, 'approval_num', 'approval_number', 'transaction_uid')
    return bool(approval) and (status in ('success', 'approved', '000', '0') or code in ('0', '000'))


def process_callback(c, raw, headers):
    if not verified_callback(raw, headers):
        raise CommerceError('invalid_callback_signature', 403)
    try:
        payload = json.loads(raw)
    except Exception as exc:
        raise CommerceError('invalid_callback_payload', 400) from exc
    order_id = str(_walk(payload, 'more_info') or '')
    request_uid = str(_walk(payload, 'payment_request_uid', 'page_request_uid') or '')
    order = c.execute('SELECT * FROM commerce_orders WHERE id=? OR provider_request_uid=?', (order_id, request_uid)).fetchone()
    if not order:
        raise CommerceError('order_not_found', 404)
    if order['status'] in ('paid', 'refunded'):
        return {'ok': True, 'status': order['status'], 'order_id': order['id'], 'idempotent': True}
    success = _callback_success(payload)
    status = 'paid' if success else 'failed'
    transaction_uid = str(_walk(payload, 'transaction_uid') or '')
    if success:
        amount = _walk(payload, 'amount', 'transaction_amount', 'amount_total')
        currency = str(_walk(payload, 'currency_code', 'currency') or '').upper()
        try: callback_cents = int((Decimal(str(amount)) * 100).quantize(Decimal('1')))
        except (InvalidOperation, ValueError, TypeError): raise CommerceError('callback_amount_missing', 400)
        if callback_cents != int(order['amount_cents']) or currency != str(order['currency']).upper():
            raise CommerceError('callback_order_mismatch', 409)
    c.execute('UPDATE commerce_orders SET status=?,provider_transaction_uid=?,raw_callback=?,updated=? WHERE id=?',
              (status, transaction_uid, raw.decode('utf-8', 'replace')[:12000], utcnow(), order['id']))
    if not success:
        return {'ok': True, 'status': status, 'order_id': order['id']}
    item = price(order['product'])
    if item['extension']:
        c.execute("UPDATE games SET max_rounds=30,rounds=30 WHERE id=? AND access_kind='paid'", (order['target_game_id'],))
    else:
        entitlement_id = secrets.token_urlsafe(18)
        if not c.execute('SELECT 1 FROM commerce_entitlements WHERE order_id=?', (order['id'],)).fetchone():
            c.execute('INSERT INTO commerce_entitlements(id,order_id,owner_key,games_total,games_remaining,created) VALUES(?,?,?,?,?,?)',
                      (entitlement_id, order['id'], order['owner_key'], item['games'], item['games'], utcnow()))
    return {'ok': True, 'status': status, 'order_id': order['id']}


def order_status(c, order_id, client_id):
    key = owner_key(client_id)
    row = c.execute('SELECT id,product,amount_cents,currency,status,updated FROM commerce_orders WHERE id=? AND owner_key=?', (str(order_id), key)).fetchone()
    if not row:
        raise CommerceError('order_not_found', 404)
    return dict(row)


def refund(c, order_id, bearer, amount_cents=None):
    expected = os.getenv('MIPO_REFUND_ADMIN_TOKEN', '')
    if not expected or not bearer or not secrets.compare_digest(str(bearer), expected):
        raise CommerceError('forbidden', 403)
    order = c.execute('SELECT * FROM commerce_orders WHERE id=?', (str(order_id),)).fetchone()
    if not order or order['status'] not in ('paid', 'refunded') or not order['provider_transaction_uid']:
        raise CommerceError('order_not_refundable', 409)
    if order['status'] == 'refunded':
        return {'ok': True, 'status': 'refunded', 'order_id': order['id'], 'idempotent': True}
    cents = int(amount_cents or order['amount_cents'])
    if cents < 1 or cents > int(order['amount_cents']):
        raise CommerceError('invalid_refund_amount', 400)
    payload = {
        'transaction_uid': order['provider_transaction_uid'], 'amount': cents / 100,
        'more_info': 'MIPO refund ' + order['id'],
    }
    if os.getenv('PAYPLUS_INITIAL_INVOICE', '').strip().lower() in ('1', 'true', 'yes', 'on'):
        payload['initial_invoice'] = True
    result = _provider_post('/Transactions/RefundByTransactionUID', payload)
    data = result.get('data') or result
    if str(_walk(data, 'status', 'code', 'status_code') or '').lower() not in ('success', 'approved', '0', '000'):
        raise CommerceError('refund_provider_failed', 502)
    c.execute("UPDATE commerce_orders SET status='refunded',updated=? WHERE id=?", (utcnow(), order['id']))
    return {'ok': True, 'status': 'refunded', 'order_id': order['id'], 'amount_cents': cents}
