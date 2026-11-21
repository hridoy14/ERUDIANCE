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
    if not spec.get('logo_sha256'): errors.append('LOGO_BINARY_NOT_VERIFIED')
    if not spec.get('font_files_verified'): errors.append('FONT_BINARY_NOT_VERIFIED')
    if not prompt.get('image_prompt'): errors.append('MISSING_IMAGE_PROMPT')
    if not prompt.get('negative_prompt'): errors.append('MISSING_NEGATIVE_PROMPT')
    return errors

def main():
    p=argparse.ArgumentParser();p.add_argument('brief');p.add_argument('prompt');p.add_argument('--output');a=p.parse_args()
    brief=json.loads(Path(a.brief).read_text());prompt=json.loads(Path(a.prompt).read_text())
    errs=validate(brief,prompt);out={'status':'REJECT' if errs else 'STRUCTURAL_PASS_ONLY','brief_sha256':sha(brief),'errors':errs,'note':'Structural PASS is not content, visual, factual, brand or owner approval.'}
    if a.output: Path(a.output).write_text(json.dumps(out,indent=2))
    print(json.dumps(out,indent=2));return 1 if errs else 0
if __name__=='__main__':sys.exit(main())
