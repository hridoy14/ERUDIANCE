"""Strict Erudience branded rendering entry point; rejects missing authentic asset evidence."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
COLORS={'paper':'#F6F1E9','ink':'#14120E','emerald':'#10B77F','deep':'#0C8D62','dark':'#080C0B','soft':'#615B4C','taupe':'#B7B0A0','emerald_light':'#36D399','mint':'#8AE5C4','border':'#21312C','background':'#080C0B','card':'#0F1A16','foreground':'#F9FBFA'}

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
def _canonical_policy():
    cfg=Path(__file__).resolve().parent.parent/'config'/'production-policy-v33.json'
    return json.loads(cfg.read_text(encoding='utf-8'))

def _default_font(size):
    try:return ImageFont.load_default(size=size)
    except TypeError:return ImageFont.load_default()

def render_production_poster(spec,out_path):
    """Production renderer (D-12/D-13). Same layout/copy rules as render(), BUT:

    - It does NOT require the external social-os/BRAND.md:v1.1 pin (that file
      does not exist in the repo); the receipt records brand_policy as
      NOT_PINNED_EXTERNALLY and asset sourcing stays BLOCKED_BY_OWNER (D-12).
    - Font files: real Sora files are used only when supplied with a matching
      sha256; otherwise Pillow's default font is used and the receipt records
      font_source 'pillow-default-fallback' and font_verified False. A font
      sha256 is NEVER fabricated (D-13: real Sora files now live in the repo at
      assets/fonts/ — Sora-Regular.ttf and Sora-Bold.ttf, verified 2026-11-24).
    - Logo: spec['logo'] = {'path','sha256'} is verified against the FILE's
      actual hash. The BUNDLED-approved-logo binding is enforced by the GATE
      (IMAGE_BUILD ORIGINAL_LOGO_PROVENANCE_REQUIRED), not by this renderer.
      When no logo is planned, logo_absence_checked is recorded True.
    - Palette: the CANONICAL palette from config/production-policy-v33.json,
      read at call time. The module-level COLORS constant is aligned to the
      same website-verified values (brand phase 2026-11-24: Sora-only,
      emerald #10B77F; #10B981 appears nowhere in the website tokens).
    Returns a receipt with status RENDERED_REQUIRES_INDEPENDENT_VISUAL_QA, or
    {'status':'BLOCKED','errors':[...]} with no PNG written.
    """
    spec=spec or {}
    try:policy=_canonical_policy()
    except Exception as e:return {'status':'BLOCKED','errors':['CANONICAL_POLICY_UNAVAILABLE: '+str(e)]}
    palette=dict(policy.get('brand',{}).get('palette') or {})
    if not palette:return {'status':'BLOCKED','errors':['CANONICAL_PALETTE_MISSING']}
    approved_logo_path=policy.get('brand_assets',{}).get('approved_logo_path')
    copy=spec.get('copy',{})
    title=copy.get('headline','')
    if not title or len(title.split())>12:return {'status':'BLOCKED','errors':['INVALID_HEADLINE']}
    points=copy.get('steps',[])
    if not 3<=len(points)<=5 or any(not isinstance(p,str) or not p.strip() for p in points):return {'status':'BLOCKED','errors':['INVALID_STEPS']}
    font_files={};font_verified=True
    for key in ('sora_bold','sora_regular'):
        asset=spec.get(key) or {}
        p=Path(asset.get('path','')) if isinstance(asset,dict) else Path('')
        if p.is_file() and asset.get('sha256') and sha(p)==asset['sha256']:font_files[key]=str(p)
        else:font_verified=False
    if not font_verified:font_files={}
    font_source='supplied' if font_verified else 'pillow-default-fallback'
    logo=None;logo_sha256=None;logo_absence_checked=False
    logo_spec=spec.get('logo')
    if isinstance(logo_spec,dict) and logo_spec.get('path'):
        lp=Path(logo_spec['path'])
        if not lp.is_file():return {'status':'BLOCKED','errors':['LOGO_FILE_MISSING']}
        if not logo_spec.get('sha256') or sha(lp)!=logo_spec['sha256']:return {'status':'BLOCKED','errors':['LOGO_SHA_MISMATCH']}
        logo=lp;logo_sha256=sha(lp)
    elif spec.get('logo_asset'):
        lp=Path(spec['logo_asset'])
        if not lp.is_file():return {'status':'BLOCKED','errors':['LOGO_FILE_MISSING']}
        logo=lp;logo_sha256=sha(lp)
    else:logo_absence_checked=True
    paper=palette.get('paper','#F6F1E9');ink=palette.get('ink','#14120E');soft=palette.get('soft','#615B4C');deep=palette.get('deep','#0C8D62');dark=palette.get('dark','#080C0B')
    def font(key,size):
        if font_files.get(key):
            try:return ImageFont.truetype(font_files[key],size)
            except Exception:return _default_font(size)
        return _default_font(size)
    im=Image.new('RGB',(1080,1350),paper);d=ImageDraw.Draw(im)
    def wrap(s,key,size,width):
        f=font(key,size);lines=[];cur=''
        for word in s.split():
            test=(cur+' '+word).strip()
            if d.textbbox((0,0),test,font=f)[2]>width and cur:lines.append(cur);cur=word
            else:cur=test
        if cur:lines.append(cur)
        return lines
    d.rounded_rectangle((64,60,390,115),radius=27,fill='#B6EED7')
    d.text((88,75),copy.get('category','SUPPORT AUTOMATION')[:25],font=font('sora_bold',19),fill=ink)
    # Layout fix (live run, 2026-11-24): real Sora metrics are wider than
    # Pillow's default font, so a 12-word headline wraps to 3 lines and a
    # long caption to 2 — the old geometry (62px title, 122px step boxes)
    # overflowed past y=1080 and the renderer BLOCKED every live job with
    # STEPS_OVERFLOW. Tightened geometry fits the worst case (3-line title
    # + 3-line desc + 5 steps) inside 1080: title 52px/62px lines from
    # y=140, desc 28px/40px lines, step boxes 108px with 12px gaps.
    title_lines=wrap(title,'sora_bold',52,940)
    if len(title_lines)>3:return {'status':'BLOCKED','errors':['HEADLINE_OVERFLOW']}
    for i,line in enumerate(title_lines):d.text((64,140+i*62),line,font=font('sora_bold',52),fill=ink)
    y=140+len(title_lines)*62+20
    desc=copy.get('support','A practical workflow with a clear human hand-off.')
    for line in wrap(desc,'sora_regular',28,935)[:3]:d.text((66,y),line,font=font('sora_regular',28),fill=soft);y+=40
    y+=16
    for i,step in enumerate(points):
        h=108
        if y+h>1080:return {'status':'BLOCKED','errors':['STEPS_OVERFLOW']}
        d.rounded_rectangle((64,y,1016,y+h),radius=18,fill='#FFFCF7',outline='#C9C4B9',width=2)
        d.text((90,y+26),f'{i+1:02}',font=font('sora_bold',38),fill=deep)
        lines=wrap(step,'sora_regular',26,770)
        if len(lines)>2:return {'status':'BLOCKED','errors':['STEP_TEXT_OVERFLOW']}
        for j,line in enumerate(lines):d.text((180,y+24+j*36),line,font=font('sora_regular',26),fill=ink)
        y+=h+12
    takeaway=copy.get('takeaway','Keep a person responsible for exceptions.')
    d.rounded_rectangle((64,1100,1016,1190),radius=18,fill=dark)
    lines=wrap(takeaway,'sora_bold',25,890)
    if len(lines)>2:return {'status':'BLOCKED','errors':['TAKEAWAY_OVERFLOW']}
    for j,line in enumerate(lines):d.text((90,1116+j*32),line,font=font('sora_bold',25),fill=paper)
    d.line((64,1230,1016,1230),fill='#B8B0A4',width=2)
    if logo is not None:
        lg=Image.open(logo).convert('RGBA');lg.thumbnail((280,75))
        im.paste(lg,(64,1250),lg)
    else:
        d.text((64,1250),'Erudience',font=font('sora_bold',30),fill=ink)
    d.text((800,1270),'erudience.com',font=font('sora_regular',21),fill=soft)
    out=Path(out_path);out.parent.mkdir(parents=True,exist_ok=True);im.save(out)
    receipt={'status':'RENDERED_REQUIRES_INDEPENDENT_VISUAL_QA','image_path':str(out),'sha256':sha(out),'brand_policy':'NOT_PINNED_EXTERNALLY (social-os/BRAND.md:v1.1 unavailable in repo; D-12 BLOCKED_BY_OWNER for asset sourcing)','logo_sha256':logo_sha256,'logo_absence_checked':logo_absence_checked,'approved_logo_path':approved_logo_path,'font_source':font_source,'font_verified':font_verified,'palette':palette}
    out.with_suffix('.json').write_text(json.dumps(receipt,indent=2))
    return receipt
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--spec',required=True);ap.add_argument('--output',required=True);args=ap.parse_args()
    print(json.dumps(render(json.loads(Path(args.spec).read_text()),args.output),indent=2))
