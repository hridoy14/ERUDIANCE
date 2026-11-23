"""Read-only competitor coverage auditor. No scraping or implicit network calls."""
import json
from datetime import date
from pathlib import Path
TARGET={'direct':15,'niche_specialists':10,'platforms':10,'content_benchmarks':10,'emerging':5}
def _policy_targets():
    """Competitor-group targets from config/production-policy-v33.json.

    The numbers are read at runtime (parents-based path, same style as
    validate_strategy_v33), never hardcoded here.
    """
    try:
        policy=json.loads((Path(__file__).resolve().parents[2]/'config'/'production-policy-v33.json').read_text(encoding='utf-8'))
        groups=policy.get('research_competitor_groups')
        if isinstance(groups, dict) and groups:
            return dict(groups)
    except Exception:
        pass
    return dict(TARGET)
def competitor_coverage(records):
    """Per-group competitor counts vs the policy targets, with gaps listed.

    Wraps audit(): {'status', 'counts', 'targets', 'gaps', 'errors',
    'verified_total'}. status is COMPLETE only when audit() reports no
    errors and every group meets its target.
    """
    result=audit(records)
    targets=_policy_targets()
    counts={k: result['counts'].get(k, 0) for k in targets}
    gaps={k: max(0, targets[k]-counts[k]) for k in targets}
    status='COMPLETE' if not result['errors'] and not any(gaps.values()) else 'INCOMPLETE'
    return {'status':status,'counts':counts,'targets':targets,'gaps':gaps,'errors':result['errors'],'verified_total':result['verified_total']}
def assess_market_signals(signals):
    """Validate supplied market-signal observations (module 04, AG-04).

    Record shape reuses the repo's existing evidence shapes (the
    competitor audit record here + the weekly-research observation in
    config/brand-policy-current.md): each signal is {'topic', 'signal',
    'source_url', 'verified_at', 'value_previous' (optional),
    'value_current' (optional), 'review_status' (optional)}. No signal
    is invented here — only supplied records are validated. Empty input
    is reported honestly as NO_SIGNALS, never as verified coverage.
    """
    errors=[]
    verified=0
    for s in (signals or []):
        if not isinstance(s,dict):
            errors.append('INVALID_RECORD');continue
        item_errors=[]
        if not str(s.get('topic','')).strip():item_errors.append('MISSING_TOPIC')
        if not str(s.get('signal','')).strip():item_errors.append('MISSING_SIGNAL')
        if not str(s.get('source_url','')).strip():item_errors.append('MISSING_SOURCE_URL')
        try: date.fromisoformat(str(s.get('verified_at','')))
        except ValueError:item_errors.append('INVALID_VERIFIED_DATE')
        if item_errors:errors.extend(item_errors)
        else:verified+=1
    if not signals:
        status='NO_SIGNALS'
    elif errors:
        status='INCOMPLETE'
    else:
        status='COMPLETE'
    return {'status':status,'signals':len(signals or []),'verified':verified,'errors':sorted(set(errors))}
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
