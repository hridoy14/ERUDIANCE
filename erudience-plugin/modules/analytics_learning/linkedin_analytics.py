"""Compute descriptive metrics from authorized, observed values only."""
def summarize(rows):
    errors=[];out=[]
    for r in rows:
        if not r.get('source') or not r.get('observed_at') or not r.get('content_id'):
            errors.append('MISSING_ANALYTICS_PROVENANCE');continue
        m={}
        for k in ('impressions','clicks','reactions','comments','reposts','saves','qualified_enquiries'):
            v=r.get(k)
            if v is not None:
                if isinstance(v,bool) or not isinstance(v,int) or v<0:errors.append('INVALID_METRIC');continue
                m[k]=v
        if 'clicks' in m and 'impressions' in m and m['clicks']>m['impressions']:errors.append('IMPOSSIBLE_CLICKS')
        ctr=round(m['clicks']/m['impressions']*100,2) if m.get('impressions',0)>0 and 'clicks' in m else None
        out.append({'content_id':r['content_id'],'observed':m,'ctr_pct':ctr,'attribution':'not_inferred'})
    return {'status':'PASS' if not errors else 'BLOCKED','errors':sorted(set(errors)),'records':out}
