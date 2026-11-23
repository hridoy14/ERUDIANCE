"""Local SQLite evidence ledger; not an external integration or permission grant."""
import sqlite3, json, hashlib, datetime, pathlib, argparse
SCHEMA='''CREATE TABLE IF NOT EXISTS evidence (id TEXT PRIMARY KEY, job_id TEXT NOT NULL, stage TEXT NOT NULL, source_url TEXT, observed_at TEXT NOT NULL, source_hash TEXT, payload TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS receipts (id TEXT PRIMARY KEY, job_id TEXT NOT NULL, stage TEXT NOT NULL, input_hash TEXT NOT NULL, output_hash TEXT, upstream_json TEXT NOT NULL, verdict TEXT NOT NULL CHECK(verdict IN ('PASS','REJECT','NOT_VERIFIED')), evidence_json TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS approvals (id TEXT PRIMARY KEY, job_id TEXT NOT NULL, content_hash TEXT NOT NULL, actor TEXT NOT NULL, decision TEXT NOT NULL CHECK(decision IN ('APPROVE','REJECT','WRITE_AUTHORISE')), scope TEXT NOT NULL, created_at TEXT NOT NULL);'''
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(x):return hashlib.sha256(json.dumps(x,sort_keys=True).encode()).hexdigest()
def _approval_columns(db):
 return {row[1] for row in db.execute('PRAGMA table_info(approvals)').fetchall()}
def init(path):
 pathlib.Path(path).parent.mkdir(parents=True,exist_ok=True)
 db=sqlite3.connect(path);db.executescript(SCHEMA)
 # Guarded migration (D-04): old DBs created before the approval ledger gained
 # hash-chain columns keep working; only missing columns are added. content_id
 # and reason are added alongside the three named columns because the ledger
 # contract keys lookups by (job_id, content_id) and hashes the reason — the
 # original SCHEMA stores neither, so without them verify/latest could not work.
 for _col in ('content_id','reason','image_hash','record_hash','prev_hash'):
  if _col not in _approval_columns(db):
   db.execute('ALTER TABLE approvals ADD COLUMN '+_col+' TEXT')
 db.commit();return db
def _row_dict(cur,row):
 if row is None:return None
 return {d[0]:row[i] for i,d in enumerate(cur.description)}
def record_approval(db,job_id,content_id,content_hash,image_hash,actor,decision,scope='owner_review',reason=None):
 """Record one owner decision. Content-addressed hash chain: id == record_hash.
 scope='test_only' is accepted and stored (never a real approval)."""
 if decision not in ('APPROVE','REJECT'):raise ValueError('decision must be APPROVE or REJECT')
 created_at=now()
 prev=latest_approval(db,job_id,content_id)
 prev_hash=prev['record_hash'] if prev and prev.get('record_hash') else (prev['id'] if prev and prev.get('id') else 'GENESIS')
 payload={'job_id':job_id,'content_id':content_id,'content_hash':content_hash,'image_hash':image_hash,'actor':actor,'decision':decision,'scope':scope,'reason':reason,'created_at':created_at,'prev_hash':prev_hash}
 record_hash=sha(payload)
 db.execute('INSERT INTO approvals(id,job_id,content_id,content_hash,image_hash,record_hash,prev_hash,actor,decision,scope,reason,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',(record_hash,job_id,content_id,content_hash,image_hash,record_hash,prev_hash,actor,decision,scope,reason,created_at))
 db.commit()
 return {'approval_id':record_hash,'job_id':job_id,'content_id':content_id,'content_hash':content_hash,'image_hash':image_hash,'actor':actor,'decision':decision,'scope':scope,'reason':reason,'created_at':created_at,'record_hash':record_hash,'prev_hash':prev_hash}
def latest_approval(db,job_id,content_id):
 cur=db.execute('SELECT * FROM approvals WHERE job_id=? AND content_id=? ORDER BY created_at DESC, rowid DESC LIMIT 1',(job_id,content_id))
 return _row_dict(cur,cur.fetchone())
def verify_approval(db,job_id,content_id,content_hash,image_hash):
 """valid ONLY if the latest approval for (job_id, content_id) is APPROVE with
 matching content/image hashes, a recomputed record_hash equal to the stored
 one, and no later REJECT superseding it."""
 latest=latest_approval(db,job_id,content_id)
 if latest is None:return {'valid':False,'reason':'NO_APPROVAL','approval':None}
 if latest.get('decision')!='APPROVE':return {'valid':False,'reason':'NOT_APPROVED','approval':None}
 if latest.get('content_hash')!=content_hash:return {'valid':False,'reason':'CONTENT_HASH_MISMATCH','approval':None}
 if latest.get('image_hash')!=image_hash:return {'valid':False,'reason':'IMAGE_HASH_MISMATCH','approval':None}
 _row=db.execute('SELECT rowid FROM approvals WHERE id=?',(latest['id'],)).fetchone()
 if _row is not None:
  _rej=db.execute("SELECT id FROM approvals WHERE job_id=? AND content_id=? AND decision='REJECT' AND rowid>? ORDER BY rowid DESC LIMIT 1",(job_id,content_id,_row[0])).fetchone()
  if _rej:return {'valid':False,'reason':'SUPERSEDED_BY_REJECT','approval':None}
 _needed=('job_id','content_id','content_hash','image_hash','actor','decision','scope','created_at','prev_hash','record_hash')
 if any(latest.get(k) is None for k in _needed):return {'valid':False,'reason':'TAMPER_CHECK_UNAVAILABLE','approval':None}
 _recomputed=sha({'job_id':latest['job_id'],'content_id':latest['content_id'],'content_hash':latest['content_hash'],'image_hash':latest['image_hash'],'actor':latest['actor'],'decision':latest['decision'],'scope':latest['scope'],'reason':latest.get('reason'),'created_at':latest['created_at'],'prev_hash':latest['prev_hash']})
 if _recomputed!=latest['record_hash']:return {'valid':False,'reason':'TAMPER_DETECTED','approval':None}
 return {'valid':True,'reason':'OK','approval':latest}
def record_handoff(db,job_id,stage,from_agent,to_agent,input_hash,output_hash):
 stage_label='HANDOFF:'+stage
 parties={'from_agent':from_agent,'to_agent':to_agent}
 rid=sha([job_id,stage_label,input_hash,output_hash,parties,'PASS'])
 db.execute('INSERT OR REPLACE INTO receipts VALUES(?,?,?,?,?,?,?,?,?)',(rid,job_id,stage_label,input_hash,output_hash,json.dumps(parties),'PASS',json.dumps(parties),now()))
 db.commit();return rid
def record_event(db,job_id,kind,payload):
 h=sha(payload);key=sha([job_id,kind,None,h])
 db.execute('INSERT OR IGNORE INTO evidence VALUES(?,?,?,?,?,?,?)',(key,job_id,kind,None,now(),h,json.dumps(payload,ensure_ascii=False)))
 db.commit();return key
def evidence(db,job,stage,payload,url=None):
 h=sha(payload);key=sha([job,stage,url,h]);db.execute('INSERT OR IGNORE INTO evidence VALUES(?,?,?,?,?,?,?)',(key,job,stage,url,now(),h,json.dumps(payload,ensure_ascii=False)));db.commit();return key
def gate(db,job,stage,input_payload,upstream,checks):
 ih=sha(input_payload); bad=[c for c in checks if c['status']!='PASS']; verdict='PASS' if not bad else ('REJECT' if any(c['status']=='FAIL' for c in bad) else 'NOT_VERIFIED')
 for rid in upstream:
  row=db.execute('SELECT verdict FROM receipts WHERE id=? AND job_id=?',(rid,job)).fetchone()
  if not row or row[0]!='PASS':verdict='REJECT'
 rid=sha([job,stage,ih,upstream,checks,verdict]);db.execute('INSERT OR REPLACE INTO receipts VALUES(?,?,?,?,?,?,?,?,?)',(rid,job,stage,ih,sha(checks),json.dumps(upstream),verdict,json.dumps(checks),now()));db.commit();return {'receipt_id':rid,'verdict':verdict}
def can_handoff(db,job,content_hash,receipt_ids):
 if not receipt_ids:return False,'Missing gate receipts'
 for rid in receipt_ids:
  r=db.execute('SELECT verdict FROM receipts WHERE id=? AND job_id=?',(rid,job)).fetchone()
  if not r or r[0]!='PASS':return False,'Failed/stale/missing receipt '+rid
 a=db.execute("SELECT decision FROM approvals WHERE job_id=? AND content_hash=? AND decision='APPROVE' ORDER BY created_at DESC LIMIT 1",(job,content_hash)).fetchone()
 w=db.execute("SELECT decision FROM approvals WHERE job_id=? AND content_hash=? AND decision='WRITE_AUTHORISE' ORDER BY created_at DESC LIMIT 1",(job,content_hash)).fetchone()
 return (bool(a and w),'Owner approval and separate write authorisation both required' if not (a and w) else 'Ready for schema check, not yet written')
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('db');args=a.parse_args();db=init(args.db);print('Local evidence database initialised:',args.db)
