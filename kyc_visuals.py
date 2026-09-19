import base64,io,os
def _file(data_url,i):
 raw=base64.b64decode(data_url.split(',',1)[1]);f=io.BytesIO(raw);f.name=f'player_{i}.jpg';return f
def _direction(q):
 if 'אי בודד' in q:return 'Stage it on a gorgeous tropical island: featured people relaxed and smiling in the foreground; other friends can appear comically in a tiny boat offshore or reacting from the beach.'
 if 'עסק' in q or '50%' in q:return 'Stage it as an exaggerated premium startup/business success scene: featured partners confidently together; other friends reacting playfully in the background.'
 if 'Pride' in q or 'בר גאה' in q:return 'Stage it as a vibrant elegant LGBTQ+ nightlife or Pride travel scene with celebratory lighting and tasteful rainbow details; the whole crew can participate naturally.'
 if 'דייט' in q or 'crush' in q or 'היכרויות' in q:return 'Stage it as a stylish romantic-comedy dating scene, with friends in the background reacting like a playful commentary squad.'
 if '3 בלילה' in q:return 'Stage it as a funny late-night rescue situation at 3 AM, cinematic city lighting, with the trusted friend arriving to save the day and others reacting in the background.'
 if 'טיול' in q or 'טיסה' in q or 'מדינה' in q:return 'Stage it as a polished travel-adventure comedy at an airport or striking destination, with luggage and expressive group reactions.'
 if '50,000' in q or '100,000' in q:return 'Stage it as an extravagant but tasteful spending fantasy, with the main player enjoying the revealed choice and friends reacting around them.'
 return 'Build a cinematic situation that makes the revealed choice immediately understandable from body language, setting, props and group reactions.'
def prompt_for(question,answer,people,focus,selected=''):
 refs='; '.join([f'input image {i+1} = {name}' for i,name in enumerate(people)])
 composition=f'{focus} is the main character.'
 if selected and selected!=focus:composition+=f' {selected} is the second featured character beside {focus}.'
 if len(people)>2:composition+=' Include the remaining referenced friends naturally in the background with funny, readable reactions when it fits the scenario.'
 return f"""Create ONE premium cinematic comedy reveal image for a private social party game.
Reference mapping: {refs}.
Preserve each person's recognizable identity, face, approximate age and distinct appearance. Do not merge faces or invent extra people.
{composition}
Visually dramatize this exact game moment:
Question: {question}
Revealed answer: {answer}
Specific scene direction: {_direction(question)}\nMake the scene coherent, witty, photorealistic, expressive, premium, and social-media-shareable. Use natural full-body or half-body composition, believable lighting and environment, and make the joke understandable visually without written text.
When the answer names a friend, clearly feature that friend with the main character. When the scenario is about the whole group, use all referenced friends. Background friends may look mock-jealous, surprised, abandoned, celebratory or amused only when that fits the reveal.
No text, logos, nudity, sexual activity, violence, degrading humiliation, or hateful content. Dating, LGBTQ+, nightlife and adult themes must stay playful, celebratory and non-explicit."""
def generate_many(items,question,answer,focus,selected=''):
 key=os.getenv('OPENAI_API_KEY','').strip()
 clean=[(n,d) for n,d in items if d][:6]
 if not key or not clean:return ''
 prompt=prompt_for(question,answer,[n for n,d in clean],focus,selected)
 try:
  from openai import OpenAI
  client=OpenAI(api_key=key,timeout=120)
  content=[{'type':'input_text','text':prompt}]
  for n,data_url in clean:
   content.append({'type':'input_image','image_url':data_url,'detail':'high'})
  r=client.responses.create(model='gpt-5.6-luna',input=[{'role':'user','content':content}],tools=[{'type':'image_generation','model':'gpt-image-2','action':'edit','quality':'medium','size':'1024x1024'}])
  for item in r.output:
   if getattr(item,'type','')=='image_generation_call' and getattr(item,'result',None):
    return 'data:image/png;base64,'+item.result
 except Exception as e:
  print('responses image generation failed',type(e).__name__,str(e)[:350],flush=True)
 try:
  from openai import OpenAI
  files=[_file(d,i) for i,(n,d) in enumerate(clean)]
  r=OpenAI(api_key=key,timeout=120).images.edit(model='gpt-image-2',image=files,prompt=prompt,size='1024x1024',quality='medium')
  out=getattr(r.data[0],'b64_json',None)
  return 'data:image/png;base64,'+out if out else ''
 except Exception as e:
  print('fallback image edit failed',type(e).__name__,str(e)[:350],flush=True);return ''
