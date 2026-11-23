"""Mechanical PNG gate. Cannot certify subjective visual quality or authentic logo provenance alone.

v4.9.2: top-level argument parsing and checks moved into main() so the module
is safely importable (previously importing it parsed sys.argv and called
sys.exit()). CLI behaviour, checks, output format and exit codes are unchanged.
"""
import argparse,json,hashlib,pathlib,sys
from PIL import Image

def check(checks,name,condition,detail):checks.append({'id':name,'status':'PASS' if condition else 'FAIL','observed':detail})

def _luminance(rgb):
    def _lin(c):
        c=c/255.0
        return c/12.92 if c<=0.04045 else ((c+0.055)/1.055)**2.4
    r,g,b=(_lin(v) for v in rgb)
    return 0.2126*r+0.7152*g+0.0722*b

def _rgb_hex(rgb):return '#%02X%02X%02X'%tuple(rgb)

def inspect_image(path):
    """Real pixel inspection of a poster PNG (D-08/D-21). NEVER returns
    passed=True from a bare boolean input: every value is measured from pixels.

    Analysis runs on a downscaled copy (max 270x338) for speed; full-size
    dimensions are verified separately on the original. contrast_ratio_estimate
    is an ESTIMATE from the darkest/lightest sampled pixels, NOT a WCAG ratio.
    On an unreadable/missing file returns {'passed': False, 'error': ...}
    and never raises.
    """
    path=str(path)
    try:
        import hashlib
        file_sha=hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
    except Exception as e:
        return {'path':path,'passed':False,'error':'unreadable file: %s'%e}
    try:
        with Image.open(path) as im:
            fmt=im.format;size=im.size;mode=im.mode
            rgb=im.convert('RGB')
            small=rgb.copy();small.thumbnail((270,338),Image.Resampling.LANCZOS)
            sw,sh=small.size
            pixels=list(small.getdata())
            total=len(pixels)
            colors=small.getcolors(maxcolors=sw*sh)
            if not colors:
                # Too many distinct colours for getcolors: fall back to a
                # 256-colour adaptive palette and map indices back to RGB.
                q=small.quantize(colors=256,method=Image.Quantize.MEDIANCUT)
                pal=q.getpalette() or []
                ranked=sorted(((c,i) for c,i in (q.getcolors(maxcolors=sw*sh) or [])),reverse=True)
                top=[(_rgb_hex(pal[idx*3:idx*3+3]),cnt/total) for cnt,idx in ranked[:5]]
                bg=tuple(pal[ranked[0][1]*3:ranked[0][1]*3+3]) if ranked else (255,255,255)
            else:
                ranked=sorted(colors,reverse=True)
                top=[(_rgb_hex(col),cnt/total) for cnt,col in ranked[:5]]
                bg=ranked[0][1]
            def _is_ink(px):return max(abs(px[0]-bg[0]),abs(px[1]-bg[1]),abs(px[2]-bg[2]))>32
            ink=[_is_ink(px) for px in pixels]
            ink_count=sum(ink)
            ink_coverage=ink_count/total if total else 0.0
            # Contrast estimate from darkest/lightest sampled pixels.
            lums=sorted(_luminance(pixels[i]) for i in range(0,total,4))
            lmin=lums[0] if lums else 0.0;lmax=lums[-1] if lums else 0.0
            contrast=round((lmax+0.05)/(lmin+0.05),2) if lums else 0.0
            # Margin clearance: smallest distance from any edge at which
            # non-background pixels appear, scaled back to full-size px.
            scale_x=size[0]/sw if sw else 1;scale_y=size[1]/sh if sh else 1
            clearance=None;safe_ink=False
            for idx,flag in enumerate(ink):
                if not flag:continue
                x=idx%sw;y=idx//sw
                d=min(x,y,sw-1-x,sh-1-y)
                if clearance is None or d<clearance:clearance=d
                if min(x*scale_x,y*scale_y,(sw-1-x)*scale_x,(sh-1-y)*scale_y)>=64:safe_ink=True
            margin_px=int(round(clearance*scale_x)) if clearance is not None else None
            # Blank quadrants (ink coverage < 1%) and the headline band.
            def _quad_ink(x0,x1,y0,y1):
                n=0;t=0
                for y in range(y0,y1):
                    for x in range(x0,x1):
                        t+=1
                        if ink[y*sw+x]:n+=1
                return n/t if t else 0.0
            quads={'top-left':_quad_ink(0,sw//2,0,sh//2),'top-right':_quad_ink(sw//2,sw,0,sh//2),'bottom-left':_quad_ink(0,sw//2,sh//2,sh),'bottom-right':_quad_ink(sw//2,sw,sh//2,sh)}
            blank_regions=sorted([k for k,v in quads.items() if v<0.01])
            band_rows=max(1,int(sh*0.30))
            band_ink=sum(ink[y*sw+x] for y in range(band_rows) for x in range(sw))/(band_rows*sw) if band_rows and sw else 0.0
            # Mobile legibility: downscale to 360px wide, measure ink-run
            # heights in the headline band (top 30% of rows).
            mob=rgb.copy();mob.thumbnail((360,450),Image.Resampling.LANCZOS)
            mw,mh=mob.size
            mpix=list(mob.getdata())
            mband=max(1,int(mh*0.30))
            runs=[];run=0
            for y in range(mband):
                row_ink=any(_is_ink(mpix[y*mw+x]) for x in range(mw))
                if row_ink:run+=1
                elif run:runs.append(run);run=0
            if run:runs.append(run)
            solid_runs=[r for r in runs if r>=3]
            min_band=min(solid_runs) if solid_runs else 0
            mobile={'scaled_width':360,'min_text_band_height_px':min_band,'readable_proxy':bool(min_band>=8)}
            headline_blank=('top-left' in blank_regions or 'top-right' in blank_regions)
            passed=bool(fmt=='PNG' and size==(1080,1350) and mode in ('RGB','RGBA') and 0.02<ink_coverage<0.85 and margin_px is not None and margin_px>=0 and safe_ink and not headline_blank and min_band>=8)
            measurements={'dominant_colors':top,'background_color':_rgb_hex(bg),'ink_coverage':round(ink_coverage,4),'contrast_ratio_estimate':contrast,'margin_clearance_px':margin_px,'safe_area_ink':safe_ink,'blank_regions':blank_regions,'headline_band_ink_coverage':round(band_ink,4),'mobile_legibility':mobile,'analysis_size':[sw,sh]}
            evidence=['format=%s'%fmt,'size=%sx%s'%size,'mode=%s'%mode,'ink_coverage=%.4f'%ink_coverage,'dominant_color=%s (%.2f)'%(top[0][0],top[0][1]) if top else 'dominant_color=unknown','contrast_ratio_estimate=%.2f (ESTIMATE, not WCAG)'%contrast,'margin_clearance_px=%s'%margin_px,'blank_regions=%s'%(','.join(blank_regions) if blank_regions else 'none'),'headline_band_ink_coverage=%.4f'%band_ink,'mobile_text_band_height_px=%s at 360w'%min_band,'analysis_downscaled_to=%sx%s (full-size dimensions verified separately)'%(sw,sh)]
            return {'path':path,'sha256':file_sha,'format':fmt,'size':size,'mode':mode,'measurements':measurements,'passed':passed,'evidence':evidence}
    except Exception as e:
        return {'path':path,'sha256':file_sha,'passed':False,'error':'image decode failed: %s'%e}

def inspect_image_for_gate(path):
    """Boolean flags for the gate, DERIVED from inspect_image measurements.

    topic_match / text_match are NOT derivable from pixels without OCR, so they
    are always None here; the orchestrator's adapters must obtain them from the
    copy ledger + human review, never from this function.
    """
    result=inspect_image(path)
    if result.get('error') or not result.get('measurements'):
        return {'pixel_inspection':False,'mobile_inspection':False,'topic_match':None,'text_match':None,'evidence':['pixel inspection failed: %s'%result.get('error','unreadable image'),'topic_match/text_match: REQUIRES_HUMAN_OR_OCR']}
    mob=result['measurements'].get('mobile_legibility') or {}
    evidence=list(result.get('evidence') or [])
    evidence.append('topic_match: REQUIRES_HUMAN_OR_OCR (copy ledger + human review, not pixels)')
    evidence.append('text_match: REQUIRES_HUMAN_OR_OCR (copy ledger + human review, not pixels)')
    return {'pixel_inspection':bool(result.get('passed')),'mobile_inspection':bool(mob.get('readable_proxy')),'topic_match':None,'text_match':None,'evidence':evidence}

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
