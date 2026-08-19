from __future__ import annotations
import argparse,csv,hashlib,json,re,subprocess,sys,zipfile,shutil,tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright
BASE=Path('/mnt/data/L24H_v10186_GITHUB_DEPLOY_TITLE_HELP_HARDENED_R2_AUDIT_RECONCILED.zip')
BASE_SHA='760196b75ee89bb54eaf7780909028e84748ca3bc5b77b62342067fa40602494'
PROTECTED=['CORPUS','TEXT_LIBRARY','HOUR_LINKED_TEXTS','SPEECH_DATA','INTERNAL_SUBHEADINGS','SPEECH_END_VISUAL_BREAKS']

def hb(b): return hashlib.sha256(b).hexdigest()
def hf(p): return hb(Path(p).read_bytes())
def jconst(s,name):
 m=re.search(r'const\s+'+re.escape(name)+r'\s*=\s*',s)
 if not m: raise AssertionError('missing '+name)
 return json.JSONDecoder().raw_decode(s[m.end():])[0]
def ph(s):
 return {n:hb(json.dumps(jconst(s,n),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()) for n in PROTECTED}
def fail(msg): raise AssertionError(msg)

def audit(stage:Path,out_md:Path,out_json:Path):
 rows=[]
 def ck(name,cond,evidence):
  rows.append({'scenario':name,'status':'PASS' if cond else 'FAIL','evidence':evidence})
  if not cond: fail(name+': '+evidence)
 # PASS 1
 idx=stage/'index.html'; twin=stage/'luisa_24_heures.html'; s=idx.read_text('utf-8')
 ck('P1-runtime-twins',idx.read_bytes()==twin.read_bytes(),hf(idx))
 ck('P1-version',"const APP_VERSION = 'v101.87';" in s,'APP_VERSION v101.87')
 ck('P1-cache',"const CACHE_NAME = 'luisa-24h-v101-87';" in (stage/'sw.js').read_text(),'luisa-24h-v101-87')
 ck('P1-isolation-classifier','#libraryMarkerPicker' in re.search(r'function stage6fIsHighlightUiTarget\(target\).*?\n\}',s,re.S).group(0),'library picker in protected selector')
 ck('P1-suppress-library-picker','libraryPicker' in re.search(r'function stage6fShouldSuppressSelectionCapture\(\).*?\n\}',s,re.S).group(0),'library picker open suppresses capture')
 ck('P1-bind-static',"stage6fBindHighlightUiEventIsolation(document.getElementById('libraryMarkerPicker'));" in s,'static isolation binding')
 ck('P1-bind-dynamic',"stage6fBindHighlightUiEventIsolation(picker);" in re.search(r'function openLibraryMarkerPicker\(.*?\n\}',s,re.S).group(0),'defensive dynamic binding')
 # protected hashes against baseline
 with zipfile.ZipFile(BASE) as z: bs=z.read('index.html').decode('utf-8')
 ck('P1-protected-data',ph(s)==ph(bs),'6/6 protected JSON constant hashes identical to v101.86 baseline')
 ck('P1-schema','const STORAGE_SCHEMA_VERSION=8;' in s and 'const PERSONAL_SNAPSHOT_VERSION = 5;' in s,'schema8/snapshot5')
 # syntax
 scripts='\n'.join(re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>',s,re.S|re.I)); tmp=stage/'_ia.js'; tmp.write_text(scripts,'utf-8'); r=subprocess.run(['node','--check',str(tmp)],capture_output=True,text=True); tmp.unlink(); ck('P1-js-syntax',r.returncode==0,r.stderr.strip() or 'node --check PASS')
 r=subprocess.run(['node','--check',str(stage/'sw.js')],capture_output=True,text=True); ck('P1-sw-syntax',r.returncode==0,r.stderr.strip() or 'node --check PASS')
 # PASS 2 runtime via set_content (network/PWA not claimed)
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  page=browser.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
  errors=[]; page.on('pageerror',lambda e: errors.append(str(e)))
  page.set_content(s,wait_until='domcontentloaded',timeout=30000)
  ck('P2-init-version',page.evaluate('APP_VERSION')=='v101.87','runtime APP_VERSION')
  # about:blank/set_content has no durable localStorage origin in this environment; storage is protected/unmodified by this stage.
  # Stub only the commit boundary so the interaction/state/rerender paths can be exercised without falsely claiming persistence.
  page.evaluate("window.commitDurableChange = function(){ return {ok:true}; }")
  item=page.evaluate("""() => { const x=TEXT_LIBRARY.find(i=>i && i.type!=='library_group' && i.status!=='placeholder' && typeof i.content==='string' && i.content.length>0); return x&&x.id; }""")
  if not item: item=page.evaluate("""() => { const x=TEXT_LIBRARY.find(i=>i && i.type!=='library_group' && i.status!=='placeholder'); return x&&x.id; }""")
  ck('P2-library-item',bool(item),str(item))
  page.evaluate('(id)=>openLibraryText(id,false,null)',item)
  page.wait_for_timeout(50)
  ck('P2-title-button',page.locator('#libraryTitleMarkBtn').count()==1,'title marker button exists')
  page.click('#libraryTitleMarkBtn')
  ck('P2-picker-open',page.locator('#libraryMarkerPicker').evaluate("e=>e.classList.contains('open')"),'picker open')
  ck('P2-picker-classified',page.evaluate("stage6fIsHighlightUiTarget(document.getElementById('libraryMarkerPicker'))"),'shared classifier returns true')
  ck('P2-suppression-active',page.evaluate('stage6fShouldSuppressSelectionCapture()'),'selection capture suppressed')
  # Create a residual non-collapsed title selection AFTER picker is open, then dispatch events that previously escaped to document.
  page.evaluate("""() => {
    const h=document.getElementById('libraryReaderTitle'); const tn=h.firstChild || h; const r=document.createRange();
    if (tn.nodeType===3) r.selectNodeContents(h); else r.selectNodeContents(h);
    const sel=getSelection(); sel.removeAllRanges(); sel.addRange(r);
    window._selectionCaptureTimer=null;
    document.dispatchEvent(new Event('selectionchange',{bubbles:true}));
    const sw=document.querySelector('#libraryMarkerPicker [data-library-marker-color="yellow"]');
    sw.dispatchEvent(new Event('pointerup',{bubbles:true,cancelable:true}));
    sw.dispatchEvent(new Event('touchend',{bubbles:true,cancelable:true}));
  }""")
  page.wait_for_timeout(300)
  ck('P2-touch-selection-isolation',page.locator('#libraryMarkerPicker').evaluate("e=>e.classList.contains('open')") and page.evaluate('_selectionCaptureTimer===null'),'picker remained open and document selection timer not armed')
  ck('P2-no-context-bar',page.locator('#contextActionBar').count()==0 or not page.locator('#contextActionBar').is_visible(),'ordinary selection action bar did not replace title picker')
  # Choose yellow through actual click.
  page.click('#libraryMarkerPicker [data-library-marker-color="yellow"]')
  page.wait_for_timeout(50)
  ck('P2-create-yellow',page.locator('#libraryReaderTitleMark.hl-yellow').count()==1,'inline yellow mark created')
  ck('P2-persist-state',page.evaluate('(id)=>state.libraryMarks[id]&&state.libraryMarks[id].color',item)=='yellow','libraryMarks yellow')
  # direct title click -> picker; recolour blue
  page.click('#libraryReaderTitleMark')
  ck('P2-direct-title-edit',page.locator('#libraryMarkerPicker').evaluate("e=>e.classList.contains('open')"),'direct highlighted title opens picker')
  ck('P2-current-color-indicated',page.locator('[data-library-marker-color="yellow"]').get_attribute('aria-pressed')=='true','yellow aria-pressed true')
  page.click('[data-library-marker-color="blue"]'); page.wait_for_timeout(30)
  ck('P2-recolour-blue',page.locator('#libraryReaderTitleMark.hl-blue').count()==1,'blue inline mark')
  # Remove / undo exact blue
  page.click('#libraryReaderTitleMark'); ck('P2-remove-visible',page.locator('#libraryMarkerRemoveBtn').is_visible(),'remove button visible')
  page.click('#libraryMarkerRemoveBtn'); page.wait_for_timeout(30)
  ck('P2-remove',page.locator('#libraryReaderTitleMark').count()==0 and page.evaluate('(id)=>!state.libraryMarks[id]',item),'mark removed')
  page.evaluate('undoLatestLibraryMarkRemoval()'); page.wait_for_timeout(30)
  ck('P2-undo-exact-color',page.locator('#libraryReaderTitleMark.hl-blue').count()==1 and page.evaluate('(id)=>state.libraryMarks[id].color',item)=='blue','undo restores blue')
  # Keyboard Enter and Space
  page.locator('#libraryReaderTitleMark').focus(); page.keyboard.press('Enter'); ck('P2-keyboard-enter',page.locator('#libraryMarkerPicker').evaluate("e=>e.classList.contains('open')"),'Enter opens picker'); page.evaluate('closeLibraryMarkerPicker()')
  page.locator('#libraryReaderTitleMark').focus(); page.keyboard.press('Space'); ck('P2-keyboard-space',page.locator('#libraryMarkerPicker').evaluate("e=>e.classList.contains('open')"),'Space opens picker'); page.evaluate('closeLibraryMarkerPicker()')
  # Test all 5 colours through state/picker flow, one by one.
  for c in ['yellow','blue','green','purple','pink']:
   page.click('#libraryReaderTitleMark'); page.click(f'[data-library-marker-color="{c}"]'); page.wait_for_timeout(20)
   ck('P2-color-'+c,page.locator(f'#libraryReaderTitleMark.hl-{c}').count()==1,c)
  # Help truth / physical gate honesty
  ck('P2-help-title-guidance','Surligner le titre' in page.content() and 'Lectures marquées' in page.content(),'Help/title strings present')
  ck('P2-no-page-errors',len(errors)==0,'; '.join(errors) if errors else '0 page errors')
  browser.close()
 # PASS 3 active reports
 claim_lines=0; unsupported=[]
 for p in sorted((stage/'reports').glob('*')):
  if not p.is_file(): continue
  for i,line in enumerate(p.read_text('utf-8',errors='ignore').splitlines(),1):
   if line.strip(): claim_lines+=1
   if re.search(r'physical.*PASS|real[- ]device.*PASS',line,re.I) and 'NOT_TESTED' not in line: unsupported.append((p.name,i,line))
 ck('P3-active-report-honesty',not unsupported,f'{claim_lines} nonblank active report lines; unsupported physical PASS={len(unsupported)}')
 # PASS 4 current identity and stale active QA
 qa=(stage/'REAL_DEVICE_QA_CHECKLIST.md').read_text('utf-8'); qac=(stage/'REAL_DEVICE_QA_RESULTS_TEMPLATE.csv').read_text('utf-8')
 ck('P4-qa-current-version','v101.87' in qa and 'v101.87' in qac,'QA references v101.87')
 ck('P4-cache-current','luisa-24h-v101-87' in qa or 'luisa-24h-v101-87' in qac,'current cache in active QA')
 ck('P4-title-physical-not-tested','G-86' in qa and 'NOT_TESTED' in qac,'new physical title gate present/not tested')
 # output
 total=len(rows); passes=sum(r['status']=='PASS' for r in rows)
 summary={'status':'PASS','total':total,'pass':passes,'fail':0,'runtime_sha256':hf(idx),'rows':rows}
 out_json.parent.mkdir(parents=True,exist_ok=True); out_json.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n','utf-8')
 md=['# v101.87 independent four-pass audit','','**PASS**',f'- checks: {passes}/{total} PASS',f'- runtime SHA-256: `{hf(idx)}`','- physical-device title confirmation remains NOT_TESTED and is not inferred from Chromium.','','## Evidence']
 md += [f"- {r['scenario']}: **{r['status']}** — {r['evidence']}" for r in rows]
 out_md.write_text('\n'.join(md)+'\n','utf-8')
 return summary

if __name__=='__main__':
 ap=argparse.ArgumentParser(); ap.add_argument('stage'); ap.add_argument('out_md'); ap.add_argument('out_json'); a=ap.parse_args()
 try: audit(Path(a.stage),Path(a.out_md),Path(a.out_json)); print('PASS')
 except Exception as e: print('FAIL',e); sys.exit(2)
