"""Website-first 1080x1350 Erudience editorial poster; genuine font files required, logo optional."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'modules' / 'brand_claims_qa'))
from website_brand_v38 import PALETTE

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def render(spec,out):
 errors=[]
 for key in ('heading_font_file','body_font_file'):
  path=Path(spec.get(key) or '/missing')
  if not path.is_file() or not spec.get(key+'_sha256') or sha(path)!=spec[key+'_sha256']:errors.append('FONT_FILE_UNVERIFIED:'+key)
 if spec.get('logo'):
  p=Path(spec['logo'])
  if not p.is_file() or not spec.get('logo_sha256') or sha(p)!=spec['logo_sha256'] or not spec.get('logo_source'):errors.append('LOGO_UNVERIFIED')
 if spec.get('heading_font')!='Sora' or spec.get('body_font')!='Sora':errors.append('FONT_FAMILY_MISMATCH')
 if spec.get('palette')!=PALETTE:errors.append('PALETTE_MISMATCH')
 if spec.get('brand_name')!='Erudience' or spec.get('footer')!='erudience.com':errors.append('BRAND_IDENTITY_MISSING')
 title=spec.get('headline','')
 if not title or len(title.split())>12:errors.append('INVALID_HEADLINE')
 steps=spec.get('steps',[])
 if not 3<=len(steps)<=5 or any(not isinstance(x,str) or not x.strip() for x in steps):errors.append('INVALID_STEPS')
 if errors:return {'status':'BLOCKED','errors':errors}
 im=Image.new('RGB',(1080,1350),PALETTE['paper']);d=ImageDraw.Draw(im)
 head=spec['heading_font_file'];body=spec['body_font_file']
 def f(p,n):return ImageFont.truetype(p,n)
 def wrap(s,p,n,w):
  lines=[];cur=''
  for word in s.split():
   candidate=(cur+' '+word).strip()
   if cur and d.textbbox((0,0),candidate,font=f(p,n))[2]>w:lines.append(cur);cur=word
   else:cur=candidate
  if cur:lines.append(cur)
  return lines
 d.rounded_rectangle((64,60,385,114),radius=25,fill='#B6EED7')
 d.text((85,77),spec.get('category','WORKFLOW AUTOMATION')[:23],font=f(head,19),fill=PALETTE['ink'])
 title_lines=wrap(title,head,59,940)
 if len(title_lines)>3:return {'status':'BLOCKED','errors':['TITLE_OVERFLOW']}
 for i,line in enumerate(title_lines):d.text((64,160+i*72),line,font=f(head,59),fill=PALETTE['ink'])
 y=160+len(title_lines)*72+27
 for line in wrap(spec.get('support','Practical automation, with a clear human hand-off.'),body,27,940)[:3]:d.text((66,y),line,font=f(body,27),fill=PALETTE['soft']);y+=40
 y+=30
 for i,step in enumerate(steps):
  if y+126>1090:return {'status':'BLOCKED','errors':['CARD_OVERFLOW']}
  d.rounded_rectangle((64,y,1016,y+122),radius=17,fill='#FFFCF7',outline='#C9C4B9',width=2)
  d.text((88,y+25),f'{i+1:02}',font=f(head,35),fill=PALETTE['deep'])
  lines=wrap(step,body,25,790)
  if len(lines)>2:return {'status':'BLOCKED','errors':['CARD_TEXT_OVERFLOW']}
  for j,line in enumerate(lines):d.text((172,y+24+j*35),line,font=f(body,25),fill=PALETTE['ink'])
  y+=141
 d.rounded_rectangle((64,1100,1016,1195),radius=18,fill=PALETTE['dark'])
 for i,line in enumerate(wrap(spec.get('takeaway','Keep a person accountable for exceptions.'),head,25,890)[:2]):d.text((90,1118+i*32),line,font=f(head,25),fill=PALETTE['paper'])
 d.line((64,1232,1016,1232),fill='#C5BDB2',width=2)
 if spec.get('logo'):
  logo=Image.open(spec['logo']).convert('RGBA');logo.thumbnail((250,66));im.paste(logo,(64,1252),logo)
 else:d.text((64,1257),'Erudience',font=f(head,30),fill=PALETTE['ink'])
 d.text((795,1265),'erudience.com',font=f(body,21),fill=PALETTE['soft'])
 out=Path(out);out.parent.mkdir(parents=True,exist_ok=True);im.save(out)
 result={'status':'RENDERED_REQUIRES_INDEPENDENT_VISUAL_QA','image_path':str(out),'sha256':sha(out),'logo_included':bool(spec.get('logo')),'fonts':['Sora','Sora']}
 out.with_suffix('.json').write_text(json.dumps(result,indent=2));return result
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--spec',required=True);ap.add_argument('--output',required=True);args=ap.parse_args()
 print(json.dumps(render(json.loads(Path(args.spec).read_text()),args.output),indent=2))
