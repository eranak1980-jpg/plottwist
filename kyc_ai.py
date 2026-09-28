import kyc_budget as budget
import json,os,re
from kyc_locales import normalize_language,topic_labels

def clean_pack(data,language='en'):
 """Reject broken/overlong choices instead of cutting off their meaning."""
 if not isinstance(data,list):return []
 out=[];seen=set()
 for q in data:
  if not isinstance(q,dict):continue
  typ=q.get('type');text=q.get('text');opts=q.get('options',[])
  if typ not in ('know','room') or not isinstance(text,str):continue
  text=text.strip();key=re.sub(r'\W+','',text).casefold()
  if '{s}' not in text or key in seen or len(text)>(160 if language=='ja' else 280):continue
  if language!='ja' and len(text.split())>40:continue
  if not isinstance(opts,list):continue
  if typ=='know':
   if len(opts)!=4 or any(not isinstance(o,str) or not o.strip() for o in opts):continue
   opts=[o.strip() for o in opts]
   if any(len(o)>70 or (language!='ja' and len(o.split())>10) for o in opts):continue
   if len({re.sub(r'\W+','',o).casefold() for o in opts})!=4:continue
   if any('משהו אחר' in o or re.search(r'\b(something else|other answer|skip question)\b',o,re.I) for o in opts):continue
  else:opts=[]
  seen.add(key);out.append((typ,text,opts))
 return out[:10] if len(out)>=6 else []

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

Create exactly 10 excellent questions tailored to THIS group. The game loop: one spotlight player answers secretly; everyone else predicts their answer.
Return ONLY a JSON array. Each item must be either:
{{"type":"know","text":"question in the requested language containing {{s}} for spotlight player","options":["4 short mutually distinct answers in the requested language"]}}
or
{{"type":"room","text":"question in the requested language containing {{s}}","options":[]}}
For room questions the answer will be one of the other players.

Editorial standard:
- A player must understand the question on the FIRST read. Use one concrete situation and one direct question, at most two sentences and 35 words (140 characters in Japanese). Name what went wrong; never say only "things get complicated". Avoid stacked conditions, metaphors, wordplay and vague references like "this choice".
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
- At least half the pack should contain a vivid setup, dilemma, social consequence, money/time pressure, travel/nightlife/date situation, or a choice involving another player.
- For Bold and especially No Filter, DO NOT sound polite, corporate, therapeutic or overly sanitized. Use the kind of natural contemporary language friends would actually use at a party in the requested locale. Answers should have attitude and personality.
- In No Filter, sound like close adult friends talking at 1 AM, not a psychology questionnaire. Short, direct, cheeky phrasing in the requested language is preferred. Use ordinary non-graphic adult dating vocabulary that sounds natural in the requested language and locale; do not import slang from another language unless people in that locale genuinely use it. You may ask playful questions about sexual roles, adult kinks in ordinary non-graphic labels, dating-app behavior, how many matches became meetups, types, boundaries, attraction, flirting and money-dare hypotheticals. A small minority of No Filter questions should feel like a genuinely daring late-night adult friends game rather than a polite dating quiz. Keep wording short and non-graphic; never ask for detailed descriptions of an encounter.
- Use the host context when useful, but do not repeat it mechanically.
- Concrete scenarios beat generic preferences.
- Avoid trivia, boring favorites, generic personality labels, and survey-like wording. Never ask the same underlying scenario twice in one pack.
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
   r=client.responses.create(model='gpt-5.6-luna',input=prompt,max_output_tokens=3500)
  budget.finish(ticket,getattr(r,'usage',None))
  txt=r.output_text.strip();a=txt.find('[');b=txt.rfind(']')
  data=json.loads(txt[a:b+1])
  return clean_pack(data,language)
 except Exception as e:
  budget.finish(ticket,status='unknown_or_failed')
  print('custom pack generation failed',type(e).__name__,str(e)[:300],flush=True);return []
