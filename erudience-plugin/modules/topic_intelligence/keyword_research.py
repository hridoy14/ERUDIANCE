"""Deterministic keyword mapping, not search-volume estimation."""
import datetime
import json
import re
from datetime import date
from pathlib import Path
TOPIC_STATUSES_DEFAULT = ('READY', 'ENRICH', 'RESEARCH_NEEDED', 'HOLD')
def _topic_statuses():
    """Topic statuses from the policy JSON (read at runtime, with the
    policy's own list as fallback)."""
    try:
        policy = json.loads((Path(__file__).resolve().parents[2] / 'config' / 'production-policy-v33.json').read_text(encoding='utf-8'))
        statuses = policy.get('topic_statuses')
        if isinstance(statuses, list) and statuses:
            return tuple(statuses)
    except Exception:
        pass
    return TOPIC_STATUSES_DEFAULT
def _utcnow():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()
def _load_topic_store(store_path):
    path = Path(store_path)
    if not path.is_file():
        return {'topics': {}}
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return {'topics': {}}
    if not isinstance(data, dict) or not isinstance(data.get('topics'), dict):
        return {'topics': {}}
    return data
def _save_topic_store(store_path, data):
    path = Path(store_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
def _topic_key(topic):
    if isinstance(topic, dict):
        return str(topic.get('topic', '')).strip()
    return str(topic).strip()
def register_topic(store_path, topic):
    """Register a topic in the JSON-file-backed topic registry.

    topic is a string or a dict {'topic': ..., 'status': ...}. New topics
    start at RESEARCH_NEEDED unless a valid status is supplied.
    Re-registering an existing topic returns its stored record unchanged
    (status is only changed via set_topic_status). The store file lives
    under the caller-supplied state dir, never in the repo.
    Returns the stored topic record dict.
    """
    key = _topic_key(topic)
    if not key:
        raise ValueError('TOPIC_REQUIRED')
    statuses = _topic_statuses()
    status = 'RESEARCH_NEEDED'
    if isinstance(topic, dict) and topic.get('status') is not None:
        if topic['status'] not in statuses:
            raise ValueError('INVALID_TOPIC_STATUS')
        status = topic['status']
    data = _load_topic_store(store_path)
    if key in data['topics']:
        return dict(data['topics'][key])
    now = _utcnow()
    record = {'topic': key, 'status': status, 'registered_at': now, 'updated_at': now}
    data['topics'][key] = record
    _save_topic_store(store_path, data)
    return dict(record)
def get_topic(store_path, topic):
    """Return the stored record for a topic, or None if not registered."""
    data = _load_topic_store(store_path)
    record = data['topics'].get(_topic_key(topic))
    return dict(record) if record is not None else None
def set_topic_status(store_path, topic, status):
    """Set a registered topic's status (READY/ENRICH/RESEARCH_NEEDED/HOLD
    per policy). Registers the topic first if it is not yet known.
    Raises ValueError on an invalid status. Returns the updated record.
    """
    if status not in _topic_statuses():
        raise ValueError('INVALID_TOPIC_STATUS')
    key = _topic_key(topic)
    if not key:
        raise ValueError('TOPIC_REQUIRED')
    data = _load_topic_store(store_path)
    record = data['topics'].get(key)
    if record is None:
        record = register_topic(store_path, key)
        data = _load_topic_store(store_path)
        record = data['topics'][key]
    record['status'] = status
    record['updated_at'] = _utcnow()
    data['topics'][key] = record
    _save_topic_store(store_path, data)
    return dict(record)
def check_topic_preserved(store_path, topics):
    """Errors if a registered topic was deleted from the supplied list.

    topic_delete_allowed is false in the policy, so any registered topic
    missing from `topics` is an error: 'TOPIC_DELETED:<topic>'.
    Returns a sorted list (empty = all preserved).
    """
    data = _load_topic_store(store_path)
    wanted = set()
    for topic in topics or []:
        key = _topic_key(topic)
        if key:
            wanted.add(key)
    return sorted('TOPIC_DELETED:' + key for key in data['topics'] if key not in wanted)
def _parse_verified_date(value):
    """Parse a verified_at value to a date, or None if unparseable.

    Accepts 'YYYY-MM-DD' and ISO datetimes. 'fixture-only' and anything
    else unparseable return None (never treated as fresh).
    """
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        pass
    try:
        return datetime.datetime.fromisoformat(text).date()
    except ValueError:
        return None
def assess_source_freshness(sources, max_age_days=7, today=None):
    """Measure each source's verified_at age in days vs today (capability:
    freshness_control).

    Dates are compared as calendar dates. The policy timezone is
    Asia/Dhaka; `today` defaults to the current UTC date, so a UTC date
    taken near midnight can differ from the Dhaka calendar date by one
    day -- pass `today` explicitly (a date or ISO string) when the
    caller's local date matters. A source with no parseable verified_at
    is NOT_VERIFIED, never claimed fresh.
    Returns {'status': 'FRESH'|'STALE'|'NOT_VERIFIED', 'sources': [...],
    'fresh_count', 'stale_count', 'unverified_count', 'max_age_days',
    'today', 'timezone_note'}; each per-source entry is {'url',
    'verified_at', 'age_days', 'fresh', 'stale', 'label'}.
    """
    if today is None:
        ref = datetime.datetime.now(datetime.timezone.utc).date()
    elif isinstance(today, datetime.datetime):
        ref = today.date()
    elif isinstance(today, date):
        ref = today
    else:
        ref = _parse_verified_date(str(today)) or datetime.datetime.now(datetime.timezone.utc).date()
    per_source = []
    fresh_count = stale_count = unverified_count = 0
    for source in sources or []:
        if not isinstance(source, dict):
            per_source.append({'url': None, 'verified_at': None, 'age_days': None,
                               'fresh': False, 'stale': False, 'label': 'NOT_VERIFIED'})
            unverified_count += 1
            continue
        verified = _parse_verified_date(source.get('verified_at'))
        if verified is None:
            per_source.append({'url': source.get('url'), 'verified_at': source.get('verified_at'),
                               'age_days': None, 'fresh': False, 'stale': False,
                               'label': 'NOT_VERIFIED'})
            unverified_count += 1
            continue
        age = (ref - verified).days
        fresh = age <= max_age_days
        if fresh:
            fresh_count += 1
        else:
            stale_count += 1
        per_source.append({'url': source.get('url'), 'verified_at': source.get('verified_at'),
                           'age_days': age, 'fresh': fresh, 'stale': not fresh,
                           'label': 'FRESH' if fresh else 'STALE'})
    if unverified_count:
        status = 'NOT_VERIFIED'
    elif stale_count:
        status = 'STALE'
    else:
        status = 'FRESH'
    return {'status': status, 'sources': per_source, 'fresh_count': fresh_count,
            'stale_count': stale_count, 'unverified_count': unverified_count,
            'max_age_days': max_age_days, 'today': ref.isoformat(),
            'timezone_note': 'Calendar-date comparison; policy timezone is Asia/Dhaka, today defaults to the UTC date.'}
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
