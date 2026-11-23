#!/usr/bin/env python3
"""Deterministic structural gate for Erudience creative brief/prompt handoff.
This does not substitute for factual, brand, human or visual review.
"""
import argparse, hashlib, json, sys
from pathlib import Path

def sha(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()

def validate(brief, prompt):
    errors=[]
    for k in ('content_id','source_sha256','audience','buyer_problem','core_message','funnel_stage','visual_concept','layout','headline','cta','exact_copy','evidence_refs','asset_requirements'):
        if not brief.get(k): errors.append('BRIEF_MISSING:'+k)
    if not isinstance(brief.get('exact_copy'),list) or not all(isinstance(t,str) and t.strip() for t in brief.get('exact_copy',[])):
        errors.append('BRIEF_INVALID_EXACT_COPY')
    if not isinstance(brief.get('evidence_refs'),list): errors.append('BRIEF_INVALID_EVIDENCE')
    if prompt.get('content_id') != brief.get('content_id'): errors.append('CONTENT_ID_MISMATCH')
    if prompt.get('brief_sha256') != sha(brief): errors.append('BRIEF_HASH_MISMATCH')
    spec=prompt.get('render_spec',{})
    if spec.get('exact_copy') != brief.get('exact_copy'): errors.append('COPY_MISMATCH')
    if spec.get('dimensions') != [1080,1350]: errors.append('DIMENSIONS_MISMATCH')
    # Owner decision 2026-11-24 (C3): the logo is OPTIONAL. Verification
    # is required only when a logo is actually planned for this poster;
    # when logo_planned is False the absence is legitimate, not an error.
    # The default (flag absent) preserves the old strict behaviour for
    # every existing caller and test.
    if spec.get('logo_planned', True) and not spec.get('logo_sha256'): errors.append('LOGO_BINARY_NOT_VERIFIED')
    if not spec.get('font_files_verified'): errors.append('FONT_BINARY_NOT_VERIFIED')
    if not prompt.get('image_prompt'): errors.append('MISSING_IMAGE_PROMPT')
    if not prompt.get('negative_prompt'): errors.append('MISSING_NEGATIVE_PROMPT')
    return errors

def build_brief(content, brand, template_id, positioning, funnel_stage):
    """Build a creative brief from locked content (module 09, AG-14).

    content is a locked content record (see content_engine.lock_content)
    with content_id/topic/caption/keywords/poster_text/content_hash.
    Returns {'poster_text', 'brand', 'template_id', 'positioning',
    'funnel_stage', 'content_hash'} plus the full 'brief', the matching
    'prompt', and 'validation_errors' from the existing structural gate
    validate(brief, prompt). Validation errors are REPORTED, not hidden:
    in fixture mode the only expected errors are LOGO_BINARY_NOT_VERIFIED
    and FONT_BINARY_NOT_VERIFIED (no real font/logo binaries are supplied
    by a fixture); the caller decides whether errors block (live mode
    must block on any error).
    """
    poster_text = content.get('poster_text') or {}
    headline = poster_text.get('headline', '')
    steps = poster_text.get('steps') or []
    exact_copy = [headline] + [str(s) for s in steps] + [poster_text.get('footer', '')]
    exact_copy = [line for line in exact_copy if isinstance(line, str) and line.strip()]
    brief = {
        'content_id': content.get('content_id'),
        'source_sha256': content.get('content_hash', ''),
        'audience': content.get('audience', 'Small business owners adopting AI automation'),
        'buyer_problem': content.get('buyer_pain') or ('Manual work around ' + str(content.get('topic', ''))),
        'core_message': content.get('caption', ''),
        'funnel_stage': funnel_stage,
        'visual_concept': 'Portrait workflow poster: headline first, numbered steps second, footer last.',
        'layout': 'Portrait 1080x1350, headline top, steps centre, footer bottom.',
        'headline': headline,
        'cta': content.get('cta', 'Read checklist'),
        'exact_copy': exact_copy,
        'evidence_refs': list(content.get('evidence_refs') or []),
        'asset_requirements': {'logo': 'approved-only', 'fonts': ['Sora']},
    }
    prompt = {
        'content_id': brief['content_id'],
        'brief_sha256': sha(brief),
        'render_spec': {'exact_copy': brief['exact_copy'], 'dimensions': [1080, 1350],
                        'logo_sha256': content.get('logo_sha256'),
                        'logo_planned': content.get('logo_planned', True),
                        'font_files_verified': bool(content.get('font_files_verified'))},
        'image_prompt': 'Erudience LinkedIn poster for: ' + headline,
        'negative_prompt': 'No invented claims, no generated logos, no text beyond the exact copy.',
    }
    errors = validate(brief, prompt)
    return {'poster_text': poster_text, 'brand': brand, 'template_id': template_id,
            'positioning': positioning, 'funnel_stage': funnel_stage,
            'content_hash': content.get('content_hash', ''),
            'brief': brief, 'prompt': prompt, 'validation_errors': errors}

def plan_image(content, brief):
    """Build the image plan (module 10, AG-15) from locked content + brief.

    Returns {'dimensions': [1080, 1350], 'poster_text', 'template_id',
    'positioning', 'funnel_stage', 'content_hash', 'design_rationale',
    'negative_constraints'}.
    """
    poster_text = content.get('poster_text') or brief.get('poster_text') or {}
    template_id = brief.get('template_id')
    positioning = brief.get('positioning')
    funnel_stage = brief.get('funnel_stage')
    return {'dimensions': [1080, 1350], 'poster_text': poster_text,
            'template_id': template_id, 'positioning': positioning,
            'funnel_stage': funnel_stage,
            'content_hash': content.get('content_hash', '') or brief.get('content_hash', ''),
            'design_rationale': ('Template ' + str(template_id) + ' positions ' + str(positioning)
                                 + ' for ' + str(funnel_stage) + ' readers: headline first, '
                                 'numbered steps second, footer last.'),
            'negative_constraints': ['no invented claims', 'no generated logos',
                                     'no text beyond exact copy',
                                     'no extra services beyond the brief']}

def main():
    p=argparse.ArgumentParser();p.add_argument('brief');p.add_argument('prompt');p.add_argument('--output');a=p.parse_args()
    brief=json.loads(Path(a.brief).read_text());prompt=json.loads(Path(a.prompt).read_text())
    errs=validate(brief,prompt);out={'status':'REJECT' if errs else 'STRUCTURAL_PASS_ONLY','brief_sha256':sha(brief),'errors':errs,'note':'Structural PASS is not content, visual, factual, brand or owner approval.'}
    if a.output: Path(a.output).write_text(json.dumps(out,indent=2))
    print(json.dumps(out,indent=2));return 1 if errs else 0
if __name__=='__main__':sys.exit(main())
