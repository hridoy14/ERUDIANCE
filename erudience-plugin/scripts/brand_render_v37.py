"""Strict Erudience branded rendering entry point; rejects missing authentic asset evidence."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
COLORS={'paper':'#F6F1E9','ink':'#14120E','emerald':'#10B981','deep':'#0A6E3E','dark':'#0A100E','soft':'#615B4C'}

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def verify_assets(spec):
    problems=[]
    for key in ('logo','sora_regular','sora_bold'):
        asset=spec.get(key,{})
        p=Path(asset.get('path',''))
        if not p.is_file() or not asset.get('sha256') or sha(p)!=asset['sha256'] or not asset.get('source'):
            problems.append('UNVERIFIED_'+key.upper())
    if spec.get('palette')!=COLORS:problems.append('PALETTE_MISMATCH')
    if spec.get('brand_policy')!='social-os/BRAND.md:v1.1':problems.append('POLICY_NOT_PINNED')
    return problems

def render(spec,out):
    problems=verify_assets(spec)
    if problems:return {'status':'BLOCKED','errors':problems}
    copy=spec.get('copy',{})
    title=copy.get('headline','')
    if not title or len(title.split())>12:return {'status':'BLOCKED','errors':['INVALID_HEADLINE']}
    points=copy.get('steps',[])
    if not 3<=len(points)<=5 or any(not isinstance(p,str) or not p.strip() for p in points):return {'status':'BLOCKED','errors':['INVALID_STEPS']}
    im=Image.new('RGB',(1080,1350),COLORS['paper']);d=ImageDraw.Draw(im)
    bold=spec['sora_bold']['path'];regular=spec['sora_regular']['path']
    def font(p,n):return ImageFont.truetype(p,n)
    def wrap(s,p,size,width):
        f=font(p,size);lines=[];cur=''
        for word in s.split():
            test=(cur+' '+word).strip()
            if d.textbbox((0,0),test,font=f)[2]>width and cur:lines.append(cur);cur=word
            else:cur=test
        if cur:lines.append(cur)
        return lines
    d.rounded_rectangle((64,60,390,115),radius=27,fill='#B6EED7')
    d.text((88,75),copy.get('category','SUPPORT AUTOMATION')[:25],font=font(bold,19),fill=COLORS['ink'])
    title_lines=wrap(title,bold,62,940)
    if len(title_lines)>3:return {'status':'BLOCKED','errors':['HEADLINE_OVERFLOW']}
    for i,line in enumerate(title_lines):d.text((64,155+i*75),line,font=font(bold,62),fill=COLORS['ink'])
    y=155+len(title_lines)*75+35
    desc=copy.get('support','A practical workflow with a clear human hand-off.')
    for line in wrap(desc,regular,28,935)[:3]:d.text((66,y),line,font=font(regular,28),fill=COLORS['soft']);y+=43
    y+=22
    for i,step in enumerate(points):
        h=122
        if y+h>1080:return {'status':'BLOCKED','errors':['STEPS_OVERFLOW']}
        d.rounded_rectangle((64,y,1016,y+h),radius=18,fill='#FFFCF7',outline='#C9C4B9',width=2)
        d.text((90,y+26),f'{i+1:02}',font=font(bold,38),fill=COLORS['deep'])
        lines=wrap(step,regular,26,770)
        if len(lines)>2:return {'status':'BLOCKED','errors':['STEP_TEXT_OVERFLOW']}
        for j,line in enumerate(lines):d.text((180,y+24+j*36),line,font=font(regular,26),fill=COLORS['ink'])
        y+=h+18
    takeaway=copy.get('takeaway','Keep a person responsible for exceptions.')
    d.rounded_rectangle((64,1100,1016,1190),radius=18,fill=COLORS['dark'])
    lines=wrap(takeaway,bold,25,890)
    if len(lines)>2:return {'status':'BLOCKED','errors':['TAKEAWAY_OVERFLOW']}
    for j,line in enumerate(lines):d.text((90,1116+j*32),line,font=font(bold,25),fill=COLORS['paper'])
    d.line((64,1230,1016,1230),fill='#B8B0A4',width=2)
    logo=Image.open(spec['logo']['path']).convert('RGBA');logo.thumbnail((280,75))
    im.paste(logo,(64,1250),logo)
    d.text((800,1270),'erudience.com',font=font(regular,21),fill=COLORS['soft'])
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True);im.save(out)
    receipt={'status':'RENDERED_REQUIRES_INDEPENDENT_VISUAL_QA','image_path':str(out),'sha256':sha(out),'brand_policy':spec['brand_policy'],'logo_sha256':spec['logo']['sha256']}
    out.with_suffix('.json').write_text(json.dumps(receipt,indent=2))
    return receipt
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--spec',required=True);ap.add_argument('--output',required=True);args=ap.parse_args()
    print(json.dumps(render(json.loads(Path(args.spec).read_text()),args.output),indent=2))
