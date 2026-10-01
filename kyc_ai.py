import kyc_budget as budget
import json,os,re,unicodedata
from difflib import SequenceMatcher
from kyc_locales import normalize_language,topic_labels

def _normalize(value):
 """A stable comparison form for short multilingual game copy."""
 value=unicodedata.normalize('NFKD',str(value or '').casefold()).replace('{s}',' ')
 value=''.join(ch for ch in value if not unicodedata.combining(ch))
 return re.sub(r'[^\w\u0590-\u05ff\u3040-\u30ff\u3400-\u9fff]+',' ',value,flags=re.UNICODE).strip()

_DODGE_PHRASES={
 'en':('it depends','depends','both','either','neither','none','all of them','all of the above','something else','other answer','other option','skip','not sure','whatever','any of them','third option','refuses to choose','finds a loophole','stays home'),
 'es':('depende','ambos','los dos','las dos','cualquiera','ninguno','ninguna','otra cosa','otra respuesta','otra opcion','saltar','no se','se niega a elegir','busca una tercera opcion','se queda en casa'),
 'pt-BR':('depende','ambos','os dois','as duas','qualquer um','nenhum','nenhuma','outra coisa','outra resposta','outra opcao','pular','nao sei','se recusa a escolher','procura uma terceira opcao','fica em casa'),
 'fr':('ca depend','cela depend','les deux','n importe lequel','aucun','aucune','autre chose','autre reponse','autre option','passer','je ne sais pas','refuse de choisir','troisieme option','reste chez soi'),
 'ja':('場合による','どちらも','両方','どれでも','どちらでも','どっちも','わからない','分からない','スキップ','その他','別の答え','選ばない','家にいる'),
 'he':('תלוי','שניהם','שתיהן','שניהם טובים','הכול','הכל','אף אחד','אף אחת','שום דבר','משהו אחר','אפשרות אחרת','תשובה אחרת','לא יודע','לא יודעת','מדלג','מדלגת','מסרב לבחור','מסרבת לבחור','מחפש פרצה','מחפשת פרצה','אופציה שלישית','נשאר בבית','נשארת בבית')
}

_VAGUE_QUESTION_PATTERNS={
 'en':(r'\bwhat (?:is|matters) most (?:to|for)\b',r'\bwhat does .+ value most\b',r'\bwhich word (?:best )?describes\b',r'\bwhat fits .+ best\b',r'\bthings get complicated\b',r'\bthis choice\b'),
 'es':(r'\bque es lo mas importante para\b',r'\bque valora mas\b',r'\bque palabra describe\b',r'\bque le pega mas\b',r'\blas cosas se complican\b',r'\besta eleccion\b'),
 'pt-BR':(r'\bo que e mais importante para\b',r'\bo que .+ mais valoriza\b',r'\bqual palavra descreve\b',r'\bo que mais combina com\b',r'\bas coisas ficam complicadas\b',r'\bessa escolha\b'),
 'fr':(r'\bqu est ce qui compte le plus pour\b',r'\bque valorise .+ le plus\b',r'\bquel mot decrit\b',r'\bqu est ce qui correspond le mieux\b',r'\bles choses se compliquent\b',r'\bce choix\b'),
 'ja':(r'一番大切なのは',r'最も大事なのは',r'どんな言葉で表す',r'一番合うのは',r'事態が複雑',r'この選択'),
 'he':(r'\bמה הכי חשוב ל',r'\bמה .+ הכי מעריכ',r'\bאיזו מילה .+ מתאר',r'\bמה הכי מתאים ל',r'\bהדברים מסתבכים\b',r'\bהבחירה הזאת\b',r'\bאמיתי\b')
}

# A party question may be heightened, but it still has to feel like something
# players can picture happening to them.  These patterns cover the recurring
# "random sketch" setups that tested poorly in live play.
_CONTRIVED_QUESTION_PATTERNS={
 'en':(r'robot .{0,35}(?:every|literal)',r'(?:million|50,?000).{0,45}(?:midnight|24 hours)',r'(?:movie|film).{0,35}(?:shout|yell).{0,30}(?:cucumber|pickle)',r'identical .{0,20}(?:shirt|outfit).{0,35}(?:change|replace)'),
 'es':(r'robot .{0,35}(?:cada|literal)',r'(?:millon|50,?000).{0,45}(?:medianoche|24 horas)',r'(?:pelicula|cine).{0,35}(?:gritar).{0,30}(?:pepino)',r'identic.{0,20}(?:camisa|ropa).{0,35}(?:cambiar)'),
 'pt-BR':(r'robo .{0,35}(?:toda|literal)',r'(?:milhao|50,?000).{0,45}(?:meia noite|24 horas)',r'(?:filme|cinema).{0,35}(?:gritar).{0,30}(?:pepino)',r'identic.{0,20}(?:camisa|roupa).{0,35}(?:trocar)'),
 'fr':(r'robot .{0,35}(?:chaque|litteral)',r'(?:million|50,?000).{0,45}(?:minuit|24 heures)',r'(?:film|cinema).{0,35}(?:crier).{0,30}(?:concombre)',r'identique.{0,20}(?:chemise|tenue).{0,35}(?:changer)'),
 'ja':(r'ロボット.{0,25}(?:命令|文字通り)',r'(?:100万|50,?000).{0,30}(?:深夜|24時間)',r'(?:映画|撮影).{0,25}(?:叫).{0,20}(?:きゅうり)',r'同じ.{0,12}(?:服|シャツ).{0,25}(?:着替|変え)'),
 'he':(r'רובוט .{0,35}(?:כל בקשה|מילולי)',r'(?:מיליון|50,?000|50 אלף).{0,45}(?:חצות|24 שעות)',r'(?:סרט|צילומים).{0,35}(?:לצעוק|צועק).{0,30}(?:מלפפון)',r'(?:חולצה|בגד).{0,20}(?:זהה|אותו דבר).{0,35}(?:להחליף|תחליף)')
}

# These tags describe whole scenarios, not isolated keywords.  They catch the
# common failure mode where the model rewrites the same setup with new wording.
_SCENARIOS={
 'wrong_message':r'wrong (?:chat|group|person)|sent .{0,35} by mistake|voice note|קבוצה הלא נכונה|צ.?אט הלא נכון|הודעה .{0,25} בטעות|grupo equivocado|chat equivocado|mensaje .{0,25} error|grupo errado|chat errado|mensagem .{0,25} engano|mauvais (?:groupe|chat|destinataire)|message .{0,25} erreur|間違.{0,12}(?:送|チャット|グループ)',
 'flight_problem':r'flight|airport|plane ticket|luggage|טיס|שדה תעופה|מזווד|מטוס|vuelo|aeropuerto|maleta|voo|aeroporto|bagagem|\bvol\b|aeroport|bagage|飛行機|空港|フライト|航空券|荷物',
 'hotel_problem':r'hotel|booking|reservation|מלון|הזמנה לחדר|reserva de hotel|reserva do hotel|h[oô]tel|ホテル|宿泊',
 'social_post':r'story|social media|instagram|tiktok|סטורי|רשתות חברתיות|אינסטגרם|redes sociales|r[eé]seaux sociaux|ストーリー|インスタ|SNS',
 'karaoke':r'karaoke|קריוקי|カラオケ',
 'screen_share':r'screen shar|search history|שיתוף מסך|היסטוריית חיפוש|compartir pantalla|historial de busqueda|compartilhar a tela|historico de pesquisa|partage d.?ecran|historique de recherche|画面共有|検索履歴',
 'card_declined':r'card (?:is |gets )?declined|כרטיס .{0,12}נדחה|tarjeta .{0,12}rechaz|cartao .{0,12}recus|carte .{0,12}refus|カード.{0,8}(?:拒否|使え)',
 'wrong_meeting':r'wrong meeting|first day .{0,20}work|ישיבה הלא נכונה|יום הראשון בעבודה|reunion equivocada|reuniao errada|mauvaise reunion|間違.{0,8}会議',
 'phone_dead':r'(?:phone|battery).{0,30}(?:one percent|1%)|אחוז אחד|סוללה .{0,12}נגמר|bateria.{0,15}(?:1%|uno por ciento|um por cento)|batterie.{0,15}(?:1%|un pour cent)|バッテリー.{0,8}(?:1%|切れ)',
 'restaurant_problem':r'restaurant|waiter|menu|dish|מסעדה|מלצר|מנה|restaurante|camarero|garcom|serveur|レストラン|店員|料理',
 'locked_out':r'locked out|ננעל.{0,12}מחוץ|fuera de casa sin llaves|trancad.{0,12}fora|porte claquee|締め出',
 'hot_mic':r'mic(?:rophone)?.{0,25}(?:on|open)|מיקרופון .{0,25}(?:פתוח|נשאר)|microfono .{0,20}abierto|microfone .{0,20}aberto|micro .{0,20}ouvert|マイク.{0,12}(?:オン|切り忘れ)'
}

def _contains_phrase(text,phrase):
 phrase=_normalize(phrase)
 if re.search(r'[\u3040-\u30ff\u3400-\u9fff]',phrase):return phrase in text
 return re.search(r'(?<!\w)'+re.escape(phrase)+r'(?!\w)',text,re.UNICODE) is not None

def _dodging_option(option,language):
 normalized=_normalize(option)
 return any(_contains_phrase(normalized,phrase) for phrase in _DODGE_PHRASES.get(language,_DODGE_PHRASES['en']))

def _vague_question(text,language):
 normalized=_normalize(text)
 return any(re.search(pattern,normalized,re.I|re.UNICODE) for pattern in _VAGUE_QUESTION_PATTERNS.get(language,_VAGUE_QUESTION_PATTERNS['en']))

def _contrived_question(text,language):
 normalized=_normalize(text)
 return any(re.search(pattern,normalized,re.I|re.UNICODE) for pattern in _CONTRIVED_QUESTION_PATTERNS.get(language,_CONTRIVED_QUESTION_PATTERNS['en']))

def _scenario_fingerprint(text):
 normalized=_normalize(text)
 return frozenset(tag for tag,pattern in _SCENARIOS.items() if re.search(pattern,normalized,re.I|re.UNICODE))

def _content_tokens(text):
 stop={'the','a','an','to','of','and','or','what','does','do','is','are','with','for','in','on','at','how','then','מה','איך','של','עם','את','או','על','אם','אז','הוא','היא','que','como','con','para','une','un','le','la','les','des','de','et','ou','com','como','uma','um','e','o','a'}
 return {token for token in _normalize(text).split() if len(token)>2 and token not in stop}

def _semantic_duplicate(text,previous):
 normalized=_normalize(text)
 tags=_scenario_fingerprint(text)
 tokens=_content_tokens(text)
 for old in previous:
  old_normalized=_normalize(old)
  if normalized==old_normalized:return True
  old_tags=_scenario_fingerprint(old)
  if tags and old_tags and tags.intersection(old_tags):return True
  old_tokens=_content_tokens(old)
  union=tokens|old_tokens
  if union and len(tokens&old_tokens)/len(union)>=0.58:return True
  if len(normalized)>24 and len(old_normalized)>24 and SequenceMatcher(None,normalized,old_normalized).ratio()>=0.84:return True
 return False

def _distinct_options(options):
 normalized=[_normalize(option) for option in options]
 for index,left in enumerate(normalized):
  left_tokens=set(left.split())
  for right in normalized[index+1:]:
   if left==right:return False
   right_tokens=set(right.split());union=left_tokens|right_tokens
   if union and len(left_tokens&right_tokens)/len(union)>=0.72:return False
   if min(len(left),len(right))>=8 and SequenceMatcher(None,left,right).ratio()>=0.9:return False
 return True

def clean_pack(data,language='en'):
 """Reject broken/overlong choices instead of cutting off their meaning."""
 language=normalize_language(language)
 if not isinstance(data,list):return []
 out=[];seen_text=[]
 for q in data:
  if not isinstance(q,dict):continue
  typ=q.get('type');text=q.get('text');opts=q.get('options',[])
  if typ not in ('know','room') or not isinstance(text,str):continue
  text=text.strip()
  if '{s}' not in text or _semantic_duplicate(text,seen_text) or _vague_question(text,language) or _contrived_question(text,language) or len(text)>(160 if language=='ja' else 280):continue
  if language!='ja' and (len(text.split())<7 or len(text.split())>35):continue
  if not isinstance(opts,list):continue
  if typ=='know':
   if len(opts)!=4 or any(not isinstance(o,str) or not o.strip() for o in opts):continue
   opts=[o.strip() for o in opts]
   if any(len(o)>70 or (language!='ja' and len(o.split())>10) for o in opts):continue
   if not _distinct_options(opts) or any(_dodging_option(o,language) for o in opts):continue
  else:opts=[]
  seen_text.append(text);out.append((typ,text,opts))
 return out[:12] if len(out)>=6 else []

def generate_pack(topics,context,spice,language='en'):
 language=normalize_language(language)
 key=os.getenv('OPENAI_API_KEY','').strip()
 if not key:return []
 level={1:'Chill: playful and broadly comfortable',2:'Bold: personal, cheeky and revealing but not sexual unless the selected topics call for it',3:'No Filter: adults-only, bold, cheeky and genuinely spicy. Questions may involve dating apps, attraction, sexual chemistry, flirting, hookups, types, turn-ons/turn-offs and sex-life preferences, while staying non-graphic and never pressuring anyone to disclose a specific private sexual event'}[int(spice)]
 names={'en':'English','es':'Spanish','pt-BR':'Brazilian Portuguese','fr':'French','ja':'Japanese','he':'Hebrew'}
 natural={'en':'natural contemporary English used by friends at a party','es':'natural contemporary Spanish that sounds native and social, not translated','pt-BR':'natural contemporary Brazilian Portuguese, casual and social, not European Portuguese','fr':'natural contemporary French used by friends, not literal translation','ja':'natural contemporary Japanese used by friends at a casual party, lively and idiomatic, not a literal translation','he':'natural contemporary Hebrew used by friends at a party'}
 display_topics=topic_labels(topics,language)
 prompt=f"""You design premium social party-game questions for PlotTwist: Know Your Crew.
Write DIRECTLY in {names[language]}. Do not translate from Hebrew or English. Think and write natively in {natural[language]}.
All player-facing question text and answer options must be in {names[language]}. Player names stay unchanged.
All players are adults when spice=3.
Selected topics: {', '.join(display_topics) if display_topics else 'mixed'}
Host description of the group: {context or 'none'}
Spice level: {level}

Create exactly 12 excellent questions tailored to THIS group. This gives the game a small reserve when a question is filtered or was already played, without padding the pack with weaker variations. At least 10 must be "know" questions and at most 2 may be "room" questions. The game loop: one spotlight player answers secretly; everyone else predicts their answer.
Return ONLY a JSON array. Each item must be either:
{{"type":"know","text":"question in the requested language containing {{s}} for spotlight player","options":["4 short mutually distinct answers in the requested language"]}}
or
{{"type":"room","text":"question in the requested language containing {{s}}","options":[]}}
For room questions the answer will be one of the other players.

Editorial standard:
- REAL-LIFE FIRST: at least 9 of the 12 questions must be recognizable everyday moments that could plausibly happen this week: group chats, arriving late, ordering food, splitting a bill, family WhatsApp, getting ready, hosting, dating apps, work messages, travel planning, lending things, shopping, chores, calls, photos or ordinary nights out. Players should instantly think "that is so them".
- Use no more than 2 heightened hypotheticals in the whole pack. Never build random sketch-comedy worlds just to sound creative: no magical or overly literal robots, bizarre movie lines, forced costume coincidences, sudden viral fame, celebrity encounters, or fortunes that must be spent by midnight. Funny comes from a believable human reaction, not an absurd setup.
- Prefer observed habits and small social frictions over fantasy stakes. A good question exposes what the person actually tends to do: ignore a message, arrive late, avoid a bill, overpack, call a friend, change plans, order the same meal, or pretend everything is fine.
- A player must understand the question on the FIRST read. Use one concrete situation and one direct question. Aim for 12–24 words; never exceed two sentences or 35 words (140 characters in Japanese). Name what went wrong; never say only "things get complicated". Avoid stacked conditions, metaphors, wordplay and vague references like "this choice".
- Every answer must directly answer that exact question in at most 8 words (35 characters in Japanese). Four distinct actions, not overlapping categories. Never use a request for "something else", another answer, a skip, or a joke about the questionnaire as an answer option. If asking what someone would NOT do, ensure all options and the question use that meaning consistently.
- Before returning, silently read each question with EACH answer. Rewrite unclear setups and answers that need explanation. Remove rhetorical fluff such as "the photo will forgive". Replace generic chemistry/value checklists with a specific awkward date or funny decision.
- Bold level means sharper COMEDY, not just more personal questions. Give each setup a specific comic problem and four funny, believable reactions. Avoid filler choices like "both", "depends", "balance" or "stay home" that dodge the dilemma.
- Reject moral no-brainers (a wonderful real evening versus a fake social-media evening), generic values comparisons and abstract tradeoffs. Each option should have its own tempting upside and comic cost.
- For Hebrew: write like friends joking out loud. Example tone: "{{s}} שלח/ה בטעות הודעה קולית לקבוצה הלא נכונה. איך יוצאים מזה?" with distinct reactions, not personality labels. Do not repeat this example.
- Adult dating/intimacy only when explicitly selected, or at level 3. Family/children context always overrides adult suggestions: keep the pack clean, warm and funny.
- Every question must earn its place: it should trigger laughter, surprise, debate, 'what?!', affectionate teasing, or reveal something socially interesting.
- Chill is NOT boring or formal. For family, parent/child, or low-spice groups, create funny everyday dilemmas, old memories, travel mishaps, money hypotheticals, family habits, embarrassing-but-safe moments, and “I can’t believe you picked that” choices. Keep it warm and safe, but still entertaining.
- If the group has only two players, never create room questions. Every question must give the spotlight player 4 plausible choices so the other person has something real to predict.
- Write like a sharp party-game writer, not a therapist, survey, HR form, or personality test. Use short, conversational, native-sounding phrasing in the requested language. Concrete scenes, awkward choices, funny stakes, and recognizable real-life moments.
- Reject bland prompts such as generic 'what is most important to X', 'what would X prefer', or abstract self-development language unless the scenario makes it funny.
- At least half the pack should involve a familiar social consequence or a choice involving another player, but keep the setup ordinary and believable. Do not add artificial deadlines, large sums or fantasy stakes merely to make it vivid.
- For Bold and especially No Filter, DO NOT sound polite, corporate, therapeutic or overly sanitized. Use the kind of natural contemporary language friends would actually use at a party in the requested locale. Answers should have attitude and personality.
- In No Filter, sound like close adult friends talking at 1 AM, not a psychology questionnaire. Short, direct, cheeky phrasing in the requested language is preferred. Use ordinary non-graphic adult dating vocabulary that sounds natural in the requested language and locale; do not import slang from another language unless people in that locale genuinely use it. You may ask playful questions about sexual roles, adult kinks in ordinary non-graphic labels, dating-app behavior, how many matches became meetups, types, boundaries, attraction, flirting and money-dare hypotheticals. A small minority of No Filter questions should feel like a genuinely daring late-night adult friends game rather than a polite dating quiz. Keep wording short and non-graphic; never ask for detailed descriptions of an encounter.
- Use the host context when useful, but do not repeat it mechanically.
- Concrete scenarios beat generic preferences.
- Avoid trivia, boring favorites, generic personality labels, and survey-like wording. Never ask the same underlying scenario twice in one pack, even when the location, amount, tense, or phrasing changes. Before returning, compare the core event in every pair and replace any semantic duplicate.
- No politics, religion, health, trauma, illegal behavior, body/appearance ranking, outing, infidelity accusations, coercion, humiliation, or asking players to reveal a specific private sexual event.
- LGBTQ+ and adult themes are welcome when requested. No Filter may be sexy and cheeky, but keep it consensual and game-friendly.
- Do not invent facts about players.
- Vary dating, friendship, nightlife, travel, trust, dilemmas, and group dynamics according to the chosen topics.
"""
 ticket=None
 try:
  from openai import OpenAI
  ticket=budget.begin('text','gpt-5.6-luna')
  with OpenAI(api_key=key,timeout=45,max_retries=0) as client:
   r=client.responses.create(model='gpt-5.6-luna',input=prompt,max_output_tokens=4000)
  budget.finish(ticket,getattr(r,'usage',None))
  txt=r.output_text.strip();a=txt.find('[');b=txt.rfind(']')
  data=json.loads(txt[a:b+1])
  return clean_pack(data,language)
 except Exception as e:
  budget.finish(ticket,status='unknown_or_failed')
  print('custom pack generation failed',type(e).__name__,str(e)[:300],flush=True);return []
