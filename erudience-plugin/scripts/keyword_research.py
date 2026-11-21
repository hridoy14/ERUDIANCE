"""Deterministic keyword mapping, not search-volume estimation."""
import re
TYPES={'primary','secondary','semantic','long_tail','problem','question','informational','commercial','transactional','branded','competitor','industry','geographic','entity','negative'}
INTENTS={'informational','commercial','transactional','navigational'}
def normalize(term):
    return ' '.join(str(term).casefold().split())
def validate_cluster(cluster):
    errors=[]
    if not isinstance(cluster,dict):return ['INVALID_CLUSTER']
    items=cluster.get('keywords',[])
    if not isinstance(items,list) or not items:return ['KEYWORDS_REQUIRED']
    seen=set();primary=0
    for k in items:
        if not isinstance(k,dict):errors.append('INVALID_KEYWORD');continue
        term=normalize(k.get('term',''));kind=k.get('type');intent=k.get('intent')
        if not term or len(term)>150:errors.append('INVALID_TERM')
        if kind not in TYPES:errors.append('INVALID_TYPE')
        if intent not in INTENTS:errors.append('INVALID_INTENT')
        if term in seen:errors.append('DUPLICATE_KEYWORD')
        seen.add(term);primary+=kind=='primary'
        if k.get('volume') is not None and not k.get('volume_source'):errors.append('UNSOURCED_VOLUME')
    if primary!=1:errors.append('EXACTLY_ONE_PRIMARY')
    return sorted(set(errors))
def map_content(content,cluster):
    errors=validate_cluster(cluster)
    if errors:return {'status':'BLOCKED','errors':errors}
    primary=next(k['term'] for k in cluster['keywords'] if k['type']=='primary')
    text=' '.join([content.get('hook',''),content.get('body','')]).casefold()
    if normalize(primary) not in normalize(text):errors.append('PRIMARY_KEYWORD_NOT_IN_COPY')
    return {'status':'PASS' if not errors else 'REVIEW','errors':errors,'primary':primary,'intent':cluster.get('buyer_intent','unverified')}
