import base64,io,os
def _file(data_url,i):
 raw=base64.b64decode(data_url.split(',',1)[1]);f=io.BytesIO(raw);f.name=f'player_{i}.jpg';return f
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
Make the scene coherent, witty, photorealistic, expressive, premium, and social-media-shareable. Use natural full-body or half-body composition, believable lighting and environment, and make the joke understandable visually without written text.
When the answer names a friend, clearly feature that friend with the main character. When the scenario is about the whole group, use all referenced friends. Background friends may look mock-jealous, surprised, abandoned, celebratory or amused only when that fits the reveal.
No text, logos, nudity, sexual activity, violence, degrading humiliation, or hateful content. Dating, LGBTQ+, nightlife and adult themes must stay playful, celebratory and non-explicit."""
def generate_many(items,question,answer,focus,selected=''):
 key=os.getenv('OPENAI_API_KEY','').strip()
 clean=[(n,d) for n,d in items if d][:5]
 if not key or not clean:return ''
 try:
  from openai import OpenAI
  files=[_file(d,i) for i,(n,d) in enumerate(clean)]
  r=OpenAI(api_key=key,timeout=120).images.edit(model='gpt-image-1',image=files,prompt=prompt_for(question,answer,[n for n,d in clean],focus,selected),size='1024x1024',quality='medium',input_fidelity='high')
  out=r.data[0].b64_json
  return 'data:image/png;base64,'+out if out else ''
 except Exception as e:
  print('group hero generation failed',type(e).__name__,str(e)[:350],flush=True);return ''
