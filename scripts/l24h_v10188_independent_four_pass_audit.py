from __future__ import annotations
import argparse,csv,hashlib,json,re,subprocess,sys,zipfile
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE=Path('/mnt/data/L24H_v10187_GITHUB_DEPLOY_TITLE_REAL_DEVICE_ISOLATION_R1.zip')
BASE_SHA='710416524b57501f5154fd9b333c19ac622b3352c2d36a6d7af8f07172538d28'
PROTECTED=['CORPUS','TEXT_LIBRARY','HOUR_LINKED_TEXTS','SPEECH_DATA','INTERNAL_SUBHEADINGS','SPEECH_END_VISUAL_BREAKS']

def hb(b): return hashlib.sha256(b).hexdigest()
def hf(p): return hb(Path(p).read_bytes())
def jconst(s,name):
    m=re.search(r'const\s+'+re.escape(name)+r'\s*=\s*',s)
    if not m: raise AssertionError('missing const '+name)
    return json.JSONDecoder().raw_decode(s[m.end():])[0]
def ph(s):
    return {n:hb(json.dumps(jconst(s,n),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()) for n in PROTECTED}
def audit(stage:Path,out_md:Path,out_json:Path):
    rows=[]
    def ck(name,cond,evidence):
        rows.append({'scenario':name,'status':'PASS' if cond else 'FAIL','evidence':evidence})
        if not cond: raise AssertionError(name+': '+evidence)
    idx=stage/'index.html'; twin=stage/'luisa_24_heures.html'; s=idx.read_text('utf-8')
    with zipfile.ZipFile(BASE) as z: bs=z.read('index.html').decode('utf-8')
    # Pass 1
    ck('P1-runtime-twins',idx.read_bytes()==twin.read_bytes(),hf(idx))
    ck('P1-version',"const APP_VERSION = 'v101.88';" in s,'v101.88')
    ck('P1-cache',"const CACHE_NAME = 'luisa-24h-v101-88';" in (stage/'sw.js').read_text('utf-8'),'cache v101-88')
    ck('P1-schema','const STORAGE_SCHEMA_VERSION=8;' in s and 'const PERSONAL_SNAPSHOT_VERSION = 5;' in s,'schema8/snapshot5')
    ck('P1-protected',ph(s)==ph(bs),'6/6 protected hashes identical to v101.87')
    ck('P1-title-helper','function makeLibraryTitleId(itemId)' in s,'stable .TITLE helper')
    ck('P1-title-target',"type:'library_title'" in s,'getTargetInfo library_title')
    ck('P1-shared-selector','SELECTABLE_TEXT_SURFACE_SELECTOR' in s and '.library-title-selectable' in s,'shared selectable selector')
    ck('P1-marker-separation','library-title-inline-mark' not in re.search(r'function renderLibraryReaderTitleInner\(item\).*?\n\}',s,re.S).group(0),'title renderer no libraryMarks wrapper')
    ck('P1-marker-wording','Marquer cette lecture' in s and 'Surligner le titre' not in re.search(r'function refreshLibraryMarkerTitleUi\(itemId\).*?\n\}',s,re.S).group(0),'reading marker distinct')
    # syntax
    scripts='\n'.join(re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>',s,re.S|re.I)); tmp=stage/'_v10188_check.js'; tmp.write_text(scripts,'utf-8')
    r=subprocess.run(['node','--check',str(tmp)],capture_output=True,text=True); tmp.unlink(); ck('P1-js-syntax',r.returncode==0,r.stderr.strip() or 'node --check PASS')
    r=subprocess.run(['node','--check',str(stage/'sw.js')],capture_output=True,text=True); ck('P1-sw-syntax',r.returncode==0,r.stderr.strip() or 'node --check PASS')

    # Pass 2 runtime. set_content has opaque origin, so stub durability only; annotation/state/render logic is real.
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
        errors=[]; page.on('pageerror',lambda e: errors.append(str(e)))
        page.set_content(s,wait_until='domcontentloaded',timeout=30000)
        page.evaluate("window.commitDurableChange=function(){return {ok:true};}; window.saveState=function(){return {ok:true};};")
        ck('P2-version-runtime',page.evaluate('APP_VERSION')=='v101.88','runtime v101.88')
        items=page.evaluate("""() => TEXT_LIBRARY.filter(i=>i&&i.id&&i.id.startsWith('PASSION24.TEXT.')&&i.type!=='library_group'&&i.status!=='hidden_scope_excluded'&&i.status!=='placeholder').map(i=>i.id)""")
        ck('P2-visible-title-count',len(items)==33,f'{len(items)} titles')
        # all title targets
        all_ok=page.evaluate("""ids => ids.every(id=>{const tid=makeLibraryTitleId(id),x=getTargetInfo(tid);return !!x&&x.type==='library_title'&&x.libraryId===id&&x.text===getLibraryItem(id).title&&validPersonalId(tid);})""",items)
        ck('P2-all-title-targets',all_ok,'33/33 target registry')
        item=items[0]
        page.evaluate('(id)=>openLibraryText(id,false,null)',item); page.wait_for_timeout(30)
        tid=page.evaluate('(id)=>makeLibraryTitleId(id)',item)
        ck('P2-title-dom',page.locator('.library-title-selectable').count()==1 and page.locator('#'+tid.replace('.','\\.')).count()==1,'selectable title DOM + stable id')
        ck('P2-title-not-ui',not page.locator('.library-title-selectable').evaluate("e=>e.matches('[data-highlight-ui], [role=button]')"),'title is content, not marker UI')
        ck('P2-marker-button',page.locator('#libraryTitleMarkBtn').inner_text().strip()=='Marquer cette lecture','separate reading marker')
        # Real Range inside title
        result=page.evaluate("""() => {
          const el=document.querySelector('.library-title-selectable'); const tn=el.firstChild; const text=el.textContent;
          const start=Math.max(0,Math.min(2,text.length-4)); const end=Math.min(text.length,start+Math.max(3,Math.min(8,text.length-start)));
          const r=document.createRange(); r.setStart(tn,start); r.setEnd(tn,end);
          const selected=r.toString(); const ok=setPendingSelectionFromRange(r,null,true);
          return {ok,selected,pending:state._pending,bar:!!document.getElementById('contextActionBar')};
        }""")
        ck('P2-title-range-capture',result['ok'] and result['pending']['paraId']==tid and result['pending']['text']==result['selected'] and result['bar'],'native-range pipeline')
        bartext=page.locator('#contextActionBar').inner_text()
        ck('P2-title-actions',all(x in bartext for x in ['Surligner','Note','Copier','Fermer']),bartext.replace('\n',' / '))
        # highlight selected part
        page.click('#contextActionBar button:has-text("Surligner")'); page.wait_for_timeout(10)
        page.click('#colourPicker .cp-yellow'); page.wait_for_timeout(30)
        arr=page.evaluate('(id)=>state.textHighlights[id]||[]',tid)
        ck('P2-title-highlight-created',len(arr)==1 and arr[0]['color']=='yellow' and arr[0]['target_type']=='library_title','title textHighlight yellow')
        ck('P2-title-highlight-inline',page.locator(f'#{tid.replace(".","\\.")} mark.hl-yellow').count()==1,'only selected words rendered with normal mark')
        ck('P2-integrity-fields',all(arr[0].get(k) for k in ['text_hash','para_hash','paragraph_fingerprint']),'hash metadata present')
        # recolour/remove/undo existing generic highlight
        page.locator(f'#{tid.replace(".","\\.")} mark.hl-yellow').click(); page.click('#colourPicker .cp-blue'); page.wait_for_timeout(20)
        ck('P2-title-recolour',page.locator(f'#{tid.replace(".","\\.")} mark.hl-blue').count()==1,'blue')
        page.locator(f'#{tid.replace(".","\\.")} mark.hl-blue').click(); ck('P2-remove-visible',page.locator('#cpRemoveBtn').is_visible(),'remove button')
        page.click('#cpRemoveBtn'); page.wait_for_timeout(20)
        ck('P2-title-remove',not page.evaluate('(id)=>!!(state.textHighlights[id]&&state.textHighlights[id].length)',tid),'removed')
        page.evaluate('undoLatestAnnotationDeletion()'); page.wait_for_timeout(20)
        ck('P2-title-undo',page.locator(f'#{tid.replace(".","\\.")} mark.hl-blue').count()==1,'undo restores blue')
        # second non-overlapping title highlight by direct state + rerender through generic renderer
        page.evaluate("""id => { const info=getTargetInfo(id); const a=state.textHighlights[id][0]; const st=Math.min(info.text.length-2,a.end_offset+1); if(st+1<info.text.length){state.textHighlights[id].push({id:'hl_second',target_id:id,target_type:'library_title',start_offset:st,end_offset:Math.min(info.text.length,st+2),start:st,end:Math.min(info.text.length,st+2),color:'green',text:info.text.slice(st,Math.min(info.text.length,st+2)),selected_text_snapshot:info.text.slice(st,Math.min(info.text.length,st+2)),text_hash:stableTextHash(info.text),para_hash:stableTextHash(info.text.slice(st,Math.min(info.text.length,st+2))),paragraph_fingerprint:stableTextHash(info.text),schema_version:STORAGE_SCHEMA_VERSION,created_at:new Date().toISOString(),updated_at:new Date().toISOString()});rerenderPara(id);} }""",tid)
        ck('P2-multiple-title-highlights',page.locator(f'#{tid.replace(".","\\.")} mark.hl').count()>=2,'two title marks coexist')
        # whole-reading marker must not rewrite title highlights
        page.click('#libraryTitleMarkBtn'); page.click('#libraryMarkerPicker [data-library-marker-color="pink"]'); page.wait_for_timeout(20)
        ck('P2-reading-mark-coexist',page.evaluate('(id)=>state.libraryMarks[id]&&state.libraryMarks[id].color',item)=='pink' and page.locator(f'#{tid.replace(".","\\.")} mark.hl').count()>=2,'libraryMark independent of title textHighlights')
        ck('P2-marker-ui-renamed',page.locator('#libraryTitleMarkBtn').inner_text().strip()=='Modifier / retirer le repère','reading-marker wording')
        # Note action on title from fresh selection
        page.evaluate("""() => {closeLibraryMarkerPicker(); const el=document.querySelector('.library-title-selectable'),tn=el.firstChild; const r=document.createRange();r.setStart(tn,0);r.setEnd(tn,Math.min(4,tn.nodeValue.length));setPendingSelectionFromRange(r,null,true);}""")
        page.click('#contextActionBar button:has-text("Note")'); ck('P2-title-note-modal',page.locator('#noteModal').evaluate("e=>e.classList.contains('open')"),'note modal')
        page.fill('#noteTextarea','Note titre test'); page.click('.note-save-btn'); page.wait_for_timeout(10)
        ck('P2-title-note-store',page.evaluate('(id)=>!!(state.notes[id]&&state.notes[id][0]&&state.notes[id][0].text==="Note titre test")',tid),'note stored on title target')
        page.evaluate('closeNoteModal()')
        # Copy path capture
        page.evaluate("""() => {window.__copied=''; window.fallbackCopyText=(t)=>{window.__copied=t;}; const el=document.querySelector('.library-title-selectable'),tn=el.firstChild; const r=document.createRange();r.setStart(tn,0);r.setEnd(tn,Math.min(5,tn.nodeValue.length));setPendingSelectionFromRange(r,null,true);}""")
        page.click('#contextActionBar button:has-text("Copier")'); page.wait_for_timeout(30)
        ck('P2-title-copy',bool(page.evaluate('window.__copied')),'copy wrote selected title text/context')
        # Mon Espace finds title highlight/note; open target returns library view
        page.evaluate('showEspaceView(false)'); page.wait_for_timeout(20)
        ck('P2-espace-title-highlight','Titre —' in page.content(),'Mon Espace title target label')
        page.evaluate('(id)=>openHighlightTarget(id)',tid); page.wait_for_timeout(120)
        ck('P2-open-highlight-target',page.evaluate('state.view')=='libraryText' and page.evaluate('state.currentSection')==item,'reopens reading')
        # body highlight regression
        body=page.locator('.library-reader-body .para-text').first
        ck('P2-body-present',body.count()==1,'body surface')
        page.evaluate("""() => {const el=document.querySelector('.library-reader-body .para-text'),tn=el.firstChild;if(!tn||tn.nodeType!==3){return false;}const r=document.createRange();r.setStart(tn,0);r.setEnd(tn,Math.min(4,tn.nodeValue.length));return setPendingSelectionFromRange(r,null,true);}""")
        page.click('#contextActionBar button:has-text("Surligner")'); page.click('#colourPicker .cp-yellow');
        ck('P2-body-highlight-regression',page.locator('.library-reader-body mark.hl-yellow').count()>=1,'ordinary body highlight still works')
        # Android must not claim title as paragraph target in explicit paragraph mode
        page.evaluate("""() => {document.documentElement.classList.add('android-scroll-fix');_androidAppHighlightMode=true;updateAndroidHighlightModeUi();}""")
        title_android=page.evaluate("""() => {const el=document.querySelector('.library-title-selectable'); return stage6hPrepareAndroidParagraphPending(el);}""")
        ck('P2-samsung-title-not-added',title_android is False,'title excluded from Samsung paragraph mode')
        page.evaluate("""() => {const el=document.querySelector('.library-reader-body .para-text'); state._pending=null; return stage6hPrepareAndroidParagraphPending(el);}""")
        ck('P2-samsung-body-preserved',page.evaluate('!!(state._pending&&state._pending.android_paragraph_mode)'),'body paragraph mode unchanged')
        # Help truth
        html=page.content()
        ck('P2-help-separation','Marquer cette lecture' in html and 'sélectionnez' in html and 'titre' in html.lower(),'Help distinguishes title text and reading marker')
        ck('P2-no-page-errors',len(errors)==0,'; '.join(errors) if errors else '0 page errors')
        browser.close()

    # Pass 3: active report honesty + packaged decision lock is prepackage pending, not false final PASS
    active=[stage/'README.md',stage/'REAL_DEVICE_QA_CHECKLIST.md',stage/'REAL_DEVICE_QA_RESULTS_TEMPLATE.csv']+[p for p in sorted((stage/'reports').glob('*')) if p.name!='independent_four_pass_summary.json']
    nonblank=0; unsupported=[]
    for p in active:
        if not p.exists(): continue
        for i,line in enumerate(p.read_text('utf-8',errors='ignore').splitlines(),1):
            if line.strip(): nonblank+=1
            lo=line.lower()
            if ('physical' in lo or 'iphone' in lo or 'real-device' in lo or 'real device' in lo) and re.search(r'\bpass\b',lo) and 'not_tested' not in lo and 'not tested' not in lo and 'previous' not in lo and 'failed' not in lo:
                unsupported.append((p.name,i,line))
    ck('P3-active-report-honesty',not unsupported,f'{nonblank} nonblank lines; unsupported physical claims={len(unsupported)}')
    lock=json.loads((stage/'metadata/final_decision_lock.json').read_text('utf-8'))
    ck('P3-prepackage-lock-honest',lock.get('final_status')=='PENDING_POSTPACKAGE_AUDITS' and lock.get('physical_exact_title_selection')=='NOT_TESTED','prepackage lock honest')

    # Pass 4 current-facing stale/contradiction checks
    qa=(stage/'REAL_DEVICE_QA_CHECKLIST.md').read_text('utf-8'); qac=(stage/'REAL_DEVICE_QA_RESULTS_TEMPLATE.csv').read_text('utf-8'); readme=(stage/'README.md').read_text('utf-8')
    ck('P4-current-version',all('v101.88' in x for x in [qa,qac,readme]),'active QA/README v101.88')
    ck('P4-current-cache','luisa-24h-v101-88' in qa or 'luisa-24h-v101-88' in qac,'cache current')
    ck('P4-old-title-wording-current','Surligner le titre' not in qa and 'Surligner le titre' not in readme,'old whole-reading wording removed from current instructions')
    ck('P4-physical-gate','exact title' in qa.lower() and 'NOT_TESTED' in qac,'physical exact-title gate present')

    summary={'status':'PASS','total':len(rows),'pass':sum(r['status']=='PASS' for r in rows),'fail':0,'runtime_sha256':hf(idx),'rows':rows}
    out_json.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n','utf-8')
    md=['# v101.88 independent four-pass audit','','**PASS**',f'- checks: {summary["pass"]}/{summary["total"]} PASS',f'- runtime SHA-256: `{hf(idx)}`','- physical iPhone exact-title-selection remains NOT_TESTED for v101.88.','','## Evidence']+[f"- {r['scenario']}: **{r['status']}** — {r['evidence']}" for r in rows]
    out_md.write_text('\n'.join(md)+'\n','utf-8')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('stage');ap.add_argument('out_md');ap.add_argument('out_json');a=ap.parse_args()
    try:
        audit(Path(a.stage),Path(a.out_md),Path(a.out_json)); print('PASS')
    except Exception as e:
        print('FAIL',repr(e)); sys.exit(2)
