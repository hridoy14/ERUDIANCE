"""Compute descriptive metrics from authorized, observed values only."""
import datetime
import json
from pathlib import Path
ALLOWED_METRIC_FIELDS = {'impressions', 'clicks', 'reactions', 'comments', 'reposts', 'saves', 'qualified_enquiries', 'ctr', 'source', 'observed_at'}
def _utcnow():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()
def _read_jsonl(store_path):
    path = Path(store_path)
    if not path.is_file():
        return []
    rows = []
    for line in path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows
def _append_jsonl(store_path, row):
    path = Path(store_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + '\n')
def record_outcome(store_path, content_id, metrics):
    """Record one observed outcome row (module 13, AG-18; feedback_loop).

    Appends a metrics row to a JSONL file under the caller-supplied
    state dir. Validation reuses summarize()'s rules: source and
    observed_at provenance are required (never defaulted/invented),
    metric counts must be non-negative ints, clicks may not exceed
    impressions; additionally ctr, when present, must be in [0, 1] and
    no field outside ALLOWED_METRIC_FIELDS is accepted. On failure
    nothing is appended. Returns {'status': 'PASS'|'BLOCKED', 'errors',
    'content_id', 'row'}.
    """
    if not isinstance(metrics, dict):
        return {'status': 'BLOCKED', 'errors': ['INVALID_METRICS']}
    errors = []
    unknown = sorted(set(metrics) - ALLOWED_METRIC_FIELDS)
    if unknown:
        errors.append('UNKNOWN_METRIC_FIELD')
    ctr = metrics.get('ctr')
    if ctr is not None and (isinstance(ctr, bool) or not isinstance(ctr, (int, float)) or not 0 <= ctr <= 1):
        errors.append('INVALID_CTR')
    row = {'content_id': content_id, 'source': metrics.get('source'), 'observed_at': metrics.get('observed_at')}
    for key in ('impressions', 'clicks', 'reactions', 'comments', 'reposts', 'saves', 'qualified_enquiries'):
        if metrics.get(key) is not None:
            row[key] = metrics[key]
    checked = summarize([row])
    errors.extend(checked['errors'])
    errors = sorted(set(errors))
    if errors:
        return {'status': 'BLOCKED', 'errors': errors}
    _append_jsonl(store_path, row)
    return {'status': 'PASS', 'content_id': content_id, 'row': row}
def feedback_summary(store_path):
    """Summarise all recorded outcomes (module 13, AG-18; feedback_loop).

    Runs summarize() over every recorded row and adds learning notes:
    top/bottom performers by CTR, computed only from recorded rows.
    No claims are invented: with no rows the notes say so.
    Returns summarize()'s result plus 'count', 'top_performer',
    'bottom_performer' and 'notes'.
    """
    rows = _read_jsonl(store_path)
    checked = summarize(rows)
    records = checked['records']
    scored = [r for r in records if r.get('ctr_pct') is not None]
    top = max(scored, key=lambda r: r['ctr_pct']) if scored else None
    bottom = min(scored, key=lambda r: r['ctr_pct']) if scored else None
    notes = []
    if not rows:
        notes.append('No recorded outcomes yet -- no learning claims made.')
    else:
        if top is not None:
            notes.append('Top performer by CTR: ' + str(top['content_id']) + ' (' + str(top['ctr_pct']) + '%).')
        if bottom is not None and bottom is not top:
            notes.append('Lowest performer by CTR: ' + str(bottom['content_id']) + ' (' + str(bottom['ctr_pct']) + '%).')
        notes.append(str(len(records)) + ' recorded outcome(s) summarised; only computed values reported.')
    return {'status': checked['status'], 'errors': checked['errors'], 'records': records,
            'count': len(records),
            'top_performer': top['content_id'] if top is not None else None,
            'bottom_performer': bottom['content_id'] if bottom is not None else None,
            'notes': notes}
def record_experiment(store_path, name, hypothesis, variant, result):
    """Record one experiment (capability: experimentation).

    One variable, like-for-like: name/hypothesis/variant are required
    non-empty strings and result must be a dict of measured values only
    (nothing is computed or invented here). Appends to a JSONL file
    under the caller-supplied state dir. Returns {'status', 'errors',
    'experiment'}.
    """
    errors = []
    for label, value in (('name', name), ('hypothesis', hypothesis), ('variant', variant)):
        if not isinstance(value, str) or not value.strip():
            errors.append('EXPERIMENT_' + label.upper() + '_REQUIRED')
    if not isinstance(result, dict):
        errors.append('EXPERIMENT_RESULT_REQUIRED')
    if errors:
        return {'status': 'BLOCKED', 'errors': sorted(set(errors))}
    record = {'name': name, 'hypothesis': hypothesis, 'variant': variant,
              'result': result, 'recorded_at': _utcnow()}
    _append_jsonl(store_path, record)
    return {'status': 'PASS', 'experiment': record}
def list_experiments(store_path):
    """Return all recorded experiments (empty list when none exist)."""
    return _read_jsonl(store_path)
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
