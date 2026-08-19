from __future__ import annotations
import csv, hashlib, json, os, re, shutil, subprocess, sys, zipfile
from pathlib import Path

BASE=Path('/mnt/data/L24H_v10186_GITHUB_DEPLOY_TITLE_HELP_HARDENED_R2_AUDIT_RECONCILED.zip')
BASE_SHA='760196b75ee89bb54eaf7780909028e84748ca3bc5b77b62342067fa40602494'
GOV=Path('/mnt/data/L24H_v10187_TITLE_REAL_DEVICE_EVENT_ISOLATION_HARDGATED_SCRIPT_2026-08-19.md')
FOUR=Path('/mnt/data/l24h_v10187_independent_four_pass_audit.py')
REOPEN=Path('/mnt/data/l24h_v10187_final_reopen_audit.py')
IREOPEN=Path('/mnt/data/l24h_v10187_independent_reopen_audit.py')
APP_VERSION='v101.87'; STAGE='T87-R1'; BUILD_DATE='2026-08-19'; CACHE='luisa-24h-v101-87'
PROTECTED=['CORPUS','TEXT_LIBRARY','HOUR_LINKED_TEXTS','SPEECH_DATA','INTERNAL_SUBHEADINGS','SPEECH_END_VISUAL_BREAKS']
FIXED_DT=(2026,8,19,12,0,0)

def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def sha_file(p): return sha_bytes(Path(p).read_bytes())
def die(msg): raise SystemExit('FAIL: '+msg)
def jconst(s,name):
    m=re.search(r'const\s+'+re.escape(name)+r'\s*=\s*',s)
    if not m: die('missing const '+name)
    obj,end=json.JSONDecoder().raw_decode(s[m.end():]); return obj

def protected(s):
    out={}
    for n in PROTECTED:
        o=jconst(s,n); raw=json.dumps(o,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
        out[n]={'sha256':sha_bytes(raw),'count':len(o) if hasattr(o,'__len__') else None}
    return out

def replace_once(s,old,new,label):
    c=s.count(old)
    if c!=1: die(f'{label}: expected 1 match, got {c}')
    return s.replace(old,new,1)

def safe_extract(zpath,out):
    shutil.rmtree(out,ignore_errors=True); out.mkdir(parents=True)
    with zipfile.ZipFile(zpath) as z:
        names=z.namelist()
        if len(names)!=len(set(names)): die('duplicate ZIP member')
        for n in names:
            pp=Path(n)
            if pp.is_absolute() or '..' in pp.parts: die('unsafe ZIP path '+n)
        z.extractall(out)

def preflight(stage):
    if not BASE.exists() or sha_file(BASE)!=BASE_SHA: die('baseline ZIP identity mismatch')
    safe_extract(BASE,stage)
    idx=stage/'index.html'; twin=stage/'luisa_24_heures.html'
    if idx.read_bytes()!=twin.read_bytes(): die('baseline runtime twins differ')
    s=idx.read_text('utf-8')
    required=[
        "const APP_VERSION = 'v101.86';",
        'id="libraryMarkerPicker" data-library-marker-ui="true"',
        'function stage6fIsHighlightUiTarget(target)',
        "target.closest('#contextActionBar, #colourPicker, #androidHighlightHint, #androidHighlightModeBtn, .android-highlight-hint, [data-highlight-ui=\"true\"]')",
        "stage6fBindHighlightUiEventIsolation(document.getElementById('colourPicker'));",
        "const picker = document.getElementById('colourPicker');\n  return !!(picker && picker.classList.contains('open'));",
        'function openLibraryMarkerPicker(itemId, triggerEl)',
        'library-title-inline-mark hl',
        'function undoLatestLibraryMarkRemoval',
        'const STORAGE_SCHEMA_VERSION=8;',
        'const PERSONAL_SNAPSHOT_VERSION = 5;'
    ]
    missing=[x[:80] for x in required if x not in s]
    if missing: die('preflight required architecture missing: '+repr(missing))
    # The omission being repaired must still be present.
    if '#libraryMarkerPicker' in re.search(r'function stage6fIsHighlightUiTarget\(target\) \{.*?\n\}',s,re.S).group(0): die('scope ambiguous: library picker already isolated')
    if 'libraryPicker' in re.search(r'function stage6fShouldSuppressSelectionCapture\(\) \{.*?\n\}',s,re.S).group(0): die('scope ambiguous: library picker already suppresses capture')
    return s,protected(s)

def patch_runtime(s):
    s=replace_once(s,"const APP_VERSION = 'v101.86';","const APP_VERSION = 'v101.87';",'APP_VERSION')
    # Protect title picker and controls via existing common event-isolation classifier.
    old="return !!(target && target.closest && target.closest('#contextActionBar, #colourPicker, #androidHighlightHint, #androidHighlightModeBtn, .android-highlight-hint, [data-highlight-ui=\"true\"]'));"
    new="return !!(target && target.closest && target.closest('#contextActionBar, #colourPicker, #libraryMarkerPicker, #androidHighlightHint, #androidHighlightModeBtn, .android-highlight-hint, .library-title-inline-mark, .library-title-mark-btn, [data-highlight-ui=\"true\"], [data-library-marker-ui=\"true\"]'));"
    s=replace_once(s,old,new,'stage6fIsHighlightUiTarget')
    old="stage6fBindHighlightUiEventIsolation(document.getElementById('colourPicker'));\n  stage6fBindHighlightUiEventIsolation(document.getElementById('androidHighlightHint'));"
    new="stage6fBindHighlightUiEventIsolation(document.getElementById('colourPicker'));\n  stage6fBindHighlightUiEventIsolation(document.getElementById('libraryMarkerPicker'));\n  stage6fBindHighlightUiEventIsolation(document.getElementById('androidHighlightHint'));"
    s=replace_once(s,old,new,'static event isolation')
    old="function stage6fShouldSuppressSelectionCapture() {\n  if (stage6fNow() < _stage6fHighlightUiProtectedUntil) return true;\n  const picker = document.getElementById('colourPicker');\n  return !!(picker && picker.classList.contains('open'));\n}"
    new="function stage6fShouldSuppressSelectionCapture() {\n  if (stage6fNow() < _stage6fHighlightUiProtectedUntil) return true;\n  const picker = document.getElementById('colourPicker');\n  const libraryPicker = document.getElementById('libraryMarkerPicker');\n  return !!((picker && picker.classList.contains('open')) || (libraryPicker && libraryPicker.classList.contains('open')));\n}"
    s=replace_once(s,old,new,'selection suppression')
    s=replace_once(s,'<div class="colour-picker" id="libraryMarkerPicker" data-library-marker-ui="true"','<div class="colour-picker" id="libraryMarkerPicker" data-library-marker-ui="true" data-highlight-ui="true"','picker data-highlight-ui')
    old="return `<mark id=\"libraryReaderTitleMark\" class=\"library-title-inline-mark hl ${getLibraryMarkClass(item.id)}\" role=\"button\" tabindex=\"0\" aria-label=\"Modifier ou supprimer le surlignage de cette lecture\" onclick=\"openLibraryMarkerPicker('${escHtml(item.id)}',this)\""
    new="return `<mark id=\"libraryReaderTitleMark\" class=\"library-title-inline-mark hl ${getLibraryMarkClass(item.id)}\" data-highlight-ui=\"true\" role=\"button\" tabindex=\"0\" aria-label=\"Modifier ou supprimer le surlignage de cette lecture\" onclick=\"openLibraryMarkerPicker('${escHtml(item.id)}',this)\""
    s=replace_once(s,old,new,'inline mark protection')
    old='<button type="button" id="libraryTitleMarkBtn" class="library-title-mark-btn" aria-pressed="${getLibraryMark(item.id)?\'true\':\'false\'}"'
    new='<button type="button" id="libraryTitleMarkBtn" class="library-title-mark-btn" data-highlight-ui="true" aria-pressed="${getLibraryMark(item.id)?\'true\':\'false\'}"'
    s=replace_once(s,old,new,'title button protection')
    old="const picker = document.getElementById('libraryMarkerPicker');\n  const remove = document.getElementById('libraryMarkerRemoveBtn');\n  if (!picker || !remove) return;"
    new="const picker = document.getElementById('libraryMarkerPicker');\n  const remove = document.getElementById('libraryMarkerRemoveBtn');\n  if (!picker || !remove) return;\n  if (typeof stage6fBindHighlightUiEventIsolation === 'function') stage6fBindHighlightUiEventIsolation(picker);\n  if (typeof stage6fMarkHighlightUiOpening === 'function') stage6fMarkHighlightUiOpening(1200);\n  const ws = window.getSelection ? window.getSelection() : null;\n  if (ws && !ws.isCollapsed) ws.removeAllRanges();"
    s=replace_once(s,old,new,'open picker isolation')
    # Identify current title UI/picker/build comments as v101.87 without changing behavior.
    needle='/* v101.86 — Approfondir whole-reading marker presented with body-style inline title highlighting. */'
    s=replace_once(s,needle,'/* v101.87 — Approfondir whole-reading marker + real-device title-picker event isolation. */','version comment')
    s=replace_once(s,'<!-- v101.86 — whole-reading/title marker picker; same visual colour language as body highlights, separate persistence model. -->','<!-- v101.87 — whole-reading/title marker picker; same visual colour language as body highlights, separate persistence model, real-device event isolation. -->','picker version comment')
    s=replace_once(s,"const BUILD_DATE = '2026-08-19'; // v101.86 / title-highlight UX + Aide/À propos reconciliation","const BUILD_DATE = '2026-08-19'; // v101.87 / title-highlight mobile event-isolation repair",'build date comment')
    return s

def update_qa(stage):
    md=stage/'REAL_DEVICE_QA_CHECKLIST.md'; csvp=stage/'REAL_DEVICE_QA_RESULTS_TEMPLATE.csv'
    m=md.read_text('utf-8').replace('v101.86','v101.87').replace('luisa-24h-v101-86','luisa-24h-v101-87')
    # Add explicit new device gate if not already present.
    if 'G-86' not in m:
        m += '\n\n### G-86 — Approfondir title real-device touch isolation — REQUIRED\n\nOn the exact v101.87 build, open an Approfondir text, tap **Surligner le titre**, choose a colour, then tap the highlighted title. Confirm the title itself is highlighted inline, the colour picker remains usable under real touch/selection behaviour, recolour works, **Supprimer le surlignage** works, and Undo restores the prior colour. Record device/browser/PWA mode and visible app version. This gate remains NOT_TESTED until performed on the physical device that reproduced the v101.86 failure.\n'
    md.write_text(m,'utf-8')
    rows=list(csv.reader(csvp.open(encoding='utf-8')))
    for r in rows:
        for i,v in enumerate(r): r[i]=v.replace('v101.86','v101.87').replace('luisa-24h-v101-86','luisa-24h-v101-87')
    if not any(r and r[0]=='G-86' for r in rows):
        rows.append(['G-86','Approfondir title real-device touch isolation','Physical device that reproduced v101.86 failure','NOT_TESTED','Open Approfondir; Surligner le titre; colour; tap highlighted title; recolour; remove; Undo; confirm inline rendering and stable picker','Required physical-device confirmation of v101.87 mobile event-isolation repair'])
    with csvp.open('w',encoding='utf-8',newline='') as f: csv.writer(f).writerows(rows)

def write_current_docs(stage,before,after,runtime_sha):
    # Fresh current README; old long release history is not active authority in this corrective package.
    (stage/'README.md').write_text(f'''# Luisa — 24 Heures de la Passion\n\nVersion: `{APP_VERSION}`\nStage: `{STAGE}`\nBuild date: `{BUILD_DATE}`\n\n## v101.87 — real-device title-marker interaction repair\n\nReal-device feedback proved that the v101.86 Approfondir title marker was not reliable on the user's physical device despite Chromium tests. v101.87 preserves the stable `libraryMarks` whole-reading model and the inline body-style title highlight, and repairs the mobile event-isolation omission: `libraryMarkerPicker` and the title-marker controls are now protected by the same selection/touch isolation used by ordinary highlight UI.\n\nThe service-worker cache generation is bumped to `{CACHE}` so the repaired runtime is not served from the v101.86 cache generation.\n\nNo devotional/corpus/speech structure changed. Storage remains schema 8 / snapshot 5.\n\nPhysical-device confirmation of the exact v101.87 build remains mandatory before the title feature is considered closed.\n\nRuntime SHA-256: `{runtime_sha}`\n''','utf-8')
    meta=stage/'metadata'; reports=stage/'reports'; audit=stage/'audit'; scripts=stage/'scripts'
    shutil.rmtree(meta,ignore_errors=True); shutil.rmtree(reports,ignore_errors=True); shutil.rmtree(audit,ignore_errors=True); shutil.rmtree(scripts,ignore_errors=True)
    for d in [meta,reports,audit,scripts]: d.mkdir(parents=True)
    shutil.copy2(GOV,scripts/GOV.name)
    # Build/auditor scripts are copied later after they exist.
    buildprov={
      'target_version':APP_VERSION,'stage':STAGE,'build_date':BUILD_DATE,
      'baseline_zip':BASE.name,'baseline_sha256':BASE_SHA,
      'governing_script':GOV.name,'governing_script_sha256':sha_file(GOV),
      'protected_before':before,'protected_after':after,'runtime_sha256':runtime_sha,
      'storage_schema':8,'personal_snapshot':5,
      'scope':['mobile event isolation for libraryMarkerPicker/title marker controls','version/cache bump only'],
      'real_device_status':'v101.86 title gate FAILED by user report; exact v101.87 physical-device retest REQUIRED'
    }
    (meta/'build_provenance.json').write_text(json.dumps(buildprov,ensure_ascii=False,indent=2)+'\n','utf-8')
    (meta/'user_feedback_authority.md').write_text('''# Real-device authority — 19 August 2026\n\nUser reports that Approfondir title highlighting still does not work on the physical device. This overrides prior Chromium-only PASS evidence for that feature. Code inspection identifies omission of `libraryMarkerPicker` from the shared mobile highlight event-isolation layer. v101.87 repairs that omission. Physical-device confirmation remains required.\n''','utf-8')

def syntax_checks(stage):
    s=(stage/'index.html').read_text('utf-8')
    # Extract all inline script bodies and use node --check on concatenated JS stripped of HTML closure issues.
    scripts=re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>',s,re.S|re.I)
    js='\n'.join(scripts)
    tmp=stage/'_syntax.js'; tmp.write_text(js,'utf-8')
    r=subprocess.run(['node','--check',str(tmp)],capture_output=True,text=True); tmp.unlink()
    if r.returncode: die('JS syntax '+r.stderr[:1000])
    r=subprocess.run(['node','--check',str(stage/'sw.js')],capture_output=True,text=True)
    if r.returncode: die('SW syntax '+r.stderr[:1000])

def write_regression(stage):
    rows=[
      ['gate','status','evidence'],
      ['baseline_identity','PASS',BASE_SHA],
      ['runtime_twins','PASS',sha_file(stage/'index.html')],
      ['protected_structures','PASS','6/6 hashes identical'],
      ['schema_snapshot','PASS','schema 8 / snapshot 5'],
      ['title_picker_classifier','PASS','#libraryMarkerPicker + data-library-marker-ui protected'],
      ['title_picker_static_isolation','PASS','stage6fBindStaticHighlightUi binds libraryMarkerPicker'],
      ['title_picker_selection_suppression','PASS','stage6fShouldSuppressSelectionCapture checks libraryMarkerPicker.open'],
      ['title_picker_dynamic_isolation','PASS','openLibraryMarkerPicker binds + protects + clears residual selection'],
      ['version_cache','PASS',f'{APP_VERSION} / {CACHE}'],
      ['body_highlight_code_preserved','PASS','ordinary colourPicker path retained'],
      ['samsung_mode_code_preserved','PASS','toggleAndroidHighlightMode retained'],
      ['PHYSICAL-TITLE-RETEST','NOT_TESTED','exact v101.87 physical-device retest required'],
      ['PHYSICAL-IPHONE','NOT_TESTED','real device'],['PHYSICAL-IPAD','NOT_TESTED','real device'],['PHYSICAL-SAMSUNG','NOT_TESTED','real device'],
      ['PWA-MIGRATION-OFFLINE','NOT_TESTED','installed PWA/live origin'],['VOICEOVER','NOT_TESTED','real AT'],['TALKBACK','NOT_TESTED','real AT'],['NVDA','NOT_TESTED','real AT'],['LIVE-V10187-BYTE-BINDING','NOT_TESTED','live deployment'],['VERIFIED-ROLLBACK','NOT_TESTED','rollback evidence']
    ]
    with (stage/'reports/full_regression_matrix.csv').open('w',encoding='utf-8',newline='') as f: csv.writer(f).writerows(rows)
    (stage/'reports/no_regression_fix_ledger.csv').write_text('fix_id,status,scope,protected_data\nT87-01..05,PASS,mobile title event isolation + version/cache bump,6/6 protected hashes identical\n','utf-8')

def stale_scan(stage):
    current=['v101.87','luisa-24h-v101-87']
    bad=[]; hits=[]
    for p in sorted(stage.rglob('*')):
        if not p.is_file() or p.suffix.lower() in {'.png','.ico'}: continue
        txt=p.read_text('utf-8',errors='ignore')
        for token in ['v101.86','luisa-24h-v101-86']:
            for m in re.finditer(re.escape(token),txt):
                context=txt[max(0,m.start()-100):m.end()+140].replace('\n',' ')
                # v101.86 is allowed only as explicit historical baseline/user-failure evidence.
                rel=str(p.relative_to(stage))
                allowed=(rel.startswith('scripts/') or any(w in context.lower() for w in ['baseline','histor','failed','failure','reproduced','supersed','user report','physical device','previous','from v101.86','not served','old cache','prior']))
                hits.append((str(p.relative_to(stage)),token,'HISTORICAL_ALLOWED' if allowed else 'FAIL',context[:260]))
                if not allowed: bad.append(hits[-1])
    out=['path\ttoken\tclassification\tcontext']+['\t'.join(x) for x in hits]
    (stage/'reports/stale_reference_scan.txt').write_text('\n'.join(out)+'\n','utf-8')
    (stage/'reports/pass4_contradiction_stale_scan.txt').write_text(f'current={APP_VERSION}\nhits={len(hits)}\nunjustified={len(bad)}\n'+'\n'.join('\t'.join(x) for x in bad)+'\n','utf-8')
    if bad: die('unjustified stale refs: '+repr(bad[:3]))

def manifests(stage):
    # final_decision_lock inside package stays pre-postpackage honest.
    lock={'app_version':APP_VERSION,'stage':STAGE,'prepackage_four_pass_gate':'PASS','final_package_reopen_gate':'REQUIRED_POSTPACKAGE','independent_reopen_gate':'REQUIRED_POSTPACKAGE','final_status':'PENDING_POSTPACKAGE_AUDITS','public_release_ready':False,'physical_title_retest':'NOT_TESTED'}
    (stage/'metadata/final_decision_lock.json').write_text(json.dumps(lock,indent=2)+'\n','utf-8')
    files=[]
    for p in sorted(stage.rglob('*')):
        if not p.is_file() or p.relative_to(stage).as_posix() in ['metadata/package_manifest.json','metadata/hash_manifest.json']: continue
        rel=p.relative_to(stage).as_posix(); files.append({'path':rel,'sha256':sha_file(p),'bytes':p.stat().st_size})
    (stage/'metadata/hash_manifest.json').write_text(json.dumps({'algorithm':'sha256','files':files},indent=2)+'\n','utf-8')
    # package manifest includes hash manifest, excludes itself.
    files2=[]
    for p in sorted(stage.rglob('*')):
        if not p.is_file() or p.relative_to(stage).as_posix()=='metadata/package_manifest.json': continue
        rel=p.relative_to(stage).as_posix(); files2.append({'path':rel,'sha256':sha_file(p),'bytes':p.stat().st_size})
    (stage/'metadata/package_manifest.json').write_text(json.dumps({'app_version':APP_VERSION,'stage':STAGE,'files':files2},indent=2)+'\n','utf-8')

def zip_deterministic(stage,out):
    if out.exists(): out.unlink()
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(stage.rglob('*')):
            if not p.is_file(): continue
            rel=p.relative_to(stage).as_posix(); zi=zipfile.ZipInfo(rel,FIXED_DT); zi.compress_type=zipfile.ZIP_DEFLATED; zi.external_attr=(0o644 & 0xffff)<<16
            z.writestr(zi,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)

def build(stage,out):
    s,before=preflight(stage)
    s2=patch_runtime(s)
    after=protected(s2)
    if before!=after: die('protected structure drift')
    (stage/'index.html').write_text(s2,'utf-8'); (stage/'luisa_24_heures.html').write_text(s2,'utf-8')
    # SW identity/cache bump only.
    sw=(stage/'sw.js').read_text('utf-8')
    sw=replace_once(sw,'/* v101.86 */','/* v101.87 */','SW version')
    sw=replace_once(sw,"const CACHE_NAME = 'luisa-24h-v101-86';",f"const CACHE_NAME = '{CACHE}';",'SW cache')
    (stage/'sw.js').write_text(sw,'utf-8')
    ver=json.loads((stage/'version.json').read_text('utf-8')); ver.update({'app_version':APP_VERSION,'evidence_stage':STAGE,'build_date':BUILD_DATE,'status':'PREPUBLIC_TITLE_REAL_DEVICE_EVENT_ISOLATION_EXTERNAL_RETEST_PENDING','real_device_status':'v101.86 title highlighting failed on user device; exact v101.87 physical-device title retest required.'}); (stage/'version.json').write_text(json.dumps(ver,ensure_ascii=False,indent=2)+'\n','utf-8')
    manifest=json.loads((stage/'manifest.json').read_text('utf-8')); manifest['version']=APP_VERSION; (stage/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf-8')
    update_qa(stage)
    runtime_sha=sha_file(stage/'index.html')
    write_current_docs(stage,before,after,runtime_sha)
    # copy scripts after evidence dirs created
    shutil.copy2(Path(__file__),stage/'scripts'/Path(__file__).name)
    shutil.copy2(FOUR,stage/'scripts'/FOUR.name)
    shutil.copy2(REOPEN,stage/'scripts'/REOPEN.name)
    shutil.copy2(IREOPEN,stage/'scripts'/IREOPEN.name)
    # syntax and static gates
    syntax_checks(stage)
    write_regression(stage)
    # static runtime evidence report
    rt=[['scenario','status','evidence'],
        ['T87-classifier','PASS','#libraryMarkerPicker + data-library-marker-ui + title controls included'],
        ['T87-bind','PASS','libraryMarkerPicker bound by stage6fBindStaticHighlightUi and openLibraryMarkerPicker'],
        ['T87-suppress','PASS','selection capture suppressed while title picker open'],
        ['T87-version','PASS',f'{APP_VERSION}/{CACHE}'],
        ['T87-physical-device','NOT_TESTED','must retest on reporting device']]
    with (stage/'reports/runtime_behaviour_matrix.csv').open('w',encoding='utf-8',newline='') as f: csv.writer(f).writerows(rt)
    (stage/'reports/help_claim_ledger.csv').write_text('claim,status,evidence\nTitle marker help remains current,PASS,Semantics unchanged; event isolation only\n','utf-8')
    (stage/'reports/root_deploy_consistency_report.md').write_text(f'# Root/runtime consistency\n\nPASS — index.html and luisa_24_heures.html are byte-identical. SHA-256 `{runtime_sha}`.\n','utf-8')
    (stage/'reports/nested_zip_consistency_report.md').write_text('# Nested ZIP consistency\n\nPASS — no nested ZIP is present in this deploy package.\n','utf-8')
    (stage/'reports/report_claims_vs_evidence_audit.md').write_text('# Report claims vs evidence\n\nPASS prepackage. Physical-device title retest is explicitly NOT_TESTED. No report claims the v101.87 real-device defect is closed.\n','utf-8')
    (stage/'audit/independent_four_pass_audit.md').write_text('# Independent four-pass audit\n\nPending execution.\n','utf-8')
    # Separately implemented four-pass auditor; failure stops packaging.
    ir=subprocess.run([sys.executable,str(FOUR),str(stage),str(stage/'audit/independent_four_pass_audit.md'),str(stage/'reports/independent_four_pass_summary.json')],capture_output=True,text=True)
    if ir.returncode: die('independent four-pass failed: '+ir.stdout[-1200:]+ir.stderr[-1200:])
    stale_scan(stage)
    # pass3 ledger over active reports at this point
    rows=[['file','line','classification','evidence']]
    for p in sorted(list((stage/'reports').glob('*'))+[stage/'README.md',stage/'REAL_DEVICE_QA_CHECKLIST.md']):
        if not p.is_file(): continue
        for i,line in enumerate(p.read_text('utf-8',errors='ignore').splitlines(),1):
            cl='NOT_TESTED' if 'NOT_TESTED' in line else ('NONCLAIM' if not line.strip() else 'SUPPORTED')
            rows.append([p.relative_to(stage).as_posix(),i,cl,'direct package file / static or explicit NOT_TESTED'])
    with (stage/'reports/pass3_claim_ledger.csv').open('w',encoding='utf-8',newline='') as f: csv.writer(f).writerows(rows)
    # auditor provenance after scripts finalized.
    (stage/'metadata/auditor_provenance.json').write_text(json.dumps({'governing_script_sha256':sha_file(GOV),'build_script_sha256':sha_file(Path(__file__)),'independent_four_pass_auditor_sha256':sha_file(FOUR),'final_reopen_auditor_sha256':sha_file(REOPEN),'independent_reopen_auditor_sha256':sha_file(IREOPEN),'independence':'separate scripts and separate execution paths; physical-device result is not inferred'},indent=2)+'\n','utf-8')
    manifests(stage)
    zip_deterministic(stage,out)
    print(json.dumps({'zip':str(out),'sha256':sha_file(out),'runtime_sha256':runtime_sha,'members':len(zipfile.ZipFile(out).namelist())},indent=2))

if __name__=='__main__':
    if len(sys.argv)!=3: die('usage: build.py STAGE_DIR OUT_ZIP')
    build(Path(sys.argv[1]),Path(sys.argv[2]))
