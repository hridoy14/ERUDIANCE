"""Mechanical PNG gate. Cannot certify subjective visual quality or authentic logo provenance alone."""
import argparse,json,hashlib,pathlib,sys
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('png');p.add_argument('--require-logo',action='store_true');a=p.parse_args();f=pathlib.Path(a.png);checks=[]
def check(name,condition,detail):checks.append({'id':name,'status':'PASS' if condition else 'FAIL','observed':detail})
if not f.is_file():print('BLOCK missing PNG');sys.exit(2)
try:
 with Image.open(f) as im:
  check('decode_png',im.format=='PNG',im.format);check('dimensions',im.size==(1080,1350),im.size);check('colour_mode',im.mode in ('RGB','RGBA'),im.mode);check('size_under_5mb',f.stat().st_size<=5*1024*1024,f.stat().st_size)
except Exception as e:print('BLOCK image decode:',e);sys.exit(2)
m=f.with_suffix('.json');meta=json.loads(m.read_text()) if m.exists() else {};check('manifest_exists',bool(meta),str(m));check('checksum',meta.get('sha256')==hashlib.sha256(f.read_bytes()).hexdigest(),'matching' if meta.get('sha256')==hashlib.sha256(f.read_bytes()).hexdigest() else 'missing/mismatch');check('stage_order',meta.get('locked_stage_names')==['CAPTURE','ACKNOWLEDGE','QUALIFY','ROUTE','NEXT ACTION','OUTCOME'],meta.get('locked_stage_names'))
if a.require_logo:check('logo_declared',bool(meta.get('logo_provided') and meta.get('logo_sha256')),meta.get('logo_sha256'))
result={'verdict':'PASS_MECHANICAL_ONLY' if all(x['status']=='PASS' for x in checks) else 'BLOCK','checks':checks,'unverified':['actual visual legibility','brand asset provenance','source freshness','platform policy','owner approval','Social OS schema compatibility']};print(json.dumps(result,indent=2));sys.exit(0 if result['verdict']=='PASS_MECHANICAL_ONLY' else 2)
