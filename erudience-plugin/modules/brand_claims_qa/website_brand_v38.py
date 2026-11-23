"""Owner-approved website-first brand specification; optional logo, mandatory branding. Website-verified 2026-11-24: Sora only (Inter/DM Sans appear nowhere on the website), emerald #10B77F."""
import re
PALETTE={'paper':'#F6F1E9','ink':'#14120E','soft':'#615B4C','emerald':'#10B77F','deep':'#0C8D62','dark':'#080C0B','taupe':'#B7B0A0','emerald_light':'#36D399','mint':'#8AE5C4','border':'#21312C','background':'#080C0B','card':'#0F1A16','foreground':'#F9FBFA'}
HASHTAGS={'#AIAutomation','#WorkflowAutomation','#VoiceAI'}
BANNED=('revolutionise','unlock','leverage','seamless','cutting-edge','game-changing','supercharge')
def check(spec):
 errors=[]
 if spec.get('heading_font')!='Sora' or spec.get('body_font')!='Sora':errors.append('WEBSITE_FONT_MISMATCH')
 if spec.get('palette')!=PALETTE:errors.append('PALETTE_MISMATCH')
 if spec.get('dimensions')!=[1080,1350]:errors.append('DIMENSIONS_MISMATCH')
 if spec.get('brand_name')!='Erudience' or spec.get('footer')!='erudience.com':errors.append('BRAND_IDENTITY_MISSING')
 if len(spec.get('headline','').split())>12 or not spec.get('headline','').strip():errors.append('HEADLINE_INVALID')
 if not spec.get('font_heading_sha256') or not spec.get('font_body_sha256'):errors.append('FONT_PROVENANCE_MISSING')
 if spec.get('logo') and (not spec.get('logo_sha256') or not spec.get('logo_source')):errors.append('LOGO_PROVENANCE_MISSING')
 if not spec.get('visual_inspection_receipt'):errors.append('VISUAL_INSPECTION_MISSING')
 return errors
def check_caption(caption):
 errors=[]
 if not isinstance(caption,str) or not caption.strip():return ['CAPTION_REQUIRED']
 tags=re.findall(r'(?<!\w)#[A-Za-z0-9_]+',caption)
 if not 2<=len(tags)<=3 or any(x not in HASHTAGS for x in tags):errors.append('HASHTAG_POLICY')
 if any(re.search(r'\b'+re.escape(x)+r'\b',caption,re.I) for x in BANNED):errors.append('BANNED_LANGUAGE')
 return errors
