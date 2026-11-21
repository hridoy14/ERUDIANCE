"""Seven independent content/image jobs. Never treat a collage as a deliverable."""
from pathlib import Path
import json
from PIL import Image
from chatgpt_bridge_v43 import start,load,next_step

SLOTS=7

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
    return {'cycle':manifest['cycle'],'expected':SLOTS,'ready':sum(r['status']=='READY_FOR_OWNER_REVIEW' for r in rows),'items':rows,'batch_status':'READY_FOR_OWNER_REVIEW' if len(rows)==SLOTS and all(r['status']=='READY_FOR_OWNER_REVIEW' for r in rows) else 'NOT_APPROVED'}
