"""Local SQLite evidence ledger; not an external integration or permission grant."""
import sqlite3, json, hashlib, datetime, pathlib, argparse
SCHEMA='''CREATE TABLE IF NOT EXISTS evidence (id TEXT PRIMARY KEY, job_id TEXT NOT NULL, stage TEXT NOT NULL, source_url TEXT, observed_at TEXT NOT NULL, source_hash TEXT, payload TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS receipts (id TEXT PRIMARY KEY, job_id TEXT NOT NULL, stage TEXT NOT NULL, input_hash TEXT NOT NULL, output_hash TEXT, upstream_json TEXT NOT NULL, verdict TEXT NOT NULL CHECK(verdict IN ('PASS','REJECT','NOT_VERIFIED')), evidence_json TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS approvals (id TEXT PRIMARY KEY, job_id TEXT NOT NULL, content_hash TEXT NOT NULL, actor TEXT NOT NULL, decision TEXT NOT NULL CHECK(decision IN ('APPROVE','REJECT','WRITE_AUTHORISE')), scope TEXT NOT NULL, created_at TEXT NOT NULL);'''
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(x):return hashlib.sha256(json.dumps(x,sort_keys=True).encode()).hexdigest()
def init(path):
 db=sqlite3.connect(path);db.executescript(SCHEMA);db.commit();return db
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
