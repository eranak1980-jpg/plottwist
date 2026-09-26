import os,tempfile,importlib,sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
tmp=tempfile.TemporaryDirectory()
os.environ['DATABASE_PATH']=str(Path(tmp.name)/'qa.db')
import kyc_server as k
k.init()

def make_game(rounds=8,spice=1):
 with k.cn() as c:
  cur=c.execute("INSERT INTO games(code,host,status,round_no,topics,custom_context,spice,custom_questions,prize,rounds,created) VALUES(?,?,?,?,?,?,?,?,?,?,?)",('QA123','host','playing',0,'[]','',spice,'[]','QA Prize',rounds,k.now()))
  gid=cur.lastrowid
  for name in ['Eran','Shai','Avi']:
   c.execute("INSERT INTO players(game_id,name,token,joined) VALUES(?,?,?,?)",(gid,name,name.lower(),k.now()))
 return k.game('QA123')

g=make_game()
ps=k.players(g['id'])
assert k.total_rounds(g)==8
for rn in range(8):
 with k.cn() as c:c.execute("UPDATE games SET round_no=? WHERE id=?",(rn,g['id']))
 g=k.game('QA123')
 typ,text,opts,sub=k.qdata(g,ps)
 assert sub is not None and text and len(opts)>=2, (rn,typ,text,opts)

# Memory-based PlotTwist should stay playable and produce concrete options.
with k.cn() as c:
 c.execute("UPDATE games SET round_no=4,memory=? WHERE id=?",(json.dumps([
  {'round':0,'subject':'Eran','question':'עם מי Eran היה יוצא לחופשה?','answer':'Shai','type':'room'},
  {'round':1,'subject':'Shai','question':'מה Shai היה עושה בדייט?','answer':'זורם','type':'know'},
  {'round':2,'subject':'Avi','question':'מי Avi סומך עליו?','answer':'Eran','type':'room'}
 ]),g['id']))
g=k.game('QA123');typ,text,opts,sub=k.qdata(g,ps)
assert str(typ).startswith('callback') and len(opts)>=2
assert k.interactive_prompt(g,typ,text,opts[0],sub) is not None
print('QA_SMOKE_OK')

# Two-player / couples mode: every round must remain guessable.
with k.cn() as db:
 cur=db.execute("INSERT INTO games(code,host,status,round_no,topics,custom_context,spice,custom_questions,prize,rounds,created) VALUES(?,?,?,?,?,?,?,?,?,?,?)",('DUO12','host','playing',0,'[]','couple',1,'[]','',8,k.now()))
 gid=cur.lastrowid
 for name in ['Dana','Noa']:
  db.execute("INSERT INTO players(game_id,name,token,joined) VALUES(?,?,?,?)",(gid,name,name.lower(),k.now()))
duo=k.game('DUO12');dps=k.players(duo['id'])
for rn in range(8):
 with k.cn() as db:db.execute("UPDATE games SET round_no=? WHERE id=?",(rn,duo['id']))
 duo=k.game('DUO12');typ,text,opts,sub=k.qdata(duo,dps)
 assert sub is not None and text and len(opts)>=1, (rn,typ,text,opts)
print('QA_DUO_OK')

# Duo mode must never collapse into a one-option "who in the room" guess.
duo=k.game('DUO12');dps=k.players(duo['id'])
for rn in range(8):
 with k.cn() as db:db.execute("UPDATE games SET round_no=? WHERE id=?",(rn,duo['id']))
 duo=k.game('DUO12');typ,text,opts,sub=k.qdata(duo,dps)
 assert typ!='room', (rn,typ,text,opts)
 assert len(opts)>=3, (rn,typ,text,opts)
print('QA_DUO_MECHANIC_OK')

# Collaborative topic votes are included in the effective topic set.
with k.cn() as db:
 db.execute("INSERT INTO topic_votes(game_id,player_id,topic) VALUES(?,?,?)",(duo['id'],dps[1]['id'],'נסיעות'))
duo=k.game('DUO12')
assert 'נסיעות' in k.effective_topics(duo)
print('QA_TOPIC_VOTES_OK')

# A played prompt must not repeat verbatim on the next generated round.
g=k.game('QA123');ps=k.players(g['id'])
typ,text,opts,sub=k.qdata(g,ps)
with k.cn() as db:
 db.execute("UPDATE games SET memory=? WHERE id=?",(json.dumps([{'round':0,'subject':sub['name'],'question':text,'answer':opts[0],'type':typ}],ensure_ascii=False),g['id']))
g=k.game('QA123');typ2,text2,opts2,sub2=k.qdata(g,ps)
assert text2!=text,(text,text2)
print('QA_NO_REPEAT_OK')

# Duo callback prompts themselves must not repeat a previously played callback.
duo=k.game('DUO12');dps=k.players(duo['id'])
with k.cn() as db:
 db.execute("UPDATE games SET round_no=?,memory=? WHERE id=?",(4,json.dumps([
  {'round':0,'subject':dps[0]['name'],'question':'Q0','answer':'טיסה וחופשה מטורפת','type':'know'},
  {'round':1,'subject':dps[1]['name'],'question':'Q1','answer':'שבוע של בית ומנוחה','type':'know'},
  {'round':2,'subject':dps[0]['name'],'question':'Q2','answer':'אי טרופי','type':'know'}
 ],ensure_ascii=False),duo['id']))
duo=k.game('DUO12');cb=k.duo_callback(duo,dps,4)
if cb:
 first=cb[1]
 mm=k.mem(duo)+[{'round':4,'subject':cb[3]['name'],'question':first,'answer':cb[2][0],'type':'duo_callback'}]
 with k.cn() as db:db.execute("UPDATE games SET round_no=?,memory=? WHERE id=?",(6,json.dumps(mm,ensure_ascii=False),duo['id']))
 duo=k.game('DUO12');cb2=k.duo_callback(duo,dps,6)
 assert not cb2 or cb2[1]!=first,(first,cb2)
print('QA_DUO_CALLBACK_NO_REPEAT_OK')

# Scoring must be idempotent and survive a state/reveal race.
with k.cn() as db:
 db.execute("UPDATE games SET round_no=0,answer='טיסה וחופשה מטורפת',memory='[]' WHERE id=?",(duo['id'],))
 db.execute("DELETE FROM guesses WHERE game_id=?",(duo['id'],))
 db.execute("DELETE FROM round_scores WHERE game_id=?",(duo['id'],))
 db.execute("UPDATE players SET score=0 WHERE game_id=?",(duo['id'],))
 # Round 0 subject is Dana, Noa predicts correctly.
 db.execute("INSERT INTO guesses(game_id,round_no,player_id,guess) VALUES(?,?,?,?)",(duo['id'],0,dps[1]['id'],'טיסה וחופשה מטורפת'))
duo=k.game('DUO12');dps=k.players(duo['id'])
changed=k.ensure_round_score(duo,dps,{dps[1]['id']:'טיסה וחופשה מטורפת'})
assert changed
after=k.players(duo['id'])
assert next(p for p in after if p['id']==dps[1]['id'])['score']==1
assert not k.ensure_round_score(duo,after,{dps[1]['id']:'טיסה וחופשה מטורפת'})
assert next(p for p in k.players(duo['id']) if p['id']==dps[1]['id'])['score']==1
print('QA_SCORING_OK')


# Canonical question keys must treat the same prompt for different crew members as a repeat.
ps=k.players(g['id'])
q1=k.question_key('מה Eran היה עושה אם הטיסה בוטלה?',ps)
q2=k.question_key('מה Shai היה עושה אם הטיסה בוטלה?',ps)
assert q1==q2,(q1,q2)
print('QA_CANONICAL_REPEAT_KEY_OK')

# Same-crew history persists across games and blocks previously used prompt keys.
k.remember_question(ps,'מה Eran היה עושה אם הטיסה בוטלה?')
assert q1 in k.past_question_keys(ps)
print('QA_CREW_HISTORY_OK')

# A dropped non-subject player must stop blocking round readiness without being removed mid-round.
with k.cn() as db:
 db.execute("UPDATE games SET round_no=0,answer=? WHERE id=?",('טיסה וחופשה מטורפת',g['id']))
 db.execute("DELETE FROM guesses WHERE game_id=?",(g['id'],))
 db.execute("DELETE FROM round_scores WHERE game_id=?",(g['id'],))
 db.execute("UPDATE players SET active=1 WHERE game_id=?",(g['id'],))
ps=k.players(g['id']);sub=ps[0];guessers=[p for p in ps if p['id']!=sub['id']]
with k.cn() as db:
 db.execute("UPDATE players SET active=0 WHERE id=?",(guessers[-1]['id'],))
 db.execute("INSERT INTO guesses(game_id,round_no,player_id,guess) VALUES(?,?,?,?)",(g['id'],0,guessers[0]['id'],'טיסה וחופשה מטורפת'))
g2=k.game('QA123');ps2=k.players(g2['id'])
assert len(k.live_players(g2['id']))==2
assert k.ensure_round_score(g2,ps2,{guessers[0]['id']:'טיסה וחופשה מטורפת'})
print('QA_DROPPED_PLAYER_DOES_NOT_BLOCK_OK')

# Newly added themed categories are real server topics.
for topic in ['מה היית עושה אם…','דילמות','מביך אבל מצחיק','מי הכי…','סודות והרגלים','טיולים וחופשות','חלומות ופנטזיות','כסף מטורף']:
 assert topic in k.TOPICS and len(k.TOPICS[topic])>=6, topic
print('QA_NEW_TOPIC_PACKS_OK')


# Match Twist comparison: normalized equal answers should match; different destinations should not.
assert k.match_equal(' Tokyo ', 'tokyo')
assert k.match_equal('תאילנד!', 'תאילנד')
assert not k.match_equal('טוקיו', 'פריז')
print('QA_MATCH_TWIST_COMPARE_OK')


# Repeat guard should catch a lightly reworded version of the same scenario.
assert k.too_similar(
 'מקבל 100000 שקל שחייבים לבזבז בתוך 24 שעות לאן הכסף הולך',
 {'מקבל 100000 שקל וצריך לבזבז הכל ב 24 שעות מה קונים קודם'}
)
print('QA_SEMANTICISH_REPEAT_GUARD_OK')

# Duo callbacks now support the open-answer Match Twist too.
with k.cn() as db:
 db.execute("UPDATE games SET round_no=?,memory=? WHERE id=?",(4,json.dumps([
  {'round':0,'subject':'Dana','question':'Q0','answer':'טיסה','type':'know'},
  {'round':1,'subject':'Noa','question':'Q1','answer':'בית','type':'know'},
  {'round':2,'subject':'Dana','question':'Q2','answer':'ספונטני','type':'know'}
 ],ensure_ascii=False),duo['id']))
duo=k.game('DUO12');dps=k.players(duo['id']);cb=k.duo_callback(duo,dps,4)
if cb:
 md=k.interactive_match_data(duo,cb[0],cb[1],cb[3])
 assert md and len(md['player_ids'])==2
print('QA_DUO_MATCH_TWIST_OK')

# Core topic packs have enough curated variety even if AI generation is unavailable.
for topic in ['משפחה','דייטים','זוגיות','חיי לילה','נסיעות','כסף','קריירה ועסקים','נוסטלגיה','אוכל','מוזיקה','טכנולוגיה','תרבות ופופ']:
 assert len(k.TOPICS.get(topic,[]))>=3,(topic,len(k.TOPICS.get(topic,[])))
print('QA_CURATED_VARIETY_OK')


# Topic-led modes need enough curated depth to avoid cycling after a few questions.
for topic in ['מה היית עושה אם…','דילמות','מי הכי…','נוסטלגיה','סודות והרגלים','מביך אבל מצחיק']:
 assert len(k.TOPICS.get(topic,[]))>=10,(topic,len(k.TOPICS.get(topic,[])))
print('QA_SUBGAME_DEPTH_OK')

# new=1 must clear stale room state before the browser reads it, preventing an old-room flash.
html=(Path(__file__).resolve().parents[1]/'static'/'kyc.html').read_text()
reset=html.index("if(bootParams.get('new')==='1')")
read=html.index("JSON.parse(localStorage.getItem('kyc')")
assert reset<read,(reset,read)
print('QA_NEW_GAME_BOOT_RESET_OK')

# Polling must be change-aware rather than re-rendering the DOM on every interval.
assert "if(sig!==stateSig){stateSig=sig;render(d)}" in html
assert "if(!document.hidden)load()" in html
print('QA_POLL_RENDER_GUARD_OK')

# Poll state must never contain raw AI/image base64 payloads.
server=(Path(__file__).resolve().parents[1]/'kyc_server.py').read_text()
state_block=server[server.index("if p.startswith('/api/state/')"):server.index("def do_POST")]
assert "'hero':image_url(g," in state_block
assert "'photo_url':('/api/photo/" in state_block
assert "'image_data':" not in state_block
print('QA_STATE_PAYLOAD_REFERENCES_ONLY_OK')


# Six launch languages: English default + Spanish, Brazilian Portuguese, French, Japanese, Hebrew.
from kyc_locales import SUPPORTED_LANGUAGES,normalize_language,direction,topic_labels,general_pack
assert list(SUPPORTED_LANGUAGES)==['en','es','pt-BR','fr','ja','he'],SUPPORTED_LANGUAGES
assert normalize_language('ar')=='en'
assert normalize_language('ja-JP')=='ja'
assert direction('he')=='rtl' and direction('ja')=='ltr' and direction('en')=='ltr'
assert topic_labels(['משפחה','דייטים'],'ja')==['家族','デート']
for lang in ['en','es','pt-BR','fr','ja']:
 assert len(general_pack(lang))>=20,(lang,len(general_pack(lang)))
print('QA_MULTILANG_CORE_OK')

# Japanese rooms use native Japanese fallback questions and keep Duo mechanics valid.
with k.cn() as db:
 cur=db.execute("INSERT INTO games(code,host,status,round_no,topics,custom_context,spice,custom_questions,prize,rounds,adults_confirmed,language,created) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",('JA123','host','playing',0,'[]','',1,'[]','',8,0,'ja',k.now()))
 jgid=cur.lastrowid
 for name in ['Aki','Yuki']:
  db.execute("INSERT INTO players(game_id,name,token,joined) VALUES(?,?,?,?)",(jgid,name,name.lower(),k.now()))
jg=k.game('JA123');jps=k.players(jg['id'])
typ,jtext,jopts,jsub=k.qdata(jg,jps)
assert typ!='room' and len(jopts)>=3
assert any(('ぁ'<=ch<='ん') or ('ァ'<=ch<='ン') or ('一'<=ch<='龯') for ch in jtext),jtext
print('QA_JAPANESE_GAMEPLAY_OK')

# Browser selector exposes exactly the intended public launch set (no Arabic).
html=(Path(__file__).resolve().parents[1]/'static'/'kyc.html').read_text()
for code in ['en','es','pt-BR','fr','ja','he']:
 assert f'<option value="{code}">' in html,code
assert '<option value="ar">' not in html
assert "language:uiLang" in html
assert "d.language&&d.language!==uiLang" in html
print('QA_LANGUAGE_SELECTOR_OK')


# Launch localization must never fall back to Hebrew for non-Hebrew UI states.
from kyc_locales import ui_copy,last_resort
import re
hebrew_re=re.compile(r'[\u0590-\u05FF]')
required_polish=[
 'all_topics_selected','max_topics','adult_topic_requires','save_failed','game_updated',
 'choose_image','photo_saved','name_required','joining','game_started','join_failed',
 'score_tied','leader_one','leader_now','photo_count','photo_ready','winner_prize',
 'ai_reveal_ready','ai_reveal_generating','ai_image_missing','interactive_live',
 'match_yes','match_no','save_secret','match_saved','match_waiting','no_previous',
 'back_game','previous_view','answered','previous_note','choice_received','saving_update',
 'back_lobby_ok','replay_loading','replay_new_questions','need_two','starting',
 'game_ready','skipped_no_score','wait_all_guesses','photo_button','custom_prompt',
 'guess_board','lobby_game','edit_game','save_changes','final_hero_generating',
 'language_locked','left_game'
]
for lang in ['en','es','pt-BR','fr','ja']:
 c=ui_copy(lang)
 for key in required_polish:
  assert key in c and c[key],(lang,key)
  assert not hebrew_re.search(c[key]),(lang,key,c[key])
 text,opts=last_resort(lang,'Alex')
 assert text and len(opts)==4
 assert not hebrew_re.search(text),(lang,text)
print('QA_LOCALIZATION_POLISH_OK')

# English default markup must not flash Hebrew in core UI before locale metadata loads.
html=(Path(__file__).resolve().parents[1]/'static'/'kyc.html').read_text()
pre=html.split('<script>',1)[0]
core=pre.replace('🇮🇱 עברית','').split('<div class="inspire hidden">',1)[0]
assert not hebrew_re.search(core),hebrew_re.search(core).group(0) if hebrew_re.search(core) else ''
assert 'value="ar"' not in html
print('QA_ENGLISH_BOOT_NO_HEBREW_FLASH_OK')

