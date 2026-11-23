"""Editorial checks only; no claims about LinkedIn ranking algorithms."""
from keyword_research import validate_cluster,normalize

def review(post,cluster):
    errors=validate_cluster(cluster)
    if errors:return {'status':'BLOCKED','errors':errors}
    primary=next(x['term'] for x in cluster['keywords'] if x['type']=='primary')
    hook=post.get('hook','');body=post.get('body','');cta=post.get('cta','')
    if not hook.strip() or not body.strip() or not cta.strip():errors.append('INCOMPLETE_POST')
    if normalize(primary) not in normalize(hook+' '+body):errors.append('PRIMARY_KEYWORD_MISSING')
    words=len((hook+' '+body).split())
    if words and (hook+' '+body).casefold().count(primary.casefold())>max(3,words//60+1):errors.append('POSSIBLE_KEYWORD_STUFFING')
    if post.get('funnel_stage') not in {'awareness','consideration','decision','retention'}:errors.append('INVALID_FUNNEL')
    if post.get('claims') and not post.get('evidence_verified'):errors.append('CLAIMS_NOT_VERIFIED')
    return {'status':'PASS' if not errors else 'REVIEW_REQUIRED','errors':sorted(set(errors)),'note':'Editorial checks do not establish search rank or engagement.'}
