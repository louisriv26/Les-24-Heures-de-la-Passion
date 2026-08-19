from __future__ import annotations
import argparse,csv,hashlib,json,re,shutil,subprocess,zipfile,threading,http.server,socketserver
from pathlib import Path
from playwright.sync_api import sync_playwright

class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args): pass

def serve_dir(root):
    handler=lambda *args,**kwargs:_QuietHandler(*args,directory=str(root),**kwargs)
    server=socketserver.TCPServer(('127.0.0.1',0),handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    return server, f"http://127.0.0.1:{server.server_address[1]}/index.html"

def hf(p):
 h=hashlib.sha256();
 with open(p,'rb') as f:
  for c in iter(lambda:f.read(1<<20),b''):h.update(c)
 return h.hexdigest()
def jconst(s,n):
 m=re.search(r'const\s+'+re.escape(n)+r'\s*=\s*',s);return json.JSONDecoder().raw_decode(s[m.end():])[0]
def canon(o):return hashlib.sha256(json.dumps(o,ensure_ascii=False,separators=(',',':'),sort_keys=True).encode()).hexdigest()

def qa_truth(root):
 md=(root/'REAL_DEVICE_QA_CHECKLIST.md').read_text('utf-8')
 rows=list(csv.DictReader((root/'REAL_DEVICE_QA_RESULTS_TEMPLATE.csv').open(encoding='utf-8')))
 ids=[r['scenario_id'] for r in rows]; mdids=[f'G-{int(n):02d}' for n in re.findall(r'(?m)^(\d+)\.',md)]
 bad=['Visible version v101.85','luisa-24h-v101-84','updates to v101.85','same v101.85 build','Export/import a v101.85 backup','greater than 4','review is already closed','states that the editorial review of the current attribution layer is already closed']
 stale=[b for b in bad if b in md or any(b in (r.get('scenario') or '') for r in rows)]
 required=(
  'v101.86 TH1' in md and 'Use the exact v101.86 TH1 candidate bytes' in md and
  'Visible version v101.86' in md and 'luisa-24h-v101-86' in md and 'greater than 5' in md and
  'GE / Lumen Luminis / septembre 2021' in md and
  any(r['scenario_id']=='G-67' and 'unsupported pending/closed' in r['scenario'] for r in rows) and
  all(f'G-{n}' in ids for n in range(81,86)) and ids==mdids and len(ids)==len(set(ids)) and len(ids)==85
 )
 return {'ok':not stale and required,'stale':stale,'rows':len(rows),'md_rows':len(mdids),'first':ids[0] if ids else None,'last':ids[-1] if ids else None}

def browser(x):
 rows=[]
 def t(n,ok,e):rows.append({'test':n,'status':'PASS' if ok else 'FAIL','evidence':e})
 with sync_playwright() as p:
  b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox']);c=b.new_context(viewport={'width':390,'height':844});pg=c.new_page();pg.set_content((x/'index.html').read_text('utf-8'),wait_until='load');pg.wait_for_timeout(500);pg.evaluate("window.__s={lp24_r41_text_anchor_reset:R41_TEXT_ANCHOR_RESET_VERSION};storageRead=k=>({ok:true,value:Object.prototype.hasOwnProperty.call(__s,k)?__s[k]:null,error:null});storageWrite=(k,v)=>(__s[k]=String(v),{ok:true,error:null});storageRemove=k=>(delete __s[k],{ok:true,error:null});")
  item=pg.evaluate("()=>TEXT_LIBRARY.filter(x=>x&&x.type!=='library_group'&&isLibraryItemUserVisible(x)).sort((a,b)=>b.title.length-a.title.length)[0].id")
  pg.evaluate("id=>{state.libraryMarks={};persistPersonalSnapshot(buildPersonalSnapshotFromState(),{writeLegacy:true});openLibraryText(id,false);openLibraryMarkerPicker(id,document.getElementById('libraryTitleMarkBtn'));applyLibraryMarkerColor('yellow')}",item);pg.wait_for_timeout(80)
  q=pg.evaluate("id=>({class:document.getElementById('libraryReaderTitleMark').className,h2:document.getElementById('libraryReaderTitle').className,store:state.libraryMarks[id].color,rects:document.getElementById('libraryReaderTitleMark').getClientRects().length})",item);t('inline-title',q['store']=='yellow' and 'hl-yellow' in q['class'] and 'library-title-mark-' not in q['h2'],q)
  pg.locator('#libraryReaderTitleMark').click();pg.wait_for_timeout(50);sel=pg.evaluate("()=>Array.from(document.querySelectorAll('#libraryMarkerPicker [aria-pressed=true]')).map(x=>x.dataset.libraryMarkerColor)");t('direct-edit-current',sel==['yellow'],sel)
  pg.evaluate("applyLibraryMarkerColor('purple')");t('recolour',pg.evaluate("id=>state.libraryMarks[id].color",item)=='purple',{})
  pg.evaluate("id=>{openLibraryMarkerPicker(id,document.getElementById('libraryTitleMarkBtn'));removeLibraryMarkerFromPicker();undoLatestLibraryMarkRemoval()}",item);t('remove-undo',pg.evaluate("id=>state.libraryMarks[id].color",item)=='purple',{})
  pg.evaluate("id=>{state.libraryMarks={};loadState();openLibraryText(id,false)}",item);pg.wait_for_timeout(100);t('reload',pg.evaluate("id=>(state.libraryMarks[id]||{}).color",item)=='purple',{})
  pg.evaluate('showHelp()');pg.wait_for_timeout(60);txt=pg.locator('#helpModalOverlay').inner_text();t('help-truth',all(z in txt for z in ['Lectures marquées','GE / Lumen Luminis / septembre 2021','Modifier / retirer le surlignage','fermez complètement l’app']) and 'déjà clôturée' not in txt,{})
  t('help-anchors',pg.locator('.help-quick-btn').count()==9 and pg.locator('#help-title-mark').count()==1,{'quick':pg.locator('.help-quick-btn').count()})
  pg.keyboard.press('Escape');t('help-close',pg.locator('#helpModalOverlay').count()==0,{})
  pg.evaluate('openHour(15,false)');pg.wait_for_timeout(50);h15=pg.evaluate("()=>[document.getElementById('PASSION24.HOUR.15.P014').innerText,document.getElementById('PASSION24.HOUR.15.P015').innerText]");t('H15',h15[0].rstrip().endswith('silence,') and h15[1].startswith('il proclame'),h15)
  pg.evaluate('openHour(17,false)');pg.wait_for_timeout(50);h17=pg.evaluate("()=>document.getElementById('PASSION24.HOUR.17.P027').innerText");t('H17','contiennent, et constitue-Moi' in h17 and 'e\nt constitue-Moi' not in h17,h17[:180])
  b.close()
 return rows

def main(z,out):
 shutil.rmtree(out,ignore_errors=True);x=out/'extracted';x.mkdir(parents=True);checks=[]
 def G(n,ok,e):checks.append({'gate':n,'status':'PASS' if ok else 'FAIL','evidence':e});
 cp=subprocess.run(['unzip','-tqq',str(z)],capture_output=True,text=True);G('archive-integrity',cp.returncode==0,(cp.stdout+cp.stderr).strip() or 'PASS')
 with zipfile.ZipFile(z) as zz:
  names=zz.namelist();G('duplicates',len(names)==len(set(names)),{'members':len(names)});G('path-safety',not [n for n in names if n.startswith('/') or '..' in Path(n).parts],[]);zz.extractall(x)
 fs={p.relative_to(x).as_posix():p for p in x.rglob('*') if p.is_file()};G('member-count',len(fs)==len(names),{'actual':len(fs),'zip':len(names)})
 req=['index.html','luisa_24_heures.html','REAL_DEVICE_QA_CHECKLIST.md','REAL_DEVICE_QA_RESULTS_TEMPLATE.csv','metadata/hash_manifest.json','metadata/package_manifest.json','metadata/build_provenance.json','metadata/auditor_provenance.json','metadata/final_decision_lock.json','audit/independent_four_pass_audit.md','reports/runtime_behaviour_matrix.csv','reports/full_regression_matrix.csv','reports/help_claim_ledger.csv','reports/pass3_claim_ledger.csv','reports/stale_reference_scan.txt']
 G('required-universe',not [r for r in req if r not in fs],[r for r in req if r not in fs])
 pm=json.loads(fs['metadata/package_manifest.json'].read_text('utf-8'));pmr={r['path']:(r['sha256'],r['bytes']) for r in pm['files']};G('package-manifest-set',set(pmr)|{'metadata/package_manifest.json'}==set(fs),{'manifest':len(pmr),'actual':len(fs)});G('package-manifest-values',not [n for n,(h,b) in pmr.items() if hf(fs[n])!=h or fs[n].stat().st_size!=b],[])
 hm=json.loads(fs['metadata/hash_manifest.json'].read_text('utf-8'));hmr={r['path']:(r['sha256'],r['bytes']) for r in hm['files']};scope=set(fs)-{'metadata/hash_manifest.json','metadata/package_manifest.json'};G('hash-manifest-set',set(hmr)==scope,{'manifest':len(hmr),'scope':len(scope)});G('hash-manifest-values',not [n for n,(h,b) in hmr.items() if hf(fs[n])!=h or fs[n].stat().st_size!=b],[])
 s=fs['index.html'].read_text('utf-8');G('runtime-twins',fs['index.html'].read_bytes()==fs['luisa_24_heures.html'].read_bytes(),hf(fs['index.html']));G('version-cache',"const APP_VERSION = 'v101.86';" in s and "luisa-24h-v101-86" in fs['sw.js'].read_text('utf-8') and json.loads(fs['version.json'].read_text('utf-8'))['app_version']=='v101.86',{});qa=qa_truth(x);G('active-qa-current-parity',qa['ok'],qa)
 bp=json.loads(fs['metadata/build_provenance.json'].read_text('utf-8'));prot={n:{'sha256':canon(jconst(s,n)),'count':len(jconst(s,n))} for n in ['CORPUS','TEXT_LIBRARY','HOUR_LINKED_TEXTS','SPEECH_DATA','INTERNAL_SUBHEADINGS','SPEECH_END_VISUAL_BREAKS']};G('protected-data',prot==bp['protected_before'],prot)
 # JS syntax.
 js='\n;\n'.join(re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>',s,re.S|re.I));tmp=out/'runtime.js';tmp.write_text(js,'utf-8');r=subprocess.run(['node','--check',str(tmp)],capture_output=True,text=True);G('js-syntax',r.returncode==0,(r.stdout+r.stderr).strip() or 'PASS');r=subprocess.run(['node','--check',str(fs['sw.js'])],capture_output=True,text=True);G('sw-syntax',r.returncode==0,(r.stdout+r.stderr).strip() or 'PASS')
 # Speech actual text targets.
 targets={}
 def walk(o):
  if isinstance(o,dict):
   if isinstance(o.get('id'),str) and isinstance(o.get('t'),str):targets[o['id']]=o['t']
   for v in o.values():walk(v)
  elif isinstance(o,list):
   for v in o:walk(v)
 walk(jconst(s,'CORPUS'));walk(jconst(s,'TEXT_LIBRARY'));errs=[];seg=0
 for pid,arr in jconst(s,'SPEECH_DATA').items():
  if pid not in targets:errs.append(('missing',pid));continue
  last=-1
  for q in sorted(arr,key=lambda x:(x['start'],x['end'])):
   seg+=1;a=int(q['start']);b=int(q['end']);
   if not 0<=a<b<=len(targets[pid]):errs.append(('bounds',pid,a,b))
   if a<last:errs.append(('overlap',pid,a,last))
   last=max(last,b)
 G('speech-target-offsets',not errs,{'targets':len(targets),'segments':seg,'errors':errs[:5]})
 # Reports truth.
 rr=list(csv.DictReader(fs['reports/runtime_behaviour_matrix.csv'].open(encoding='utf-8')));G('runtime-report',rr and all(r['status']=='PASS' for r in rr),{'rows':len(rr),'fail':sum(r['status']!='PASS' for r in rr)})
 hc=list(csv.DictReader(fs['reports/help_claim_ledger.csv'].open(encoding='utf-8')));G('help-claims',hc and all(r['status']=='VERIFIED' for r in hc),{'rows':len(hc),'fail':sum(r['status']!='VERIFIED' for r in hc)})
 rg=list(csv.DictReader(fs['reports/full_regression_matrix.csv'].open(encoding='utf-8')));counts={k:sum(r['status']==k for r in rg) for k in ['PASS','NOT_TESTED','FAIL']};G('regression-truth',counts['FAIL']==0 and counts['NOT_TESTED']==11,{'rows':len(rg),**counts})
 st=fs['reports/stale_reference_scan.txt'].read_text('utf-8');G('stale-scan','status=PASS' in st and 'unjustified=0' in st,st.splitlines()[:3])
 # exact Pass3 coverage of specified active reports.
 active=['REAL_DEVICE_QA_CHECKLIST.md','REAL_DEVICE_QA_RESULTS_TEMPLATE.csv','reports/no_regression_fix_ledger.csv','reports/runtime_behaviour_matrix.csv','reports/full_regression_matrix.csv','reports/help_claim_ledger.csv','reports/root_deploy_consistency_report.md','reports/nested_zip_consistency_report.md','reports/report_claims_vs_evidence_audit.md','reports/stale_reference_scan.txt','reports/pass4_contradiction_stale_scan.txt'];expected={(r,n) for r in active for n,_ in enumerate(fs[r].read_text('utf-8').splitlines(),1)};ld=list(csv.DictReader(fs['reports/pass3_claim_ledger.csv'].open(encoding='utf-8')));actual={(r['file'],int(r['line'])) for r in ld};G('pass3-line-coverage',actual==expected and not [r for r in ld if r['classification']=='FAIL'],{'expected':len(expected),'ledger':len(actual),'missing':list(expected-actual)[:3]})
 lock=json.loads(fs['metadata/final_decision_lock.json'].read_text('utf-8'));G('package-lock-honest',lock['stage']=='TH1-R2' and lock['final_status']=='PENDING_POSTPACKAGE_AUDITS' and lock['final_package_reopen_gate']=='REQUIRED_POSTPACKAGE' and lock['public_release_ready'] is False,lock)
 br=browser(x);G('fresh-browser',all(r['status']=='PASS' for r in br),{'rows':len(br),'fail':[r for r in br if r['status']!='PASS']});(out/'browser_runtime_test.json').write_text(json.dumps(br,ensure_ascii=False,indent=2)+'\n','utf-8')
 status='PASS' if all(c['status']=='PASS' for c in checks) else 'FAIL';summary={'audit':'FINAL_PACKAGE_REOPEN_GATE','status':status,'zip':z.name,'zip_sha256':hf(z),'bytes':z.stat().st_size,'members':len(zipfile.ZipFile(z).namelist()),'runtime_sha256':hf(fs['index.html']),'checks':checks}
 (out/'V10186_TH1_FINAL_PACKAGE_REOPEN_AUDIT.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n','utf-8');lines=['# v101.86 TH1-R2 — Final immutable reopened-ZIP audit','',f'**FINAL_PACKAGE_REOPEN_GATE = {status}**','',f'- ZIP SHA-256: `{summary["zip_sha256"]}`',f'- Members: {summary["members"]}',f'- Runtime SHA-256: `{summary["runtime_sha256"]}`','','| Gate | Status | Evidence |','|---|---|---|']+[f"| {c['gate']} | {c['status']} | {str(c['evidence']).replace('|','¦').replace(chr(10),' ')[:700]} |" for c in checks];(out/'V10186_TH1_FINAL_PACKAGE_REOPEN_AUDIT.md').write_text('\n'.join(lines)+'\n','utf-8');print(json.dumps(summary,ensure_ascii=False,indent=2));raise SystemExit(0 if status=='PASS' else 1)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--zip',required=True);a.add_argument('--out',required=True);x=a.parse_args();main(Path(x.zip),Path(x.out))
