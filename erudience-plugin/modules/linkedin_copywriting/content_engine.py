"""Erudience offline content workflow. No implicit network or external writes."""
from __future__ import annotations
import argparse, hashlib, json, re
from datetime import date, timedelta
from pathlib import Path

CATEGORIES = {'buyer_pain','education','market_research','campaign','thought_leadership','case_study','trend','product_update'}
FORMATS = {'text','image','flowchart','carousel','document','campaign_poster','market_research_poster','trend_poster'}
PLATFORMS = {'linkedin','facebook','instagram','website'}
STAGES = ('RESEARCH','EVIDENCE','CONTENT','CREATIVE_BRIEF','PROMPT','BRAND','RENDER','QA','OWNER_APPROVAL','SOCIAL_OS')
REQUIRED = ('content_id','publish_date','platforms','topic','title','pillar','funnel_stage','primary_format','derivatives','keywords','buyer_pain','cta','sources','claims','copy','brand_id')

class GateError(ValueError): pass

def sha(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

def validate(item):
    missing=[k for k in REQUIRED if k not in item or item[k] in ('',None)]
    if missing: raise GateError('MISSING_FIELDS:'+','.join(missing))
    try: date.fromisoformat(item['publish_date'])
    except (ValueError,TypeError): raise GateError('INVALID_DATE')
    if not isinstance(item['platforms'],list) or not item['platforms'] or set(item['platforms'])-PLATFORMS: raise GateError('INVALID_PLATFORMS')
    if item['primary_format'] not in FORMATS: raise GateError('INVALID_FORMAT')
    if not isinstance(item['keywords'],list) or not isinstance(item['derivatives'],list): raise GateError('INVALID_LIST')
    if item['funnel_stage'] not in ('awareness','consideration','decision','retention'): raise GateError('INVALID_FUNNEL')
    if not isinstance(item['sources'],list) or not isinstance(item['claims'],list): raise GateError('INVALID_EVIDENCE')
    source_ids={s.get('source_id') for s in item['sources'] if isinstance(s,dict) and s.get('url') and s.get('retrieved_at')}
    for c in item['claims']:
        if not isinstance(c,dict) or not c.get('text') or not c.get('source_ids') or not set(c['source_ids']).issubset(source_ids):
            raise GateError('UNSUPPORTED_CLAIM')
    if not isinstance(item['copy'],str) or not item['copy'].strip(): raise GateError('EMPTY_COPY')
    return True

def route(item):
    cat=item.get('category','education')
    if cat not in CATEGORIES: raise GateError('UNKNOWN_CATEGORY')
    fmt=item['primary_format']
    if cat=='market_research' and fmt=='trend_poster' and not item['sources']: raise GateError('UNVERIFIED_MARKET_RESEARCH')
    if cat=='case_study' and not item.get('case_permission'): raise GateError('CASE_PERMISSION_REQUIRED')
    if cat=='trend' and not item['sources']: raise GateError('TREND_SOURCE_REQUIRED')
    return {'category':cat,'format':fmt,'controller_stages':list(STAGES)}

def gate(item, artifacts=None):
    artifacts=artifacts or {}
    try:
        validate(item); routing=route(item)
    except GateError as e:
        return {'content_id':item.get('content_id'),'decision':'REJECT','reason':str(e),'input_sha256':sha(item)}
    if not item['sources']:
        return {'content_id':item['content_id'],'decision':'NOT_VERIFIED','reason':'NO_RESEARCH_EVIDENCE','input_sha256':sha(item)}
    if not artifacts.get('brand_verified'):
        return {'content_id':item['content_id'],'decision':'BLOCKED','reason':'BRAND_NOT_VERIFIED','input_sha256':sha(item)}
    if not artifacts.get('creative_brief_hash') or not artifacts.get('prompt_hash'):
        return {'content_id':item['content_id'],'decision':'BLOCKED','reason':'CREATIVE_OR_PROMPT_MISSING','input_sha256':sha(item)}
    if not artifacts.get('visual_qa_pass'):
        return {'content_id':item['content_id'],'decision':'BLOCKED','reason':'VISUAL_QA_NOT_PASSED','input_sha256':sha(item)}
    return {'content_id':item['content_id'],'decision':'READY_FOR_OWNER_REVIEW','input_sha256':sha(item),'route':routing}

def calendar(items, start, days=30):
    first=date.fromisoformat(start)
    if not 1<=days<=366: raise GateError('INVALID_DAYS')
    by_date={}
    ids=set()
    for item in items:
        validate(item)
        if item['content_id'] in ids: raise GateError('DUPLICATE_CONTENT_ID')
        ids.add(item['content_id'])
        if not first<=date.fromisoformat(item['publish_date'])<first+timedelta(days=days): raise GateError('OUT_OF_WINDOW')
        by_date.setdefault(item['publish_date'],[]).append(item['content_id'])
    return [{'date':(first+timedelta(days=i)).isoformat(),'week':i//7+1,'content_ids':by_date.get((first+timedelta(days=i)).isoformat(),[])} for i in range(days)]

def weekly_batch(items, artifacts_by_id, expected=7):
    if len(items)!=expected: return {'decision':'REJECT','reason':'BATCH_COUNT_MISMATCH','expected':expected,'actual':len(items)}
    results=[gate(i,artifacts_by_id.get(i.get('content_id'),{})) for i in items]
    ready=sum(r['decision']=='READY_FOR_OWNER_REVIEW' for r in results)
    return {'decision':'READY_FOR_OWNER_REVIEW' if ready==expected else 'BLOCKED','ready':ready,'expected':expected,'results':results}

def validate_business_registry(registry):
    """Validate a business registry (module 01, AG-01) over SUPPLIED data only.

    registry = {'services': [...], 'claims': [...], 'boundaries': [...]}.
    Each service needs a non-empty name and description; each claim needs
    non-empty text, source_url and verified_at; no service/claim may fall
    outside the declared boundaries (checked only when the item declares
    a 'boundary'). Never invents services or claims. Returns sorted
    unique error codes (empty list = valid).
    """
    errors = []
    if not isinstance(registry, dict):
        return ['INVALID_REGISTRY']
    boundaries = registry.get('boundaries') or []
    if not isinstance(boundaries, list):
        boundaries = []
    for s in registry.get('services') or []:
        if not isinstance(s, dict):
            errors.append('INVALID_SERVICE')
            continue
        if not isinstance(s.get('name'), str) or not s['name'].strip():
            errors.append('SERVICE_NAME_REQUIRED')
        if not isinstance(s.get('description'), str) or not s['description'].strip():
            errors.append('SERVICE_DESCRIPTION_REQUIRED')
        boundary = s.get('boundary')
        if boundary is not None and boundaries and boundary not in boundaries:
            errors.append('SERVICE_OUTSIDE_BOUNDARY')
    for c in registry.get('claims') or []:
        if not isinstance(c, dict):
            errors.append('INVALID_CLAIM')
            continue
        if not isinstance(c.get('text'), str) or not c['text'].strip():
            errors.append('CLAIM_TEXT_REQUIRED')
        if not isinstance(c.get('source_url'), str) or not c['source_url'].strip():
            errors.append('CLAIM_SOURCE_REQUIRED')
        if not isinstance(c.get('verified_at'), str) or not c['verified_at'].strip():
            errors.append('CLAIM_VERIFIED_AT_REQUIRED')
        boundary = c.get('boundary')
        if boundary is not None and boundaries and boundary not in boundaries:
            errors.append('CLAIM_OUTSIDE_BOUNDARY')
    return sorted(set(errors))

def validate_buyer_evidence(evidence):
    """Validate buyer research evidence (module 03, AG-03) over SUPPLIED data.

    Each evidence item needs non-empty buyer_pain, job_to_be_done,
    objection and decision_criterion strings plus a source_url.
    Returns sorted unique error codes (empty list = valid).
    """
    if not isinstance(evidence, list):
        return ['INVALID_EVIDENCE']
    fields = (('buyer_pain', 'BUYER_PAIN_REQUIRED'),
              ('job_to_be_done', 'JOB_TO_BE_DONE_REQUIRED'),
              ('objection', 'OBJECTION_REQUIRED'),
              ('decision_criterion', 'DECISION_CRITERION_REQUIRED'),
              ('source_url', 'BUYER_SOURCE_REQUIRED'))
    errors = []
    for item in evidence:
        if not isinstance(item, dict):
            errors.append('INVALID_EVIDENCE_ITEM')
            continue
        for key, code in fields:
            if not isinstance(item.get(key), str) or not item[key].strip():
                errors.append(code)
    return sorted(set(errors))

FUNNEL_STAGES = ('awareness', 'consideration', 'decision', 'retention')
# CTA mapping per funnel stage (from the existing funnel_stage usage in
# this module and the strategy docs). cta_type values:
#   educational   - learn/read/guide, no pitch, destination 'none' or an
#                   educational page
#   comparison    - compare options / see how it stacks up
#   consultation  - book a call to discuss fit
#   service       - direct service offer / book / buy
#   demo          - see the product or service demonstrated
#   support       - help / onboarding for existing customers
#   referral      - invite / refer another business
CTA_BY_STAGE = {
    'awareness': {'educational'},
    'consideration': {'educational', 'comparison', 'consultation'},
    'decision': {'service', 'consultation', 'demo'},
    'retention': {'service', 'support', 'referral', 'educational'},
}

def _infer_cta_type(item):
    """Infer cta_type from an explicit field, else from cta_destination."""
    cta_type = item.get('cta_type')
    if isinstance(cta_type, str) and cta_type.strip():
        return cta_type.strip()
    dest = item.get('cta_destination')
    if not isinstance(dest, str) or not dest.strip() or dest.strip() == 'none':
        return 'educational'
    url = dest.strip().casefold()
    if any(k in url for k in ('/support', '/help', '/onboard')):
        return 'support'
    if any(k in url for k in ('/services', '/service', '/book', '/contact', '/demo', '/pricing', '/buy', '/checkout')):
        return 'service'
    return 'educational'

def plan_funnel(items):
    """Plan/validate a funnel allocation (module 07, AG-09).

    Each item needs funnel_stage in FUNNEL_STAGES plus a non-empty cta
    and cta_destination (a URL or 'none'). The CTA type (explicit
    'cta_type', else inferred from cta_destination) must be allowed for
    the item's stage per CTA_BY_STAGE. Returns
    {'status': 'PASS'|'BLOCKED', 'errors': [...],
     'allocation': {stage: count}}.
    """
    errors = []
    allocation = {stage: 0 for stage in FUNNEL_STAGES}
    if not isinstance(items, list):
        return {'status': 'BLOCKED', 'errors': ['INVALID_FUNNEL_ITEMS'], 'allocation': allocation}
    for item in items:
        if not isinstance(item, dict):
            errors.append('INVALID_FUNNEL_ITEM')
            continue
        stage = item.get('funnel_stage')
        if stage not in FUNNEL_STAGES:
            errors.append('INVALID_FUNNEL_STAGE')
            continue
        allocation[stage] += 1
        if not isinstance(item.get('cta'), str) or not item['cta'].strip():
            errors.append('CTA_REQUIRED')
        if not isinstance(item.get('cta_destination'), str) or not item['cta_destination'].strip():
            errors.append('CTA_DESTINATION_REQUIRED')
            continue
        cta_type = _infer_cta_type(item)
        if cta_type not in CTA_BY_STAGE[stage]:
            errors.append('CTA_STAGE_MISMATCH')
    return {'status': 'PASS' if not errors else 'BLOCKED',
            'errors': sorted(set(errors)), 'allocation': allocation}

def lock_content(content):
    """Lock content (module 08, AG-10): validate and return a locked record.

    Returns {'content_id', 'topic', 'caption', 'keywords', 'poster_text',
    'content_hash'} where content_hash is the SHA-256 of the canonical
    JSON of caption + keywords + poster_text. Raises GateError on
    missing/invalid fields. A changed caption, keyword or poster line
    changes the hash, so a later mismatch is detectable.
    """
    if not isinstance(content, dict):
        raise GateError('INVALID_CONTENT')
    for key in ('content_id', 'topic', 'caption'):
        if not isinstance(content.get(key), str) or not content[key].strip():
            raise GateError('LOCK_MISSING:' + key)
    keywords = content.get('keywords')
    if not isinstance(keywords, list) or not keywords or not all(isinstance(k, str) and k.strip() for k in keywords):
        raise GateError('LOCK_INVALID_KEYWORDS')
    poster_text = content.get('poster_text')
    if not isinstance(poster_text, dict):
        raise GateError('LOCK_INVALID_POSTER_TEXT')
    for key in ('headline', 'footer'):
        if not isinstance(poster_text.get(key), str) or not poster_text[key].strip():
            raise GateError('LOCK_MISSING_POSTER:' + key)
    locked = {'content_id': content['content_id'], 'topic': content['topic'],
              'caption': content['caption'], 'keywords': list(keywords),
              'poster_text': dict(poster_text)}
    locked['content_hash'] = sha({'caption': locked['caption'],
                                  'keywords': locked['keywords'],
                                  'poster_text': locked['poster_text']})
    return locked

def main():
    p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--artifacts');p.add_argument('--mode',choices=['gate','calendar','weekly'],default='gate');p.add_argument('--start');p.add_argument('--days',type=int,default=30);p.add_argument('--expected',type=int,default=7)
    a=p.parse_args(); obj=json.loads(Path(a.input).read_text()); artifacts=json.loads(Path(a.artifacts).read_text()) if a.artifacts else {}
    if a.mode=='gate': result=gate(obj,artifacts)
    elif a.mode=='calendar': result=calendar(obj,a.start,a.days)
    else: result=weekly_batch(obj,artifacts,a.expected)
    print(json.dumps(result,indent=2,ensure_ascii=False))
if __name__=='__main__': main()
