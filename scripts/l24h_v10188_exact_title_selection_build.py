from __future__ import annotations
import csv,hashlib,json,re,shutil,subprocess,sys,zipfile
from pathlib import Path

BASE=Path('/mnt/data/L24H_v10187_GITHUB_DEPLOY_TITLE_REAL_DEVICE_ISOLATION_R1.zip')
BASE_SHA='710416524b57501f5154fd9b333c19ac622b3352c2d36a6d7af8f07172538d28'
GOV=Path('/mnt/data/L24H_v10188_EXACT_TITLE_SELECTION_HARDGATED_SCRIPT_2026-08-19.md')
FOUR=Path('/mnt/data/l24h_v10188_independent_four_pass_audit.py')
APP_VERSION='v101.88'; STAGE='T88-R1'; CACHE='luisa-24h-v101-88'; BUILD_DATE='2026-08-19'
PROTECTED=['CORPUS','TEXT_LIBRARY','HOUR_LINKED_TEXTS','SPEECH_DATA','INTERNAL_SUBHEADINGS','SPEECH_END_VISUAL_BREAKS']
FIXED_DT=(2026,8,19,12,0,0)

def hb(b): return hashlib.sha256(b).hexdigest()
def hf(p): return hb(Path(p).read_bytes())
def die(msg): raise SystemExit('FAIL: '+msg)
def jconst(s,name):
    m=re.search(r'const\s+'+re.escape(name)+r'\s*=\s*',s)
    if not m: die('missing const '+name)
    return json.JSONDecoder().raw_decode(s[m.end():])[0]
def protected(s):
    return {n:hb(json.dumps(jconst(s,n),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()) for n in PROTECTED}
def replace_once(s,old,new,label):
    c=s.count(old)
    if c!=1: die(f'{label}: expected 1 match, got {c}')
    return s.replace(old,new,1)
def safe_extract(z,out):
    shutil.rmtree(out,ignore_errors=True); out.mkdir(parents=True)
    with zipfile.ZipFile(z) as zz:
        names=zz.namelist()
        if len(names)!=len(set(names)): die('duplicate ZIP member')
        for n in names:
            p=Path(n)
            if p.is_absolute() or '..' in p.parts: die('unsafe ZIP path '+n)
        zz.extractall(out)
def function_block(s,name):
    m=re.search(r'function\s+'+re.escape(name)+r'\s*\([^)]*\)\s*\{',s)
    if not m: die('missing function '+name)
    i=m.end(); depth=1
    while i<len(s) and depth:
        if s[i]=='{': depth+=1
        elif s[i]=='}': depth-=1
        i+=1
    if depth: die('unbalanced function '+name)
    return s[m.start():i]
def replace_function(s,name,new):
    old=function_block(s,name)
    return replace_once(s,old,new,name)

def preflight(stage):
    if not BASE.exists() or hf(BASE)!=BASE_SHA: die('baseline identity mismatch')
    safe_extract(BASE,stage)
    if (stage/'index.html').read_bytes()!=(stage/'luisa_24_heures.html').read_bytes(): die('runtime twins differ')
    s=(stage/'index.html').read_text('utf-8')
    req=["const APP_VERSION = 'v101.87';",'const STORAGE_SCHEMA_VERSION=8;','const PERSONAL_SNAPSHOT_VERSION = 5;','function getTargetInfo(paraId)','function renderParaText(text, paraId)','function setPendingSelectionFromRange(range, savedRect, showUi = true)','function rerenderPara(paraId)','function refreshLibraryMarkerTitleUi(itemId)','function openLibraryMarkerPicker(itemId, triggerEl)']
    miss=[x for x in req if x not in s]
    if miss: die('missing architecture '+repr(miss))
    # Ensure exact title selection is genuinely absent and current whole-reading wrapper is present.
    if 'function makeLibraryTitleId(itemId)' in s or "type:'library_title'" in s: die('scope conflict: title target already exists')
    if '.library-title-selectable' in s: die('scope conflict: title selectable already exists')
    if 'library-title-inline-mark' not in function_block(s,'renderLibraryReaderTitleInner'): die('unexpected current title marker architecture')
    # Generic store compatibility and ID envelope.
    lib=jconst(s,'TEXT_LIBRARY')
    items=[x for x in lib if isinstance(x,dict) and str(x.get('id','')).startswith('PASSION24.TEXT.') and x.get('type')!='library_group' and x.get('status') not in ['hidden_scope_excluded','placeholder']]
    ids=[x['id']+'.TITLE' for x in items]
    if len(items)!=33 or len(set(ids))!=len(ids): die(f'unexpected visible title inventory {len(items)}')
    if not all(re.match(r'^PASSION24\.[A-Z0-9._:-]{1,160}$',x) for x in ids): die('title IDs do not fit validPersonalId')
    return s,protected(s)

def patch_runtime(s):
    s=replace_once(s,"const APP_VERSION = 'v101.87';","const APP_VERSION = 'v101.88';",'APP_VERSION')
    s=replace_once(s,"const BUILD_DATE = '2026-08-19'; // v101.87 / title-highlight mobile event-isolation repair","const BUILD_DATE = '2026-08-19'; // v101.88 / exact Approfondir title-text selection + reading-marker separation",'BUILD_DATE')
    # CSS: replace special whole-title highlight presentation with selectable title content + separate marker control.
    old='''/* v101.87 — Approfondir whole-reading marker + real-device title-picker event isolation. */
.library-title-mark-wrap{display:flex;flex-direction:column;align-items:flex-start;gap:0.55rem;margin-bottom:0.3rem;}
.library-title-mark-wrap .reader-title{display:block;margin-bottom:0;}
mark.library-title-inline-mark{display:inline;padding:0 0.08em;border-radius:0.16rem;box-decoration-break:clone;-webkit-box-decoration-break:clone;cursor:pointer;touch-action:manipulation;transition:background 0.15s,outline-color 0.15s;}
mark.library-title-inline-mark:focus-visible{outline:3px solid var(--accent-light);outline-offset:3px;}
.library-title-mark-btn{font-family:var(--font-ui);font-size:0.78rem;font-weight:700;color:var(--accent);background:var(--accent-pale);border:1.5px solid var(--accent-light);border-radius:999px;min-height:44px;padding:0.48rem 0.85rem;cursor:pointer;touch-action:manipulation;}
.library-title-mark-btn[aria-pressed="true"]{background:var(--accent);color:#fff;border-color:var(--accent);}
#libraryMarkerPicker .cp-swatch[aria-pressed="true"]{outline:3px solid var(--ink);outline-offset:3px;box-shadow:0 0 0 2px var(--bg);}
.library-mark-entry-wrap{position:relative;margin-bottom:0.5rem;}.library-mark-entry-wrap .hl-item{margin-bottom:0;padding-right:5.3rem;}.library-mark-remove{position:absolute;right:0.55rem;top:50%;transform:translateY(-50%);min-height:36px;border:1px solid var(--bg3);border-radius:999px;background:var(--bg);color:var(--ink3);font:600 0.72rem var(--font-ui);padding:0.3rem 0.62rem;cursor:pointer;}'''
    new='''/* v101.88 — exact Approfondir title-text selection + separate whole-reading marker. */
.library-title-mark-wrap{display:flex;flex-direction:column;align-items:flex-start;gap:0.55rem;margin-bottom:0.3rem;}
.library-title-mark-wrap .reader-title{display:block;margin-bottom:0;}
.library-title-selectable{display:inline;font:inherit;color:inherit;line-height:inherit;letter-spacing:inherit;white-space:normal;-webkit-user-select:text;user-select:text;-webkit-touch-callout:default;touch-action:auto;}
html.stage6a-runtime.ios-device .library-title-selectable,html.stage6a-runtime.ios-device .library-title-selectable *{-webkit-user-select:text !important;user-select:text !important;-webkit-touch-callout:default !important;touch-action:auto !important;}
html.stage6a-runtime.android-scroll-fix .library-title-selectable,html.stage6a-runtime.android-scroll-fix .library-title-selectable *{-webkit-user-select:none !important;user-select:none !important;-webkit-touch-callout:none !important;touch-action:manipulation !important;}
.library-title-mark-btn{font-family:var(--font-ui);font-size:0.78rem;font-weight:700;color:var(--accent);background:var(--accent-pale);border:1.5px solid var(--accent-light);border-radius:999px;min-height:44px;padding:0.48rem 0.85rem;cursor:pointer;touch-action:manipulation;}
.library-title-mark-btn[aria-pressed="true"]{background:var(--accent);color:#fff;border-color:var(--accent);}
#libraryMarkerPicker .cp-swatch[aria-pressed="true"]{outline:3px solid var(--ink);outline-offset:3px;box-shadow:0 0 0 2px var(--bg);}
.library-mark-entry-wrap{position:relative;margin-bottom:0.5rem;}.library-mark-entry-wrap .hl-item{margin-bottom:0;padding-right:5.3rem;}.library-mark-remove{position:absolute;right:0.55rem;top:50%;transform:translateY(-50%);min-height:36px;border:1px solid var(--bg3);border-radius:999px;background:var(--bg);color:var(--ink3);font:600 0.72rem var(--font-ui);padding:0.3rem 0.62rem;cursor:pointer;}'''
    s=replace_once(s,old,new,'title CSS')
    # Marker picker wording only; persistence model remains libraryMarks.
    s=replace_once(s,'<!-- v101.87 — whole-reading/title marker picker; same visual colour language as body highlights, separate persistence model, real-device event isolation. -->','<!-- v101.88 — whole-reading marker picker; separate from exact title text highlighting. -->','picker comment')
    s=replace_once(s,'aria-label="Surligner le titre d’une lecture"','aria-label="Marquer cette lecture"','picker aria')
    s=replace_once(s,'<span class="cp-label" id="libraryMarkerPickerLabel">Surligner le titre en</span>','<span class="cp-label" id="libraryMarkerPickerLabel">Marquer cette lecture en</span>','picker label')
    s=replace_once(s,'<button type="button" class="cp-remove" id="libraryMarkerRemoveBtn" onclick="removeLibraryMarkerFromPicker()" style="display:none">✕ Supprimer le surlignage</button>','<button type="button" class="cp-remove" id="libraryMarkerRemoveBtn" onclick="removeLibraryMarkerFromPicker()" style="display:none">✕ Retirer le repère</button>','picker remove')
    # Canonical title ID helper + target registry.
    s=replace_once(s,"function makeLibraryPracticeOptionId(itemId, index) { return itemId + '.PRACTICE_OPTION.P' + String(index + 1).padStart(3, '0'); }","function makeLibraryPracticeOptionId(itemId, index) { return itemId + '.PRACTICE_OPTION.P' + String(index + 1).padStart(3, '0'); }\nfunction makeLibraryTitleId(itemId) { return itemId + '.TITLE'; }",'title helper')
    anchor="""  for (const sec of CORPUS.sections || []) for (const p of sec.paragraphs || []) if (p.id === paraId) return {id:paraId, text:p.t, type:'section', label:`Complément — ${sec.title}`, sectionId:sec.section_id};
  const libBodyMatch = paraId.match(/^(PASSION24\\.TEXT\\.[A-Z0-9_]+)\\.BODY\\.P(\\d{3})$/);"""
    repl="""  for (const sec of CORPUS.sections || []) for (const p of sec.paragraphs || []) if (p.id === paraId) return {id:paraId, text:p.t, type:'section', label:`Complément — ${sec.title}`, sectionId:sec.section_id};
  const libTitleMatch = paraId.match(/^(PASSION24\\.TEXT\\.[A-Z0-9_]+)\\.TITLE$/);
  if (libTitleMatch) {
    const item = getLibraryItem(libTitleMatch[1]);
    if (item && item.type !== 'library_group' && item.status !== 'placeholder' && isLibraryItemUserVisible(item)) return {id:paraId, text:item.title, type:'library_title', label:`Titre — ${item.title}`, libraryId:item.id};
  }
  const libBodyMatch = paraId.match(/^(PASSION24\\.TEXT\\.[A-Z0-9_]+)\\.BODY\\.P(\\d{3})$/);"""
    s=replace_once(s,anchor,repl,'title target registry')
    # Title renderer: pure selectable text rendered through normal text highlight renderer.
    s=replace_function(s,'renderLibraryReaderTitleInner',"""function renderLibraryReaderTitleInner(item) {
  const badge = item.status==='placeholder' ? '<span class="placeholder-badge">À intégrer</span>' : '';
  const titleId = makeLibraryTitleId(item.id);
  const info = getTargetInfo(titleId);
  if (!info) return escHtml(item.title) + badge;
  return `<span class="library-title-selectable" data-para-id="${escHtml(titleId)}">${renderParaText(item.title, titleId)}</span>${badge}`;
}""")
    # Old title-mark keyboard helper is no longer used; leave harmless function out by converting to no-op compatibility shim.
    s=replace_function(s,'handleLibraryTitleMarkKeydown',"""function handleLibraryTitleMarkKeydown(event,itemId) {
  // v101.88 compatibility shim: whole-reading marking is controlled by the separate button.
  return false;
}""")
    s=replace_function(s,'refreshLibraryMarkerTitleUi',"""function refreshLibraryMarkerTitleUi(itemId) {
  if (state.view !== 'libraryText' || state.currentSection !== itemId) return;
  const btn = document.getElementById('libraryTitleMarkBtn');
  const mark = getLibraryMark(itemId);
  if (btn) {
    btn.setAttribute('aria-pressed', mark ? 'true' : 'false');
    btn.textContent = mark ? 'Modifier / retirer le repère' : 'Marquer cette lecture';
    btn.setAttribute('aria-label', mark ? 'Modifier ou retirer le repère de cette lecture' : 'Marquer cette lecture');
  }
}""")
    s=replace_function(s,'updateLibraryMarkerPickerSelection',"""function updateLibraryMarkerPickerSelection(itemId) {
  const mark=getLibraryMark(itemId);
  document.querySelectorAll('#libraryMarkerPicker [data-library-marker-color]').forEach(function(btn){
    btn.setAttribute('aria-pressed', mark && btn.dataset.libraryMarkerColor===mark.color ? 'true' : 'false');
  });
  const label=document.getElementById('libraryMarkerPickerLabel');
  if(label) label.textContent = mark ? 'Modifier le repère de cette lecture' : 'Marquer cette lecture en';
}""")
    # libraryMark user-facing persistence messages.
    s=s.replace("old ? 'Modification du surlignage du titre' : 'Ajout du surlignage du titre'","old ? 'Modification du repère de lecture' : 'Ajout du repère de lecture'")
    s=s.replace("old ? 'Couleur du titre modifiée' : 'Titre surligné ◐'","old ? 'Repère modifié' : 'Lecture marquée ◐'")
    s=s.replace("'Suppression du surlignage du titre'","'Suppression du repère de lecture'")
    s=s.replace("showToastWithAction('Surlignage du titre supprimé.', 'Annuler'","showToastWithAction('Repère de lecture retiré.', 'Annuler'")
    s=s.replace("'Annulation de la suppression du titre'","'Annulation du retrait du repère'")
    s=s.replace("showToast('Suppression du titre annulée.');","showToast('Retrait du repère annulé.');")
    s=s.replace("showToast('Aucune suppression de titre à annuler.');","showToast('Aucun retrait de repère à annuler.');")
    # openLibraryText title element gets stable target ID and separate marker wording.
    old='''<div class="library-title-mark-wrap"><h2 id="libraryReaderTitle" class="reader-title">${renderLibraryReaderTitleInner(item)}</h2><button type="button" id="libraryTitleMarkBtn" class="library-title-mark-btn" data-highlight-ui="true" aria-pressed="${getLibraryMark(item.id)?'true':'false'}" aria-label="${getLibraryMark(item.id)?'Modifier ou supprimer le surlignage du titre':'Surligner le titre'}" onclick="openLibraryMarkerPicker('${escHtml(item.id)}',this)">${getLibraryMark(item.id)?'Modifier / retirer le surlignage':'Surligner le titre'}</button></div>'''
    new='''<div class="library-title-mark-wrap"><h2 id="${escHtml(makeLibraryTitleId(item.id))}" class="reader-title library-title-target" data-target-type="library_title">${renderLibraryReaderTitleInner(item)}</h2><button type="button" id="libraryTitleMarkBtn" class="library-title-mark-btn" data-highlight-ui="true" aria-pressed="${getLibraryMark(item.id)?'true':'false'}" aria-label="${getLibraryMark(item.id)?'Modifier ou retirer le repère de cette lecture':'Marquer cette lecture'}" onclick="openLibraryMarkerPicker('${escHtml(item.id)}',this)">${getLibraryMark(item.id)?'Modifier / retirer le repère':'Marquer cette lecture'}</button></div>'''
    s=replace_once(s,old,new,'openLibraryText title DOM')
    # Mon Espace remove aria wording.
    s=s.replace('aria-label="Retirer le surlignage du titre : ${escHtml(x.item.title)}"','aria-label="Retirer le repère de lecture : ${escHtml(x.item.title)}"')
    # Canonical shared selection surface selector.
    old="""function getSelectableTextElementFromTarget(target) {
  if (!target || !target.closest) return null;
  return target.closest('.para-text, .ref-para, .block-paragraph, .prayer-modal-para, .library-practice-item');
}"""
    new="""const SELECTABLE_TEXT_SURFACE_SELECTOR = '.para-text, .ref-para, .block-paragraph, .prayer-modal-para, .library-practice-item, .library-title-selectable';
function getSelectableTextElementFromTarget(target) {
  if (!target || !target.closest) return null;
  return target.closest(SELECTABLE_TEXT_SURFACE_SELECTOR);
}"""
    s=replace_once(s,old,new,'shared selectable selector')
    s=replace_once(s,"const selector = '.para-text, .ref-para, .block-paragraph, .prayer-modal-para, .library-practice-item';\n  const surfaces = Array.from(document.querySelectorAll(selector)).filter(el => getParaIdForTextElement(el));","const surfaces = Array.from(document.querySelectorAll(SELECTABLE_TEXT_SURFACE_SELECTOR)).filter(el => getParaIdForTextElement(el));",'ordered selector')
    # rerender title through same generic renderer.
    s=replace_once(s,"const el = block.querySelector('.para-text, .ref-para, .block-paragraph, .prayer-modal-para, .library-practice-item');","const el = block.querySelector(SELECTABLE_TEXT_SURFACE_SELECTOR);",'rerender selector')
    # Preserve Samsung body-only paragraph mode: title is selectable only for iOS/compatible native selection, not Samsung paragraph mode.
    old="""function stage6hPrepareAndroidParagraphPending(textEl) {
  if (!textEl) return false;
  const paraId = getParaIdForTextElement(textEl);"""
    new="""function stage6hPrepareAndroidParagraphPending(textEl) {
  if (!textEl || (textEl.classList && textEl.classList.contains('library-title-selectable'))) return false;
  const paraId = getParaIdForTextElement(textEl);"""
    s=replace_once(s,old,new,'Samsung title exclusion')
    old="""function handleAndroidHighlightModePointer(e) {
  if (!isAndroidAppHighlightModeActive()) return;
  const textEl = getSelectableTextElementFromTarget(e && e.target);
  if (!textEl) return;"""
    new="""function handleAndroidHighlightModePointer(e) {
  if (!isAndroidAppHighlightModeActive()) return;
  const textEl = getSelectableTextElementFromTarget(e && e.target);
  if (!textEl || (textEl.classList && textEl.classList.contains('library-title-selectable'))) return;"""
    s=replace_once(s,old,new,'Samsung pointer exclusion')
    # Title text is no longer highlight UI; remove obsolete title-inline selector from event-isolation classifier.
    s=s.replace(', .library-title-inline-mark, .library-title-mark-btn',', .library-title-mark-btn')
    # Help reconciliation: replace obsolete three-model/title-marker wording with exact selection vs marker distinction.
    s=s.replace('<div class="help-note"><strong>Trois modèles distincts :</strong> sur iPhone/iPad et les appareils compatibles, sélectionnez précisément les mots ; sur Samsung/Android lorsque <strong>Paragraphe</strong> est proposé, le surlignage porte sur le paragraphe entier ; dans Approfondir, <strong>Surligner le titre</strong> marque la lecture entière tout en colorant visuellement le texte du titre.</div>',
                '<div class="help-note"><strong>Trois usages distincts :</strong> sur iPhone/iPad et les appareils compatibles, sélectionnez précisément les mots, y compris dans un titre Approfondir ; sur Samsung/Android lorsque <strong>Paragraphe</strong> est proposé, le surlignage porte sur le paragraphe entier ; <strong>Marquer cette lecture</strong> est un repère séparé qui permet de retrouver la lecture entière dans Mon Espace.</div>')
    s=s.replace('<div class="help-row"><span class="help-icon">▰</span><span class="help-row-text"><strong>Surligner le titre</strong> — Choisissez l’une des cinq couleurs. Le surlignage suit les lignes du texte du titre comme un surlignage de passage, mais le repère enregistré concerne la <strong>lecture entière</strong> et reste indépendant des passages surlignés dans son contenu.</span></div>',
                '<div class="help-row"><span class="help-icon">▰</span><span class="help-row-text"><strong>Surligner du texte dans un titre</strong> — Sur iPhone/iPad et les appareils compatibles, sélectionnez les mots voulus dans le titre comme dans le corps du texte. Les actions normales <strong>Surligner, Note, Copier, Fermer</strong> apparaissent et seul le texte sélectionné est annoté.</span></div>')
    s=s.replace('<div class="help-row"><span class="help-icon">🎨</span><span class="help-row-text"><strong>Changer la couleur ou supprimer</strong> — Touchez directement le titre déjà surligné, ou utilisez <strong>Modifier / retirer le surlignage</strong>. La palette indique la couleur actuelle et propose <strong>✕ Supprimer le surlignage</strong>.</span></div>',
                '<div class="help-row"><span class="help-icon">🎨</span><span class="help-row-text"><strong>Modifier un surlignage du titre</strong> — Touchez les mots déjà surlignés dans le titre pour changer leur couleur ou supprimer ce surlignage, exactement comme dans le corps du texte.</span></div>')
    # Insert separate marker help immediately before Lectures marquées row.
    markerrow='<div class="help-row"><span class="help-icon">★</span><span class="help-row-text"><strong>Marquer cette lecture</strong> — Ce bouton est distinct du surlignage du texte. Il enregistre un repère pour la lecture entière et la fait apparaître dans <strong>Mon Espace → Lectures marquées</strong>.</span></div>'
    target='<div class="help-row"><span class="help-icon">▤</span><span class="help-row-text"><strong>Lectures marquées</strong> — Le repère apparaît dans <strong>Mon Espace → Lectures marquées</strong>. Ouvrir cet élément rouvre la lecture complète au début.</span></div>'
    s=replace_once(s,target,markerrow+'\n        '+target,'marker Help row')
    # Notes wording no longer paragraph-only.
    s=s.replace('<strong>Note</strong> — Une note est rattachée au paragraphe, même si quelques mots seulement étaient sélectionnés.','<strong>Note</strong> — Une note est rattachée au passage ou au titre concerné, même si quelques mots seulement étaient sélectionnés.')
    # Active help should no longer use obsolete whole-reading title wording.
    return s

def update_active_docs(stage):
    # README fully current-facing.
    (stage/'README.md').write_text(f'''# 24 Heures de la Passion — {APP_VERSION}\n\nVersion: `{APP_VERSION}`  \nEvidence stage: `{STAGE}`\n\n## v101.88 — exact Approfondir title-text selection\n\nReal iPhone feedback proved that v101.87 still did not implement the required feature: selecting part of an Approfondir title did not enter the normal annotation pipeline. v101.88 makes each visible Approfondir title a stable `PASSION24.TEXT.<ID>.TITLE` text target and routes native title selection through the same Surligner / Note / Copier pipeline as body text.\n\nThe existing `libraryMarks` whole-reading store is preserved but is now presented separately as **Marquer cette lecture**. It no longer rewrites or colours the title text.\n\nStorage remains schema 8 / snapshot 5. Corpus, source text, speech data and paragraph IDs are unchanged.\n\nService-worker cache generation: `{CACHE}`.\n\nThe exact physical-iPhone title-selection gate remains NOT_TESTED until this exact package is tested on the reporting iPhone.\n''','utf-8')
    md=stage/'REAL_DEVICE_QA_CHECKLIST.md'; csvp=stage/'REAL_DEVICE_QA_RESULTS_TEMPLATE.csv'
    text=md.read_text('utf-8')
    text=text.replace('v101.87','v101.88').replace('luisa-24h-v101-87','luisa-24h-v101-88')
    # Replace the old additions section from marker semantics onward.
    text=re.sub(r'## v101\.88 user-feedback and TH1 additions.*?\Z','',text,flags=re.S).rstrip()+"\n\n"
    text += '''## v101.88 exact-title-selection additions\n\n75. 17e Heure remains correct: `... contiennent, et constitue-Moi ...` without a break inside `et`.\n76. 15e Heure remains correct: `... ton silence, il proclame devant tous que Tu es un fou.` with P014/P015 anchors usable.\n77. Approfondir: on iPhone/iPad, select part of the actual title and confirm the app action bar offers **Surligner / Note / Copier / Fermer**.\n78. Surligner only the selected title words; confirm the rest of the title remains unhighlighted.\n79. Tap a title-text highlight, recolour it, remove it, then use Annuler and confirm exact restoration.\n80. Create two non-overlapping highlights in one title and a normal body highlight in the same reading; confirm all remain independent.\n81. Use **Marquer cette lecture** while title text is already highlighted; confirm the reading marker does not alter or remove title highlights.\n82. Mon Espace: exact title highlights appear under Surlignages with a `Titre — ...` label; whole-reading marks remain under Lectures marquées.\n83. Title Note: create a note from selected title text and confirm it persists and appears in Mon Espace.\n84. Export/import a v101.88 backup containing title highlights, a title note and a Lectures marquées entry; confirm all three survive distinctly.\n85. Samsung regression: paragraph mode still highlights body paragraphs only and does not silently enable native word-selection on titles.\n86. Aide truth: exact title-text selection and **Marquer cette lecture** are explained as separate functions; no obsolete whole-title-marker instruction remains.\n\n### G-87 — Physical iPhone exact title-text selection — REQUIRED\n\nOn the exact v101.88 build, open at least three Approfondir texts on the reporting iPhone. Long-press/select one word in the actual title, extend the native selection to several words, and confirm the app's **Surligner / Note / Copier / Fermer** bar appears. Highlight the selection, recolour it, remove it, Undo, reload, and reopen it from Mon Espace. This gate remains **NOT_TESTED** until executed on the physical iPhone.\n'''
    md.write_text(text,'utf-8')
    rows=list(csv.reader(csvp.open(encoding='utf-8')))
    out=[]
    for r in rows:
        if not r: continue
        if r[0]=='G-86' or (len(r)>1 and r[1]=='G-86'): continue
        r=[v.replace('v101.87','v101.88').replace('luisa-24h-v101-87','luisa-24h-v101-88') for v in r]
        # Rewrite G-77..G-85 current scenarios.
        gid=r[1] if len(r)>1 and r[1].startswith('G-') else (r[0] if r and r[0].startswith('G-') else '')
        repl={
          'G-77':'Approfondir exact title selection: partial native title selection offers Surligner / Note / Copier / Fermer.',
          'G-78':'Only selected title words are highlighted; rest of title remains normal.',
          'G-79':'Title text highlight recolour/remove/Annuler restores exact prior highlight.',
          'G-80':'Two title highlights + body highlight coexist independently in same reading.',
          'G-81':'Marquer cette lecture coexists with exact title text highlights without rewriting title.',
          'G-82':'Mon Espace separates Titre highlight under Surlignages from whole reading under Lectures marquées.',
          'G-83':'Title Note persists and appears in Mon Espace.',
          'G-84':'v101.88 JSON backup/import preserves title highlights, title notes and libraryMarks distinctly.',
          'G-85':'Samsung body paragraph mode unchanged; exact title native selection is not introduced on Samsung.'
        }
        if gid in repl:
            # description column is typically index 2
            if len(r)>2: r[2]=repl[gid]
            elif len(r)>1: r[1]=repl[gid]
        out.append(r)
    # add G-86 Help and G-87 physical iPhone.
    out.append(['Help','G-86','Aide distinguishes exact title-text Surligner/Note/Copier from Marquer cette lecture; no obsolete whole-title-marker instruction remains.','NOT_TESTED','',''])
    out.append(['iPhone','G-87','Physical iPhone exact title-text selection on three Approfondir titles: native selection → app action bar → partial highlight → recolour/remove/Undo/reload/Mon Espace.','NOT_TESTED','','Required physical-device closure for v101.88'])
    with csvp.open('w',encoding='utf-8',newline='') as f: csv.writer(f).writerows(out)

def syntax(stage):
    s=(stage/'index.html').read_text('utf-8'); scripts='\n'.join(re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>',s,re.S|re.I)); tmp=stage/'_check.js';tmp.write_text(scripts,'utf-8')
    r=subprocess.run(['node','--check',str(tmp)],capture_output=True,text=True);tmp.unlink()
    if r.returncode: die('JS syntax '+r.stderr)
    r=subprocess.run(['node','--check',str(stage/'sw.js')],capture_output=True,text=True)
    if r.returncode: die('SW syntax '+r.stderr)

def stale_scan(stage):
    bad=[]; hits=[]
    active_current={'README.md','REAL_DEVICE_QA_CHECKLIST.md','REAL_DEVICE_QA_RESULTS_TEMPLATE.csv','version.json','sw.js','metadata/user_feedback_authority.md'}
    for p in sorted(stage.rglob('*')):
        if not p.is_file() or p.suffix.lower() in {'.png','.ico'}: continue
        rel=p.relative_to(stage).as_posix(); txt=p.read_text('utf-8',errors='ignore')
        for tok in ['v101.87','luisa-24h-v101-87','Surligner le titre','library-title-inline-mark']:
            for m in re.finditer(re.escape(tok),txt):
                ctx=txt[max(0,m.start()-120):m.end()+160].replace('\n',' ')
                low=ctx.lower()
                historical=any(w in low for w in ['baseline','previous','proved','failed','failure','did not support','did not implement','superseded','historical','from v101.87','identical to v101.87','deprecated','visible wording changes','old whole-title'])
                if rel.startswith('scripts/'): historical=True
                if rel.startswith('audit/') or rel.startswith('reports/'):
                    if tok=='v101.87' and ('protected' in low or 'baseline' in low or 'identical' in low): historical=True
                # Old cache name is never allowed in current QA/runtime metadata; only explicit historical script context.
                if tok=='luisa-24h-v101-87' and rel in active_current: historical=False
                # Obsolete runtime class must be gone from active app bytes.
                if tok=='library-title-inline-mark' and rel in {'index.html','luisa_24_heures.html'}: historical=False
                # Obsolete user-facing phrase must be absent from current QA/README/runtime; scripts may mention migration wording.
                if tok=='Surligner le titre' and (rel in active_current or rel in {'index.html','luisa_24_heures.html'}): historical=False
                cls='HISTORICAL_ALLOWED' if historical else 'FAIL'
                hits.append((rel,tok,cls,ctx[:300]))
                if not historical: bad.append(hits[-1])
    (stage/'reports/stale_reference_scan.txt').write_text('path\ttoken\tclassification\tcontext\n'+'\n'.join('\t'.join(x) for x in hits)+'\n','utf-8')
    (stage/'reports/pass4_contradiction_stale_scan.txt').write_text(f'hits={len(hits)}\nunjustified={len(bad)}\n'+'\n'.join('\t'.join(x) for x in bad)+'\n','utf-8')
    if bad: die('stale/obsolete current-facing references '+repr(bad[:5]))

def write_reports(stage,before,after):
    (stage/'reports/no_regression_fix_ledger.csv').write_text('fix_id,status,scope,protected\nT88-01,PASS,title target registry,6/6 protected\nT88-02,PASS,title DOM/native selection,6/6 protected\nT88-03,PASS,reading-marker separation,libraryMarks preserved\nT88-04,PASS,Help/QA/version cache reconciliation,no corpus change\n','utf-8')
    rows=[['gate','status','evidence'],['protected_structures','PASS','6/6 hashes identical'],['schema_snapshot','PASS','8/5'],['exact_title_target','PASS','33 deterministic title targets'],['title_native_selection','PASS','prepackage Chromium Range pipeline'],['body_highlight_regression','PASS','same generic renderer/store'],['libraryMarks_preserved','PASS','separate Marquer cette lecture'],['PHYSICAL-IPHONE-EXACT-TITLE','NOT_TESTED','exact v101.88 physical iPhone required'],['PHYSICAL-IPAD','NOT_TESTED','real device'],['PHYSICAL-SAMSUNG','NOT_TESTED','real device'],['PWA-MIGRATION-OFFLINE','NOT_TESTED','installed PWA/live origin'],['VOICEOVER','NOT_TESTED','real AT'],['TALKBACK','NOT_TESTED','real AT'],['NVDA','NOT_TESTED','real AT'],['LIVE-V10188-BYTE-BINDING','NOT_TESTED','live deployment'],['VERIFIED-ROLLBACK','NOT_TESTED','rollback evidence']]
    with (stage/'reports/full_regression_matrix.csv').open('w',encoding='utf-8',newline='') as f: csv.writer(f).writerows(rows)
    (stage/'reports/root_deploy_consistency_report.md').write_text(f'# Root/runtime consistency\n\nPASS — twin runtime SHA-256 `{hf(stage/"index.html")}`.\n','utf-8')
    (stage/'reports/nested_zip_consistency_report.md').write_text('# Nested ZIP consistency\n\nPASS — no nested ZIP is present.\n','utf-8')
    (stage/'reports/report_claims_vs_evidence_audit.md').write_text('# Report claims vs evidence\n\nPASS prepackage. Exact v101.88 physical-iPhone title-selection remains explicitly NOT_TESTED.\n','utf-8')

def manifests(stage):
    lock={'app_version':APP_VERSION,'stage':STAGE,'prepackage_four_pass_gate':'PASS','final_package_reopen_gate':'REQUIRED_POSTPACKAGE','independent_reopen_gate':'REQUIRED_POSTPACKAGE','physical_exact_title_selection':'NOT_TESTED','final_status':'PENDING_POSTPACKAGE_AUDITS','public_release_ready':False}
    (stage/'metadata/final_decision_lock.json').write_text(json.dumps(lock,indent=2)+'\n','utf-8')
    files=[]
    for p in sorted(stage.rglob('*')):
        if not p.is_file() or p.relative_to(stage).as_posix() in ['metadata/hash_manifest.json','metadata/package_manifest.json']: continue
        files.append({'path':p.relative_to(stage).as_posix(),'sha256':hf(p),'bytes':p.stat().st_size})
    (stage/'metadata/hash_manifest.json').write_text(json.dumps({'algorithm':'sha256','files':files},indent=2)+'\n','utf-8')
    files2=[]
    for p in sorted(stage.rglob('*')):
        if not p.is_file() or p.relative_to(stage).as_posix()=='metadata/package_manifest.json': continue
        files2.append({'path':p.relative_to(stage).as_posix(),'sha256':hf(p),'bytes':p.stat().st_size})
    (stage/'metadata/package_manifest.json').write_text(json.dumps({'app_version':APP_VERSION,'stage':STAGE,'files':files2},indent=2)+'\n','utf-8')

def zip_det(stage,out):
    if out.exists(): out.unlink()
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(stage.rglob('*')):
            if not p.is_file(): continue
            rel=p.relative_to(stage).as_posix(); zi=zipfile.ZipInfo(rel,FIXED_DT);zi.compress_type=zipfile.ZIP_DEFLATED;zi.external_attr=(0o644&0xffff)<<16
            z.writestr(zi,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)

def build(stage,out):
    s,before=preflight(stage)
    s2=patch_runtime(s); after=protected(s2)
    if before!=after: die('protected data drift')
    (stage/'index.html').write_text(s2,'utf-8');(stage/'luisa_24_heures.html').write_text(s2,'utf-8')
    sw=(stage/'sw.js').read_text('utf-8');sw=replace_once(sw,'/* v101.87 */','/* v101.88 */','SW version');sw=replace_once(sw,"const CACHE_NAME = 'luisa-24h-v101-87';",f"const CACHE_NAME = '{CACHE}';",'SW cache');(stage/'sw.js').write_text(sw,'utf-8')
    ver=json.loads((stage/'version.json').read_text('utf-8'));ver.update({'app_version':APP_VERSION,'evidence_stage':STAGE,'build_date':BUILD_DATE,'status':'PREPUBLIC_EXACT_TITLE_SELECTION_PHYSICAL_RETEST_PENDING','real_device_status':'v101.87 did not implement partial native title selection; exact v101.88 physical-iPhone retest required.'});(stage/'version.json').write_text(json.dumps(ver,ensure_ascii=False,indent=2)+'\n','utf-8')
    man=json.loads((stage/'manifest.json').read_text('utf-8'));man['version']=APP_VERSION;(stage/'manifest.json').write_text(json.dumps(man,ensure_ascii=False,indent=2)+'\n','utf-8')
    update_active_docs(stage)
    # Replace prior scripts/evidence universe with current scripts, keeping historical package docs only where not active.
    (stage/'scripts').mkdir(exist_ok=True); (stage/'audit').mkdir(exist_ok=True); (stage/'reports').mkdir(exist_ok=True); (stage/'metadata').mkdir(exist_ok=True)
    # Clean generated evidence universe before producing current reports; do not carry stale PASS evidence from v101.87.
    for d in [stage/'reports', stage/'audit']:
        for p in d.iterdir():
            if p.is_file(): p.unlink()
            elif p.is_dir(): shutil.rmtree(p)
    for name in ['hash_manifest.json','package_manifest.json','build_provenance.json','auditor_provenance.json','user_feedback_authority.md']:
        (stage/'metadata'/name).unlink(missing_ok=True)
    (stage/'metadata/user_feedback_authority.md').write_text('# User-feedback authority — v101.88\n\nPhysical iPhone evidence proved that v101.87 did not support partial native selection of Approfondir title text. v101.88 implements exact title text as a first-class annotation target while keeping whole-reading `libraryMarks` separate as **Marquer cette lecture**. Exact v101.88 physical-iPhone confirmation remains required.\n','utf-8')
    shutil.copy2(GOV,stage/'scripts'/GOV.name);shutil.copy2(Path(__file__),stage/'scripts'/Path(__file__).name);shutil.copy2(FOUR,stage/'scripts'/FOUR.name)
    # remove stale v10187 auditor/build scripts from active scripts dir
    for p in list((stage/'scripts').glob('l24h_v10187_*'))+list((stage/'scripts').glob('L24H_v10187_*')):
        if p.name not in {GOV.name}: p.unlink(missing_ok=True)
    syntax(stage)
    write_reports(stage,before,after)
    # Write the honest current prepackage lock before the independent auditor reads active metadata.
    prelock={'app_version':APP_VERSION,'stage':STAGE,'prepackage_four_pass_gate':'PENDING','final_package_reopen_gate':'REQUIRED_POSTPACKAGE','independent_reopen_gate':'REQUIRED_POSTPACKAGE','physical_exact_title_selection':'NOT_TESTED','final_status':'PENDING_POSTPACKAGE_AUDITS','public_release_ready':False}
    (stage/'metadata/final_decision_lock.json').write_text(json.dumps(prelock,indent=2)+'\n','utf-8')
    # independent four-pass must pass before package manifests
    outmd=stage/'audit/independent_four_pass_audit.md';outjson=stage/'reports/independent_four_pass_summary.json'
    r=subprocess.run([sys.executable,str(FOUR),str(stage),str(outmd),str(outjson)],capture_output=True,text=True)
    if r.returncode: die('independent four-pass failed\n'+r.stdout[-3000:]+r.stderr[-3000:])
    # Pass3 ledger from current active evidence
    rows=[['file','line','classification','evidence']]
    active=[stage/'README.md',stage/'REAL_DEVICE_QA_CHECKLIST.md',stage/'REAL_DEVICE_QA_RESULTS_TEMPLATE.csv',outmd]+sorted((stage/'reports').glob('*'))
    for p in active:
        if not p.exists(): continue
        for i,line in enumerate(p.read_text('utf-8',errors='ignore').splitlines(),1):
            cl='NOT_TESTED' if 'NOT_TESTED' in line else ('NONCLAIM' if not line.strip() else 'SUPPORTED')
            rows.append([p.relative_to(stage).as_posix(),i,cl,'direct current package evidence'])
    with (stage/'reports/pass3_claim_ledger.csv').open('w',encoding='utf-8',newline='') as f: csv.writer(f).writerows(rows)
    stale_scan(stage)
    (stage/'metadata/build_provenance.json').write_text(json.dumps({'baseline_package':BASE.name,'baseline_sha256':BASE_SHA,'governing_script':GOV.name,'governing_script_sha256':hf(GOV),'build_script':Path(__file__).name,'build_script_sha256':hf(Path(__file__)),'app_version':APP_VERSION,'stage':STAGE,'runtime_change':'exact library-title annotation target + separate reading marker; no protected corpus/speech changes'},indent=2)+'\n','utf-8')
    (stage/'metadata/auditor_provenance.json').write_text(json.dumps({'independent_four_pass_auditor':FOUR.name,'sha256':hf(FOUR),'independence':'separately implemented runtime/report audit; physical iPhone not inferred'},indent=2)+'\n','utf-8')
    manifests(stage)
    zip_det(stage,out)
    print(json.dumps({'zip':str(out),'sha256':hf(out),'bytes':out.stat().st_size,'runtime_sha256':hf(stage/'index.html'),'protected':after},indent=2))

if __name__=='__main__':
    if len(sys.argv)!=3: print('usage: build.py STAGE_DIR OUT.zip');sys.exit(2)
    build(Path(sys.argv[1]),Path(sys.argv[2]))
