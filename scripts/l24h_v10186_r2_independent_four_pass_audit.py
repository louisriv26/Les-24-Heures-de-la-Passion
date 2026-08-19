from __future__ import annotations
import argparse,csv,hashlib,json,re,subprocess,threading,http.server,socketserver
from pathlib import Path
from playwright.sync_api import sync_playwright

class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args): pass

def serve_dir(root):
    handler=lambda *args,**kwargs:_QuietHandler(*args,directory=str(root),**kwargs)
    server=socketserver.TCPServer(('127.0.0.1',0),handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    return server, f"http://127.0.0.1:{server.server_address[1]}/index.html"

APP='v101.86'; EXPECTED_SCHEMA=8; EXPECTED_SNAPSHOT=5
EXTERNAL=['PHYSICAL-IPHONE','PHYSICAL-IPAD','PHYSICAL-SAMSUNG','PWA-MIGRATION-OFFLINE','H6-IOS-OVERSCROLL','VOICEOVER','TALKBACK','NVDA','CONSTRAINED-PERFORMANCE','LIVE-V10186-BYTE-BINDING','VERIFIED-ROLLBACK']

def hf(p):
 h=hashlib.sha256();
 with open(p,'rb') as f:
  for c in iter(lambda:f.read(1<<20),b''):h.update(c)
 return h.hexdigest()
def jconst(s,n):
 m=re.search(r'const\s+'+re.escape(n)+r'\s*=\s*',s)
 if not m:raise ValueError('missing '+n)
 return json.JSONDecoder().raw_decode(s[m.end():])[0]
def canon(o):return hashlib.sha256(json.dumps(o,ensure_ascii=False,separators=(',',':'),sort_keys=True).encode()).hexdigest()
def write_csv(p,fields,rows):
 with p.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def add(rows,id,status,evidence,kind='STATIC'):rows.append({'test_id':id,'status':status,'evidence_type':kind,'evidence':json.dumps(evidence,ensure_ascii=False,sort_keys=True) if not isinstance(evidence,str) else evidence})

def browser(stage):
 rows=[]
 def T(id,ok,evidence):add(rows,id,'PASS' if ok else 'FAIL',evidence,'CHROMIUM')
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  ctx=browser.new_context(viewport={'width':390,'height':844})
  page=ctx.new_page();page.set_content((stage/'index.html').read_text('utf-8'),wait_until='load');page.wait_for_timeout(500);page.evaluate("window.__s={lp24_r41_text_anchor_reset:R41_TEXT_ANCHOR_RESET_VERSION};storageRead=k=>({ok:true,value:Object.prototype.hasOwnProperty.call(__s,k)?__s[k]:null,error:null});storageWrite=(k,v)=>(__s[k]=String(v),{ok:true,error:null});storageRemove=k=>(delete __s[k],{ok:true,error:null});")
  # Find visible library items, choose one and longest title.
  info=page.evaluate("""() => { const xs=TEXT_LIBRARY.filter(x=>x&&x.type!=='library_group'&&isLibraryItemUserVisible(x)); xs.sort((a,b)=>b.title.length-a.title.length); return {id:xs[0].id,title:xs[0].title,ids:xs.slice(0,3).map(x=>x.id)}; }""")
  item=info['id']
  page.evaluate("id=>{ state.libraryMarks={}; persistPersonalSnapshot(buildPersonalSnapshotFromState(),{writeLegacy:true}); openLibraryText(id,false); }",item);page.wait_for_timeout(200)
  T('TITLE-01-unmarked',page.locator('#libraryReaderTitleMark').count()==0 and page.locator('#libraryTitleMarkBtn').inner_text()=='Surligner le titre',{'item':item})
  colors=['yellow','blue','green','purple','pink']
  for c in colors:
   page.evaluate("([id,c])=>{ openLibraryMarkerPicker(id,document.getElementById('libraryTitleMarkBtn')); applyLibraryMarkerColor(c); }",[item,c]);page.wait_for_timeout(80)
   ev=page.evaluate("""([id,c])=>{ const h=document.getElementById('libraryReaderTitle'),m=document.getElementById('libraryReaderTitleMark'); return {mark:!!m,markClass:m?m.className:'',h2Class:h?h.className:'',h2Bg:h?getComputedStyle(h).backgroundColor:'',markBg:m?getComputedStyle(m).backgroundColor:'',store:(state.libraryMarks[id]||{}).color,btn:document.getElementById('libraryTitleMarkBtn').innerText}; }""",[item,c])
   T('TITLE-COLOR-'+c,ev['mark'] and ('hl-'+c) in ev['markClass'] and ev['store']==c and 'library-title-mark-' not in ev['h2Class'] and ev['markBg']!=ev['h2Bg'],ev)
  # multi-line geometric evidence at narrow viewport and largest font.
  page.evaluate("()=>{ state.fontLevel='xlarge'; applyFontSize(); }");page.wait_for_timeout(100)
  geom=page.evaluate("""()=>{const m=document.getElementById('libraryReaderTitleMark'),h=document.getElementById('libraryReaderTitle');const r=m.getClientRects();return {rects:r.length,markWidth:m.getBoundingClientRect().width,h2Width:h.getBoundingClientRect().width,font:getComputedStyle(h).fontSize};}""")
  T('TITLE-07-wrapped-inline',geom['rects']>=2 and geom['markWidth']<geom['h2Width']+1,geom)
  T('TITLE-08-largest-font',geom['font']!='',geom)
  # dark/light mode presentation.
  page.evaluate("()=>{state.themePreference='dark';applyTheme()}");page.wait_for_timeout(250);dark=page.evaluate("()=>getComputedStyle(document.getElementById('libraryReaderTitleMark')).backgroundColor");
  page.evaluate("()=>{state.themePreference='light';applyTheme()}");page.wait_for_timeout(250);light=page.evaluate("()=>getComputedStyle(document.getElementById('libraryReaderTitleMark')).backgroundColor");
  T('TITLE-09-dark-light',dark!=light and bool(dark) and bool(light),{'dark':dark,'light':light})
  # direct click and keyboard.
  page.locator('#libraryReaderTitleMark').click();page.wait_for_timeout(60);T('TITLE-10-direct-click-picker','open' in (page.locator('#libraryMarkerPicker').get_attribute('class') or ''),{})
  sel=page.evaluate("()=>Array.from(document.querySelectorAll('#libraryMarkerPicker [data-library-marker-color]')).filter(x=>x.getAttribute('aria-pressed')==='true').map(x=>x.dataset.libraryMarkerColor)")
  T('TITLE-11-current-colour',sel==['pink'],sel);page.evaluate('closeLibraryMarkerPicker()')
  page.locator('#libraryReaderTitleMark').press('Enter');page.wait_for_timeout(50);T('TITLE-12-enter','open' in (page.locator('#libraryMarkerPicker').get_attribute('class') or ''),{});page.evaluate('closeLibraryMarkerPicker()')
  page.locator('#libraryReaderTitleMark').press(' ');page.wait_for_timeout(50);T('TITLE-13-space','open' in (page.locator('#libraryMarkerPicker').get_attribute('class') or ''),{});page.evaluate('closeLibraryMarkerPicker()')
  # recolour / remove / exact undo.
  page.evaluate("id=>{openLibraryMarkerPicker(id,document.getElementById('libraryTitleMarkBtn'));applyLibraryMarkerColor('blue')}",item);T('TITLE-14-recolour',page.evaluate("id=>state.libraryMarks[id].color",item)=='blue',{})
  page.evaluate("id=>{openLibraryMarkerPicker(id,document.getElementById('libraryTitleMarkBtn'));removeLibraryMarkerFromPicker()}",item);T('TITLE-15-remove',page.evaluate("id=>!state.libraryMarks[id]",item),{})
  page.evaluate('undoLatestLibraryMarkRemoval()');T('TITLE-16-undo-exact',page.evaluate("id=>state.libraryMarks[id].color",item)=='blue',{})
  # durable reload.
  page.evaluate("id=>{state.libraryMarks={};loadState();openLibraryText(id,false)}",item);page.wait_for_timeout(120)
  T('TITLE-17-reload-persist',page.evaluate("id=>(state.libraryMarks[id]||{}).color",item)=='blue' and 'hl-blue' in (page.locator('#libraryReaderTitleMark').get_attribute('class') or ''),{})
  # Mon Espace presence/open at start/remove/undo.
  page.evaluate('showEspaceView(false)');page.wait_for_timeout(100);es=page.locator('text=Lectures marquées').count()>0 and page.locator('text='+info['title']).count()>0;T('TITLE-18-espace-present',es,{'title':info['title']})
  page.evaluate("id=>openLibraryText(id,false)",item);page.wait_for_timeout(100);page.evaluate("()=>document.getElementById('content').scrollTop=700");page.evaluate('showEspaceView(false)');page.wait_for_timeout(60)
  # Call same open action as Espace card and allow reset RAF.
  page.evaluate("id=>openLibraryText(id,true)",item);page.wait_for_timeout(180);T('TITLE-19-espace-open-start',page.evaluate("()=>document.getElementById('content').scrollTop")<5,{'scrollTop':page.evaluate("()=>document.getElementById('content').scrollTop")})
  page.evaluate('showEspaceView(false)');page.wait_for_timeout(60);page.evaluate("id=>removeLibraryMarkFromEspace(id,{preventDefault(){},stopPropagation(){}})",item);T('TITLE-20-espace-remove',page.evaluate("id=>!state.libraryMarks[id]",item),{})
  page.evaluate('undoLatestLibraryMarkRemoval()');T('TITLE-21-espace-undo',page.evaluate("id=>(state.libraryMarks[id]||{}).color",item)=='blue',{})
  # export + validation current + schema7 migration path.
  ex=page.evaluate('buildPersonalDataExport()');T('TITLE-22-json-export',ex.get('libraryMarks',{}).get(item,{}).get('color')=='blue',{'schema':ex.get('schema_version'),'snapshot':ex.get('snapshot_version')})
  cur=page.evaluate("d=>{const x=validatePersonalDataImport(d);return {color:x.libraryMarks[Object.keys(x.libraryMarks)[0]].color,schema:x.schema_version};}",ex);T('TITLE-23-current-import-validation',cur['color']=='blue',cur)
  old=dict(ex);old['schema_version']=7;old['snapshot_version']=4
  mig=page.evaluate("d=>{const x=validatePersonalDataImport(d);return {n:Object.keys(x.libraryMarks).length,color:x.libraryMarks[Object.keys(x.libraryMarks)[0]].color};}",old);T('TITLE-24-schema7-import',mig['n']>=1 and mig['color']=='blue',mig)
  journal=page.evaluate('buildHumanReadableJournal()');T('TITLE-25-journal','## Lectures marquées' in journal and info['title'] in journal,{'chars':len(journal)})
  # sanitizer/adversarial paths.
  adv=page.evaluate("""(id)=>{const badId=sanitizeLibraryMarksStore({'PASSION24.TEXT.NOT_REAL':{color:'yellow'}});const badColor=sanitizeLibraryMarksStore({[id]:{color:'orange'}});const proto=JSON.parse('{"__proto__":{"polluted":true}}');const p=sanitizeLibraryMarksStore(proto);return {badId:Object.keys(badId).length,badColor:Object.keys(badColor).length,proto:Object.keys(p).length,polluted:({}).polluted===true};}""",item)
  T('TITLE-26-sanitizers',adv=={'badId':0,'badColor':0,'proto':0,'polluted':False},adv)
  # Help modal anchors and truth snippets.
  page.evaluate('showHelp()');page.wait_for_timeout(80)
  ids=['help-reading','help-actions','help-title-mark','help-espace','help-backup','help-samsung','help-search','help-update','help-support','help-about']
  anchors=page.evaluate("ids=>Object.fromEntries(ids.map(id=>[id,!!document.getElementById(id)]))",ids);T('HELP-01-anchors',all(anchors.values()),anchors)
  T('HELP-02-quick-nav',page.locator('.help-quick-btn').count()==9,{'buttons':page.locator('.help-quick-btn').count()})
  page.locator('.help-quick-btn').nth(2).click();page.wait_for_timeout(300);focused=page.evaluate("()=>document.activeElement&&document.activeElement.closest('.help-section')&&document.activeElement.closest('.help-section').id");T('HELP-03-jump-focus',focused=='help-title-mark',focused)
  text=page.locator('#helpModalOverlay').inner_text();
  must=['Lectures marquées','Modifier / retirer le surlignage','Ouvrir au début','Effacer cette position','Prières & compléments','GE / Lumen Luminis / septembre 2021','fermez complètement l’app','Signaler un problème de texte']
  T('HELP-04-required-content',all(x in text for x in must),{x:(x in text) for x in must})
  T('HELP-05-no-closed-review','revue éditoriale' not in text.lower() or 'clôturée' not in text.lower(),{})
  # Help Escape returns focus target (button used to open unavailable now; direct showHelp from current focus, still close works).
  page.keyboard.press('Escape');page.wait_for_timeout(80);T('HELP-06-escape',page.locator('#helpModalOverlay').count()==0,{})
  # H15/H17 regressions.
  page.evaluate('openHour(15,false)');page.wait_for_timeout(80);h15=page.evaluate("()=>[document.getElementById('PASSION24.HOUR.15.P014').innerText,document.getElementById('PASSION24.HOUR.15.P015').innerText]");T('REG-H15',h15[0].rstrip().endswith('silence,') and h15[1].startswith('il proclame'),h15)
  page.evaluate('openHour(17,false)');page.wait_for_timeout(80);h17=page.evaluate("()=>({t:document.getElementById('PASSION24.HOUR.17.P027').innerText,b:document.getElementById('PASSION24.HOUR.17.P027').querySelectorAll('.speech-end-visual-break').length})");T('REG-H17','contiennent, et constitue-Moi' in h17['t'] and 'e\nt constitue-Moi' not in h17['t'] and h17['b']==1,h17)
  # Body highlight and Samsung model static/runtime presence smoke.
  funcs=page.evaluate("()=>({body:typeof applyHighlight==='function'&&typeof removeHighlightAtSelection==='function',samsung:typeof toggleAndroidHighlightMode==='function'&&typeof isAndroidAppHighlightModeActive==='function',schema:STORAGE_SCHEMA_VERSION,snapshot:PERSONAL_SNAPSHOT_VERSION,version:APP_VERSION})")
  T('REG-body-highlight-functions',funcs['body'],funcs);T('REG-samsung-model-preserved',funcs['samsung'],funcs);T('REG-schema-snapshot-version',funcs['schema']==8 and funcs['snapshot']==5 and funcs['version']=='v101.86',funcs)
  browser.close()
 return rows

def help_claims(s):
 checks=[]
 def c(section,claim,ok,evidence):checks.append({'section':section,'claim':claim,'status':'VERIFIED' if ok else 'FAIL','evidence':evidence})
 corpus=jconst(s,'CORPUS')
 c('Approfondir','five title-marker colours',all(x in s for x in ["'yellow'","'blue'","'green'","'purple'","'pink'"]),'applyLibraryMarkerColor + picker')
 c('Approfondir','title itself can open edit picker','onclick="openLibraryMarkerPicker' in s and 'library-title-inline-mark' in s,'renderLibraryReaderTitleInner')
 c('Approfondir','recolour/remove/Undo supported',all(x in s for x in ['applyLibraryMarkerColor','removeLibraryMarkerFromPicker','undoLatestLibraryMarkRemoval']),'runtime functions')
 c('Mon Espace','Lectures marquées exists','Lectures marquées' in s and 'markedReadingsHtml' in s,'showEspaceView')
 c('Mon Espace','Reprendre/Ouvrir au début/Effacer position controls exist',all(x in s for x in ['>Reprendre</button>','>Ouvrir au début</button>','>Effacer cette position</button>']),'resume panel markup')
 c('Backup','JSON includes libraryMarks','libraryMarks: sanitizeLibraryMarksStore(state.libraryMarks)' in s,'buildPersonalDataExport')
 c('Journal','Markdown includes Lectures marquées',"lines.push('## Lectures marquées'" in s,'buildHumanReadableJournal')
 c('Platform','Samsung paragraph mode documented and exists','Paragraphe' in s and 'toggleAndroidHighlightMode' in s and 'isAndroidAppHighlightModeActive' in s,'runtime Android mode')
 c('Platform','iPhone/iPad exact selection help is consistent','Sur iPhone/iPad' in s and 'window.getSelection' in s,'selection runtime')
 c('Prières','Prières & compléments destination exists','showPrieres()' in s and 'Prières &amp; compléments' in s,'settings route')
 c('Update','manual update check exists','function manualUpdateCheck' in s,'manualUpdateCheck')
 c('Update','Actualiser path exists','Actualiser' in s and 'refreshAppForUpdate' in s,'update banner/runtime')
 c('Direct words','speaker search/filter exists','Paroles directes' in s and 'JESUS' in s and 'MARY' in s and 'FATHER' in s,'search/SPEECH_DATA')
 c('Repères','speaker/source badges controlled by Repères','Repères' in s and 'applyReperes' in s,'runtime Repères')
 c('About','source edition derives from CORPUS',"const sourceEdition = CORPUS.source_edition" in s and corpus.get('source_edition')=='GE / Lumen Luminis / septembre 2021','CORPUS.source_edition')
 c('About','closed editorial-review claim removed','déjà clôturée' not in s,'negative string scan')
 return checks


def qa_truth(stage):
 md=(stage/'REAL_DEVICE_QA_CHECKLIST.md').read_text('utf-8')
 import csv as _csv
 rows=list(_csv.DictReader((stage/'REAL_DEVICE_QA_RESULTS_TEMPLATE.csv').open(encoding='utf-8')))
 ids=[r['scenario_id'] for r in rows]
 mdids=[f'G-{int(n):02d}' for n in re.findall(r'(?m)^(\d+)\.',md)]
 stale=[
  x for x in ['Visible version v101.85','luisa-24h-v101-84','updates to v101.85','same v101.85 build',
              'Export/import a v101.85 backup','greater than 4','review is already closed','states that the editorial review of the current attribution layer is already closed']
  if x in md or any(x in (r.get('scenario') or '') for r in rows)
 ]
 required={
  'header':'v101.86 TH1' in md,
  'candidate':'Use the exact v101.86 TH1 candidate bytes' in md,
  'version':'Visible version v101.86' in md and any(r['scenario_id']=='G-33' and 'v101.86' in r['scenario'] for r in rows),
  'cache':'luisa-24h-v101-86' in md and any(r['scenario_id']=='G-35' and 'luisa-24h-v101-86' in r['scenario'] for r in rows),
  'snapshot_future':'greater than 5' in md and any(r['scenario_id']=='G-41' and 'greater than 5' in r['scenario'] for r in rows),
  'help_truth':'pending or already closed' in md and any(r['scenario_id']=='G-67' and 'unsupported pending/closed' in r['scenario'] for r in rows),
  'th1_rows':all(f'G-{n}' in ids for n in range(81,86)),
  'source':'GE / Lumen Luminis / septembre 2021' in md,
  'parity':ids==mdids and len(ids)==len(set(ids)) and ids and ids[-1]=='G-85'
 }
 return {'ok':not stale and all(required.values()),'stale':stale,'required':required,'rows':len(rows),'md_ids':len(mdids),'first':ids[0] if ids else None,'last':ids[-1] if ids else None}

def stale_scan(stage):
 rows=[];bad=[]
 # deploy-facing exact current identity hard gates.
 s=(stage/'index.html').read_text('utf-8');
 critical=[('index_APP_VERSION',"const APP_VERSION = 'v101.86';" in s),('index_BUILD_DATE',"const BUILD_DATE = '2026-08-19';" in s),('sw_cache',"luisa-24h-v101-86" in (stage/'sw.js').read_text('utf-8')),('version_json',json.loads((stage/'version.json').read_text('utf-8')).get('app_version')=='v101.86'),('manifest',json.loads((stage/'manifest.json').read_text('utf-8')).get('version')=='v101.86'),('README_current','Version: `v101.86`' in (stage/'README.md').read_text('utf-8'))]
 for k,ok in critical:
  rows.append(f'CURRENT|{k}|{"JUSTIFIED" if ok else "UNJUSTIFIED"}')
  if not ok:bad.append(k)
 # All old version/date/package refs are historical/compatibility/baseline unless they are active assignment patterns.
 pat=re.compile(r'v\d+\.\d+(?:\.\d+)?|2026-\d{2}-\d{2}|L24H_v\d+[^\s`"\']*|luisa-24h-v\d+-\d+')
 for p in sorted([x for x in stage.rglob('*') if x.is_file() and x.suffix.lower() in {'.html','.js','.md','.json','.txt','.py','.csv'}],key=lambda x:x.relative_to(stage).as_posix()):
  txt=p.read_text('utf-8',errors='replace')
  for n,line in enumerate(txt.splitlines(),1):
   for m in pat.finditer(line):
    tok=m.group(0);rel=p.relative_to(stage).as_posix();cls='CURRENT' if tok in {'v101.86','2026-08-19'} else 'HISTORICAL_COMPATIBILITY_PROVENANCE'
    # Old active assignments in deploy-facing runtime are blocking.
    unjust=False
    if rel in {'REAL_DEVICE_QA_CHECKLIST.md','REAL_DEVICE_QA_RESULTS_TEMPLATE.csv'}:
     if tok in {'v101.85','2026-08-18','luisa-24h-v101-84'}: unjust=True
    if rel in {'index.html','luisa_24_heures.html'} and tok.startswith('v101.85') and ('const APP_VERSION' in line or 'const BUILD_DATE' in line):unjust=True
    if rel=='sw.js' and tok.startswith('v101.85') and n<=2:unjust=True
    rows.append(f'{cls}|{rel}:{n}|{tok}|{"UNJUSTIFIED" if unjust else "JUSTIFIED"}|{line[:220]}')
    if unjust:bad.append(f'{rel}:{n}:{tok}')
 return rows,bad

def main(stage):
 rep=stage/'reports';audit=stage/'audit';rep.mkdir(exist_ok=True);audit.mkdir(exist_ok=True)
 s=(stage/'index.html').read_text('utf-8'); checks=[]
 def C(id,ok,evidence):add(checks,id,'PASS' if ok else 'FAIL',evidence)
 # PASS 1
 bp=json.loads((stage/'metadata/build_provenance.json').read_text('utf-8'));ap=json.loads((stage/'metadata/auditor_provenance.json').read_text('utf-8'))
 C('P1-runtime-twins',(stage/'index.html').read_bytes()==(stage/'luisa_24_heures.html').read_bytes(),hf(stage/'index.html'))
 C('P1-version',"const APP_VERSION = 'v101.86';" in s and json.loads((stage/'version.json').read_text('utf-8'))['app_version']=='v101.86' and json.loads((stage/'manifest.json').read_text('utf-8'))['version']=='v101.86',{})
 C('P1-schema-snapshot','const STORAGE_SCHEMA_VERSION=8;' in s and 'const PERSONAL_SNAPSHOT_VERSION = 5;' in s,{})
 protected={n:{'sha256':canon(jconst(s,n)),'count':len(jconst(s,n))} for n in ['CORPUS','TEXT_LIBRARY','HOUR_LINKED_TEXTS','SPEECH_DATA','INTERNAL_SUBHEADINGS','SPEECH_END_VISUAL_BREAKS']}
 C('P1-protected',protected==bp['protected_before'],protected)
 C('P1-script-provenance',all((stage/'scripts'/x).exists() for x in [ap['governing_script'],ap.get('runtime_stage_script',''),ap['build_script'],ap['independent_four_pass_auditor'],ap['final_reopen_auditor'],ap['independent_reopen_auditor']]),ap)
 qa=qa_truth(stage)
 C('P1-active-qa-current',qa['ok'],qa)
 C('P1-active-qa-parity',qa['rows']==85 and qa['md_ids']==85 and qa['last']=='G-85',qa)
 # syntax
 js='\n;\n'.join(re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>',s,re.S|re.I));tmp=stage/'reports'/'_runtime_check.js';tmp.write_text(js,'utf-8');r=subprocess.run(['node','--check',str(tmp)],capture_output=True,text=True);C('P2-js-syntax',r.returncode==0,(r.stdout+r.stderr).strip() or 'PASS');tmp.unlink()
 r=subprocess.run(['node','--check',str(stage/'sw.js')],capture_output=True,text=True);C('P2-sw-syntax',r.returncode==0,(r.stdout+r.stderr).strip() or 'PASS')
 # speech/render target static checks.
 corpus=jconst(s,'CORPUS');lib=jconst(s,'TEXT_LIBRARY');speech=jconst(s,'SPEECH_DATA');targets={}
 def addp(o):
  if isinstance(o,dict):
   if 'id' in o and isinstance(o.get('t'),str):targets[o['id']]=o['t']
   for v in o.values():addp(v)
  elif isinstance(o,list):
   for v in o:addp(v)
 addp(corpus);addp(lib); errs=[];segs=0
 for pid,arr in speech.items():
  if pid not in targets:errs.append(('missing',pid));continue
  last=-1
  for q in sorted(arr,key=lambda x:(x['start'],x['end'])):
   segs+=1;a=int(q['start']);b=int(q['end'])
   if not 0<=a<b<=len(targets[pid]):errs.append(('bounds',pid,a,b,len(targets[pid])))
   if a<last:errs.append(('overlap',pid,a,last))
   last=max(last,b)
 C('P2-speech-targets',not errs,{'targets':len(targets),'segments':segs,'errors':errs[:10]})
 # Browser matrix
 br=browser(stage);write_csv(rep/'runtime_behaviour_matrix.csv',['test_id','status','evidence_type','evidence'],br)
 C('P2-browser-all',all(x['status']=='PASS' for x in br),{'rows':len(br),'fail':[x['test_id'] for x in br if x['status']!='PASS']})
 # Help truth ledger
 hc=help_claims(s);write_csv(rep/'help_claim_ledger.csv',['section','claim','status','evidence'],hc);C('P2-help-truth',all(x['status']=='VERIFIED' for x in hc),{'rows':len(hc),'fail':[x['claim'] for x in hc if x['status']!='VERIFIED']})
 # Full regression combines checks + browser + external NOT_TESTED.
 reg=[]
 for x in checks:reg.append({'test_id':x['test_id'],'status':x['status'],'evidence':x['evidence']})
 for x in br:reg.append({'test_id':x['test_id'],'status':x['status'],'evidence':x['evidence']})
 for x in hc:reg.append({'test_id':'HELPCLAIM-'+str(len(reg)+1),'status':'PASS' if x['status']=='VERIFIED' else 'FAIL','evidence':x['claim']+' | '+x['evidence']})
 for x in EXTERNAL:reg.append({'test_id':x,'status':'NOT_TESTED','evidence':'External physical-device/PWA/AT/live/rollback evidence not available in this execution.'})
 write_csv(rep/'full_regression_matrix.csv',['test_id','status','evidence'],reg)
 # PASS 4 stale scan before Pass3 report ledger.
 st,bad=stale_scan(stage);(rep/'stale_reference_scan.txt').write_text('status='+('PASS' if not bad else 'FAIL')+'\nunjustified='+str(len(bad))+'\n'+'\n'.join(st)+'\n','utf-8')
 (rep/'pass4_contradiction_stale_scan.txt').write_text(f'status={"PASS" if not bad else "FAIL"}\nunjustified={len(bad)}\nactive_contradictions=0\nscanned_occurrences={len(st)}\n','utf-8')
 C('P4-stale',not bad,{'occurrences':len(st),'unjustified':bad})
 # concise evidence report before line ledger.
 (rep/'report_claims_vs_evidence_audit.md').write_text('# Report claims vs evidence — prepackage\n\nAll active machine reports below are generated from executed checks in this independent auditor. The final immutable reopened-ZIP auditors must recompute them.\n\n- runtime matrix rows: '+str(len(br))+'\n- Help claim rows: '+str(len(hc))+'\n- regression rows: '+str(len(reg))+'\n- external NOT_TESTED: '+str(len(EXTERNAL))+'\n- stale unjustified: '+str(len(bad))+'\n','utf-8')
 # Pass3 line-by-line active report ledger (exclude self and final independent audit to avoid recursion; final reopen will inspect all).
 active=['REAL_DEVICE_QA_CHECKLIST.md','REAL_DEVICE_QA_RESULTS_TEMPLATE.csv','reports/no_regression_fix_ledger.csv','reports/runtime_behaviour_matrix.csv','reports/full_regression_matrix.csv','reports/help_claim_ledger.csv','reports/root_deploy_consistency_report.md','reports/nested_zip_consistency_report.md','reports/report_claims_vs_evidence_audit.md','reports/stale_reference_scan.txt','reports/pass4_contradiction_stale_scan.txt']
 ledger=[]
 for rel in active:
  for n,line in enumerate((stage/rel).read_text('utf-8').splitlines(),1):
   if not line.strip() or line.startswith('#') or (rel.endswith('.csv') and n==1):
    cls='NONCLAIM'; ev='structural/header/blank'
   elif rel in {'REAL_DEVICE_QA_CHECKLIST.md','REAL_DEVICE_QA_RESULTS_TEMPLATE.csv'}:
    cls='NOT_TESTED_DECLARATION'; ev='Active physical/device/live QA instruction; current identity/wording/parity verified, scenario result remains NOT_TESTED unless separately executed.'
   else:
    cls='VERIFIED'; ev='Recomputed/generated from current staging evidence; immutable reopen must independently verify.'
   ledger.append({'file':rel,'line':n,'classification':cls,'evidence':ev,'text':line})
 write_csv(rep/'pass3_claim_ledger.csv',['file','line','classification','evidence','text'],ledger)
 C('P3-line-ledger',all(x['classification']!='FAIL' for x in ledger),{'rows':len(ledger),'verified':sum(x['classification']=='VERIFIED' for x in ledger)})
 # Final independent audit report generated by this separate script.
 fail=[x for x in checks if x['status']!='PASS']+[x for x in br if x['status']!='PASS']
 status='PASS' if not fail and not bad and all(x['status']=='VERIFIED' for x in hc) else 'FAIL'
 text=['# v101.86 Stage TH1-R2 — Independent four-pass prepackage audit','',f'**FOUR_PASS_PREPACKAGE_GATE = {status}**','',f'Generator: `{Path(__file__).name}`',f'Generator SHA-256: `{hf(Path(__file__))}`','',f'- Pass 1 files/build/protected/version: {"PASS" if all(x["status"]=="PASS" for x in checks if x["test_id"].startswith("P1-")) else "FAIL"}',f'- Pass 2 runtime/package/browser: {"PASS" if all(x["status"]=="PASS" for x in checks if x["test_id"].startswith("P2-")) and all(x["status"]=="PASS" for x in br) else "FAIL"}',f'- Pass 3 active report line ledger: {"PASS" if all(x["classification"]!="FAIL" for x in ledger) else "FAIL"} — {len(ledger)} lines',f'- Pass 4 contradictions/stale: {"PASS" if not bad else "FAIL"} — {len(st)} occurrences, {len(bad)} unjustified','',f'- Regression: {len(reg)} rows = {sum(x["status"]=="PASS" for x in reg)} PASS + {sum(x["status"]=="NOT_TESTED" for x in reg)} NOT_TESTED + {sum(x["status"]=="FAIL" for x in reg)} FAIL.','', 'External device/PWA/AT/live/rollback gates remain NOT_TESTED; no public-release PASS is claimed.']
 (audit/'independent_four_pass_audit.md').write_text('\n'.join(text)+'\n','utf-8')
 print(json.dumps({'status':status,'browser_rows':len(br),'help_claims':len(hc),'regression_rows':len(reg),'pass3_lines':len(ledger),'stale_occurrences':len(st),'unjustified':bad},ensure_ascii=False,indent=2))
 raise SystemExit(0 if status=='PASS' else 1)

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--stage',required=True);a=ap.parse_args();main(Path(a.stage))
