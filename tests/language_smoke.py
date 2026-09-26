import json, os, re, sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
tmp=tempfile.TemporaryDirectory()
os.environ['DATABASE_PATH']=str(Path(tmp.name)/'lang-qa.db')
os.environ.pop('DATABASE_URL',None)
os.environ.pop('OPENAI_API_KEY',None)

import kyc_server as k
from kyc_locales import SUPPORTED_LANGUAGES, OTHER_LABELS, localized_general, last_resort_question

k.init()
HE=re.compile(r'[\u0590-\u05ff]')
JP=re.compile(r'[\u3040-\u30ff\u3400-\u9fff]')

def insert_game(code,lang,names=('A','B','C')):
 with k.cn() as db:
  cur=db.execute("INSERT INTO games(code,host,status,round_no,topics,custom_context,spice,custom_questions,prize,rounds,language,created) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
   (code,'host','playing',0,'[]','',1,'[]','',8,lang,k.now()))
  gid=cur.lastrowid
  for i,name in enumerate(names):
   db.execute("INSERT INTO players(game_id,name,token,joined,active,last_seen,client_id) VALUES(?,?,?,?,1,?,?)",(gid,name,code+str(i),k.now(),k.now(),code+'dev'+str(i)))
 return k.game(code)

assert list(SUPPORTED_LANGUAGES)==['en','es','pt-BR','fr','ja','he']
assert set(OTHER_LABELS)==set(SUPPORTED_LANGUAGES)
print('LANG_SUPPORTED_SET_OK')

# New public rooms default to English through the API contract; internal legacy rows
# without an explicit language remain Hebrew for backwards compatibility.
with k.cn() as db:
 cur=db.execute("INSERT INTO games(code,host,created) VALUES(?,?,?)",('LEGHE','h',k.now()))
legacy=k.game('LEGHE')
assert k.language_code(legacy)=='he'
print('LANG_LEGACY_HEBREW_OK')

for i,lang in enumerate(['en','es','pt-BR','fr','ja']):
 g=insert_game('L'+str(i)+'XYZ',lang)
 ps=k.players(g['id'])
 typ,text,opts,sub=k.qdata(g,ps)
 assert text and opts and sub
 assert not HE.search(text),(lang,text)
 assert all(not HE.search(str(x)) for x in opts),(lang,opts)
 if lang=='ja':
  assert JP.search(text) or any(JP.search(str(x)) for x in opts),(lang,text,opts)
 fallback,fbopts=last_resort_question(g,sub['name'])
 assert not HE.search(fallback),(lang,fallback)
 assert all(not HE.search(str(x)) for x in fbopts),(lang,fbopts)
print('LANG_NON_HEBREW_POOLS_OK')

he=insert_game('HE123','he')
ht,ho,hs=k.qdata(he,k.players(he['id']))[:3]
assert HE.search(ho) or any(HE.search(str(x)) for x in hs),(ho,hs)
print('LANG_HEBREW_POOL_OK')

# Enough local questions exist to keep the game usable with no AI key.
for lang in ['en','es','pt-BR','fr','ja']:
 g=insert_game(('Q'+lang.replace('-',''))[:5].upper().ljust(5,'X'),lang)
 assert len(localized_general(g))>=30,(lang,len(localized_general(g)))
print('LANG_OFFLINE_DEPTH_OK')

# Client layer: English is UI default, all six options are present, Hebrew alone is RTL,
# and canonical topic ids remain separate from translated display labels.
root=Path(__file__).resolve().parents[1]
html=(root/'static'/'kyc.html').read_text()
i18n=(root/'static'/'kyc_i18n.js').read_text()
assert "localStorage.getItem('plot_ui_language')||'en'" in i18n
for lang in ['en','es','pt-BR','fr','ja','he']:
 assert "['"+lang+"'," in i18n or "'"+lang+"':" in i18n,lang
assert "document.documentElement.dir=l==='he'?'rtl':'ltr'" in i18n
assert 'id="languageSelect"' in html
assert "dataset.topic=t" in html
assert "language:uiLang" in html
assert "d.language&&d.language!==uiLang" in html
print('LANG_CLIENT_WIRING_OK')

# Question generation prompt explicitly receives and requests the room language.
ai=(root/'kyc_ai.py').read_text()
assert "def generate_pack(topics,context,spice,language='en')" in ai
assert "naturally in {lang_name}" in ai
print('LANG_AI_QUESTION_PROMPT_OK')

print('LANGUAGE_SMOKE_OK')
tmp.cleanup()
