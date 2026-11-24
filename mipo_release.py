"""Free release switches shared by commerce, server and HTML bootstrap."""
import os
import re

def free_play():
    return os.getenv('MIPO_FREE_PLAY', '1').strip().lower() not in ('0', 'false', 'off', 'no')

def portal_name(name):
    # Portal usernames are display labels only, never account authentication.
    value = str(name or '').strip()[:40]
    blocked = ('fuck', 'shit', 'bitch', 'cunt', 'nigger', 'faggot', 'זונה', 'כוס', 'זין', 'שרמוט', 'كس', 'قحبة')
    letters = re.sub(r'[^\w]', '', value.casefold())
    return value if value and not any(word in letters for word in blocked) else 'Player'

def portal_card_ok(card):
    text = ' '.join([str(card[1]), *map(str, card[2])]).casefold()
    blocked = ('sex', 'drunk', 'alcohol', 'beer', 'wine', 'vodka', 'weed', 'cannabis', 'strip', 'naked', 'porn', 'dating app', 'grindr', 'tinder', 'סקס', 'מיניות', 'אלכוהול', 'שיכור', 'בירה', 'וודקה', 'קנאביס', 'סמים', 'עירום', 'פורנו', 'אינטימי', 'שתייה חריפה', 'גריינדר', 'טינדר', 'sexo', 'borracho', 'alcool', 'ivrogne', 'sexe', '酔', 'セックス', '酒')
    return card[0] in ('know', 'room') and not any(word in text for word in blocked)
