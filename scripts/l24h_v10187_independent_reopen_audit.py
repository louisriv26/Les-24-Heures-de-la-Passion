from __future__ import annotations
import argparse,hashlib,json,re,shutil,sys,zipfile
from pathlib import Path
from playwright.sync_api import sync_playwright

def shab(b):return hashlib.sha256(b).hexdigest()
def shaf(p):return shab(Path(p).read_bytes())
def extract(z,o):
 shutil.rmtree(o,ignore_errors=True);Path(o).mkdir(parents=True)
 with zipfile.ZipFile(z) as f:
  ns=f.namelist(); assert len(ns)==len(set(ns))
  for n in ns:
   p=Path(n); assert not p.is_absolute() and '..' not in p.parts
  f.extractall(o)
def run(z,o,md,js):
 extract(z,o);o=Path(o);z=Path(z);checks=[]
 def c(n,v,e):
  checks.append({'name':n,'status':'PASS' if v else 'FAIL','evidence':e})
  if not v:raise AssertionError(n+': '+e)
 s=(o/'index.html').read_text();c('twins',(o/'index.html').read_bytes()==(o/'luisa_24_heures.html').read_bytes(),shaf(o/'index.html'))
 c('identity',"const APP_VERSION = 'v101.87';" in s and 'v101.87' in (o/'version.json').read_text(),'v101.87')
 c('sw-cache',"luisa-24h-v101-87" in (o/'sw.js').read_text(),'cache v101-87')
 # Independent manifest enumeration: package manifest excludes only itself; hash manifest excludes itself + package manifest.
 pm=json.load(open(o/'metadata/package_manifest.json'));hm=json.load(open(o/'metadata/hash_manifest.json'))
 pbad=[]
 for r in pm['files']:
  p=o/r['path'];
  if not p.exists() or shaf(p)!=r['sha256'] or p.stat().st_size!=r['bytes']:pbad.append(r['path'])
 c('package-manifest',not pbad,f"{len(pm['files'])} entries")
 hbad=[]
 for r in hm['files']:
  p=o/r['path'];
  if not p.exists() or shaf(p)!=r['sha256'] or p.stat().st_size!=r['bytes']:hbad.append(r['path'])
 c('hash-manifest',not hbad,f"{len(hm['files'])} entries")
 # Independently reason over exact event isolation blocks.
 classifier=re.search(r'function stage6fIsHighlightUiTarget\(target\) \{(.*?)\n\}',s,re.S).group(1)
 suppressor=re.search(r'function stage6fShouldSuppressSelectionCapture\(\) \{(.*?)\n\}',s,re.S).group(1)
 opener=re.search(r'function openLibraryMarkerPicker\(itemId, triggerEl\) \{(.*?)\n\}',s,re.S).group(1)
 c('classifier-scope',all(x in classifier for x in ['#libraryMarkerPicker','[data-library-marker-ui="true"]','.library-title-inline-mark','.library-title-mark-btn']),'all title marker UI selectors protected')
 c('suppression-scope','libraryMarkerPicker' in suppressor and 'libraryPicker.classList.contains(\'open\')' in suppressor,'title picker open suppresses selection')
 c('opener-isolation','stage6fBindHighlightUiEventIsolation(picker)' in opener and 'stage6fMarkHighlightUiOpening(1200)' in opener and 'removeAllRanges' in opener,'dynamic isolation + protection + residual selection clear')
 # Runtime independent flow: use direct DOM events rather than Playwright clicks for key touch path.
 with sync_playwright() as pw:
  b=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox']);p=b.new_page(viewport={'width':375,'height':812},is_mobile=True,has_touch=True);errs=[];p.on('pageerror',lambda e:errs.append(str(e)));p.set_content(s,wait_until='domcontentloaded',timeout=30000)
  p.evaluate("window.commitDurableChange=function(){return {ok:true};}")
  item=p.evaluate("() => (TEXT_LIBRARY.find(x=>x&&x.type!=='library_group'&&x.status!=='placeholder')||{}).id");p.evaluate('(id)=>openLibraryText(id,false,null)',item)
  p.evaluate("document.getElementById('libraryTitleMarkBtn').click()")
  c('runtime-open',p.evaluate("document.getElementById('libraryMarkerPicker').classList.contains('open')"),'picker opened')
  # Event path must be stopped at picker before document touch/pointer handlers.
  ev=p.evaluate("""() => { let docTouch=0,docPointer=0; const a=()=>docTouch++, b=()=>docPointer++; document.addEventListener('touchend',a,{once:true});document.addEventListener('pointerup',b,{once:true}); const x=document.querySelector('#libraryMarkerPicker [data-library-marker-color="yellow"]');x.dispatchEvent(new Event('touchend',{bubbles:true,cancelable:true}));x.dispatchEvent(new Event('pointerup',{bubbles:true,cancelable:true})); return {docTouch,docPointer}; }""")
  c('runtime-event-stop',ev['docTouch']==0 and ev['docPointer']==0,f"document touch/pointer counts {ev}")
  p.evaluate("document.querySelector('[data-library-marker-color=yellow]').click()");c('runtime-create',p.locator('#libraryReaderTitleMark.hl-yellow').count()==1,'yellow')
  p.evaluate("document.getElementById('libraryReaderTitleMark').click();document.querySelector('[data-library-marker-color=blue]').click()");c('runtime-recolour',p.locator('#libraryReaderTitleMark.hl-blue').count()==1,'blue')
  p.evaluate("document.getElementById('libraryReaderTitleMark').click();document.getElementById('libraryMarkerRemoveBtn').click()");c('runtime-remove',p.locator('#libraryReaderTitleMark').count()==0,'removed')
  p.evaluate('undoLatestLibraryMarkRemoval()');c('runtime-undo',p.locator('#libraryReaderTitleMark.hl-blue').count()==1,'blue restored')
  c('runtime-errors',not errs,'0 page errors' if not errs else ';'.join(errs));b.close()
 qa=(o/'REAL_DEVICE_QA_CHECKLIST.md').read_text();csv=(o/'REAL_DEVICE_QA_RESULTS_TEMPLATE.csv').read_text();c('physical-gate-honesty','G-86' in qa and 'G-86' in csv and 'NOT_TESTED' in csv,'v101.87 physical title retest remains open')
 summary={'status':'PASS','zip_sha256':shaf(z),'runtime_sha256':shaf(o/'index.html'),'checks':checks};Path(js).write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');Path(md).write_text('# v101.87 independent reopened-ZIP audit\n\n**PASS**\n\n'+f'- ZIP SHA-256: `{shaf(z)}`\n- physical-device G-86 remains NOT_TESTED.\n\n'+'\n'.join(f"- {x['name']}: **{x['status']}** — {x['evidence']}" for x in checks)+'\n');print('PASS')
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('zip');ap.add_argument('outdir');ap.add_argument('md');ap.add_argument('json');a=ap.parse_args()
 try:run(a.zip,a.outdir,a.md,a.json)
 except Exception as e:print('FAIL',e);sys.exit(2)
