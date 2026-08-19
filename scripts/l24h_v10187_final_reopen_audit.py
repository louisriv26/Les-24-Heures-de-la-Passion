from __future__ import annotations
import argparse,hashlib,json,re,shutil,subprocess,sys,zipfile
from pathlib import Path
from playwright.sync_api import sync_playwright
BASE=Path('/mnt/data/L24H_v10186_GITHUB_DEPLOY_TITLE_HELP_HARDENED_R2_AUDIT_RECONCILED.zip')
BASE_SHA='760196b75ee89bb54eaf7780909028e84748ca3bc5b77b62342067fa40602494'
PROTECTED=['CORPUS','TEXT_LIBRARY','HOUR_LINKED_TEXTS','SPEECH_DATA','INTERNAL_SUBHEADINGS','SPEECH_END_VISUAL_BREAKS']
def hb(b):return hashlib.sha256(b).hexdigest()
def hf(p):return hb(Path(p).read_bytes())
def jconst(s,n):
 m=re.search(r'const\s+'+re.escape(n)+r'\s*=\s*',s); assert m,n
 return json.JSONDecoder().raw_decode(s[m.end():])[0]
def ph(s):return {n:hb(json.dumps(jconst(s,n),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()) for n in PROTECTED}
def safe_extract(z,out):
 shutil.rmtree(out,ignore_errors=True);out.mkdir(parents=True)
 with zipfile.ZipFile(z) as zz:
  names=zz.namelist();assert len(names)==len(set(names))
  for n in names:
   p=Path(n);assert not p.is_absolute() and '..' not in p.parts
  zz.extractall(out)
def main(zpath,outdir,md,jsonp):
 z=Path(zpath);out=Path(outdir);safe_extract(z,out);rows=[]
 def ck(n,c,e):
  rows.append((n,'PASS' if c else 'FAIL',e))
  if not c: raise AssertionError(n+': '+e)
 idx=out/'index.html';s=idx.read_text('utf-8')
 ck('zip-open',zipfile.is_zipfile(z),hf(z));ck('runtime-twins',idx.read_bytes()==(out/'luisa_24_heures.html').read_bytes(),hf(idx))
 ck('version',"const APP_VERSION = 'v101.87';" in s,'v101.87');ck('cache',"luisa-24h-v101-87" in (out/'sw.js').read_text(),'cache 87')
 # manifests
 pm=json.load(open(out/'metadata/package_manifest.json')); hm=json.load(open(out/'metadata/hash_manifest.json'))
 bad=[]
 for rec in pm['files']:
  p=out/rec['path'];
  if not p.exists() or hf(p)!=rec['sha256'] or p.stat().st_size!=rec['bytes']:bad.append(rec['path'])
 ck('package-manifest',not bad,f"{len(pm['files'])} checked; bad={bad}")
 bad=[]
 for rec in hm['files']:
  p=out/rec['path'];
  if not p.exists() or hf(p)!=rec['sha256'] or p.stat().st_size!=rec['bytes']:bad.append(rec['path'])
 ck('hash-manifest',not bad,f"{len(hm['files'])} checked; bad={bad}")
 with zipfile.ZipFile(BASE) as bz:bs=bz.read('index.html').decode()
 ck('protected-data',ph(s)==ph(bs),'6/6 hashes identical')
 ck('schema-snapshot','const STORAGE_SCHEMA_VERSION=8;' in s and 'const PERSONAL_SNAPSHOT_VERSION = 5;' in s,'8/5')
 ck('event-isolation','#libraryMarkerPicker' in re.search(r'function stage6fIsHighlightUiTarget\(target\).*?\n\}',s,re.S).group(0),'picker protected')
 ck('selection-suppression','libraryPicker' in re.search(r'function stage6fShouldSuppressSelectionCapture\(\).*?\n\}',s,re.S).group(0),'picker suppresses capture')
 # actual UI stress independent from prepackage auditor
 with sync_playwright() as pw:
  b=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  p=b.new_page(viewport={'width':430,'height':932},is_mobile=True,has_touch=True);errs=[];p.on('pageerror',lambda e:errs.append(str(e)));p.set_content(s,wait_until='domcontentloaded',timeout=30000)
  p.evaluate("window.commitDurableChange=function(){return {ok:true};}")
  item=p.evaluate("() => { const x=TEXT_LIBRARY.find(i=>i&&i.type!=='library_group'&&i.status!=='placeholder'); return x&&x.id; }")
  p.evaluate('(id)=>openLibraryText(id,false,null)',item);p.wait_for_timeout(30);p.click('#libraryTitleMarkBtn')
  # Assert classifier and timer isolation under selection pressure.
  c=p.evaluate("stage6fIsHighlightUiTarget(document.getElementById('libraryMarkerPicker')) && stage6fShouldSuppressSelectionCapture()")
  ck('runtime-picker-protected',c,'classifier + suppression true')
  p.evaluate("""() => { const h=document.getElementById('libraryReaderTitle'); const r=document.createRange(); r.selectNodeContents(h); const s=getSelection();s.removeAllRanges();s.addRange(r);window._selectionCaptureTimer=null;document.dispatchEvent(new Event('selectionchange'));const x=document.querySelector('#libraryMarkerPicker .cp-swatch');x.dispatchEvent(new Event('touchend',{bubbles:true,cancelable:true}));x.dispatchEvent(new Event('pointerup',{bubbles:true,cancelable:true})); }""");p.wait_for_timeout(280)
  ck('runtime-selection-pressure',p.evaluate("document.getElementById('libraryMarkerPicker').classList.contains('open') && _selectionCaptureTimer===null"),'picker survives touch/selection pressure')
  p.click('[data-library-marker-color="green"]');p.wait_for_timeout(20);ck('runtime-create',p.locator('#libraryReaderTitleMark.hl-green').count()==1,'green inline title')
  p.click('#libraryReaderTitleMark');p.click('[data-library-marker-color="purple"]');p.wait_for_timeout(20);ck('runtime-recolour',p.locator('#libraryReaderTitleMark.hl-purple').count()==1,'purple')
  p.click('#libraryReaderTitleMark');p.click('#libraryMarkerRemoveBtn');p.wait_for_timeout(20);ck('runtime-remove',p.locator('#libraryReaderTitleMark').count()==0,'removed')
  p.evaluate('undoLatestLibraryMarkRemoval()');p.wait_for_timeout(20);ck('runtime-undo',p.locator('#libraryReaderTitleMark.hl-purple').count()==1,'purple restored')
  ck('runtime-errors',not errs,'0 page errors' if not errs else ';'.join(errs));b.close()
 # honest physical gate
 qa=(out/'REAL_DEVICE_QA_CHECKLIST.md').read_text();qac=(out/'REAL_DEVICE_QA_RESULTS_TEMPLATE.csv').read_text()
 ck('physical-title-not-tested','G-86' in qa and 'NOT_TESTED' in qac,'physical v101.87 retest still open')
 status='PASS';summary={'status':status,'zip_sha256':hf(z),'runtime_sha256':hf(idx),'checks':[{'name':a,'status':b,'evidence':c} for a,b,c in rows]}
 Path(jsonp).write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');Path(md).write_text('# v101.87 final immutable ZIP reopen audit\n\n**PASS**\n\n'+f'- ZIP SHA-256: `{hf(z)}`\n- runtime SHA-256: `{hf(idx)}`\n- physical-device title retest remains NOT_TESTED.\n\n'+'\n'.join(f'- {a}: **{b}** — {c}' for a,b,c in rows)+'\n')
 print('PASS')
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('zip');ap.add_argument('outdir');ap.add_argument('md');ap.add_argument('json');a=ap.parse_args()
 try:main(a.zip,a.outdir,a.md,a.json)
 except Exception as e:print('FAIL',e);sys.exit(2)
