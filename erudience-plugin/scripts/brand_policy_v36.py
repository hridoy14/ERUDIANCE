"""Deterministic editorial brand checks; does not replace visual inspection or authenticate asset provenance."""
import re
ALLOWED_HASHTAGS={'#AIAutomation','#WorkflowAutomation','#VoiceAI'}
BANNED=('revolutionise','unlock','leverage','seamless','cutting-edge','game-changing','supercharge')
PALETTE={'paper':'#F6F1E9','ink':'#14120E','soft':'#615B4C','emerald':'#10B981','deep':'#0A6E3E','dark':'#0A100E'}
def check_caption(caption, *, audience='', workflow='', handoff='', cta=''):
    errors=[]
    if not isinstance(caption,str) or not caption.strip(): return ['CAPTION_REQUIRED']
    hashtags=re.findall(r'(?<!\w)#[A-Za-z0-9_]+',caption)
    if not 2<=len(hashtags)<=3 or any(h not in ALLOWED_HASHTAGS for h in hashtags):errors.append('HASHTAG_POLICY')
    if any(re.search(r'\b'+re.escape(w)+r'\b',caption,re.I) for w in BANNED):errors.append('BANNED_BRAND_LANGUAGE')
    for k,v in [('AUDIENCE',audience),('WORKFLOW',workflow),('HANDOFF',handoff),('CTA',cta)]:
        if not isinstance(v,str) or not v.strip():errors.append('MISSING_'+k+'_REVIEW')
    return errors
def check_poster_spec(spec):
    errors=[]
    if spec.get('font_family')!='Sora':errors.append('SOCIAL_FONT_NOT_SORA')
    if spec.get('dimensions')!=[1080,1350]:errors.append('INVALID_DIMENSIONS')
    if spec.get('palette')!=PALETTE:errors.append('PALETTE_MISMATCH')
    if not spec.get('authentic_logo_sha256'):errors.append('LOGO_NOT_AUTHENTICATED')
    if not spec.get('logo_source_commit'):errors.append('LOGO_SOURCE_NOT_PINNED')
    if len(str(spec.get('headline','')).split())>12:errors.append('HEADLINE_TOO_LONG')
    if not spec.get('visual_inspection_receipt'):errors.append('VISUAL_INSPECTION_REQUIRED')
    if not spec.get('orchestrator_execution_id'):errors.append('ORCHESTRATOR_NOT_EXECUTED')
    return errors
