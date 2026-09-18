import base64,io,os
def prompt_for(question,answer,names):
 cast=', '.join(names)
 return f"""Create a premium cinematic comedy reveal image for a private social party game. The uploaded reference images correspond, in order, to these players: {cast}. Preserve each referenced person's recognizable face, identity, approximate age and natural proportions. Put the referenced people together naturally in ONE coherent cinematic scene rather than separate portraits or pasted heads.

Visually dramatize this game reveal:
Question: {question}
Answer: {answer}
Featured players: {cast}

Make the result witty, polished, photorealistic, expressive and social-media-shareable. Use cinematic lighting, believable body language, a rich environment, depth, and a clear visual joke. The chosen/featured pair should be visually central when two people are provided. Do not add written text, captions, logos or fake publication branding. No nudity, sexual activity, violence, humiliation or hateful content. For dating, LGBTQ+ life, nightlife or intimacy, keep the scene playful, celebratory, adult and non-explicit."""
def _file(data_url,i):
 raw=base64.b64decode(data_url.split(',',1)[1]);f=io.BytesIO(raw);f.name=f'player_{i}.png';return f
def generate(people,question,answer):
 key=os.getenv('OPENAI_API_KEY','').strip()
 people=[p for p in people if p.get('photo')]
 if not key or not people:return ''
 try:
  from openai import OpenAI
  files=[_file(p['photo'],i) for i,p in enumerate(people)]
  image_arg=files if len(files)>1 else files[0]
  r=OpenAI(api_key=key,timeout=120).images.edit(model='gpt-image-1',image=image_arg,prompt=prompt_for(question,answer,[p['name'] for p in people]),size='1024x1024',quality='medium',input_fidelity='high')
  out=r.data[0].b64_json
  return 'data:image/png;base64,'+out if out else ''
 except Exception as e:
  print('hero generation failed',type(e).__name__,str(e)[:400],flush=True);return ''
