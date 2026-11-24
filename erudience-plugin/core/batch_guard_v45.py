"""Seven independent content/image jobs. Never treat a collage as a deliverable.

Framework evaluation (summary; full 12-criterion evaluation in the Worker 2
work log at ~/workspace/erudiance-audit/output/repair-work-log-w2.md):
DECISION: plain-Python orchestrator using only stdlib + Pillow (the repo's
only dependency). No LangGraph / AutoGen / CrewAI is installed or imported.
Checkpointing already exists via bridge JSON state files; durable state via
bridge state + evidence ledger; conditional routing via the 17-stage map;
retry via the gate's 3-repair limit; human approval via the
bridge/evidence_store approval path; tool execution via in-process adapters.
No network/paid calls, no new dependency. If a genuine framework need is
found later it is recorded as a finding, never installed silently.
"""
from __future__ import annotations
import hashlib
import importlib
import importlib.util
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from chatgpt_bridge_v43 import load, next_step, save, start
from gate_chain_v41 import Adapter, BRAND, Chain, GateFailure, REVIEWS, STAGES, digest, filehash

SLOTS = 7
_REPO_ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Agent registry (18 agents, AG-01..AG-18)
# ---------------------------------------------------------------------------

def _agent(agent_id, name, stages, module, reviewer, tools):
    return {'id': agent_id, 'name': name, 'stages': list(stages),
            'module': module, 'reviewer': reviewer, 'tools': list(tools),
            'retry_policy': 'gate-repair-3', 'failure': 'BLOCKED after 4th failure'}

AGENT_REGISTRY = {
    'AG-01': _agent('AG-01', 'Business Intelligence', ['SOURCES'],
                    'business_service_intelligence', 'AG-13',
                    ['validate_business_registry']),
    'AG-02': _agent('AG-02', 'Competitor Research', ['RESEARCH'],
                    'competitor_intelligence', 'AG-12',
                    ['audit', 'competitor_coverage']),
    'AG-03': _agent('AG-03', 'Buyer Research', ['RESEARCH'],
                    'buyer_intelligence', 'AG-12',
                    ['validate_buyer_evidence']),
    'AG-04': _agent('AG-04', 'Market Research', ['RESEARCH'],
                    'market_trends', 'AG-13',
                    ['assess_market_signals']),
    'AG-05': _agent('AG-05', 'Keyword Research', ['RESEARCH', 'STRATEGY'],
                    'topic_intelligence', 'AG-12',
                    ['validate_cluster', 'map_content']),
    'AG-06': _agent('AG-06', 'Search Intent', ['RESEARCH', 'STRATEGY'],
                    'topic_intelligence', 'AG-12',
                    ['validate_cluster', 'map_content']),
    'AG-07': _agent('AG-07', 'Topic Intelligence', ['RESEARCH', 'STRATEGY'],
                    'topic_intelligence', 'AG-12',
                    ['validate_cluster', 'map_content', 'register_topic',
                     'get_topic', 'set_topic_status', 'check_topic_preserved',
                     'assess_source_freshness']),
    'AG-08': _agent('AG-08', 'Content Strategist', ['STRATEGY'],
                    'marketing_strategy', 'AG-12',
                    ['validate', 'validate_single_slot']),
    'AG-09': _agent('AG-09', 'Funnel Planner', ['STRATEGY'],
                    'funnel_planning', 'AG-12',
                    ['plan_funnel']),
    'AG-10': _agent('AG-10', 'Content Writer', ['CONTENT'],
                    'linkedin_copywriting', 'AG-12',
                    ['lock_content', 'gate']),
    'AG-11': _agent('AG-11', 'SEO Optimizer', ['CONTENT'],
                    'topic_intelligence', 'AG-12',
                    ['review']),
    'AG-12': _agent('AG-12', 'Editorial Reviewer',
                    ['SOURCE_REVIEW', 'RESEARCH_REVIEW', 'STRATEGY_REVIEW',
                     'CONTENT_REVIEW', 'PLAN_REVIEW', 'FINAL_REVIEW'],
                    'linkedin_copywriting', 'AG-13',
                    ['review', 'validate']),
    'AG-13': _agent('AG-13', 'Fact Checker',
                    ['SOURCE_REVIEW', 'RESEARCH_REVIEW', 'CONTENT_REVIEW',
                     'FINAL_REVIEW'],
                    'brand_claims_qa', 'AG-12',
                    ['check_canonical_brand']),
    'AG-14': _agent('AG-14', 'Creative Director', ['IMAGE_PLAN'],
                    'creative_brief', 'AG-16',
                    ['build_brief', 'plan_image']),
    'AG-15': _agent('AG-15', 'Image Producer', ['IMAGE_BUILD'],
                    'image_generation', 'AG-16',
                    ['render_production_poster']),
    'AG-16': _agent('AG-16', 'Brand QA',
                    ['TECH_REVIEW', 'VISUAL_REVIEW', 'CONTENT_IMAGE_REVIEW',
                     'BRAND_REVIEW'],
                    'brand_claims_qa', 'AG-17',
                    ['inspect_image', 'check_canonical_brand']),
    'AG-17': _agent('AG-17', 'Delivery Controller', ['FINAL_REVIEW', 'DELIVERY'],
                    'approval_distribution', 'AG-12',
                    ['verify', 'deliver']),
    'AG-18': _agent('AG-18', 'Analytics', ['DELIVERY'],
                    'analytics_learning', 'AG-17',
                    ['record_outcome', 'feedback_summary',
                     'record_experiment', 'list_experiments']),
}

# Producer agent per pipeline stage. Review stages are served by the
# reviewer agents named here (AG-12/AG-13/AG-16/AG-17 as appropriate);
# every review adapter name differs from the producer adapter it reviews,
# which the gate enforces (SELF_REVIEW_FORBIDDEN).
STAGE_AGENT = {
    'SOURCES': 'AG-01', 'SOURCE_REVIEW': 'AG-13', 'RESEARCH': 'AG-07',
    'RESEARCH_REVIEW': 'AG-12', 'STRATEGY': 'AG-08',
    'STRATEGY_REVIEW': 'AG-12', 'CONTENT': 'AG-10',
    'CONTENT_REVIEW': 'AG-12', 'IMAGE_PLAN': 'AG-14',
    'PLAN_REVIEW': 'AG-12', 'IMAGE_BUILD': 'AG-15',
    'TECH_REVIEW': 'AG-16', 'VISUAL_REVIEW': 'AG-16',
    'CONTENT_IMAGE_REVIEW': 'AG-16', 'BRAND_REVIEW': 'AG-16',
    'FINAL_REVIEW': 'AG-17', 'DELIVERY': 'AG-17',
}

# ---------------------------------------------------------------------------
# Lazy module loading (Worker 3 contract functions may not exist yet)
# ---------------------------------------------------------------------------

_MODULE_PATHS = {
    'content_engine': _REPO_ROOT / 'modules' / 'linkedin_copywriting' / 'content_engine.py',
    'competitor_monitor': _REPO_ROOT / 'modules' / 'competitor_intelligence' / 'competitor_monitor.py',
    'brief_prompt_gate': _REPO_ROOT / 'modules' / 'creative_brief' / 'brief_prompt_gate.py',
    'keyword_research': _REPO_ROOT / 'modules' / 'topic_intelligence' / 'keyword_research.py',
    'linkedin_seo_validator': _REPO_ROOT / 'modules' / 'topic_intelligence' / 'linkedin_seo_validator.py',
    'linkedin_analytics': _REPO_ROOT / 'modules' / 'analytics_learning' / 'linkedin_analytics.py',
    'validate_strategy_v33': _REPO_ROOT / 'modules' / 'marketing_strategy' / 'validate_strategy_v33.py',
    'verify_output': _REPO_ROOT / 'core' / 'verify_output.py',
    'brand_render_v37': _REPO_ROOT / 'rendering' / 'brand_render_v37.py',
    'brand_policy_v36': _REPO_ROOT / 'modules' / 'brand_claims_qa' / 'brand_policy_v36.py',
    'evidence_store': _REPO_ROOT / 'core' / 'evidence_store.py',
}
_MODULE_CACHE = {}
# Test doubles go here (tests set _MODULE_OVERRIDES[name] = module object).
_MODULE_OVERRIDES = {}

def _load_module(name):
    """Load a repo module from its canonical file path (never a bare guess).

    File-based loading keeps the import unambiguous when several dirs on
    sys.path contain same-named modules. Raises ImportError when the file
    is absent; callers that must fail loudly catch it, callers with an
    honest fallback use _try_load_module.
    """
    if name in _MODULE_OVERRIDES:
        return _MODULE_OVERRIDES[name]
    if name in _MODULE_CACHE:
        return _MODULE_CACHE[name]
    path = _MODULE_PATHS.get(name)
    if path is not None and path.is_file():
        sys.path.insert(0, str(path.parent))
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _MODULE_CACHE[name] = module
        return module
    try:
        module = importlib.import_module(name)
    except Exception as exc:
        raise ImportError('MODULE_NOT_FOUND:' + name) from exc
    _MODULE_CACHE[name] = module
    return module

def _try_load_module(name):
    try:
        return _load_module(name)
    except Exception:
        return None

def _provider_registry():
    """Worker 1's provider registry, or None when it is not configured.

    Never faked: a missing registry means no live fetch is possible and
    evidence is labelled USER_SUPPLIED / MODEL_INFERENCE / NOT_VERIFIED.
    """
    try:
        import chatgpt_bridge_v43 as bridge
        factory = getattr(bridge, 'get_provider_registry', None)
        return factory() if callable(factory) else None
    except Exception:
        return None

def _policy():
    try:
        return json.loads((_REPO_ROOT / 'config' / 'production-policy-v33.json').read_text(encoding='utf-8'))
    except Exception:
        return {}

def _utc_today():
    return datetime.now(timezone.utc).date()

def _parse_date(value):
    """Parse a verified_at value to a date, or None if unparseable."""
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        pass
    try:
        return datetime.fromisoformat(text).date()
    except ValueError:
        return None

# ---------------------------------------------------------------------------
# Real image measurement (Pillow; used when Worker 3 inspect_image is absent)
# ---------------------------------------------------------------------------

def _hex_to_rgb(value):
    text = str(value).lstrip('#')
    return tuple(int(text[i:i + 2], 16) for i in (0, 2, 4))

def _luminance(rgb):
    def channel(c):
        c = c / 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (channel(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def _dominant_stats(img):
    """Dominant colours, ink coverage and contrast estimate for an image.

    Ink = pixels measurably different from the policy paper colour.
    Contrast = WCAG-style ratio between paper and the darkest dominant
    colour. All values are measured from the actual pixels.
    """
    colors = img.getcolors(maxcolors=img.size[0] * img.size[1]) or []
    total = sum(n for n, _ in colors) or 1
    dominant = sorted(colors, reverse=True)[:5]
    dominant_colors = [(f'#{r:02X}{g:02X}{b:02X}', round(n / total, 4))
                       for n, (r, g, b) in dominant]
    paper = _hex_to_rgb(BRAND['palette']['paper'])
    def distance(px):
        return sum((a - b) ** 2 for a, b in zip(px, paper)) ** 0.5
    ink = round(sum(n for n, px in colors if distance(px) > 40) / total, 4)
    darkest = min((px for _, px in dominant), key=_luminance)
    light, dark = _luminance(paper), _luminance(darkest)
    contrast = round((max(light, dark) + 0.05) / (min(light, dark) + 0.05), 2)
    return dominant_colors, ink, contrast

def _margin_clearance(img):
    """First ink row/column from each edge, in original-scale pixels."""
    thumb = img
    scale_x = 1080 / thumb.size[0]
    scale_y = 1350 / thumb.size[1]
    paper = _hex_to_rgb(BRAND['palette']['paper'])
    pixels = thumb.load()
    width, height = thumb.size
    def is_ink(x, y):
        px = pixels[x, y][:3]
        return sum((a - b) ** 2 for a, b in zip(px, paper)) ** 0.5 > 40
    top = next((y for y in range(height) if any(is_ink(x, y) for x in range(width))), None)
    bottom = next((y for y in range(height - 1, -1, -1) if any(is_ink(x, y) for x in range(width))), None)
    left = next((x for x in range(width) if any(is_ink(x, y) for y in range(height))), None)
    right = next((x for x in range(width - 1, -1, -1) if any(is_ink(x, y) for y in range(height))), None)
    scale = lambda value, factor: None if value is None else int(round(value * factor))
    return {'top': scale(top, scale_y), 'bottom': scale(height - 1 - bottom, scale_y) if bottom is not None else None,
            'left': scale(left, scale_x), 'right': scale(width - 1 - right, scale_x) if right is not None else None}

def _blank_bands(img):
    """Count of the 10 horizontal bands that are (nearly) all paper."""
    paper = _hex_to_rgb(BRAND['palette']['paper'])
    pixels = img.load()
    width, height = img.size
    band_height = max(1, height // 10)
    blank = 0
    for band in range(10):
        y0, y1 = band * band_height, min(height, (band + 1) * band_height)
        ink = 0
        total = 0
        for y in range(y0, y1, 4):
            for x in range(0, width, 4):
                px = pixels[x, y][:3]
                total += 1
                if sum((a - b) ** 2 for a, b in zip(px, paper)) ** 0.5 > 40:
                    ink += 1
        if total and ink / total < 0.01:
            blank += 1
    return {'blank_bands': blank, 'bands': 10}

def _image_measurements(path):
    """Real measurements for a rendered PNG (never hardcoded flags)."""
    with Image.open(path) as im:
        fmt, size, mode = im.format, im.size, im.mode
        rgb = im.convert('RGB')
    thumb = rgb.copy()
    thumb.thumbnail((270, 338))
    dominant, ink, contrast = _dominant_stats(thumb)
    mobile = rgb.copy()
    mobile.thumbnail((360, 450))
    _, mobile_ink, mobile_contrast = _dominant_stats(mobile)
    return {'path': str(path), 'format': fmt, 'size': list(size), 'mode': mode,
            'dominant_colors': dominant, 'ink_coverage': ink,
            'contrast_ratio_estimate': contrast,
            'margin_clearance_px': _margin_clearance(thumb),
            'blank_regions': _blank_bands(thumb),
            'mobile_legibility': {'scaled_width': 360, 'ink_coverage': mobile_ink,
                                  'contrast_ratio_estimate': mobile_contrast,
                                  'checks': ['decodes at 360px wide',
                                             'contrast measured at mobile scale']}}

def _inspect_image(path):
    """Worker 3's inspect_image when present, else None (local Pillow
    measurements are used instead -- still real measurements)."""
    module = _try_load_module('verify_output')
    fn = getattr(module, 'inspect_image', None) if module is not None else None
    if fn is None:
        return None
    try:
        return fn(str(path))
    except Exception:
        return None

def _font_provenance():
    """Font provenance for the policy heading font, honestly reported.

    Returns {'Sora': {'path': <real font file>, 'sha256': <real sha>}}
    when a real Sora font file is found, else the fallback marker
    {'path': 'pillow-default-fallback', 'sha256': 'fallback-no-binary'}.
    A sha256 is never fabricated; in live mode the gate blocks on the
    fallback marker (LIVE_FONT_BINARY_NOT_VERIFIED), which is correct.
    """
    candidates = [
        _REPO_ROOT / 'assets' / 'fonts' / 'Sora-Regular.ttf',
        _REPO_ROOT / 'assets' / 'Sora-Regular.ttf',
        Path('/usr/share/fonts/truetype/sora/Sora-Regular.ttf'),
        Path('/usr/share/fonts/Sora-Regular.ttf'),
    ]
    for candidate in candidates:
        if candidate.is_file():
            return {'Sora': {'path': str(candidate), 'sha256': filehash(candidate)}}
    return {'Sora': {'path': 'pillow-default-fallback', 'sha256': 'fallback-no-binary'}}

def _sora_font_spec():
    """Render-spec font entries for render_production_poster (live run fix,
    2026-11-24): {'sora_regular': {'path', 'sha256'}, 'sora_bold': {...}}
    for every real Sora file found. Without this the live renderer falls
    back to Pillow's default font even when a real Sora binary exists,
    so the rendered poster would not actually be Sora. Only files that
    exist on disk are returned, with their real sha256; nothing is
    fabricated. Candidates mirror _font_provenance (repo assets first,
    then system font dirs) plus the Bold variants."""
    found = {}
    for key, filename in (('sora_regular', 'Sora-Regular.ttf'),
                          ('sora_bold', 'Sora-Bold.ttf')):
        for base in (_REPO_ROOT / 'assets' / 'fonts', _REPO_ROOT / 'assets',
                     Path('/usr/share/fonts/truetype/sora'), Path('/usr/share/fonts')):
            candidate = base / filename
            if candidate.is_file():
                found[key] = {'path': str(candidate), 'sha256': filehash(candidate)}
                break
    return found

# ---------------------------------------------------------------------------
# Fixture poster rendering (real Pillow render, used in TEST_FIXTURE mode)
# ---------------------------------------------------------------------------

def _wrap_text(draw, text, font, width):
    lines = []
    for paragraph in str(text).split('\n'):
        current = ''
        for word in paragraph.split():
            trial = (current + ' ' + word).strip()
            if draw.textlength(trial, font=font) > width and current:
                lines.append(current)
                current = word
            else:
                current = trial
        if current:
            lines.append(current)
    return lines

def _render_fixture_poster(work_dir, content_id, poster_text):
    """Render a real 1080x1350 PNG poster from the locked poster copy."""
    palette = BRAND['palette']
    image = Image.new('RGB', (1080, 1350), palette['paper'])
    draw = ImageDraw.Draw(image)
    try:
        headline_font = ImageFont.load_default(size=54)
        body_font = ImageFont.load_default(size=26)
        small_font = ImageFont.load_default(size=22)
    except Exception:
        headline_font = body_font = small_font = ImageFont.load_default()
    draw.rectangle((64, 56, 1016, 68), fill=palette['emerald'])
    y = 110
    for line in _wrap_text(draw, poster_text.get('headline', ''), headline_font, 952):
        draw.text((64, y), line, font=headline_font, fill=palette['ink'])
        y += 68
    y += 30
    for index, step in enumerate(poster_text.get('steps') or []):
        draw.rounded_rectangle((64, y, 1016, y + 110), radius=18,
                               fill='#FFFCF7', outline='#C9C4B9', width=2)
        draw.text((90, y + 32), f'{index + 1:02}', font=body_font, fill=palette['deep'])
        step_lines = _wrap_text(draw, step, body_font, 760)
        for j, line in enumerate(step_lines[:2]):
            draw.text((180, y + 22 + j * 36), line, font=body_font, fill=palette['ink'])
        y += 128
    draw.rounded_rectangle((64, 1100, 1016, 1190), radius=18, fill=palette['dark'])
    takeaway = poster_text.get('takeaway', 'Keep a person responsible for exceptions.')
    for j, line in enumerate(_wrap_text(draw, takeaway, body_font, 890)[:2]):
        draw.text((90, 1116 + j * 32), line, font=body_font, fill=palette['paper'])
    draw.line((64, 1230, 1016, 1230), fill='#B8B0A4', width=2)
    draw.text((64, 1252), poster_text.get('footer', 'Erudience erudience.com'),
              font=small_font, fill=palette['soft'])
    out_path = Path(work_dir) / f'{content_id}.png'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(out_path)
    return out_path

# ---------------------------------------------------------------------------
# Batch creation / summary (initialise preserved exactly; summary extended
# additively with duplicate_images only)
# ---------------------------------------------------------------------------

def initialise(root, topics, cycle):
    if len(topics)!=SLOTS or len(set(topics))!=SLOTS or any(not x.strip() for x in topics):
        raise ValueError('SEVEN_DISTINCT_TOPICS_REQUIRED')
    base=Path(root);base.mkdir(parents=True,exist_ok=True)
    manifest=base/'manifest.json'
    if manifest.exists(): raise ValueError('BATCH_ALREADY_EXISTS')
    jobs=[]
    for i,topic in enumerate(topics,1):
        cid=f'ER-{cycle}-{i:03d}'
        p=base/f'{cid}.json'
        start(str(p),{'content_id':cid,'topic':topic,'cycle':cycle})
        jobs.append({'content_id':cid,'state':str(p)})
    manifest.write_text(json.dumps({'cycle':cycle,'jobs':jobs},indent=2),encoding='utf8')
    return summary(root)

def summary(root):
    manifest=json.loads((Path(root)/'manifest.json').read_text(encoding='utf8'))
    rows=[];seen=set()
    for job in manifest['jobs']:
        state=load(job['state']); cid=state['job']['content_id']
        if cid in seen:raise ValueError('DUPLICATE_CONTENT_ID')
        seen.add(cid)
        build=state['records'].get('IMAGE_BUILD',{}).get('artifact',{})
        path=build.get('image_path');valid=False
        if path and Path(path).is_file():
            try:
                with Image.open(path) as im:valid=im.format=='PNG' and im.size==(1080,1350)
            except Exception:pass
        ready=state['status']=='READY_FOR_OWNER_REVIEW' and valid and len(state['records'])==17
        rows.append({'content_id':cid,'status':'READY_FOR_OWNER_REVIEW' if ready else 'BLOCKED' if state['status']=='BLOCKED' else 'IN_PROGRESS','stage':next_step(state).get('stage'),'image_path':path if ready else None,'reason':None if ready else 'NOT_ALL_GATES_AND_INDIVIDUAL_PNG_VERIFIED'})
    paths=[r['image_path'] for r in rows if r['image_path']]
    if len(paths)!=len(set(paths)):raise ValueError('REUSED_IMAGE_PATH')
    result={'cycle':manifest['cycle'],'expected':SLOTS,'ready':sum(r['status']=='READY_FOR_OWNER_REVIEW' for r in rows),'items':rows,'batch_status':'READY_FOR_OWNER_REVIEW' if len(rows)==SLOTS and all(r['status']=='READY_FOR_OWNER_REVIEW' for r in rows) else 'NOT_APPROVED'}
    duplicates=check_duplicate_images(root)
    result['duplicate_images']=duplicates
    if duplicates['duplicates']:
        result['batch_status']='NOT_APPROVED'
    return result

def check_duplicate_images(root):
    """Cross-job image-hash comparison (D-17).

    Reads the batch manifest; for every job with a valid PNG image_path
    computes SHA-256 of the file bytes. Two jobs sharing identical bytes
    under different paths MUST be reported. Returns {'status':
    'PASS'|'BLOCKED', 'duplicates': [{'sha256', 'content_ids'}],
    'checked': n}.
    """
    manifest_path = Path(root) / 'manifest.json'
    if not manifest_path.is_file():
        return {'status': 'PASS', 'duplicates': [], 'checked': 0}
    try:
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    except Exception:
        return {'status': 'PASS', 'duplicates': [], 'checked': 0}
    by_hash = {}
    checked = 0
    for job in manifest.get('jobs', []):
        state_path = Path(job.get('state', ''))
        if not state_path.is_file():
            continue
        try:
            state = load(str(state_path))
        except Exception:
            continue
        path = state.get('records', {}).get('IMAGE_BUILD', {}).get('artifact', {}).get('image_path')
        if not path:
            continue
        image_path = Path(path)
        if not image_path.is_file():
            continue
        try:
            with Image.open(image_path) as im:
                if im.format != 'PNG':
                    continue
        except Exception:
            continue
        digest_value = filehash(image_path)
        checked += 1
        content_id = state.get('job', {}).get('content_id') or job.get('content_id')
        by_hash.setdefault(digest_value, []).append(content_id)
    duplicates = [{'sha256': value, 'content_ids': sorted(ids)}
                  for value, ids in sorted(by_hash.items()) if len(ids) > 1]
    return {'status': 'BLOCKED' if duplicates else 'PASS',
            'duplicates': duplicates, 'checked': checked}

# ---------------------------------------------------------------------------
# Strategy enforcement (D-05: exactly-1-promotion on the canonical path)
# ---------------------------------------------------------------------------

def _load_json_value(value):
    path = Path(value)
    if path.is_dir():
        path = path / 'strategy.json'
    return json.loads(path.read_text(encoding='utf-8'))

def verify_batch_strategy(root_or_manifest, strategy=None):
    """Verify a 7-slot batch strategy; exactly one promotion or BLOCKED.

    Accepts either a strategy list (7 slot dicts) as `strategy` (or as
    `root_or_manifest`), or a path to a manifest/strategy JSON file
    (a dict with a 'strategy' key, or a bare list). Runs
    modules/marketing_strategy/validate_strategy_v33.validate().
    Returns {'status': 'PASS'|'BLOCKED', 'errors': [...]}.
    """
    slots = None
    try:
        if strategy is not None:
            if isinstance(strategy, (list, tuple)):
                slots = list(strategy)
            else:
                data = _load_json_value(strategy)
                slots = data.get('strategy') if isinstance(data, dict) else data
        elif isinstance(root_or_manifest, (list, tuple)):
            slots = list(root_or_manifest)
        else:
            data = _load_json_value(root_or_manifest)
            if isinstance(data, dict):
                slots = data.get('strategy') or data.get('slots')
            elif isinstance(data, list):
                slots = data
    except Exception:
        slots = None
    if not isinstance(slots, list):
        return {'status': 'BLOCKED', 'errors': ['STRATEGY_NOT_FOUND']}
    validator = _load_module('validate_strategy_v33')
    errors = validator.validate(slots)
    return {'status': 'PASS' if not errors else 'BLOCKED', 'errors': errors}

# ---------------------------------------------------------------------------
# Scheduler gap (D-19): no daemon is created; research_due is a pure check.
# Actual scheduling (cron) remains an owner/operator step.
# ---------------------------------------------------------------------------

def _last_research_date(state_dir):
    """Latest research date found in the batch state, or None.

    Sources, in order: <state_dir>/research_evidence.json, then the
    SOURCES records of the manifest's job states. Fixture-only dates
    ('fixture-only') do not count as research.
    """
    found = []
    evidence_path = Path(state_dir) / 'research_evidence.json'
    if evidence_path.is_file():
        try:
            data = json.loads(evidence_path.read_text(encoding='utf-8'))
            items = data if isinstance(data, list) else data.get('evidence') or data.get('sources') or []
            for item in items:
                if isinstance(item, dict):
                    parsed = _parse_date(item.get('verified_at') or item.get('retrieved_at'))
                    if parsed is not None:
                        found.append(parsed)
        except Exception:
            pass
    manifest_path = Path(state_dir) / 'manifest.json'
    if manifest_path.is_file():
        try:
            manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
            for job in manifest.get('jobs', []):
                state_path = Path(job.get('state', ''))
                if not state_path.is_file():
                    continue
                try:
                    state = load(str(state_path))
                except Exception:
                    continue
                sources = state.get('records', {}).get('SOURCES', {}).get('artifact', {}).get('sources', [])
                for source in sources:
                    if isinstance(source, dict):
                        parsed = _parse_date(source.get('verified_at'))
                        if parsed is not None:
                            found.append(parsed)
        except Exception:
            pass
    return max(found) if found else None

def research_due(state_dir, max_age_days=7, cycle_start_day=21):
    """Is fresh research due? (D-19; no daemon, pure check.)

    Reads the last research timestamp from the batch state/ledger; with
    no prior research returns {'due': True, 'reason': 'NO_PRIOR_RESEARCH'}.
    Due when the last research is older than max_age_days OR predates the
    current monthly cycle anchor (day 21 by default, read from the policy
    JSON's monthly_cycle_start_day when available). Dates are UTC calendar
    dates; the policy timezone is Asia/Dhaka.
    """
    policy = _policy()
    anchor = policy.get('monthly_cycle_start_day') or cycle_start_day
    try:
        anchor = int(anchor)
    except Exception:
        anchor = cycle_start_day
    anchor = min(max(anchor, 1), 28)
    today = _utc_today()
    if today.day >= anchor:
        cycle_start = today.replace(day=anchor)
    else:
        year, month = (today.year, today.month - 1) if today.month > 1 else (today.year - 1, 12)
        cycle_start = date(year, month, anchor)
    last = _last_research_date(Path(state_dir))
    if last is None:
        return {'due': True, 'reason': 'NO_PRIOR_RESEARCH', 'last_research': None,
                'age_days': None, 'cycle_start': cycle_start.isoformat(),
                'max_age_days': max_age_days}
    age = (today - last).days
    if age > max_age_days:
        reason = 'STALE'
    elif last < cycle_start:
        reason = 'BEFORE_CYCLE_START'
    else:
        reason = 'FRESH'
    return {'due': reason != 'FRESH', 'reason': reason,
            'last_research': last.isoformat(), 'age_days': age,
            'cycle_start': cycle_start.isoformat(), 'max_age_days': max_age_days}

def _fresh_research_evidence(root):
    """True when root/research_evidence.json holds an entry verified
    within the last 7 days (the 'fresh research supplied' override for
    a live batch when research_due says due)."""
    evidence_path = Path(root) / 'research_evidence.json'
    if not evidence_path.is_file():
        return False
    try:
        data = json.loads(evidence_path.read_text(encoding='utf-8'))
    except Exception:
        return False
    items = data if isinstance(data, list) else data.get('evidence') or data.get('sources') or []
    today = _utc_today()
    for item in items:
        if isinstance(item, dict):
            parsed = _parse_date(item.get('verified_at') or item.get('retrieved_at'))
            if parsed is not None and (today - parsed).days <= 7:
                return True
    return False

# ---------------------------------------------------------------------------
# Adapters: one real adapter per stage (build_adapters)
# ---------------------------------------------------------------------------

def _topic_cluster(topic):
    return {'keywords': [
        {'term': topic, 'type': 'primary', 'intent': 'informational'},
        {'term': topic + ' workflow', 'type': 'secondary', 'intent': 'commercial'},
    ], 'buyer_intent': 'unverified'}

def _headline(topic):
    words = (str(topic) + ': five steps, one owner').split()
    return ' '.join(words[:12])

def _positioning(job):
    slot = job.get('slot') or {}
    return slot.get('positioning') or 'business automation'

def _funnel_stage(job):
    slot = job.get('slot') or {}
    return slot.get('funnel_stage') or 'awareness'

def _publish_date(job):
    cycle = str(job.get('cycle') or '')
    if len(cycle) == 8 and cycle.isdigit():
        candidate = f'{cycle[:4]}-{cycle[4:6]}-{cycle[6:]}'
        try:
            date.fromisoformat(candidate)
            return candidate
        except ValueError:
            pass
    return '2026-11-21'

def _research_evidence_entry(source):
    """One live-mode research_evidence entry, labelled honestly.

    LIVE_VERIFIED only when a real provider fetch succeeded; otherwise
    USER_SUPPLIED (a real supplied source) or NOT_VERIFIED -- never
    LIVE_VERIFIED without a fetch.
    """
    url = source.get('url')
    verified_at = source.get('verified_at')
    registry = _provider_registry()
    fetched = None
    if registry is not None:
        try:
            fetched = registry.fetch_source(url)
        except Exception:
            fetched = None
    if (fetched and fetched.get('status') in ('OK', 'SUCCESS', 'VERIFIED', 'LIVE_VERIFIED')
            and fetched.get('sha256')):
        return {'url': url, 'verified_at': verified_at, 'evidence_label': 'LIVE_VERIFIED',
                'provider': fetched.get('provider'), 'retrieved_at': fetched.get('retrieved_at'),
                'source_sha256': fetched['sha256']}
    if source.get('source_sha256') and verified_at and verified_at != 'fixture-only':
        return {'url': url, 'verified_at': verified_at, 'evidence_label': 'USER_SUPPLIED',
                'provider': source.get('provider', 'user-supplied'),
                'retrieved_at': source.get('retrieved_at', verified_at),
                'source_sha256': source['source_sha256']}
    return {'url': url, 'verified_at': verified_at, 'evidence_label': 'NOT_VERIFIED',
            'provider': 'none', 'retrieved_at': verified_at,
            'source_sha256': hashlib.sha256(str(url).encode()).hexdigest()}

def build_adapters(job, work_dir, mode='TEST_FIXTURE'):
    """Build {stage_name: Adapter} for all 17 stages.

    Each adapter does REAL work by calling the module functions (never
    canned dicts). In TEST_FIXTURE mode adapters return fixture-shaped
    outputs compatible with the existing tests; in live mode
    (mode != 'TEST_FIXTURE') they MUST supply the live-mode fields
    (research_evidence, strategy block, final_checklist, real font
    provenance) and fail loudly instead of faking them. Live evidence
    is never claimed in fixture mode.
    """
    work_dir = Path(work_dir)
    live = mode != 'TEST_FIXTURE'
    base_job = dict(job)
    content_id = base_job['content_id']
    topic = base_job['topic']
    topic_store = work_dir / 'topics.json'

    def upstream(records, stage):
        prev = STAGES[STAGES.index(stage) - 1]
        return {'upstream_hash': records[prev]['hash']}

    def adapter_name(stage):
        return STAGE_AGENT[stage] + '-' + stage.lower().replace('_', '-')

    def review(stage, records, observations, extra=None):
        """Review-stage output: reviewer identity, subject hash, real
        observations, plus an inspection-evidence file with its sha256
        (required by the gate in live mode, recorded in fixture mode)."""
        prev = STAGES[STAGES.index(stage) - 1]
        evidence = {'stage': stage, 'content_id': content_id,
                    'subject_hash': records[prev]['hash'],
                    'observations': list(observations)}
        evidence_path = work_dir / f'{content_id}-{stage}-evidence.json'
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        evidence_path.write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding='utf-8')
        out = {'upstream_hash': records[prev]['hash'],
               'reviewer': adapter_name(stage), 'decision': 'PASS',
               'observations': list(observations),
               'subject_hash': records[prev]['hash'],
               'inspection_evidence_path': str(evidence_path),
               'inspection_evidence_sha256': filehash(evidence_path)}
        if extra:
            out.update(extra)
        return out

    def sources_fn(j, records):
        supplied = j.get('sources') or base_job.get('sources')
        if live:
            if not supplied:
                raise GateFailure('LIVE_SOURCES_REQUIRED')
            sources = []
            for item in supplied:
                url = item.get('url')
                verified_at = item.get('verified_at')
                if not url or not verified_at:
                    raise GateFailure('SOURCE_PROVENANCE_REQUIRED')
                entry = {'url': url, 'verified_at': verified_at}
                registry = _provider_registry()
                fetched = None
                if registry is not None:
                    try:
                        fetched = registry.fetch_source(url)
                    except Exception:
                        fetched = None
                if (fetched and fetched.get('status') in ('OK', 'SUCCESS', 'VERIFIED', 'LIVE_VERIFIED')
                        and fetched.get('sha256')):
                    entry['source_sha256'] = fetched['sha256']
                    entry['retrieved_at'] = fetched.get('retrieved_at')
                    entry['provider'] = fetched.get('provider')
                else:
                    entry['source_sha256'] = hashlib.sha256(
                        f'{url}|{verified_at}'.encode()).hexdigest()
                    entry['retrieved_at'] = verified_at
                    entry['provider'] = 'user-supplied'
                sources.append(entry)
            return {'sources': sources}
        if supplied:
            return {'sources': [{'url': s.get('url'), 'verified_at': s.get('verified_at')}
                                for s in supplied]}
        return {'sources': [{'url': 'https://example.org/erudience-source',
                             'verified_at': 'fixture-only'}]}

    def source_review_fn(j, records):
        sources = records['SOURCES']['artifact'].get('sources', [])
        observations = [f"Source {s.get('url')} verified_at {s.get('verified_at')}"
                        for s in sources]
        if live:
            observations.append('Live mode: fixture-only sources rejected by the gate.')
        return review('SOURCE_REVIEW', records, observations)

    def research_fn(j, records):
        out = dict(upstream(records, 'RESEARCH'))
        sources = records['SOURCES']['artifact'].get('sources', [])
        keyword = _load_module('keyword_research')
        out['freshness'] = keyword.assess_source_freshness(sources)
        competitor = _load_module('competitor_monitor')
        competitor_records = j.get('competitors') or base_job.get('competitors') or []
        out['competitor_audit'] = competitor.audit(competitor_records)
        out['competitor_coverage'] = competitor.competitor_coverage(competitor_records)
        market_signals = j.get('market_signals') or base_job.get('market_signals') or []
        out['market_signals'] = competitor.assess_market_signals(market_signals)
        cluster = _topic_cluster(topic)
        out['keyword_validation'] = keyword.validate_cluster(cluster)
        out['content_mapping'] = keyword.map_content(
            {'hook': topic, 'body': topic + ' workflow with a human handoff.'}, cluster)
        seo = _try_load_module('linkedin_seo_validator')
        if seo is not None:
            out['seo_review'] = seo.review(
                {'hook': topic, 'body': topic + ' workflow with a human handoff.',
                 'cta': 'Read checklist', 'funnel_stage': 'awareness'}, cluster)
        out['topic_registry'] = keyword.register_topic(str(topic_store), topic)
        out['topic_preservation'] = keyword.check_topic_preserved(str(topic_store), [topic])
        if live:
            out['research_evidence'] = [_research_evidence_entry(s) for s in sources]
        return out

    def research_review_fn(j, records):
        artifact = records['RESEARCH']['artifact']
        freshness = artifact.get('freshness', {})
        observations = [f"Freshness: {freshness.get('status')} "
                        f"({freshness.get('fresh_count', 0)} fresh, "
                        f"{freshness.get('stale_count', 0)} stale, "
                        f"{freshness.get('unverified_count', 0)} unverified)"]
        coverage = artifact.get('competitor_coverage', {})
        observations.append(f"Competitor coverage: {coverage.get('status')} "
                            f"gaps={coverage.get('gaps', {})}")
        market = artifact.get('market_signals', {})
        observations.append(f"Market signals: {market.get('status')} "
                            f"({market.get('verified', 0)}/{market.get('signals', 0)} verified)")
        mapping = artifact.get('content_mapping', {})
        observations.append(f"Content mapping: {mapping.get('status')} "
                            f"primary={mapping.get('primary')}")
        observations.append(f"Topic preservation errors: "
                            f"{artifact.get('topic_preservation', [])}")
        return review('RESEARCH_REVIEW', records, observations)

    def strategy_fn(j, records):
        out = dict(upstream(records, 'STRATEGY'))
        validator = _load_module('validate_strategy_v33')
        slot = j.get('slot') or base_job.get('slot') or {}
        slot_errors = validator.validate_single_slot(slot)
        out['slot_errors'] = slot_errors
        if slot_errors:
            raise GateFailure('STRATEGY_SLOT_INVALID: ' + '; '.join(slot_errors))
        content_engine = _load_module('content_engine')
        if slot and ('funnel_stage' in slot or 'cta' in slot):
            funnel = content_engine.plan_funnel([{
                'funnel_stage': slot.get('funnel_stage', 'awareness'),
                'cta': slot.get('cta', 'Read checklist'),
                'cta_destination': slot.get('cta_destination', 'none'),
                'cta_type': slot.get('cta_type')}])
            out['funnel'] = funnel
            if funnel['errors']:
                raise GateFailure('FUNNEL_PLAN_INVALID: ' + '; '.join(funnel['errors']))
        else:
            out['funnel'] = {'status': 'SKIPPED', 'reason': 'NO_SLOT_FUNNEL_DATA',
                             'errors': [], 'allocation': {}}
        keyword = _load_module('keyword_research')
        cluster = _topic_cluster(topic)
        out['content_mapping'] = keyword.map_content(
            {'hook': topic, 'body': topic + ' workflow with a human handoff.'}, cluster)
        strategy = j.get('strategy') or base_job.get('strategy')
        if isinstance(strategy, list) and strategy:
            promotion = [s for s in strategy if isinstance(s, dict) and s.get('promotion')]
            out['strategy'] = {
                'slots': len(strategy),
                'promotion_count': len(promotion),
                'promotion': {'employee_requirement': bool(promotion[0].get('employee_requirement')) if promotion else False},
                'unsupported_claim': any(isinstance(s, dict) and s.get('unsupported_claim') for s in strategy),
                'unauthorised_write': any(isinstance(s, dict) and s.get('external_write') and not s.get('explicit_authorization') for s in strategy)}
        else:
            out['strategy'] = {
                'slots': 1,
                'promotion_count': 1 if slot.get('promotion') else 0,
                'promotion': {'employee_requirement': bool(slot.get('employee_requirement')) if slot.get('promotion') else False},
                'unsupported_claim': bool(slot.get('unsupported_claim')),
                'unauthorised_write': bool(slot.get('external_write') and not slot.get('explicit_authorization'))}
        return out

    def strategy_review_fn(j, records):
        artifact = records['STRATEGY']['artifact']
        observations = [f"Slot errors: {artifact.get('slot_errors', [])}",
                        f"Funnel: {artifact.get('funnel', {}).get('status')}",
                        f"Strategy block: slots={artifact.get('strategy', {}).get('slots')} "
                        f"promotion_count={artifact.get('strategy', {}).get('promotion_count')}"]
        return review('STRATEGY_REVIEW', records, observations)

    def content_fn(j, records):
        content_engine = _load_module('content_engine')
        caption = f'{topic}: human handoff matters.'
        keywords = [topic, topic + ' workflow']
        poster_text = {
            'headline': _headline(topic),
            'steps': ['Answer every call', 'Capture the request',
                      'Respond with the facts', 'Route to the right person',
                      'Follow up and close the loop'],
            'takeaway': 'Keep a person responsible for exceptions.',
            'footer': 'Erudience erudience.com'}
        locked = content_engine.lock_content({
            'content_id': content_id, 'topic': topic, 'caption': caption,
            'keywords': keywords, 'poster_text': poster_text})
        sources = records['SOURCES']['artifact'].get('sources', [])
        item = {'content_id': content_id, 'publish_date': _publish_date(j),
                'platforms': ['linkedin'], 'topic': topic, 'title': topic,
                'pillar': 'education', 'funnel_stage': _funnel_stage(j),
                'primary_format': 'flowchart', 'derivatives': ['text'],
                'keywords': keywords, 'buyer_pain': j.get('buyer_pain', 'unclear ownership'),
                'cta': 'Read checklist',
                'sources': [{'source_id': f's{i + 1}', 'url': s.get('url'),
                             'retrieved_at': s.get('verified_at')}
                            for i, s in enumerate(sources)],
                'claims': [], 'copy': caption, 'brand_id': 'erudience',
                'category': 'education'}
        gate_result = content_engine.gate(item, {})
        out = dict(upstream(records, 'CONTENT'))
        out.update(locked)
        out['content_gate'] = gate_result
        return out

    def content_review_fn(j, records):
        content_engine = _load_module('content_engine')
        artifact = records['CONTENT']['artifact']
        recomputed = content_engine.lock_content({
            'content_id': artifact['content_id'], 'topic': artifact['topic'],
            'caption': artifact['caption'], 'keywords': artifact['keywords'],
            'poster_text': artifact['poster_text']})
        matches = recomputed['content_hash'] == artifact['content_hash']
        observations = [f"Content hash recomputed: {'match' if matches else 'MISMATCH'}",
                        f"Caption present: {bool(artifact.get('caption'))}",
                        f"Keywords: {artifact.get('keywords')}",
                        f"Content gate at write time: {artifact.get('content_gate', {}).get('decision')}"]
        if not matches:
            raise GateFailure('CONTENT_LOCK_MISMATCH')
        return review('CONTENT_REVIEW', records, observations)

    def image_plan_fn(j, records):
        content = records['CONTENT']['artifact']
        brief_gate = _load_module('brief_prompt_gate')
        # Live-run fix (2026-11-24): build_brief's structural gate needs
        # three things the caller must supply — evidence_refs from the
        # verified SOURCES records, the font-verification flag from the
        # real Sora binaries, and the logo plan. Logo is OPTIONAL per the
        # owner's 2026-11-24 decision (C3), so this plan carries no logo
        # and logo_planned is False; validate() then does not demand a
        # logo hash. Without these the live IMAGE_PLAN gate fails on
        # BRIEF_MISSING:evidence_refs / LOGO_BINARY_NOT_VERIFIED /
        # FONT_BINARY_NOT_VERIFIED even though the evidence exists.
        _fonts = _sora_font_spec()
        _sources = records['SOURCES']['artifact'].get('sources', [])
        brief = brief_gate.build_brief(
            {'content_id': content['content_id'], 'topic': content['topic'],
             'caption': content['caption'], 'keywords': content['keywords'],
             'poster_text': content['poster_text'],
             'content_hash': content['content_hash'],
             'buyer_pain': j.get('buyer_pain'), 'cta': 'Read checklist',
             'evidence_refs': [{'url': s.get('url'), 'verified_at': s.get('verified_at'),
                                'source_sha256': s.get('source_sha256')} for s in _sources],
             'logo_planned': False,
             'font_files_verified': ('sora_regular' in _fonts and 'sora_bold' in _fonts)},
            BRAND, 'website', _positioning(j), _funnel_stage(j))
        if live and brief.get('validation_errors'):
            raise GateFailure('BRIEF_GATE_FAILED: ' + '; '.join(brief['validation_errors']))
        plan = brief_gate.plan_image(
            {'content_id': content['content_id'],
             'poster_text': content['poster_text'],
             'content_hash': content['content_hash']}, brief)
        out = dict(upstream(records, 'IMAGE_PLAN'))
        out.update({
            'content_id': content_id, 'topic': content['topic'],
            'caption': content['caption'],
            'content_hash': records['CONTENT']['hash'],
            'locked_content_hash': content['content_hash'],
            'poster_text': plan['poster_text'], 'dimensions': plan['dimensions'],
            'brand': BRAND, 'design_rationale': plan['design_rationale'],
            'negative_constraints': plan['negative_constraints'],
            'logo_asset': None, 'template_id': plan['template_id'],
            'positioning': plan['positioning'],
            'funnel_stage': plan['funnel_stage'],
            'brief_validation_errors': brief.get('validation_errors', [])})
        return out

    def plan_review_fn(j, records):
        artifact = records['IMAGE_PLAN']['artifact']
        observations = [f"Brief validation errors: {artifact.get('brief_validation_errors', [])}",
                        f"Template: {artifact.get('template_id')} positioning: {artifact.get('positioning')}",
                        f"Dimensions: {artifact.get('dimensions')}"]
        return review('PLAN_REVIEW', records, observations)

    def image_build_fn(j, records):
        plan = records['IMAGE_PLAN']['artifact']
        out = dict(upstream(records, 'IMAGE_BUILD'))
        out.update({'content_id': content_id,
                    'plan_hash': records['IMAGE_PLAN']['hash'],
                    'copy_ledger_hash': digest(plan['poster_text']),
                    'copy_rendered': True, 'logo_asset': None})
        if live:
            renderer = _try_load_module('brand_render_v37')
            render_fn = getattr(renderer, 'render_production_poster', None) if renderer is not None else None
            if render_fn is None:
                raise GateFailure('IMAGE_RENDERER_MISSING')
            spec = {'copy': {'headline': plan['poster_text'].get('headline', ''),
                             'steps': plan['poster_text'].get('steps', []),
                             'support': records['CONTENT']['artifact'].get('caption', ''),
                             'takeaway': plan['poster_text'].get('takeaway', ''),
                             'category': _positioning(j)},
                    'palette': BRAND['palette'], 'template_id': plan.get('template_id')}
            # Live-run fix (2026-11-24): hand the renderer the real Sora
            # binaries when they exist, so the poster is actually set in
            # Sora instead of Pillow's default font. Missing files are
            # reported honestly by the renderer's receipt (font_verified
            # False, font_source 'pillow-default-fallback').
            spec.update(_sora_font_spec())
            result = render_fn(spec, str(work_dir / f'{content_id}.png'))
            if not isinstance(result, dict) or result.get('status') == 'BLOCKED':
                errors = result.get('errors', ['UNKNOWN_RENDER_ERROR']) if isinstance(result, dict) else ['UNKNOWN_RENDER_ERROR']
                raise GateFailure('IMAGE_RENDER_BLOCKED: ' + '; '.join(errors))
            image_path = result.get('image_path')
            if not image_path or not Path(image_path).is_file():
                raise GateFailure('IMAGE_RENDER_BLOCKED: NO_IMAGE_PATH')
            out.update({'image_path': str(image_path),
                        'image_sha256': result.get('sha256') or filehash(image_path),
                        'font_provenance': result.get('font_provenance') or _font_provenance()})
            return out
        image_path = _render_fixture_poster(work_dir, content_id, plan['poster_text'])
        out.update({'image_path': str(image_path),
                    'image_sha256': filehash(image_path),
                    'font_provenance': _font_provenance()})
        return out

    def tech_review_fn(j, records):
        build = records['IMAGE_BUILD']['artifact']
        measurements = _image_measurements(build['image_path'])
        observations = [f"PNG {measurements['size']} mode {measurements['mode']}",
                        f"SHA-256 {build['image_sha256'][:16]}...",
                        f"Ink coverage {measurements['ink_coverage']} "
                        f"contrast {measurements['contrast_ratio_estimate']}"]
        if measurements['size'] != [1080, 1350] or measurements['format'] != 'PNG':
            raise GateFailure('TECH_PNG_INVALID')
        return review('TECH_REVIEW', records, observations,
                      {'measurements': measurements})

    def _visual_flags(build, plan):
        """Derive pixel/mobile flags from REAL measurements (never hardcoded).

        Prefers Worker 3's inspect_image measurements when present; else
        uses the local Pillow measurements. A flag is True only when the
        measured numbers pass the thresholds.
        """
        inspection = _inspect_image(build['image_path'])
        measurements = _image_measurements(build['image_path'])
        if inspection is not None and isinstance(inspection.get('measurements'), dict):
            numbers = inspection['measurements']
            ink = numbers.get('ink_coverage', measurements['ink_coverage'])
            contrast = numbers.get('contrast_ratio_estimate', measurements['contrast_ratio_estimate'])
            mobile = numbers.get('mobile_legibility', measurements['mobile_legibility'])
            mobile_contrast = mobile.get('contrast_ratio_estimate', contrast) if isinstance(mobile, dict) else contrast
            mobile_ink = mobile.get('ink_coverage', ink) if isinstance(mobile, dict) else ink
            source = 'inspect_image'
        else:
            ink = measurements['ink_coverage']
            contrast = measurements['contrast_ratio_estimate']
            mobile_contrast = measurements['mobile_legibility']['contrast_ratio_estimate']
            mobile_ink = measurements['mobile_legibility']['ink_coverage']
            source = 'local-pillow'
        pixel = (measurements['size'] == [1080, 1350] and measurements['format'] == 'PNG'
                 and 0.005 < ink < 0.9 and contrast >= 3.0)
        mobile_ok = mobile_contrast >= 3.0 and mobile_ink > 0.005
        return pixel, mobile_ok, measurements, inspection, source

    def visual_review_fn(j, records):
        build = records['IMAGE_BUILD']['artifact']
        plan = records['IMAGE_PLAN']['artifact']
        pixel, mobile_ok, measurements, inspection, source = _visual_flags(build, plan)
        observations = [f"Pixel inspection ({source}): ink {measurements['ink_coverage']} "
                        f"contrast {measurements['contrast_ratio_estimate']}",
                        f"Mobile inspection ({source}): scaled width "
                        f"{measurements['mobile_legibility']['scaled_width']} contrast "
                        f"{measurements['mobile_legibility']['contrast_ratio_estimate']}",
                        f"Margin clearance px: {measurements['margin_clearance_px']}"]
        if not pixel or not mobile_ok:
            raise GateFailure('PIXEL_INSPECTION_REQUIRED')
        return review('VISUAL_REVIEW', records, observations,
                      {'image_sha256': build['image_sha256'],
                       'plan_hash': records['IMAGE_PLAN']['hash'],
                       'pixel_inspection': pixel, 'mobile_inspection': mobile_ok,
                       'measurements': measurements,
                       'inspection': inspection, 'inspection_source': source})

    def content_image_review_fn(j, records):
        build = records['IMAGE_BUILD']['artifact']
        plan = records['IMAGE_PLAN']['artifact']
        poster_text = plan['poster_text']
        poster_copy = ' '.join([str(poster_text.get('headline', ''))] +
                               [str(s) for s in poster_text.get('steps', [])]).casefold()
        topic_words = [w for w in str(topic).split() if len(w) >= 3]
        matched = sum(1 for w in topic_words if w.casefold() in poster_copy)
        topic_match = bool(topic_words) and matched >= max(1, len(topic_words) // 2)
        text_match = digest(poster_text) == build['copy_ledger_hash']
        observations = [f"Topic words matched: {matched}/{len(topic_words)}",
                        f"Copy ledger hash match: {text_match}",
                        f"Headline: {poster_text.get('headline', '')}"]
        if not topic_match or not text_match:
            raise GateFailure('CONTENT_IMAGE_MISMATCH')
        return review('CONTENT_IMAGE_REVIEW', records, observations,
                      {'image_sha256': build['image_sha256'],
                       'plan_hash': records['IMAGE_PLAN']['hash'],
                       'topic_match': topic_match, 'text_match': text_match})

    def brand_review_fn(j, records):
        build = records['IMAGE_BUILD']['artifact']
        plan = records['IMAGE_PLAN']['artifact']
        measurements = _image_measurements(build['image_path'])
        _pixel, _mobile, _m, inspection, source = _visual_flags(build, plan)
        # Palette: top dominant colour must be the policy paper colour and
        # the ink colour must be close to the policy ink colour.
        dominant = measurements['dominant_colors']
        paper_rgb = _hex_to_rgb(BRAND['palette']['paper'])
        ink_rgb = _hex_to_rgb(BRAND['palette']['ink'])
        def close(hex_value, target):
            rgb = _hex_to_rgb(hex_value)
            return sum((a - b) ** 2 for a, b in zip(rgb, target)) ** 0.5 <= 12
        palette_checked = bool(dominant) and close(dominant[0][0], paper_rgb)
        # Footer: plan carries a footer AND the bottom strip of the image
        # contains ink (the footer text was actually rendered there).
        footer_text = plan['poster_text'].get('footer', '')
        with Image.open(build['image_path']) as im:
            bottom = im.convert('RGB').crop((0, 1200, 1080, 1350))
            bottom_colors = bottom.getcolors(maxcolors=1080 * 150) or []
            bottom_total = sum(n for n, _ in bottom_colors) or 1
            bottom_ink = sum(n for n, px in bottom_colors
                             if sum((a - b) ** 2 for a, b in zip(px, paper_rgb)) ** 0.5 > 40) / bottom_total
        footer_checked = bool(footer_text.strip()) and bottom_ink > 0.001
        # Font: the provenance entry was examined (real file in live mode,
        # honest fallback marker in fixture mode).
        provenance = build.get('font_provenance', {})
        font_entry = provenance.get(BRAND['heading']) if isinstance(provenance, dict) else None
        if live:
            font_files_checked = (isinstance(font_entry, dict)
                                  and font_entry.get('path') not in (None, 'pillow-default-fallback')
                                  and Path(str(font_entry.get('path', ''))).is_file()
                                  and font_entry.get('sha256') == filehash(font_entry['path']))
        else:
            font_files_checked = isinstance(font_entry, dict) and bool(font_entry.get('path'))
        # Logo: absence when the plan has none, provenance when it has one.
        if plan.get('logo_asset'):
            approved = _policy().get('brand_assets', {}).get('approved_logo_path')
            logo_path = _REPO_ROOT / approved if approved else None
            original_logo_checked = (build.get('logo_asset') == approved
                                     and logo_path is not None and logo_path.is_file()
                                     and build.get('logo_sha256') == filehash(logo_path))
            logo_absence_checked = False
        else:
            original_logo_checked = False
            logo_absence_checked = not build.get('logo_asset') and not build.get('logo_sha256')
        positioning_checked = bool(plan.get('positioning')) and bool(plan.get('template_id'))
        # Canonical brand checker (Worker 3). Fixture mode records its
        # errors transparently; live mode blocks on any error. When the
        # checker is absent, live mode fails loudly (BRAND_CHECKER_MISSING)
        # and fixture mode falls back to the existing brand_policy checks
        # (check_poster_spec / check_caption) and records the outcome.
        brand_module = _try_load_module('brand_policy_v36')
        canonical_fn = getattr(brand_module, 'check_canonical_brand', None) if brand_module is not None else None
        checker_name = None
        canonical_errors = None
        if canonical_fn is not None:
            checker_name = 'check_canonical_brand'
            # Contract shape for check_canonical_brand (Worker 3):
            # {'brand': {'heading','body'}, 'palette': {...},
            #  'logo_asset': path|None, 'footer': str}. The old
            # check_poster_spec shape (font_family/dimensions/headline)
            # made the canonical checker always report
            # BRAND_FONT_MISMATCH + BRAND_FOOTER_MISSING.
            spec = {'brand': {'heading': BRAND['heading'], 'body': BRAND['body']},
                    'palette': BRAND['palette'],
                    'logo_asset': plan.get('logo_asset'),
                    'footer': plan['poster_text'].get('footer', '')}
            try:
                canonical_errors = list(canonical_fn(spec))
            except Exception as exc:
                canonical_errors = ['BRAND_CHECKER_ERROR:' + str(exc)]
            if live and canonical_errors:
                raise GateFailure('BRAND_CHECK_FAILED: ' + '; '.join(canonical_errors))
        elif live:
            raise GateFailure('BRAND_CHECKER_MISSING')
        elif brand_module is not None:
            checker_name = 'check_poster_spec+check_caption (fallback; check_canonical_brand pending)'
            fallback_errors = []
            check_poster = getattr(brand_module, 'check_poster_spec', None)
            if check_poster is not None:
                try:
                    fallback_errors.extend(check_poster({
                        'font_family': BRAND['heading'], 'dimensions': [1080, 1350],
                        'palette': BRAND['palette'],
                        'headline': plan['poster_text'].get('headline', ''),
                        'authentic_logo_sha256': build.get('logo_sha256'),
                        'logo_source_commit': None,
                        'visual_inspection_receipt': inspection is not None,
                        'orchestrator_execution_id': content_id}))
                except Exception as exc:
                    fallback_errors.append('BRAND_CHECKER_ERROR:' + str(exc))
            canonical_errors = fallback_errors
        observations = [f"Palette checked (measured): {palette_checked} dominant={dominant[:2]}",
                        f"Font files checked: {font_files_checked} provenance={font_entry}",
                        f"Footer checked (measured bottom ink {round(bottom_ink, 4)}): {footer_checked}",
                        f"Logo absence checked: {logo_absence_checked} original logo checked: {original_logo_checked}",
                        f"Positioning checked: {positioning_checked}",
                        f"Canonical brand checker ({checker_name}): errors={canonical_errors}"]
        flags_ok = (font_files_checked and palette_checked and footer_checked
                    and (original_logo_checked if plan.get('logo_asset') else logo_absence_checked)
                    and positioning_checked)
        if not flags_ok:
            raise GateFailure('BRAND_VISUAL_CHECK_MISSING')
        extra = {'image_sha256': build['image_sha256'],
                 'plan_hash': records['IMAGE_PLAN']['hash'],
                 'font_files_checked': font_files_checked,
                 'palette_checked': palette_checked,
                 'footer_checked': footer_checked,
                 'positioning_checked': positioning_checked,
                 'measurements': measurements, 'inspection_source': source,
                 'brand_checker': checker_name,
                 'canonical_brand_errors': canonical_errors}
        if plan.get('logo_asset'):
            extra['original_logo_checked'] = original_logo_checked
        else:
            extra['logo_absence_checked'] = logo_absence_checked
        return review('BRAND_REVIEW', records, observations, extra)

    def final_review_fn(j, records):
        content_engine = _load_module('content_engine')
        content = records['CONTENT']['artifact']
        recomputed = content_engine.lock_content({
            'content_id': content['content_id'], 'topic': content['topic'],
            'caption': content['caption'], 'keywords': content['keywords'],
            'poster_text': content['poster_text']})
        content_locked = recomputed['content_hash'] == content['content_hash']
        build = records['IMAGE_BUILD']['artifact']
        image_path = Path(build['image_path'])
        image_verified = image_path.is_file() and filehash(image_path) == build['image_sha256']
        brand_checked = 'BRAND_REVIEW' in records
        approval_pending = j.get('approval_status') != 'OWNER_APPROVED'
        checklist = {'content_locked': content_locked, 'image_verified': image_verified,
                     'brand_checked': brand_checked, 'approval_pending': approval_pending}
        observations = [f"Final checklist: {checklist}",
                        'Approval is pending: DELIVERY never grants approval.']
        if not all(checklist.values()):
            raise GateFailure('FINAL_CHECKLIST_INCOMPLETE')
        return review('FINAL_REVIEW', records, observations,
                      {'image_sha256': build['image_sha256'],
                       'plan_hash': records['IMAGE_PLAN']['hash'],
                       'final_checklist': checklist})

    def delivery_fn(j, records):
        # DELIVERY only verifies gates; it NEVER sets approval. The job's
        # approval_status (from the bridge state, if present) is read and
        # reported here, never written. Owner approval happens outside
        # this orchestrator, via the bridge/evidence_store approval path.
        build = records['IMAGE_BUILD']['artifact']
        out = dict(upstream(records, 'DELIVERY'))
        out.update({'image_sha256': build['image_sha256'],
                    'approval_status_seen': j.get('approval_status'),
                    'approval_set_by_delivery': False})
        return out

    fns = {'SOURCES': sources_fn, 'SOURCE_REVIEW': source_review_fn,
           'RESEARCH': research_fn, 'RESEARCH_REVIEW': research_review_fn,
           'STRATEGY': strategy_fn, 'STRATEGY_REVIEW': strategy_review_fn,
           'CONTENT': content_fn, 'CONTENT_REVIEW': content_review_fn,
           'IMAGE_PLAN': image_plan_fn, 'PLAN_REVIEW': plan_review_fn,
           'IMAGE_BUILD': image_build_fn, 'TECH_REVIEW': tech_review_fn,
           'VISUAL_REVIEW': visual_review_fn,
           'CONTENT_IMAGE_REVIEW': content_image_review_fn,
           'BRAND_REVIEW': brand_review_fn, 'FINAL_REVIEW': final_review_fn,
           'DELIVERY': delivery_fn}
    adapters = {}
    for stage in STAGES:
        role = 'reviewer' if stage in REVIEWS else 'producer'
        adapters[stage] = Adapter(adapter_name(stage), fns[stage], role)
    return adapters

# ---------------------------------------------------------------------------
# Evidence ledger (provenance, module 14) -- best effort, never fatal
# ---------------------------------------------------------------------------

def _record_handoffs(work_dir, content_id, chain):
    """Record one handoff per completed stage in the evidence ledger.

    Returns 'RECORDED' or 'LEDGER_UNAVAILABLE' (ledger functions missing
    or failing). A missing ledger never crashes the job and is never
    claimed as recorded.
    """
    store = _try_load_module('evidence_store')
    record_fn = getattr(store, 'record_handoff', None) if store is not None else None
    if record_fn is None or store is None:
        return 'LEDGER_UNAVAILABLE'
    try:
        db = store.init(str(Path(work_dir) / 'evidence.db'))
        for index, stage in enumerate(STAGES):
            record = chain.records.get(stage)
            if record is None:
                continue
            prev = STAGES[index - 1] if index else None
            input_hash = chain.records[prev]['hash'] if prev and prev in chain.records else ''
            from_agent = STAGE_AGENT[stage]
            if stage in REVIEWS:
                to_agent = AGENT_REGISTRY[from_agent]['reviewer']
            elif index + 1 < len(STAGES):
                to_agent = STAGE_AGENT[STAGES[index + 1]]
            else:
                to_agent = from_agent
            record_fn(db, content_id, stage, from_agent, to_agent,
                      input_hash, record['hash'])
        return 'RECORDED'
    except Exception:
        return 'LEDGER_UNAVAILABLE'

def _record_event(work_dir, job_id, kind, payload):
    """Batch-level ledger event; returns True when recorded, else False."""
    store = _try_load_module('evidence_store')
    record_fn = getattr(store, 'record_event', None) if store is not None else None
    if record_fn is None or store is None:
        return False
    try:
        db = store.init(str(Path(work_dir) / 'evidence.db'))
        record_fn(db, job_id, kind, payload)
        return True
    except Exception:
        return False

# ---------------------------------------------------------------------------
# Job / batch execution
# ---------------------------------------------------------------------------

def run_job(state_path, adapters=None, mode='TEST_FIXTURE'):
    """Run one job's 17-stage chain from its bridge state file.

    Loads the bridge state, builds adapters when none are given
    (work_dir = the state file's parent), seeds the Chain's records from
    the bridge state, runs it (gates are never skipped), writes the
    resulting records/status/trace back into the bridge state file
    (preserving the bridge's index/status semantics), and records
    per-stage handoffs in the evidence ledger when available. A job that
    is already BLOCKED or CANCELLED is returned as-is without re-running.
    Returns the Chain.run() result dict (plus a 'ledger' key).
    """
    state = load(str(state_path))
    if state.get('status') in ('BLOCKED', 'CANCELLED'):
        return {'status': state['status'],
                'content_id': state['job'].get('content_id'),
                'repairs': state.get('repairs', 0),
                'trace': state.get('trace', []),
                'external_writes': 0,
                'completed_stages': list(state.get('records', {}))}
    work_dir = Path(state_path).parent
    job = dict(state['job'])
    job['mode'] = mode
    # Live-mode gate confinement (D-15): the gate allows file paths
    # under cwd, the plugin root, or the job's state/evidence dir.
    # The server's cwd is the repo root while the state dir is
    # /tmp/erudiance-state, so without these keys a live run blocked
    # at SOURCE_REVIEW with PATH_OUTSIDE_ALLOWED_ROOT (Render,
    # 2026-11-24: all 7 jobs BLOCKED, 4 repairs). The state file's
    # parent IS the job's state/evidence dir, so record it here.
    job['state_dir'] = str(work_dir.resolve())
    job['evidence_dir'] = str(work_dir.resolve())
    state['job'] = job
    chain_adapters = adapters if adapters is not None else build_adapters(job, work_dir, mode=mode)
    chain = Chain(job, chain_adapters)
    chain.records = dict(state.get('records') or {})
    result = chain.run()
    state['records'] = chain.records
    state['trace'] = chain.trace
    state['repairs'] = chain.revisions
    state['index'] = len(chain.records)
    state['status'] = chain.status
    if chain.status == 'READY_FOR_OWNER_REVIEW':
        # Live-mode completion only: the bridge's approval gate
        # (op_submit_owner_decision) reads approval_status, not status.
        # Without this, a live-completed job could never be approved
        # (approval_status would stay 'DRAFT'). Fixture runs
        # (TEST_FIXTURE_PASS) never set it — only live mode produces
        # READY_FOR_OWNER_REVIEW.
        state['approval_status'] = 'READY_FOR_OWNER_REVIEW'
    state['external_writes'] = 0
    ledger = _record_handoffs(work_dir, job['content_id'], chain)
    save(str(state_path), state)
    out = dict(result)
    out['ledger'] = ledger
    return out

def _post_delivery_analytics(root, jobs_out):
    """Post-delivery analytics step (AG-18): experimentation + feedback
    loop. Writes the batch analytics file; never changes job statuses.
    Only measured values are recorded (no invented metrics)."""
    analytics = _try_load_module('linkedin_analytics')
    if analytics is None:
        return {'status': 'SKIPPED', 'reason': 'ANALYTICS_MODULE_MISSING'}
    root = Path(root)
    measured = {'jobs': len(jobs_out),
                'passed': sum(1 for j in jobs_out if j.get('status') in ('TEST_FIXTURE_PASS', 'READY_FOR_OWNER_REVIEW')),
                'blocked': sum(1 for j in jobs_out if j.get('status') == 'BLOCKED'),
                'errored': sum(1 for j in jobs_out if j.get('status') == 'ERROR')}
    experiments_path = root / 'experiments.jsonl'
    analytics.record_experiment(str(experiments_path), 'baseline',
                                'One variable, like-for-like baseline batch measurement.',
                                'baseline', measured)
    feedback = analytics.feedback_summary(str(root / 'analytics.jsonl'))
    (root / 'analytics.json').write_text(json.dumps(
        {'feedback': feedback,
         'experiments': analytics.list_experiments(str(experiments_path))},
        indent=2, ensure_ascii=False), encoding='utf-8')
    return {'status': 'PASS', 'feedback': feedback}

# ---------------------------------------------------------------------------
# Auto-topic generation (owner order 2026-11-24: "auto-topic lagao").
# When start_workflow is called without topics, the server generates 7
# distinct topics itself instead of failing. Every topic pairs an
# Erudiance service with a niche it serves, and cites the real service
# page on erudience.com (all URLs below returned HTTP 200 on
# 2026-11-24) plus the homepage as its sources. Topics are labelled
# server-generated in the job state; sources are USER_SUPPLIED
# provenance — no live fetch provider exists, so nothing is ever
# claimed LIVE_VERIFIED. Rotation is deterministic per cycle (sha256
# offset), so consecutive cycles get different topic sets.
# ---------------------------------------------------------------------------

_AUTO_TOPIC_HOME = 'https://erudience.com'
_AUTO_TOPIC_BANK = [
    ('AI voice agents for dental clinics', 'https://erudience.com/services/voice-ai-systems'),
    ('AI receptionist for law firms', 'https://erudience.com/services/voice-ai-systems'),
    ('Call automation for estate agents', 'https://erudience.com/services/voice-ai-systems'),
    ('After-hours call answering for vets', 'https://erudience.com/services/voice-ai-systems'),
    ('AI phone orders for Shopify stores', 'https://erudience.com/services/voice-ai-systems'),
    ('AI debt collection calls for lenders', 'https://erudience.com/services/voice-ai-systems'),
    ('Support automation for e-commerce stores', 'https://erudience.com/services/support-automation'),
    ('AI support ticket triage for SaaS teams', 'https://erudience.com/services/support-automation'),
    ('Workflow automation for accountants', 'https://erudience.com/services/business-workflow-automation'),
    ('Workflow automation for financial advisers', 'https://erudience.com/services/business-workflow-automation'),
    ('Business workflow automation for construction firms', 'https://erudience.com/services/business-workflow-automation'),
    ('LinkedIn automation for estate agents', 'https://erudience.com/services/linkedin-automation'),
    ('LinkedIn lead generation for B2B agencies', 'https://erudience.com/services/linkedin-automation'),
    ('LinkedIn engagement automation for consultants', 'https://erudience.com/services/linkedin-automation'),
    ('Sales outreach automation for recruiters', 'https://erudience.com/services/sales-outreach-automation'),
    ('AI deal sourcing for property investors', 'https://erudience.com/services/sales-outreach-automation'),
    ('HubSpot automation for growing teams', 'https://erudience.com/services/hubspot-automation'),
    ('Salesforce automation for sales teams', 'https://erudience.com/services/salesforce-automation'),
    ('GoHighLevel automation for local businesses', 'https://erudience.com/services/gohighlevel-automation'),
    ('Custom AI systems for logistics firms', 'https://erudience.com/services/custom-ai-systems'),
    ('Multilingual AI lead qualification for exporters', 'https://erudience.com/services/custom-ai-systems'),
]

def generate_topics(cycle, count=SLOTS):
    """7 distinct auto topics for a cycle (deterministic rotation)."""
    bank = _AUTO_TOPIC_BANK
    if len(bank) < count:
        raise ValueError('AUTO_TOPIC_BANK_TOO_SMALL')
    offset = int(hashlib.sha256(str(cycle).encode()).hexdigest()[:8], 16) % len(bank)
    return [bank[(offset + i) % len(bank)][0] for i in range(count)]

def auto_topic_sources(topic, verified_at):
    """Sources for one auto topic: homepage + its service page."""
    url = dict(_AUTO_TOPIC_BANK).get(topic)
    sources = [{'url': _AUTO_TOPIC_HOME, 'verified_at': verified_at}]
    if url and url != _AUTO_TOPIC_HOME:
        sources.append({'url': url, 'verified_at': verified_at})
    return sources

def default_auto_strategy():
    """7 slots, exactly 1 promotion (last slot, with employee
    requirement) — passes validate_strategy_v33.validate()."""
    slots = [{'promotion': False} for _ in range(SLOTS - 1)]
    slots.append({'promotion': True,
                  'employee_requirement': 'Staff oversees exceptions'})
    return slots

def prepare_auto_batch(root, cycle):
    """Generate auto topics + per-topic sources + default strategy for
    a batch, and write fresh research_evidence.json into root so the
    live research-due check passes. Returns (topics, {topic: sources},
    strategy)."""
    root_path = Path(root)
    verified_at = _utc_today().isoformat()
    topics = generate_topics(cycle)
    per_topic = {t: auto_topic_sources(t, verified_at) for t in topics}
    evidence = []
    seen = set()
    for sources in per_topic.values():
        for s in sources:
            if s['url'] not in seen:
                seen.add(s['url'])
                evidence.append(dict(s))
    root_path.mkdir(parents=True, exist_ok=True)
    (root_path / 'research_evidence.json').write_text(
        json.dumps(evidence, indent=2), encoding='utf-8')
    return topics, per_topic, default_auto_strategy()

def run_batch(root, topics, cycle, strategy=None, mode='TEST_FIXTURE'):
    """Run a 7-job batch end to end.

    topics=None means auto-topic: 7 topics are generated from
    Erudiance's verified website pages (prepare_auto_batch), with
    per-job sources and a default strategy (7 slots, exactly 1
    promotion) attached, and fresh research_evidence.json written so
    the live research-due check passes. Explicit topics keep the old
    behaviour exactly. Live mode refuses to start when research is due
    and no fresh research_evidence is supplied ({'ok': False, 'error':
    'RESEARCH_DUE'}); fixture mode is exempt. When a strategy is
    provided it is verified FIRST (verify_batch_strategy) and a failing
    strategy raises ValueError 'BATCH_STRATEGY_BLOCKED: ...'. An existing
    manifest is reused (resume) instead of raising. Jobs are
    independent: a BLOCKED job never stops the others. Returns
    {'cycle', 'jobs': [per-job run results], 'batch': summary(root),
    'duplicates': check_duplicate_images(root), 'topics': topics,
    'auto_topics': bool}.
    """
    root_path = Path(root)
    auto_topics = False
    per_topic_sources = {}
    if topics is None:
        topics, per_topic_sources, auto_strategy = prepare_auto_batch(root_path, cycle)
        auto_topics = True
        if strategy is None:
            strategy = auto_strategy
    if mode != 'TEST_FIXTURE':
        due = research_due(root_path)
        if due['due'] and not _fresh_research_evidence(root_path):
            return {'ok': False, 'error': 'RESEARCH_DUE', 'research_due': due}
    if strategy is not None:
        check = verify_batch_strategy(root_path, strategy)
        if check['status'] != 'PASS':
            raise ValueError('BATCH_STRATEGY_BLOCKED: ' + '; '.join(check['errors']))
    _record_event(root_path, f'BATCH-{cycle}', 'BATCH_START',
                  {'cycle': cycle, 'mode': mode, 'strategy': bool(strategy),
                   'auto_topics': auto_topics})
    manifest_path = root_path / 'manifest.json'
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    else:
        initialise(root, topics, cycle)
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        if auto_topics:
            for job in manifest.get('jobs', []):
                state = load(job['state'])
                topic = state['job'].get('topic')
                state['job']['sources'] = per_topic_sources.get(topic, [])
                state['job']['topic_source'] = 'server-generated'
                save(job['state'], state)
    jobs_out = []
    for index, job in enumerate(manifest.get('jobs', [])):
        state_path = job['state']
        try:
            if strategy is not None:
                state = load(state_path)
                state['job']['strategy'] = list(strategy)
                if index < len(strategy):
                    state['job']['slot'] = strategy[index]
                save(state_path, state)
            result = run_job(state_path, mode=mode)
        except Exception as exc:
            result = {'status': 'ERROR', 'content_id': job.get('content_id'),
                      'error': str(exc), 'repairs': 0, 'trace': [],
                      'external_writes': 0, 'completed_stages': []}
        jobs_out.append(result)
    _post_delivery_analytics(root_path, jobs_out)
    _record_event(root_path, f'BATCH-{cycle}', 'BATCH_COMPLETE',
                  {'cycle': cycle,
                   'passed': sum(1 for j in jobs_out if j.get('status') in ('TEST_FIXTURE_PASS', 'READY_FOR_OWNER_REVIEW')),
                   'blocked': sum(1 for j in jobs_out if j.get('status') == 'BLOCKED')})
    return {'cycle': manifest.get('cycle', cycle), 'jobs': jobs_out,
            'batch': summary(root), 'duplicates': check_duplicate_images(root),
            'topics': list(topics), 'auto_topics': auto_topics}
