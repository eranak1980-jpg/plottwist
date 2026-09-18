import base64,io,os
def prompt_for(question,answer,name):
 return f"""Create a premium cinematic comedy reveal image for a private social party game. Use the uploaded person's face as the recognizable main character and preserve identity. The scene should visually dramatize this game reveal: Question: {question}. Answer: {answer}. Main player: {name}. Make it witty, polished, photorealistic, expressive and social-media-shareable, with a coherent environment and natural body proportions. No text, logos, nudity, sexual activity, violence, humiliation, or hateful content. If the topic is dating, LGBTQ+ life, nightlife or intimacy, keep the visual playful, celebratory and non-explicit."""
def generate(data_url,question,answer,name):
 key=os.getenv('OPENAI_API_KEY','').strip()
 if not key or not data_url:return ''
 try:
  from openai import OpenAI
  raw=base64.b64decode(data_url.split(',',1)[1]);f=io.BytesIO(raw);f.name='player.png'
  r=OpenAI(api_key=key,timeout=90).images.edit(model='gpt-image-1',image=f,prompt=prompt_for(question,answer,name),size='1024x1024',quality='medium',input_fidelity='high')
  out=r.data[0].b64_json
  return 'data:image/png;base64,'+out if out else ''
 except Exception as e:
  print('hero generation failed',type(e).__name__,str(e)[:250],flush=True);return ''
