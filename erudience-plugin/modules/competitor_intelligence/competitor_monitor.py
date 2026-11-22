"""Read-only competitor coverage auditor. No scraping or implicit network calls."""
from datetime import date
TARGET={'direct':15,'niche_specialists':10,'platforms':10,'content_benchmarks':10,'emerging':5}
def audit(records):
    errors=[];counts={k:0 for k in TARGET};seen=set()
    for r in records:
        if not isinstance(r,dict):errors.append('INVALID_RECORD');continue
        name=str(r.get('name','')).strip().casefold();group=r.get('group')
        if not name or not r.get('source_url') or not r.get('retrieved_at'):errors.append('MISSING_PROVENANCE')
        try: date.fromisoformat(str(r.get('retrieved_at','')))
        except ValueError:errors.append('INVALID_RETRIEVAL_DATE')
        if name in seen:errors.append('DUPLICATE_COMPETITOR')
        seen.add(name)
        if group not in TARGET:errors.append('UNKNOWN_GROUP')
        else:counts[group]+=1
    gaps={k:max(0,TARGET[k]-counts[k]) for k in TARGET}
    return {'status':'COMPLETE' if not errors and not any(gaps.values()) else 'INCOMPLETE','counts':counts,'gaps':gaps,'errors':sorted(set(errors)),'verified_total':len(seen) if not errors else None}
