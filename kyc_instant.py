"""Deterministic portrait posters. No network or generative AI on this path."""
import base64, hashlib, io, json, os, re, time
from functools import lru_cache
from pathlib import Path
from kyc_visuals import decode_image

# Language-independent assets; keyword matching only selects decoration, never questions.
CATEGORIES = {
 'travel': 'travel trip flight airport vacation holiday suitcase viaje vacances viagem 旅行 טיול טיסה חופשה',
 'money': 'money cash dollar spend bank lottery budget dinero argent dinheiro お金 כסף דולר תקציב',
 'dating': 'date dating crush romance romantic kiss love cita amour encontro デート דייט אהבה זוגיות נשיקה',
 'nightlife': 'nightclub nightlife bar club midnight disco לילה מועדון בר',
 'food': 'food meal restaurant menu dinner cook pizza comida repas comida 食べ אוכל מסעדה ארוחה תפריט',
 'adventure': 'adventure mountain hike camping survival aventura aventure 冒険 הרפתקה טיפוס קמפינג',
 'work': 'work office boss job meeting trabajo travail trabalho 仕事 עבודה משרד בוס',
 'family': 'family parent mother father child familia famille família 家族 משפחה אמא אבא ילדים',
 'funny': 'embarrass awkward ridiculous shame funny vergüenza drôle vergonha 恥 מביך בושה מצחיק',
 'winner': 'winner champion trophy victory ganador gagnant vencedor 優勝 מנצח אלוף גביע',
 'luxury': 'luxury yacht millionaire mansion lujo luxe luxo 豪華 יוקרה יאכטה מיליונר',
 'beach': 'beach ocean island sea playa plage praia ビーチ חוף ים אי בודד',
 'party': 'party dance sing karaoke fiesta fête festa パーティ מסיבה ריקוד שיר קריוקי',
 'dilemma': 'dilemma choose choice either decision dilema dilemme 選択 דילמה לבחור בחירה',
 'general': ''}
COLORS = {'travel':(50,160,190),'money':(208,174,67),'dating':(210,87,135),
 'nightlife':(114,74,225),'food':(216,135,56),'adventure':(77,154,112),
 'work':(69,134,205),'family':(216,167,105),'funny':(216,92,66),
 'winner':(229,187,79),'luxury':(200,168,101),'beach':(53,183,185),
 'party':(187,83,207),'dilemma':(98,128,213),'general':(139,102,215)}

def init(c):
 c.execute('CREATE TABLE IF NOT EXISTS visual_portraits(player_id BIGINT PRIMARY KEY,photo_hash TEXT,image_data TEXT,seconds REAL)')
 c.execute('CREATE TABLE IF NOT EXISTS instant_scenes(game_id BIGINT,image_run INTEGER,round_no INTEGER,category TEXT,image_data TEXT,seconds REAL,UNIQUE(game_id,image_run,round_no))')

def data_url(im, fmt='JPEG'):
 out=io.BytesIO();im.save(out,format=fmt,**({'quality':86,'optimize':True} if fmt=='JPEG' else {}))
 return 'data:image/'+fmt.lower()+';base64,'+base64.b64encode(out.getvalue()).decode()

_segmenter=None
from threading import RLock
_segment_lock=RLock()

def warm():
 global _segmenter
 # The live game must never sacrifice room/join responsiveness for portrait
 # segmentation. U2NetP is opt-in because it can consume most of a small
 # Render instance's CPU/RAM. The default fast path keeps the original photo
 # pixels and uses the feathered portrait montage in compose().
 if os.getenv('ENABLE_U2NET_CUTOUT','0').strip()!='1':
  _segmenter=None
  print(json.dumps({'event':'instant_cutout_runtime_skipped','mode':'fast_portrait'}),flush=True)
  return
 try:
  import onnxruntime as ort
  options=ort.SessionOptions();options.intra_op_num_threads=1;options.inter_op_num_threads=1
  options.enable_cpu_mem_arena=False;options.enable_mem_pattern=False
  options.graph_optimization_level=ort.GraphOptimizationLevel.ORT_ENABLE_BASIC
  _segmenter=ort.InferenceSession(str(Path(__file__).parent/'models'/'u2netp.onnx'),sess_options=options,providers=['CPUExecutionProvider'])
  print(json.dumps({'event':'instant_cutout_runtime_ready','model':'u2netp'}),flush=True)
 except Exception as exc:
  _segmenter=None
  print(json.dumps({'event':'instant_cutout_runtime_unavailable','type':type(exc).__name__}),flush=True)

def cutout(im):
 if _segmenter is None:return im
 import numpy as np
 from PIL import Image
 # U2NetP's standard 320-square input affects only the alpha mask. RGB pixels
 # come from the original upload, so faces and body proportions are never generated.
 rgb=np.asarray(im.resize((320,320),Image.Resampling.LANCZOS),dtype=np.float32)
 rgb/=max(float(rgb.max()),1.0)
 rgb=(rgb-np.array([.485,.456,.406],dtype=np.float32))/np.array([.229,.224,.225],dtype=np.float32)
 tensor=rgb.transpose(2,0,1)[None].astype(np.float32)
 with _segment_lock:mask=_segmenter.run(None,{_segmenter.get_inputs()[0].name:tensor})[0][0,0]
 spread=float(mask.max()-mask.min())
 if spread<.01:return im
 mask=(mask-mask.min())/spread
 # Reject near-empty masks and retain the safe portrait fallback.
 coverage=float((mask>.5).mean())
 if not .06<coverage<.98:return im
 alpha=Image.fromarray((mask*255).astype('uint8')).resize(im.size,Image.Resampling.LANCZOS)
 result=im.convert('RGBA');result.putalpha(alpha)
 return result

def preprocess(data):
 with _segment_lock:return _preprocess(data)

def _preprocess(data):
 # Keep all source pixels in a contained portrait. Never synthesize/crop a face.
 from PIL import Image, ImageOps
 started=time.monotonic();_,raw=decode_image(data)
 with Image.open(io.BytesIO(raw)) as source:
  source.draft('RGB',(560,700));source.thumbnail((700,700),Image.Resampling.LANCZOS)
  im=ImageOps.exif_transpose(source).convert('RGB');im.thumbnail((560,700),Image.Resampling.LANCZOS)
  try:im=cutout(im)
  except Exception as exc:print(json.dumps({'event':'instant_cutout_fallback','type':type(exc).__name__}),flush=True)
  result=data_url(im,'PNG' if im.mode=='RGBA' else 'JPEG')
 return result,round(time.monotonic()-started,4)

def save_portrait(c,pid,data):
 digest=hashlib.sha256(data.encode()).hexdigest()
 old=c.execute('SELECT photo_hash FROM visual_portraits WHERE player_id=?',(pid,)).fetchone()
 if old and old['photo_hash']==digest:return
 result,seconds=preprocess(data)
 c.execute('INSERT INTO visual_portraits(player_id,photo_hash,image_data,seconds) VALUES(?,?,?,?) ON CONFLICT(player_id) DO UPDATE SET photo_hash=EXCLUDED.photo_hash,image_data=EXCLUDED.image_data,seconds=EXCLUDED.seconds',(pid,digest,result,seconds))
 print(json.dumps({'event':'instant_portrait_saved','player_id':pid,'seconds':seconds}),flush=True)

def category(question,answer,final=False):
 if final:return 'winner'
 def score(text,words):
  t=text.casefold()
  return sum(1 for w in words.split() if (w in t if not w.isascii() else re.search(r'\b'+re.escape(w)+r'\w*\b',t)))
 scores={k:score(question,v)+2*score(answer,v) for k,v in CATEGORIES.items() if v}
 if re.search(r'[$€£₪¥]\s*[\d,]+',question+' '+answer):scores['money']+=2
 best=max(scores,key=scores.get)
 return best if scores[best] else 'general'

@lru_cache(maxsize=3)
def background(cat):
 from PIL import Image, ImageDraw, ImageFilter
 root=Path(__file__).parent/'static'/'visual-scenes'
 asset=cat if (root/(cat+'.jpg')).exists() else ('dating' if cat=='family' else 'money' if cat in ('winner','luxury','work') else 'travel' if cat in ('adventure','beach') else 'general')
 path=root/(asset+'.jpg')
 if path.exists():
  from PIL import ImageOps
  with Image.open(path) as im:canvas=ImageOps.fit(im.convert('RGB'),(640,800))
 else:canvas=Image.new('RGB',(640,800),(18,16,31))
 # Category-specific cinematic lighting; immutable cached background.
 wash=Image.new('RGB',canvas.size,COLORS[cat]);canvas=Image.blend(canvas,wash,.10)
 shade=Image.new('RGBA',canvas.size);d=ImageDraw.Draw(shade)
 for y in range(800):d.line((0,y,640,y),fill=(4,5,15,int(105*abs(y-360)/440)))
 canvas=Image.alpha_composite(canvas.convert('RGBA'),shade)
 return canvas

def compose(portraits,cat):
 from PIL import Image, ImageDraw, ImageFilter
 canvas=background(cat).copy();count=min(2,len(portraits));accent=COLORS[cat]
 # Portraits are an intentional photographic movie-poster montage, not fake bodies.
 for i,data in enumerate(portraits[:2]):
  _,raw=decode_image(data)
  with Image.open(io.BytesIO(raw)) as src:
   im=src.convert('RGBA');im.thumbnail((560 if count==1 else 305,650 if count==1 else 490),Image.Resampling.LANCZOS)
  w,h=im.size;x=(640-w)//2 if count==1 else (12 if i==0 else 323)+(305-w)//2;y=int((800-h)*.62)
  mask=im.getchannel('A')
  if mask.getextrema()==(255,255):
   # If segmentation is unavailable, feather a photographic portrait montage.
   mask=Image.new('L',(w,h));md=ImageDraw.Draw(mask);md.rounded_rectangle((18,18,w-18,h-18),radius=50,fill=255);mask=mask.filter(ImageFilter.GaussianBlur(18))
  # Soft falloff at the source photo's bottom edge avoids an abrupt torso cut.
  import PIL.ImageChops as chops
  fade=Image.new('L',(w,h),255);fd=ImageDraw.Draw(fade)
  for yy in range(max(0,h-55),h):fd.line((0,yy,w,yy),fill=int(255*(h-yy)/55))
  mask=chops.multiply(mask,fade)
  # Blur a small single-channel mask, not four full-size RGBA canvases.
  # This also keeps two-player composition inside the small Render CPU budget.
  from PIL import ImageOps
  padded=ImageOps.expand(mask,border=30,fill=0)
  glow=padded.filter(ImageFilter.GaussianBlur(12)).point(lambda value:int(value*.40))
  canvas.paste((*accent,255),(x-30,y-30,x+w+30,y+h+30),glow)
  shadow=padded.filter(ImageFilter.GaussianBlur(9)).point(lambda value:int(value*.65))
  canvas.paste((0,0,0,255),(x-21,y-18,x+w+39,y+h+42),shadow)
  canvas.paste(im,(x,y),mask)
 return data_url(canvas.convert('RGB'))

def prepare(cn,g,rn,payload,ps):
 started=time.monotonic()
 with cn() as c:
  # Same row lock as the image job/replay path: at most one composition per round.
  if not c.pg:c.execute('BEGIN IMMEDIATE')
  current=c.execute('SELECT image_run FROM games WHERE id=?'+(' FOR UPDATE' if c.pg else ''),(g['id'],)).fetchone()
  if not current or current['image_run']!=g['image_run']:return
  if c.execute('SELECT 1 FROM instant_scenes WHERE game_id=? AND image_run=? AND round_no=?',(g['id'],g['image_run'],rn)).fetchone():return
  refs=[]
  for name,data in payload['items'][:1 if payload.get('final') else 2]:
   p=next((p for p in ps if p['name']==name),None)
   if p:
    save_portrait(c,p['id'],data)
    refs.append(c.execute('SELECT image_data FROM visual_portraits WHERE player_id=?',(p['id'],)).fetchone()['image_data'])
  if not refs:return
  cat=category(payload['question'],payload['answer'],payload.get('final',False));art=compose(refs,cat)
  elapsed=round(time.monotonic()-started,4)
  c.execute('INSERT INTO instant_scenes(game_id,image_run,round_no,category,image_data,seconds) VALUES(?,?,?,?,?,?) ON CONFLICT(game_id,image_run,round_no) DO NOTHING',(g['id'],g['image_run'],rn,cat,art,elapsed))
 print(json.dumps({'event':'instant_visual_saved','game_id':g['id'],'run':g['image_run'],'round':rn,'category':cat,'seconds':elapsed,'cast_count':len(refs)}),flush=True)
