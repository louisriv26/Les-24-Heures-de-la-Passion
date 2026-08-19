from __future__ import annotations
import argparse,csv,hashlib,json,re,shutil,zipfile,threading,http.server,socketserver
from pathlib import Path
from playwright.sync_api import sync_playwright

class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args): pass

def serve_dir(root):
    handler=lambda *args,**kwargs:_QuietHandler(*args,directory=str(root),**kwargs)
    server=socketserver.TCPServer(('127.0.0.1',0),handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    return server, f"http://127.0.0.1:{server.server_address[1]}/index.html"

def hf(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def jc(s,n):
 m=re.search(r'const\s+'+re.escape(n)+r'\s*=\s*',s);return json.JSONDecoder().raw_decode(s[m.end():])[0]

def qa_truth(root):
 md=(root/'REAL_DEVICE_QA_CHECKLIST.md').read_text('utf-8')
 rows=list(csv.DictReader((root/'REAL_DEVICE_QA_RESULTS_TEMPLATE.csv').open(encoding='utf-8')))
 ids=[r['scenario_id'] for r in rows]; mdids=[f'G-{int(n):02d}' for n in re.findall(r'(?m)^(\d+)\.',md)]
 bad=['Visible version v101.85','luisa-24h-v101-84','updates to v101.85','same v101.85 build','Export/import a v101.85 backup','greater than 4','review is already closed','states that the editorial review of the current attribution layer is already closed']
 stale=[b for b in bad if b in md or any(b in (r.get('scenario') or '') for r in rows)]
 ok=(not stale and len(rows)==85 and ids==mdids and len(ids)==len(set(ids)) and
     'Visible version v101.86' in md and 'luisa-24h-v101-86' in md and 'greater than 5' in md and
     'GE / Lumen Luminis / septembre 2021' in md and
     any(r['scenario_id']=='G-67' and 'unsupported pending/closed' in r['scenario'] for r in rows) and
     all(f'G-{n}' in ids for n in range(81,86)))
 return {'ok':ok,'stale':stale,'rows':len(rows),'last':ids[-1] if ids else None}
def main(z,out):
 shutil.rmtree(out,ignore_errors=True);x=out/'fresh';x.mkdir(parents=True);rows=[]
 def q(n,ok,e):rows.append({'gate':n,'status':'PASS' if ok else 'FAIL','evidence':e})
 with zipfile.ZipFile(z) as zz:
  names=zz.namelist();q('zip-unique-safe',len(names)==len(set(names)) and not [n for n in names if n.startswith('/') or '..' in Path(n).parts],{'members':len(names)});zz.extractall(x)
 fs={p.relative_to(x).as_posix():p for p in x.rglob('*') if p.is_file()};q('member-parity',len(fs)==len(names),len(fs))
 pm=json.loads(fs['metadata/package_manifest.json'].read_text('utf-8'));bad=[r['path'] for r in pm['files'] if r['path'] not in fs or hf(fs[r['path']])!=r['sha256'] or fs[r['path']].stat().st_size!=r['bytes']];q('package-manifest',not bad,bad)
 hm=json.loads(fs['metadata/hash_manifest.json'].read_text('utf-8'));bad=[r['path'] for r in hm['files'] if r['path'] not in fs or hf(fs[r['path']])!=r['sha256']];q('hash-manifest',not bad,bad)
 s=fs['index.html'].read_text('utf-8');q('twins-version',fs['index.html'].read_bytes()==fs['luisa_24_heures.html'].read_bytes() and "const APP_VERSION = 'v101.86';" in s and 'luisa-24h-v101-86' in fs['sw.js'].read_text('utf-8'),hf(fs['index.html']));qa=qa_truth(x);q('active-qa-current-parity',qa['ok'],qa)
 bp=json.loads(fs['metadata/build_provenance.json'].read_text('utf-8'));prot={n:{'sha256':hashlib.sha256(json.dumps(jc(s,n),ensure_ascii=False,separators=(',',':'),sort_keys=True).encode()).hexdigest(),'count':len(jc(s,n))} for n in ['CORPUS','TEXT_LIBRARY','HOUR_LINKED_TEXTS','SPEECH_DATA','INTERNAL_SUBHEADINGS','SPEECH_END_VISUAL_BREAKS']};q('protected',prot==bp['protected_before'],prot)
 # Independently inspect UX with fresh browser implementation.
 with sync_playwright() as p:
  b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox']);c=b.new_context(viewport={'width':430,'height':932});pg=c.new_page();pg.set_content(fs['index.html'].read_text('utf-8'),wait_until='load');pg.wait_for_timeout(500);pg.evaluate("window.__s={lp24_r41_text_anchor_reset:R41_TEXT_ANCHOR_RESET_VERSION};storageRead=k=>({ok:true,value:Object.prototype.hasOwnProperty.call(__s,k)?__s[k]:null,error:null});storageWrite=(k,v)=>(__s[k]=String(v),{ok:true,error:null});storageRemove=k=>(delete __s[k],{ok:true,error:null});");item=pg.evaluate("()=>TEXT_LIBRARY.find(x=>x&&x.type!=='library_group'&&isLibraryItemUserVisible(x)).id")
  pg.evaluate("id=>{state.libraryMarks={};openLibraryText(id,false);openLibraryMarkerPicker(id,document.getElementById('libraryTitleMarkBtn'));applyLibraryMarkerColor('green')}",item);pg.wait_for_timeout(70);d=pg.evaluate("id=>({tag:document.getElementById('libraryReaderTitleMark').tagName,cls:document.getElementById('libraryReaderTitleMark').className,h2:document.getElementById('libraryReaderTitle').className,color:state.libraryMarks[id].color})",item);q('browser-inline-mark',d['tag']=='MARK' and 'hl-green' in d['cls'] and 'library-title-mark-' not in d['h2'] and d['color']=='green',d)
  pg.locator('#libraryReaderTitleMark').click();pg.wait_for_timeout(40);q('browser-direct-picker','open' in (pg.locator('#libraryMarkerPicker').get_attribute('class') or ''),{});pg.evaluate("applyLibraryMarkerColor('pink')");q('browser-recolour',pg.evaluate("id=>state.libraryMarks[id].color",item)=='pink',{})
  pg.evaluate("id=>{openLibraryMarkerPicker(id,document.getElementById('libraryTitleMarkBtn'));removeLibraryMarkerFromPicker();undoLatestLibraryMarkRemoval()}",item);q('browser-remove-undo',pg.evaluate("id=>state.libraryMarks[id].color",item)=='pink',{})
  pg.evaluate('showHelp()');pg.wait_for_timeout(50);ht=pg.locator('#helpModalOverlay').inner_text();q('browser-help',all(x in ht for x in ['Que voulez-vous faire ?','Lectures marquées','Source principale du corpus','GE / Lumen Luminis / septembre 2021']) and 'déjà clôturée' not in ht,{});q('browser-help-jumps',pg.locator('.help-quick-btn').count()==9,pg.locator('.help-quick-btn').count());b.close()
 # Independent report/decision checks.
 reg=list(csv.DictReader(fs['reports/full_regression_matrix.csv'].open(encoding='utf-8')));q('regression',sum(r['status']=='FAIL' for r in reg)==0 and sum(r['status']=='NOT_TESTED' for r in reg)==11,{'rows':len(reg)})
 stale=fs['reports/stale_reference_scan.txt'].read_text('utf-8');q('stale','status=PASS' in stale and 'unjustified=0' in stale,stale.splitlines()[:2]);q('four-pass','FOUR_PASS_PREPACKAGE_GATE = PASS' in fs['audit/independent_four_pass_audit.md'].read_text('utf-8'),{})
 lock=json.loads(fs['metadata/final_decision_lock.json'].read_text('utf-8'));q('prepackage-lock-honest',lock['stage']=='TH1-R2' and lock['final_status']=='PENDING_POSTPACKAGE_AUDITS' and lock['public_release_ready'] is False,lock)
 status='PASS' if all(r['status']=='PASS' for r in rows) else 'FAIL';summary={'audit':'INDEPENDENT_REOPENED_ZIP_AUDIT_GATE','status':status,'zip_sha256':hf(z),'members':len(names),'runtime_sha256':hf(fs['index.html']),'checks':rows};(out/'V10186_TH1_R2_INDEPENDENT_REOPEN_AUDIT.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n','utf-8');lines=['# v101.86 TH1-R2 — Independent reopened-ZIP audit','',f'**INDEPENDENT_REOPENED_ZIP_AUDIT_GATE = {status}**','',f'- ZIP SHA-256: `{summary["zip_sha256"]}`',f'- Runtime SHA-256: `{summary["runtime_sha256"]}`','','| Gate | Status | Evidence |','|---|---|---|']+[f"| {r['gate']} | {r['status']} | {str(r['evidence']).replace('|','¦')[:700]} |" for r in rows];(out/'V10186_TH1_R2_INDEPENDENT_REOPEN_AUDIT.md').write_text('\n'.join(lines)+'\n','utf-8');print(json.dumps(summary,ensure_ascii=False,indent=2));raise SystemExit(0 if status=='PASS' else 1)
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--zip',required=True);a.add_argument('--out',required=True);v=a.parse_args();main(Path(v.zip),Path(v.out))
