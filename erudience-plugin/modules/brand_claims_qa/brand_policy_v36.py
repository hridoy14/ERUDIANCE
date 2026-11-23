"""Deterministic editorial brand checks; does not replace visual inspection or authenticate asset provenance."""
import json,re
from pathlib import Path
ALLOWED_HASHTAGS={'#AIAutomation','#WorkflowAutomation','#VoiceAI'}
BANNED=('revolutionise','unlock','leverage','seamless','cutting-edge','game-changing','supercharge')
PALETTE={'paper':'#F6F1E9','ink':'#14120E','soft':'#615B4C','emerald':'#10B77F','deep':'#0C8D62','dark':'#080C0B','taupe':'#B7B0A0','emerald_light':'#36D399','mint':'#8AE5C4','border':'#21312C','background':'#080C0B','card':'#0F1A16','foreground':'#F9FBFA'}
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
def _canonical_policy():
    cfg=Path(__file__).resolve().parent.parent.parent/'config'/'production-policy-v33.json'
    try:return json.loads(cfg.read_text(encoding='utf-8'))
    except Exception:return None
def check_canonical_brand(spec):
    """Canonical brand check (D-03/D-11). Expected font/palette/logo values are
    read from config/production-policy-v33.json at call time, never hardcoded
    here. Website-verified 2026-11-24 (Sora-only, emerald #10B77F); the logo
    rule is unchanged — logo optional-vs-required (C3) still awaits an
    explicit owner decision. spec =
    {'brand': {'heading','body'}, 'palette': {'emerald',...},
    'logo_asset': path|None, 'footer': str}. Returns sorted unique error codes."""
    policy=_canonical_policy()
    if not policy:return ['CANONICAL_POLICY_UNAVAILABLE']
    brand=policy.get('brand',{})
    palette_c=brand.get('palette',{})
    approved_logo=policy.get('brand_assets',{}).get('approved_logo_path')
    errors=[]
    spec_brand=spec.get('brand') if isinstance(spec,dict) else None
    if not isinstance(spec_brand,dict) or spec_brand.get('heading')!=brand.get('heading') or spec_brand.get('body')!=brand.get('body'):
        errors.append('BRAND_FONT_MISMATCH')
    spec_palette=spec.get('palette') if isinstance(spec,dict) else None
    if not isinstance(spec_palette,dict) or spec_palette.get('emerald')!=palette_c.get('emerald'):
        errors.append('BRAND_PALETTE_MISMATCH')
    footer=spec.get('footer') if isinstance(spec,dict) else None
    if footer is None and isinstance(spec_brand,dict):footer=spec_brand.get('footer')
    if not isinstance(footer,str) or 'erudience.com' not in footer:
        errors.append('BRAND_FOOTER_MISSING')
    logo_asset=spec.get('logo_asset') if isinstance(spec,dict) else None
    if logo_asset is not None and str(logo_asset)!=str(approved_logo):
        errors.append('UNAPPROVED_LOGO')
    return sorted(set(errors))
