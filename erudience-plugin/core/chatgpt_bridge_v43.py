"""ChatGPT tool handoff: durable, fail-closed 17-stage checkpoint controller.
Tools execute OUTSIDE this process; evidence receipts must be submitted back. No fake providers.
"""
import argparse,json,os,tempfile
from pathlib import Path
from hashlib import sha256
from gate_chain_v41 import STAGES,REPAIR,Adapter,Chain,digest,GateFailure

def save(path,state):
 p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.NamedTemporaryFile('w',dir=p.parent,delete=False,encoding='utf8') as f:
  json.dump(state,f,indent=2,ensure_ascii=False);tmp=f.name
 os.replace(tmp,p)
def load(path):return json.loads(Path(path).read_text(encoding='utf8'))
def start(path,job):
 if Path(path).exists():raise ValueError('JOB_ALREADY_EXISTS')
 if not job.get('content_id') or not job.get('topic'):raise ValueError('JOB_REQUIRED')
 state={'schema':'erudience.chatgpt.v4.3','job':job,'index':0,'records':{},'trace':[],'repairs':0,'status':'AWAITING_TOOL_EXECUTION','external_writes':0}
 save(path,state);return state
def next_step(state):
 if state['status']!='AWAITING_TOOL_EXECUTION':return {'status':state['status']}
 stage=STAGES[state['index']];previous=STAGES[state['index']-1] if state['index'] else None
 return {'status':state['status'],'stage':stage,'requires_independent_reviewer':stage.endswith('REVIEW'),'upstream_hash':state['records'][previous]['hash'] if previous else None,'content_hash':state['records'].get('CONTENT',{}).get('hash'),'plan_hash':state['records'].get('IMAGE_PLAN',{}).get('hash'),'image_sha256':state['records'].get('IMAGE_BUILD',{}).get('artifact',{}).get('image_sha256')}
def submit(path,stage,adapter_name,role,artifact):
 state=load(path)
 if state['status']!='AWAITING_TOOL_EXECUTION':raise ValueError('JOB_NOT_ACCEPTING_RECEIPTS')
 if STAGES[state['index']]!=stage:raise ValueError('OUT_OF_ORDER_STAGE')
 # Reuse the same production gate validators as the synchronous controller.
 c=Chain(state['job'],{},limit=3);c.records=state['records']
 try:
  c.verify(stage,artifact,Adapter(adapter_name,lambda *_:artifact,role))
  h=digest(artifact);state['records'][stage]={'artifact':artifact,'hash':h,'adapter':adapter_name}
  state['trace'].append({'stage':stage,'event':'PASS','sha256':h});state['index']+=1
  if state['index']==len(STAGES):state['status']='TEST_FIXTURE_PASS' if state['job'].get('mode')=='TEST_FIXTURE' else 'READY_FOR_OWNER_REVIEW'
 except Exception as e:
  target=e.repair_at if isinstance(e,GateFailure) and e.repair_at in STAGES and STAGES.index(e.repair_at)<=state['index'] else REPAIR[stage]
  state['repairs']+=1;state['trace'].append({'stage':stage,'event':'FAIL','reason':str(e),'return_to':target,'repair':state['repairs']})
  if state['repairs']>3:state['status']='BLOCKED'
  else:
   for s in STAGES[STAGES.index(target):]:state['records'].pop(s,None)
   state['index']=STAGES.index(target)
 save(path,state);return {'status':state['status'],'next':next_step(state),'repairs':state['repairs'],'last':state['trace'][-1]}
def main():
 p=argparse.ArgumentParser();p.add_argument('command',choices=['start','next','submit','status']);p.add_argument('--state',required=True);p.add_argument('--job');p.add_argument('--stage');p.add_argument('--adapter');p.add_argument('--role',default='producer');p.add_argument('--receipt');a=p.parse_args()
 if a.command=='start':out=start(a.state,load(a.job))
 elif a.command=='next':out=next_step(load(a.state))
 elif a.command=='status':out=load(a.state)
 else:
  if not all([a.stage,a.adapter,a.receipt]):p.error('submit requires --stage --adapter --receipt')
  out=submit(a.state,a.stage,a.adapter,a.role,load(a.receipt))
 print(json.dumps(out,indent=2,ensure_ascii=False))
if __name__=='__main__':main()
