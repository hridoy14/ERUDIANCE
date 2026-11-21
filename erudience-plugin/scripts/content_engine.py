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

def main():
    p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--artifacts');p.add_argument('--mode',choices=['gate','calendar','weekly'],default='gate');p.add_argument('--start');p.add_argument('--days',type=int,default=30);p.add_argument('--expected',type=int,default=7)
    a=p.parse_args(); obj=json.loads(Path(a.input).read_text()); artifacts=json.loads(Path(a.artifacts).read_text()) if a.artifacts else {}
    if a.mode=='gate': result=gate(obj,artifacts)
    elif a.mode=='calendar': result=calendar(obj,a.start,a.days)
    else: result=weekly_batch(obj,artifacts,a.expected)
    print(json.dumps(result,indent=2,ensure_ascii=False))
if __name__=='__main__': main()
