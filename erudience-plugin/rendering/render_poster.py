"""Deterministic review-draft renderer. Requires original logo and actual Inter/DM Sans files for final branded output."""
import argparse, pathlib, hashlib, json, sys
from PIL import Image, ImageDraw, ImageFont
W,H=1080,1350
PAPER='#F6F1E9';INK='#14120E';EMERALD='#10B981';DEEP='#0A6E3E';SOFT='#615B4C';DARK='#0A100E'
STAGES=[('01','CAPTURE','Track every enquiry.'),('02','ACKNOWLEDGE','Confirm receipt and next steps.'),('03','QUALIFY','Collect the details that matter.'),('04','ROUTE','Assign one accountable owner.'),('05','NEXT ACTION','Set a deadline and escalation path.'),('06','OUTCOME','Record what actually happened.')]
def font(path,size):
 if not path or not pathlib.Path(path).is_file():raise ValueError('Exact font path missing; install Inter and DM Sans and provide file paths')
 return ImageFont.truetype(path,size)
def fit(draw,text,f,maxwidth):return draw.textbbox((0,0),text,font=f)[2]<=maxwidth
def drawfit(draw,xy,text,path,start,width,fill,minsize=18):
 for size in range(start,minsize-1,-1):
  f=font(path,size)
  if fit(draw,text,f,width):draw.text(xy,text,font=f,fill=fill);return size
 raise ValueError('Text too long for allocated width: '+text)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--inter-bold',required=True);ap.add_argument('--inter-semibold',required=True);ap.add_argument('--dm-regular',required=True);ap.add_argument('--dm-medium',required=True);ap.add_argument('--brief',help='JSON brief with category, headline_lines (2), emphasis, support, stages (6 objects), takeaway, diagnostic, cta, domain');ap.add_argument('--logo',help='Genuine verified logo PNG; do not supply invented image');ap.add_argument('--output',required=True);ap.add_argument('--review-draft',action='store_true');args=ap.parse_args()
 if not args.logo and not args.review_draft:raise SystemExit('BLOCK: genuine logo required for branded final. Use --review-draft for a labelled draft.')
 brief=json.loads(pathlib.Path(args.brief).read_text()) if args.brief else {}
 category=brief.get('category','SALES & WORKFLOW AUTOMATION'); lines=brief.get('headline_lines',['YOUR CRM CAPTURED','THE LEAD.']); emphasis=brief.get('emphasis','WHO OWNS THE NEXT STEP?'); support=brief.get('support','Six checks for an accountable enquiry workflow.'); stages=brief.get('stages',[{'number':n,'title':t,'description':desc} for n,t,desc in STAGES]); takeaway=brief.get('takeaway','A notification is not a completed follow-up.'); diagnostic=brief.get('diagnostic','Can you trace your last five enquiries from capture to outcome?'); cta=brief.get('cta','Book your AI consultation'); domain=brief.get('domain','erudience.com')
 if len(lines)!=2 or len(stages)!=6:raise ValueError('Brief requires exactly 2 headline lines and 6 cards for this template; choose a suitable alternate template for other structures')
 im=Image.new('RGB',(W,H),PAPER);d=ImageDraw.Draw(im)
 d.rounded_rectangle((66,64,495,110),radius=23,fill='#B6EED7');drawfit(d,(88,76),category,args.inter_semibold,21,386,INK)
 drawfit(d,(66,150),lines[0],args.inter_bold,63,945,INK)
 drawfit(d,(66,221),lines[1],args.inter_bold,63,945,INK)
 drawfit(d,(66,303),emphasis,args.inter_bold,54,945,DEEP)
 drawfit(d,(67,383),support,args.dm_regular,29,940,SOFT)
 y0=466;cw=456;ch=158;gapx=24;gapy=19
 for i,item in enumerate(stages):
  num,title,desc=item['number'],item['title'],item['description']
  col=i%2;row=i//2;x=66+col*(cw+gapx);y=y0+row*(ch+gapy)
  d.rounded_rectangle((x,y,x+cw,y+ch),radius=21,fill='#FFFDF9',outline='#D8D1C5',width=2)
  drawfit(d,(x+23,y+18),num,args.inter_bold,37,65,DEEP)
  drawfit(d,(x+99,y+25),title,args.inter_bold,28,cw-118,INK)
  drawfit(d,(x+23,y+90),desc,args.dm_medium,24,cw-45,SOFT,minsize=18)
 y=1013;d.rounded_rectangle((66,y,1014,y+102),radius=19,fill=DARK)
 drawfit(d,(91,y+31),takeaway,args.inter_semibold,30,892,'#F6F1E9')
 drawfit(d,(66,1140),diagnostic,args.dm_medium,26,948,INK)
 drawfit(d,(66,1191),cta,args.inter_semibold,27,600,DEEP)
 d.line((66,1250,1014,1250),fill='#BFB8AB',width=2)
 if args.logo:
  src=pathlib.Path(args.logo);logo=Image.open(src).convert('RGBA');logo.thumbnail((270,65),Image.Resampling.LANCZOS)
  im.paste(logo,(66,1265),logo)
 else:
  drawfit(d,(66,1271),'REVIEW DRAFT — LOGO NOT VERIFIED',args.inter_semibold,16,580,SOFT,minsize=12)
 drawfit(d,(790,1274),domain,args.dm_medium,20,224,SOFT)
 out=pathlib.Path(args.output);out.parent.mkdir(parents=True,exist_ok=True);im.save(out,'PNG',optimize=True)
 payload={'path':str(out),'width':W,'height':H,'mode':im.mode,'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'logo_provided':bool(args.logo),'logo_sha256':hashlib.sha256(pathlib.Path(args.logo).read_bytes()).hexdigest() if args.logo else None,'font_files':{k:getattr(args,k) for k in ['inter_bold','inter_semibold','dm_regular','dm_medium']},'locked_stage_names':[s['title'] for s in stages], 'brief_sha256':hashlib.sha256(pathlib.Path(args.brief).read_bytes()).hexdigest() if args.brief else None,'status':'REVIEW_DRAFT' if args.review_draft else 'REQUIRES_VISUAL_AND_SOURCE_QA'}
 out.with_suffix('.json').write_text(json.dumps(payload,indent=2));print(json.dumps(payload,indent=2))
if __name__=='__main__':main()
