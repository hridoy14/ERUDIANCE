"""Mechanical PNG gate. Cannot certify subjective visual quality or authentic logo provenance alone.

v4.9.2: top-level argument parsing and checks moved into main() so the module
is safely importable (previously importing it parsed sys.argv and called
sys.exit()). CLI behaviour, checks, output format and exit codes are unchanged.
"""
import argparse,json,hashlib,pathlib,sys
from PIL import Image

def check(checks,name,condition,detail):checks.append({'id':name,'status':'PASS' if condition else 'FAIL','observed':detail})

def main(argv=None):
    p=argparse.ArgumentParser();p.add_argument('png');p.add_argument('--require-logo',action='store_true');a=p.parse_args(argv);f=pathlib.Path(a.png);checks=[]
    if not f.is_file():print('BLOCK missing PNG');return 2
    try:
     with Image.open(f) as im:
      check(checks,'decode_png',im.format=='PNG',im.format);check(checks,'dimensions',im.size==(1080,1350),im.size);check(checks,'colour_mode',im.mode in ('RGB','RGBA'),im.mode);check(checks,'size_under_5mb',f.stat().st_size<=5*1024*1024,f.stat().st_size)
    except Exception as e:print('BLOCK image decode:',e);return 2
    m=f.with_suffix('.json');meta=json.loads(m.read_text()) if m.exists() else {};check(checks,'manifest_exists',bool(meta),str(m));check(checks,'checksum',meta.get('sha256')==hashlib.sha256(f.read_bytes()).hexdigest(),'matching' if meta.get('sha256')==hashlib.sha256(f.read_bytes()).hexdigest() else 'missing/mismatch');check(checks,'stage_order',meta.get('locked_stage_names')==['CAPTURE','ACKNOWLEDGE','QUALIFY','ROUTE','NEXT ACTION','OUTCOME'],meta.get('locked_stage_names'))
    if a.require_logo:check(checks,'logo_declared',bool(meta.get('logo_provided') and meta.get('logo_sha256')),meta.get('logo_sha256'))
    result={'verdict':'PASS_MECHANICAL_ONLY' if all(x['status']=='PASS' for x in checks) else 'BLOCK','checks':checks,'unverified':['actual visual legibility','brand asset provenance','source freshness','platform policy','owner approval','Social OS schema compatibility']};print(json.dumps(result,indent=2));return 0 if result['verdict']=='PASS_MECHANICAL_ONLY' else 2

if __name__=='__main__':sys.exit(main())
