"""Real bundled ONNX execution and memory gate, no provider mock."""
import base64,io,os,resource,sys
from pathlib import Path
from PIL import Image,ImageDraw
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
os.environ['ENABLE_U2NET_CUTOUT']='1'
import kyc_instant as instant
instant.warm()
assert instant._segmenter is not None
im=Image.new('RGB',(1254,1254),'#ddd');ImageDraw.Draw(im).ellipse((230,160,1020,1190),fill='#a86e4c')
out=io.BytesIO();im.save(out,format='PNG')
portrait,seconds=instant.preprocess('data:image/png;base64,'+base64.b64encode(out.getvalue()).decode())
assert portrait.startswith('data:image/')
peak_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
assert peak_kib<330000,peak_kib
print({'real_cutout_seconds':seconds,'peak_memory_mib':round(peak_kib/1024,1)})
