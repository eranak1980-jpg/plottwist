import json,os
def generate_pack(topics,context,spice):
 key=os.getenv('OPENAI_API_KEY','').strip()
 if not key:return []
 level={1:'Chill: playful and broadly comfortable',2:'Bold: personal, cheeky and revealing but not sexual unless the selected topics call for it',3:'No Filter: adults-only, cheeky questions may involve dating, attraction, sexuality and sex-life preferences, but never pressure anyone to disclose a specific sexual act or private history'}[int(spice)]
 prompt=f"""You design premium social party-game questions for PlotTwist: Know Your Crew.
All players are adults when spice=3.
Selected topics: {', '.join(topics) if topics else 'mixed'}
Host description of the group: {context or 'none'}
Spice level: {level}

Create exactly 10 excellent questions tailored to THIS group. The game loop: one spotlight player answers secretly; everyone else predicts their answer.
Return ONLY a JSON array. Each item must be either:
{{"type":"know","text":"Hebrew question containing {{s}} for spotlight player","options":["4 short mutually distinct Hebrew answers"]}}
or
{{"type":"room","text":"Hebrew question containing {{s}}","options":[]}}
For room questions the answer will be one of the other players.

Editorial standard:
- Questions should trigger laughter, surprise, debate, 'what?!', or affectionate teasing after reveal.
- Use the host context when useful, but do not repeat it mechanically.
- Concrete scenarios beat generic preferences.
- Avoid trivia and boring favorites.
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
