import unittest,tempfile,json,hashlib
from datetime import date,datetime,timedelta,timezone
from pathlib import Path
from unittest import mock
from PIL import Image
from batch_guard_v45 import initialise,summary,AGENT_REGISTRY,STAGE_AGENT,build_adapters,run_job,run_batch,run_plan,plan_summary,verify_batch_strategy,check_duplicate_images,research_due,generate_topics,prepare_auto_batch,default_auto_strategy
import batch_guard_v45
from competitor_monitor import assess_market_signals
from chatgpt_bridge_v43 import load,save
from gate_chain_v41 import Chain,Adapter,GateFailure,STAGES,filehash
class BatchTests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=self.tmp.name
 def tearDown(self):self.tmp.cleanup()
 def test_seven_independent_jobs(self):
  x=initialise(self.root,[f'Topic {i}' for i in range(7)],'20261121');self.assertEqual(len(x['items']),7);self.assertEqual(x['ready'],0);self.assertEqual(len({r['content_id'] for r in x['items']}),7)
 def test_no_duplicate_topics(self):
  with self.assertRaisesRegex(ValueError,'SEVEN_DISTINCT'):initialise(self.root,['Same']*7,'20261121')
 def test_no_reinitialisation(self):
  initialise(self.root,[f'Topic {i}' for i in range(7)],'20261121')
  with self.assertRaisesRegex(ValueError,'BATCH_ALREADY'):initialise(self.root,[f'Topic {i}' for i in range(7)],'20261121')
 def test_image_must_be_portrait(self):
  p=Path(self.root)/'collage.png';Image.new('RGB',(2100,1350)).save(p)
  c=Chain({'content_id':'ER-1','topic':'T','mode':'TEST_FIXTURE'},{});c.records={'IMAGE_PLAN':{'hash':'plan','artifact':{'poster_text':'hello'}},'PLAN_REVIEW':{'hash':'review'}}
  from gate_chain_v41 import filehash,digest
  with self.assertRaises(GateFailure) as cm:c.verify('IMAGE_BUILD',{'content_id':'ER-1','plan_hash':'plan','upstream_hash':'review','image_path':str(p),'image_sha256':filehash(p),'copy_ledger_hash':digest('hello'),'font_provenance':{'Sora':1,'Sora':1}},Adapter('builder',None))
  self.assertEqual(str(cm.exception),'INDIVIDUAL_PORTRAIT_PNG_REQUIRED')
 def test_wrong_content_id_rejected(self):
  c=Chain({'content_id':'ER-1','topic':'T'},{});c.records={'CONTENT':{'hash':'h','artifact':{'topic':'T','caption':'caption'}},'CONTENT_REVIEW':{'hash':'review'}}
  with self.assertRaisesRegex(GateFailure,'PLAN_CONTENT_ID_MISMATCH'):c.verify('IMAGE_PLAN',{'content_id':'ER-2','upstream_hash':'review'},Adapter('planner',None))
class AutoTopicTests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=self.tmp.name
 def tearDown(self):self.tmp.cleanup()
 def test_generate_topics_seven_distinct(self):
  topics=generate_topics('20261124')
  self.assertEqual(len(topics),7);self.assertEqual(len(set(topics)),7)
  self.assertEqual(topics,generate_topics('20261124'))
  self.assertTrue(all(isinstance(t,str) and t.strip() for t in topics))
 def test_generate_topics_rotates_by_cycle(self):
  self.assertNotEqual(generate_topics('20261124'),generate_topics('20261125'))
 def test_default_auto_strategy_passes(self):
  self.assertEqual(verify_batch_strategy(default_auto_strategy(),None)['status'],'PASS')
 def test_prepare_auto_batch_writes_evidence(self):
  topics,per_topic,strategy=prepare_auto_batch(self.root,'20261124')
  self.assertEqual(len(topics),7)
  ev=json.loads((Path(self.root)/'research_evidence.json').read_text())
  self.assertTrue(any(e['url']=='https://erudience.com' for e in ev))
  for t in topics:
   self.assertTrue(any(s['url'].startswith('https://erudience.com/services/') for s in per_topic[t]))
 def test_run_batch_auto_topics_fixture(self):
  r=run_batch(self.root,None,'20261124')
  self.assertTrue(r['auto_topics']);self.assertEqual(len(r['jobs']),7)
  self.assertTrue(all(j['status']=='TEST_FIXTURE_PASS' for j in r['jobs']))
  self.assertEqual(len(set(r['topics'])),7)
  manifest=json.loads((Path(self.root)/'manifest.json').read_text())
  for job in manifest['jobs']:
   state=load(job['state'])
   self.assertEqual(state['job'].get('topic_source'),'server-generated')
   self.assertTrue(state['job'].get('sources'))
   path=state['records']['IMAGE_BUILD']['artifact']['image_path']
   with Image.open(path) as im:self.assertEqual(im.size,(1080,1350))
 def test_run_batch_auto_topics_live_cwd_differs(self):
  # Regression: the live gate confines evidence paths to cwd, the
  # plugin root, or the job's state/evidence dir. On Render the
  # server cwd is the repo root while the state dir is
  # /tmp/erudiance-state, so a live run blocked at SOURCE_REVIEW
  # with PATH_OUTSIDE_ALLOWED_ROOT (all 7 jobs BLOCKED, 4 repairs)
  # even though the same run passes when cwd == batch root. This
  # test runs WITHOUT chdir, so it fails before the run_job fix
  # (job['state_dir'] set from the state file's parent) and passes
  # after it.
  r=run_batch(self.root,None,'20261124',mode='LIVE')
  self.assertTrue(r['auto_topics'])
  self.assertTrue(all(j['status']=='READY_FOR_OWNER_REVIEW' for j in r['jobs']),r['jobs'])
  self.assertEqual(r['batch']['batch_status'],'READY_FOR_OWNER_REVIEW')
 def test_run_batch_auto_topics_live(self):
  import os
  old=os.getcwd()
  try:
   os.chdir(self.root)
   r=run_batch(self.root,None,'20261124',mode='LIVE')
  finally:
   os.chdir(old)
  self.assertTrue(r['auto_topics'])
  self.assertTrue(all(j['status']=='READY_FOR_OWNER_REVIEW' for j in r['jobs']),r['jobs'])
  self.assertEqual(r['batch']['batch_status'],'READY_FOR_OWNER_REVIEW')
  manifest=json.loads((Path(self.root)/'manifest.json').read_text())
  seen=set()
  for job in manifest['jobs']:
   state=load(job['state'])
   self.assertEqual(state['approval_status'],'READY_FOR_OWNER_REVIEW')
   self.assertEqual(state['job'].get('topic_source'),'server-generated')
   self.assertTrue(state['job'].get('sources'))
   path=state['records']['IMAGE_BUILD']['artifact']['image_path']
   with Image.open(path) as im:self.assertEqual(im.size,(1080,1350))
   seen.add(filehash(path))
  self.assertEqual(len(seen),7)
 def test_run_batch_explicit_topics_live(self):
  # Explicit topics (e.g. researched by Claude) with caller-supplied
  # sources run live: the sources the caller actually read are
  # attached (USER_SUPPLIED) with fresh research evidence. Without
  # caller-supplied sources the live gates apply as before
  # (RESEARCH_DUE / LIVE_SOURCES_REQUIRED) — see
  # test_run_batch_live_research_due.
  from datetime import date as _date
  today = _date.today().isoformat()
  topics=['AI voice agents for dental clinics','AI receptionist for law firms','Call automation for estate agents','After-hours call answering for vets','AI phone orders for Shopify stores','Support automation for e-commerce stores','Workflow automation for accountants']
  urls={'AI voice agents for dental clinics':'https://erudience.com/services/voice-ai-systems','AI receptionist for law firms':'https://erudience.com/services/voice-ai-systems','Call automation for estate agents':'https://erudience.com/services/voice-ai-systems','After-hours call answering for vets':'https://erudience.com/services/voice-ai-systems','AI phone orders for Shopify stores':'https://erudience.com/services/voice-ai-systems','Support automation for e-commerce stores':'https://erudience.com/services/support-automation','Workflow automation for accountants':'https://erudience.com/services/business-workflow-automation'}
  sources={t:[{'url':'https://erudience.com','verified_at':today},{'url':urls[t],'verified_at':today}] for t in topics}
  r=run_batch(self.root,topics,'20261124',mode='LIVE',per_topic_sources=sources)
  self.assertFalse(r['auto_topics'])
  self.assertTrue(all(j['status']=='READY_FOR_OWNER_REVIEW' for j in r['jobs']),r['jobs'])
  self.assertEqual(r['batch']['batch_status'],'READY_FOR_OWNER_REVIEW')
  manifest=json.loads((Path(self.root)/'manifest.json').read_text())
  for job in manifest['jobs']:
   state=load(job['state'])
   self.assertEqual(state['job'].get('topic_source'),'user-supplied')
   self.assertTrue(state['job'].get('sources'))
class PlanTests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=self.tmp.name
 def tearDown(self):self.tmp.cleanup()
 def test_generate_topics_30_distinct(self):
  topics=generate_topics('20261124',30)
  self.assertEqual(len(topics),30);self.assertEqual(len(set(topics)),30)
 def test_run_plan_1day_fixture(self):
  r=run_plan(self.root,None,'20261124',plan='1-day')
  self.assertEqual(r['plan'],'1-day');self.assertEqual(len(r['jobs']),1)
  self.assertTrue(all(j['status']=='TEST_FIXTURE_PASS' for j in r['jobs']))
  self.assertEqual([s['day'] for s in r['schedule']],[1])
  self.assertEqual([j['scheduled_day'] for j in r['jobs']],[1])
  self.assertEqual(r['jobs'][0]['content_id'],'ER-20261124-001')
  plan=json.loads((Path(self.root)/'plan.json').read_text())
  self.assertEqual(plan['plan'],'1-day');self.assertEqual(plan['kind'],'daily')
  self.assertEqual(len(plan['jobs']),1)
  agg=plan_summary(self.root)
  self.assertEqual(agg['expected'],1);self.assertEqual(len(agg['items']),1)
  self.assertEqual(agg['batch_status'],'NOT_APPROVED')  # fixture jobs are not READY
 def test_plan_summary_lists_removed_job(self):
  # Removing a daily job's state file (op_remove_content) must not
  # crash the plan report: the job shows under "removed" and the plan
  # can never read READY while a day is missing.
  run_plan(self.root,None,'20261124',plan='1-day')
  (Path(self.root)/'ER-20261124-001.json').unlink()
  agg=plan_summary(self.root)
  self.assertEqual(agg['expected'],1);self.assertEqual(agg['items'],[])
  self.assertEqual(agg['removed'],['ER-20261124-001'])
  self.assertEqual(agg['ready'],0)
  self.assertEqual(agg['batch_status'],'NOT_APPROVED')
 def test_run_plan_7day_fixture(self):
  r=run_plan(self.root,None,'20261124',plan='7-day')
  self.assertEqual(r['plan'],'7-day');self.assertEqual(len(r['jobs']),7)
  self.assertTrue(all(j['status']=='TEST_FIXTURE_PASS' for j in r['jobs']))
  self.assertEqual([s['day'] for s in r['schedule']],[1,2,3,4,5,6,7])
  self.assertEqual([j['scheduled_day'] for j in r['jobs']],[1,2,3,4,5,6,7])
 def test_run_plan_month_fixture(self):
  r=run_plan(self.root,None,'20261124',plan='1-month')
  self.assertEqual(r['plan'],'1-month');self.assertEqual(len(r['jobs']),30)
  self.assertTrue(all(j['status']=='TEST_FIXTURE_PASS' for j in r['jobs']))
  self.assertEqual(len(set(r['topics'])),30)
  self.assertEqual([s['day'] for s in r['schedule']],list(range(1,31)))
  self.assertEqual([s['week'] for s in r['schedule']],[1]*7+[2]*7+[3]*7+[4]*7+[5]*2)
  self.assertTrue(all(j['content_id'].startswith('ER-20261124-0') for j in r['jobs']))
  self.assertFalse(any('-w' in j['content_id'] for j in r['jobs']))
  # Promotion slots: days 7, 14, 21, 28 carry the promotion slot.
  for day in (7,14,21,28):
   state=load(str(Path(self.root)/('ER-20261124-%03d.json'%day)))
   self.assertTrue(state['job']['slot'].get('promotion'))
  for day in (1,8,15,22,29,30):
   state=load(str(Path(self.root)/('ER-20261124-%03d.json'%day)))
   self.assertFalse(state['job']['slot'].get('promotion'))
  plan=json.loads((Path(self.root)/'plan.json').read_text())
  self.assertEqual(plan['plan'],'1-month');self.assertEqual(plan['kind'],'daily')
  self.assertEqual(len(plan['jobs']),30)
  agg=plan_summary(self.root)
  self.assertEqual(agg['expected'],30);self.assertEqual(len(agg['items']),30)
  self.assertEqual(agg['batch_status'],'NOT_APPROVED')  # fixture jobs are not READY
  # Every daily job carries the full 7-slot strategy.
  state=load(str(Path(self.root)/'ER-20261124-030.json'))
  self.assertEqual(len(state['job']['strategy']),7)
  self.assertEqual(sum(1 for s in state['job']['strategy'] if s.get('promotion')),1)
 def test_run_plan_invalid_plan(self):
  with self.assertRaises(ValueError):
   run_plan(self.root,None,'20261124',plan='1-year')
 def test_run_plan_month_wrong_topic_count(self):
  with self.assertRaises(ValueError):
   run_plan(self.root,['only-one-topic'],'20261124',plan='1-month')
class RegistryTests(unittest.TestCase):
 def test_eighteen_agents(self):
  self.assertEqual(len(AGENT_REGISTRY),18)
  self.assertEqual(sorted(AGENT_REGISTRY),[f'AG-{i:02d}' for i in range(1,19)])
 def test_names_in_order(self):
  names=['Business Intelligence','Competitor Research','Buyer Research','Market Research','Keyword Research','Search Intent','Topic Intelligence','Content Strategist','Funnel Planner','Content Writer','SEO Optimizer','Editorial Reviewer','Fact Checker','Creative Director','Image Producer','Brand QA','Delivery Controller','Analytics']
  self.assertEqual([AGENT_REGISTRY[f'AG-{i:02d}']['name'] for i in range(1,19)],names)
 def test_no_self_review_and_distinct_reviewers(self):
  for aid,a in AGENT_REGISTRY.items():
   self.assertNotEqual(a['reviewer'],aid)
   self.assertIn(a['reviewer'],AGENT_REGISTRY)
   for key in ('id','name','stages','module','reviewer','tools','retry_policy','failure'):
    self.assertIn(key,a)
   self.assertEqual(a['id'],aid)
   self.assertEqual(a['retry_policy'],'gate-repair-3')
   self.assertEqual(a['failure'],'BLOCKED after 4th failure')
 def test_all_stages_covered(self):
  covered=set()
  for a in AGENT_REGISTRY.values():covered.update(a['stages'])
  self.assertEqual(covered,set(STAGES))
 def test_review_stages_map_to_reviewer_agents(self):
  for stage,agent in STAGE_AGENT.items():
   if stage.endswith('REVIEW'):
    self.assertIn(agent,('AG-12','AG-13','AG-16','AG-17'))

class AdapterTests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=self.tmp.name;self.job={'content_id':'ER-20261121-001','topic':'AI Voice Automation','mode':'TEST_FIXTURE'}
 def tearDown(self):self.tmp.cleanup()
 def test_all_17_stages_callable(self):
  adapters=build_adapters(self.job,self.root)
  self.assertEqual(set(adapters),set(STAGES))
  for s,a in adapters.items():
   self.assertIsInstance(a,Adapter);self.assertTrue(callable(a.fn))
   self.assertEqual(a.role,'reviewer' if s.endswith('REVIEW') else 'producer')
  for s in STAGES:
   if s.endswith('REVIEW'):
    prev=STAGES[STAGES.index(s)-1]
    self.assertNotEqual(adapters[s].name,adapters[prev].name)
 def test_run_job_full_fixture_pass(self):
  initialise(self.root,[f'Topic {i}' for i in range(7)],'20261121')
  manifest=json.loads((Path(self.root)/'manifest.json').read_text())
  state_path=manifest['jobs'][0]['state']
  r=run_job(state_path)
  self.assertEqual(r['status'],'TEST_FIXTURE_PASS');self.assertEqual(len(r['completed_stages']),17)
  state=load(state_path);self.assertEqual(state['status'],'TEST_FIXTURE_PASS');self.assertEqual(state['index'],17);self.assertEqual(len(state['records']),17)
  self.assertIn(r['ledger'],('RECORDED','LEDGER_UNAVAILABLE'))
 def test_image_plan_brief_has_no_errors_with_wired_evidence(self):
  # Live-run fix regression (2026-11-24): image_plan_fn must wire
  # evidence_refs from SOURCES, the real Sora font flag, and
  # logo_planned False (owner: logo optional). Without the wiring the
  # live IMAGE_PLAN gate fails on BRIEF_MISSING:evidence_refs /
  # LOGO_BINARY_NOT_VERIFIED / FONT_BINARY_NOT_VERIFIED.
  initialise(self.root,[f'Topic {i}' for i in range(7)],'20261121')
  manifest=json.loads((Path(self.root)/'manifest.json').read_text())
  state_path=manifest['jobs'][0]['state']
  r=run_job(state_path)
  self.assertEqual(r['status'],'TEST_FIXTURE_PASS')
  plan=load(state_path)['records']['IMAGE_PLAN']['artifact']
  self.assertEqual(plan.get('brief_validation_errors'),[])
  self.assertTrue(plan.get('poster_text',{}).get('headline'))
 def test_run_job_blocked_stays_blocked(self):
  initialise(self.root,[f'Topic {i}' for i in range(7)],'20261121')
  manifest=json.loads((Path(self.root)/'manifest.json').read_text())
  state_path=manifest['jobs'][0]['state']
  state=load(state_path);state['status']='BLOCKED';save(state_path,state)
  r=run_job(state_path)
  self.assertEqual(r['status'],'BLOCKED');self.assertEqual(r['trace'],[])
  self.assertEqual(load(state_path)['status'],'BLOCKED')
 def test_run_batch_strategy_enforcement(self):
  valid=[{"promotion":False} for _ in range(6)]+[{"promotion":True,"employee_requirement":"Staff oversees exceptions"}]
  r=run_batch(self.root,[f'Topic {i}' for i in range(7)],'20261121',strategy=valid)
  self.assertEqual(len(r['jobs']),7)
  self.assertTrue(all(j['status']=='TEST_FIXTURE_PASS' for j in r['jobs']))
  self.assertEqual(r['duplicates']['status'],'PASS')
  self.assertIn('duplicate_images',r['batch'])
 def test_run_batch_zero_promotion_rejected(self):
  with self.assertRaisesRegex(ValueError,'BATCH_STRATEGY_BLOCKED'):
   run_batch(self.root,[f'Topic {i}' for i in range(7)],'20261121',strategy=[{"promotion":False} for _ in range(7)])
 def test_run_batch_two_promotions_rejected(self):
  bad=[{"promotion":True,"employee_requirement":"x"} if i<2 else {"promotion":False} for i in range(7)]
  with self.assertRaisesRegex(ValueError,'BATCH_STRATEGY_BLOCKED'):
   run_batch(self.root,[f'Topic {i}' for i in range(7)],'20261121',strategy=bad)
 def test_run_batch_resume_existing_manifest(self):
  initialise(self.root,[f'Topic {i}' for i in range(7)],'20261121')
  r=run_batch(self.root,[f'Topic {i}' for i in range(7)],'20261121')
  self.assertEqual(len(r['jobs']),7)
  self.assertTrue(all(j['status']=='TEST_FIXTURE_PASS' for j in r['jobs']))
 def test_run_batch_live_research_due(self):
  r=run_batch(self.root,[f'Topic {i}' for i in range(7)],'20261121',mode='LIVE')
  self.assertEqual(r,{'ok':False,'error':'RESEARCH_DUE','research_due':r['research_due']})
  self.assertFalse((Path(self.root)/'manifest.json').exists())
 def test_check_duplicate_images(self):
  p1=Path(self.root)/'a.png';p2=Path(self.root)/'b.png'
  Image.new('RGB',(1080,1350)).save(p1);Image.new('RGB',(1080,1350)).save(p2)
  states=[]
  for cid,p in (('ER-X-001',p1),('ER-X-002',p2)):
   sp=Path(self.root)/f'{cid}.json'
   sp.write_text(json.dumps({'job':{'content_id':cid,'topic':'T'},'status':'READY_FOR_OWNER_REVIEW','records':{'IMAGE_BUILD':{'artifact':{'image_path':str(p)}}},'index':17,'trace':[],'repairs':0}))
   states.append({'content_id':cid,'state':str(sp)})
  (Path(self.root)/'manifest.json').write_text(json.dumps({'cycle':'20261121','jobs':states}))
  dup=check_duplicate_images(self.root)
  self.assertEqual(dup['status'],'BLOCKED');self.assertEqual(dup['checked'],2)
  self.assertEqual(dup['duplicates'][0]['content_ids'],['ER-X-001','ER-X-002'])
  self.assertEqual(dup['duplicates'][0]['sha256'],filehash(p1))
  Image.new('RGB',(1080,1350),color='red').save(p2)
  self.assertEqual(check_duplicate_images(self.root)['status'],'PASS')
 def test_summary_surfaces_duplicates(self):
  x=initialise(self.root,[f'Topic {i}' for i in range(7)],'20261121')
  self.assertEqual(x['duplicate_images'],{'status':'PASS','duplicates':[],'checked':0})
 def test_summary_lists_removed_job(self):
  # Removing a batch job's state file (op_remove_content) must not
  # crash the batch report: the job shows under "removed" and the
  # batch can never read READY while a slot is missing.
  initialise(self.root,[f'Topic {i}' for i in range(7)],'20261121')
  manifest=json.loads((Path(self.root)/'manifest.json').read_text())
  first=manifest['jobs'][0]
  Path(first['state']).unlink()
  s=summary(self.root)
  self.assertEqual(s['removed'],[first['content_id']])
  self.assertEqual(len(s['items']),6)
  self.assertEqual(s['batch_status'],'NOT_APPROVED')
 def test_research_due(self):
  d=research_due(self.root)
  self.assertTrue(d['due']);self.assertEqual(d['reason'],'NO_PRIOR_RESEARCH')
  today=datetime.now(timezone.utc).date()
  (Path(self.root)/'research_evidence.json').write_text(json.dumps([{'url':'https://example.org','verified_at':today.isoformat()}]))
  d=research_due(self.root);self.assertFalse(d['due']);self.assertEqual(d['reason'],'FRESH')
  stale=(today-timedelta(days=30)).isoformat()
  (Path(self.root)/'research_evidence.json').write_text(json.dumps([{'url':'https://example.org','verified_at':stale}]))
  d=research_due(self.root);self.assertTrue(d['due']);self.assertEqual(d['reason'],'STALE')
 def test_verify_batch_strategy(self):
  valid=[{"promotion":False} for _ in range(6)]+[{"promotion":True,"employee_requirement":"Staff oversees exceptions"}]
  self.assertEqual(verify_batch_strategy(valid,None)['status'],'PASS')
  self.assertEqual(verify_batch_strategy(None,[{"promotion":False} for _ in range(7)])['status'],'BLOCKED')
  bad=valid.copy();del bad[-1]['employee_requirement']
  self.assertIn('Promotion missing employee requirement',verify_batch_strategy(bad)['errors'])
 def test_live_image_build_uses_real_renderer(self):
  # Replaces the old test_live_image_build_missing_renderer: Worker 3 has
  # landed render_production_poster, so the live IMAGE_BUILD path now
  # renders through the real production renderer instead of raising
  # IMAGE_RENDERER_MISSING. The fixture plan (headline <= 12 words,
  # exactly 5 steps) satisfies the production renderer's copy rules.
  initialise(self.root,[f'Topic {i}' for i in range(7)],'20261121')
  manifest=json.loads((Path(self.root)/'manifest.json').read_text())
  state_path=manifest['jobs'][0]['state']
  run_job(state_path)
  state=load(state_path)
  live_job=dict(state['job'],mode='LIVE')
  adapters=build_adapters(live_job,self.root,mode='LIVE')
  out=adapters['IMAGE_BUILD'].fn(live_job,state['records'])
  self.assertTrue(Path(out['image_path']).is_file())
  self.assertEqual(out['image_sha256'],filehash(out['image_path']))
  with Image.open(out['image_path']) as im:self.assertEqual(im.size,(1080,1350))
 def test_live_image_build_uses_mocked_renderer(self):
  png=Path(self.root)/'mock.png';Image.new('RGB',(1080,1350)).save(png)
  fake=mock.Mock()
  fake.render_production_poster.return_value={'status':'RENDERED','image_path':str(png),'sha256':filehash(png),'font_provenance':{'Sora':{'path':'pillow-default-fallback','sha256':'fallback-no-binary'}}}
  batch_guard_v45._MODULE_OVERRIDES['brand_render_v37']=fake
  try:
   initialise(self.root,[f'Topic {i}' for i in range(7)],'20261121')
   manifest=json.loads((Path(self.root)/'manifest.json').read_text())
   state=load(manifest['jobs'][0]['state'])
   live_job=dict(state['job'],mode='LIVE')
   adapters=build_adapters(live_job,self.root,mode='LIVE')
   # Fixture records give IMAGE_BUILD a real plan to build from.
   run_job(manifest['jobs'][0]['state'])
   state=load(manifest['jobs'][0]['state'])
   out=adapters['IMAGE_BUILD'].fn(live_job,state['records'])
   self.assertEqual(out['image_path'],str(png))
   self.assertEqual(out['image_sha256'],filehash(png))
   fake.render_production_poster.assert_called_once()
  finally:
   batch_guard_v45._MODULE_OVERRIDES.pop('brand_render_v37',None)
 def test_real_inspect_image_when_available(self):
  module=batch_guard_v45._try_load_module('verify_output')
  fn=getattr(module,'inspect_image',None) if module is not None else None
  if fn is None:
   self.skipTest('verify_output.inspect_image not yet implemented by Worker 3')
  png=Path(self.root)/'check.png';Image.new('RGB',(1080,1350)).save(png)
  result=fn(str(png))
  self.assertIsInstance(result,dict)
  self.assertTrue('measurements' in result or 'passed' in result)
 def test_real_render_production_poster_when_available(self):
  module=batch_guard_v45._try_load_module('brand_render_v37')
  fn=getattr(module,'render_production_poster',None) if module is not None else None
  if fn is None:
   self.skipTest('rendering.brand_render_v37.render_production_poster not yet implemented by Worker 3')
  out=str(Path(self.root)/'poster.png')
  result=fn({'copy':{'headline':'Five call handling steps','steps':['answer','capture','respond','route','follow up'],'support':'A practical workflow.','takeaway':'Keep a person responsible.','category':'SUPPORT AUTOMATION'},'palette':{'paper':'#F6F1E9','ink':'#14120E','soft':'#615B4C','emerald':'#10B77F','deep':'#0C8D62','dark':'#080C0B'},'template_id':'website'},out)
  self.assertIsInstance(result,dict)
  self.assertTrue('image_path' in result or result.get('status')=='BLOCKED')
 def test_real_check_canonical_brand_when_available(self):
  module=batch_guard_v45._try_load_module('brand_policy_v36')
  fn=getattr(module,'check_canonical_brand',None) if module is not None else None
  if fn is None:
   self.skipTest('modules.brand_claims_qa.brand_policy_v36.check_canonical_brand not yet implemented by Worker 3')
  self.assertIsInstance(fn({'font_family':'Sora','dimensions':[1080,1350]}),list)
 def test_real_record_handoff_when_available(self):
  module=batch_guard_v45._try_load_module('evidence_store')
  fn=getattr(module,'record_handoff',None) if module is not None else None
  if fn is None:
   self.skipTest('core.evidence_store.record_handoff not yet implemented by Worker 3')
  db=module.init(str(Path(self.root)/'evidence.db'))
  self.assertIsInstance(fn(db,'job1','SOURCES','AG-01','AG-13','in-hash','out-hash'),str)
 def test_real_provider_registry_when_available(self):
  import chatgpt_bridge_v43 as bridge
  factory=getattr(bridge,'get_provider_registry',None)
  if factory is None:
   self.skipTest('chatgpt_bridge_v43.get_provider_registry not yet implemented by Worker 1')
  registry=factory()
  self.assertTrue(hasattr(registry,'fetch_source'))
class MarketSignalsTests(unittest.TestCase):
 """assess_market_signals (module 04, AG-04): pure validation of supplied
 market-signal observations; shape reuses the competitor audit record +
 the weekly-research observation (source URL, verification date,
 previous/current value, review status). Nothing is invented."""
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=self.tmp.name
 def tearDown(self):self.tmp.cleanup()
 def _signal(self,**over):
  s={'topic':'AI voice agents','signal':'Adoption rising among dental practices','source_url':'https://example.org/market','verified_at':'2026-11-20','value_previous':'12%','value_current':'18%','review_status':'reviewed'}
  s.update(over);return s
 def test_valid_signals_complete(self):
  r=assess_market_signals([self._signal(),self._signal(topic='Call automation')])
  self.assertEqual(r['status'],'COMPLETE');self.assertEqual(r['signals'],2);self.assertEqual(r['verified'],2);self.assertEqual(r['errors'],[])
 def test_empty_signals_reported_honestly(self):
  r=assess_market_signals([])
  self.assertEqual(r['status'],'NO_SIGNALS');self.assertEqual(r['signals'],0);self.assertEqual(r['verified'],0)
 def test_missing_fields_incomplete(self):
  bad=self._signal();del bad['source_url'];bad['verified_at']='not-a-date'
  r=assess_market_signals([self._signal(),bad])
  self.assertEqual(r['status'],'INCOMPLETE');self.assertEqual(r['verified'],1)
  self.assertIn('MISSING_SOURCE_URL',r['errors']);self.assertIn('INVALID_VERIFIED_DATE',r['errors'])
 def test_market_signals_wired_into_research(self):
  initialise(self.root,[f'Topic {i}' for i in range(7)],'20261121')
  manifest=json.loads((Path(self.root)/'manifest.json').read_text())
  state_path=manifest['jobs'][0]['state']
  state=load(state_path);state['job']['market_signals']=[self._signal()];save(state_path,state)
  r=run_job(state_path)
  self.assertEqual(r['status'],'TEST_FIXTURE_PASS')
  artifact=load(state_path)['records']['RESEARCH']['artifact']['market_signals']
  self.assertEqual(artifact['status'],'COMPLETE');self.assertEqual(artifact['verified'],1)
if __name__=='__main__':unittest.main()
