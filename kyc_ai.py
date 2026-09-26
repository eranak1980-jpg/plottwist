import json,os
from kyc_locales import normalize_language,topic_labels

def generate_pack(topics,context,spice,language='en'):
 language=normalize_language(language)
 key=os.getenv('OPENAI_API_KEY','').strip()
 if not key:return []
 level={1:'Chill: playful and broadly comfortable',2:'Bold: personal, cheeky and revealing but not sexual unless the selected topics call for it',3:'No Filter: adults-only, bold, cheeky and genuinely spicy. Questions may involve dating apps, attraction, sexual chemistry, flirting, hookups, types, turn-ons/turn-offs and sex-life preferences, while staying non-graphic and never pressuring anyone to disclose a specific private sexual event'}[int(spice)]
 names={'en':'English','es':'Spanish','pt-BR':'Brazilian Portuguese','fr':'French','ar':'Arabic','he':'Hebrew'}
 natural={'en':'natural contemporary English used by friends at a party','es':'natural contemporary Spanish that sounds native and social, not translated','pt-BR':'natural contemporary Brazilian Portuguese, casual and social, not European Portuguese','fr':'natural contemporary French used by friends, not literal translation','ar':'natural conversational modern Arabic that is widely understandable, warm and social, not stiff MSA','he':'natural contemporary Hebrew used by friends at a party'}
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
- Every question must earn its place: it should trigger laughter, surprise, debate, 'what?!', affectionate teasing, or reveal something socially interesting.
- Chill is NOT boring or formal. For family, parent/child, or low-spice groups, create funny everyday dilemmas, old memories, travel mishaps, money hypotheticals, family habits, embarrassing-but-safe moments, and “I can’t believe you picked that” choices. Keep it warm and safe, but still entertaining.
- If the group has only two players, never create room questions. Every question must give the spotlight player 4 plausible choices so the other person has something real to predict.
- Write like a sharp party-game writer, not a therapist, survey, HR form, or personality test. Short conversational Hebrew. Concrete scenes, awkward choices, funny stakes, and recognizable real-life moments.
- Reject bland prompts such as generic 'what is most important to X', 'what would X prefer', or abstract self-development language unless the scenario makes it funny.
- At least half the pack should contain a vivid setup, dilemma, social consequence, money/time pressure, travel/nightlife/date situation, or a choice involving another player.
- For Bold and especially No Filter, DO NOT sound polite, corporate, therapeutic or overly sanitized. Use natural contemporary Hebrew friends would actually say at a party. Answers should have attitude and personality.
- In No Filter, sound like close adult friends talking at 1 AM, not a psychology questionnaire. Short, direct, cheeky Hebrew is preferred. You may use ordinary non-graphic adult dating/sexual vocabulary such as אקטיבי, פסיבי, ורסטילי, סטוץ, גריינדר, מאץ׳, קראש, קינק, טייפ and sexual chemistry. You may ask playful questions about sexual roles, adult kinks in ordinary non-graphic labels, dating-app behavior, how many matches became meetups, types, boundaries, attraction, flirting and money-dare hypotheticals. A small minority of No Filter questions should feel like a genuinely daring late-night adult friends game rather than a polite dating quiz. Keep wording short and non-graphic; never ask for detailed descriptions of an encounter.
- Use the host context when useful, but do not repeat it mechanically.
- Concrete scenarios beat generic preferences.
- Avoid trivia, boring favorites, generic personality labels, and survey-like wording. Never ask the same underlying scenario twice in one pack.
- No politics, religion, health, trauma, illegal behavior, body/appearance ranking, outing, infidelity accusations, coercion, humiliation, or asking players to reveal a specific private sexual event.
- LGBTQ+ and adult themes are welcome when requested. No Filter may be sexy and cheeky, but keep it consensual and game-friendly.
- Do not invent facts about players.
- Vary dating, friendship, nightlife, travel, trust, dilemmas, and group dynamics according to the chosen topics.
"""
 try:
  from openai import OpenAI
  r=OpenAI(api_key=key,timeout=45).responses.create(model='gpt-5.6-luna',input=prompt)
  txt=r.output_text.strip();a=txt.find('[');b=txt.rfind(']')
  data=json.loads(txt[a:b+1])
  out=[]
  for q in data:
   typ=q.get('type');text=str(q.get('text','')).strip();opts=q.get('options',[])
   if typ not in ('know','room') or '{s}' not in text:continue
   if typ=='know' and (not isinstance(opts,list) or len(opts)!=4):continue
   out.append((typ,text,[str(x)[:90] for x in opts]))
  return out[:10] if len(out)>=6 else []
 except Exception as e:
  print('custom pack generation failed',type(e).__name__,str(e)[:300],flush=True);return []
