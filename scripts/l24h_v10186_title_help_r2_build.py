from __future__ import annotations
import argparse,csv,hashlib,json,re,shutil,zipfile,subprocess
from pathlib import Path

BASE=Path('/mnt/data/L24H_v10185_GITHUB_DEPLOY_USER_FEEDBACK_CORRECTED_HARDENED_R4_AUDIT_RECONCILED.zip')
BASE_SHA='09ef964e62dfe3005637c20b5a5fde0094bd9767a85ef6513582e81cb84d0ea5'
BASE_RUNTIME_SHA='c43ff8934c12b24668c9c0cf55ebb12a9eb6ecd8ed265e68e4d78aaf0fd86050'
GOV=Path('/mnt/data/L24H_v10186_TH1_R2_FOUR_PASS_RECONCILIATION_SCRIPT_2026-08-19.md')
RUNTIME_GOV=Path('/mnt/data/L24H_v10186_STAGE_TITLE_HELP_HARDGATED_SCRIPT_2026-08-19.md')
THIS=Path('/mnt/data/l24h_v10186_title_help_r2_build.py')
FOUR=Path('/mnt/data/l24h_v10186_r2_independent_four_pass_audit.py')
REOPEN=Path('/mnt/data/l24h_v10186_r2_final_reopen_audit.py')
IREOPEN=Path('/mnt/data/l24h_v10186_r2_independent_reopen_audit.py')
APP_VERSION='v101.86'; BUILD_DATE='2026-08-19'; SCHEMA=8; SNAPSHOT=5
PROTECTED=['CORPUS','TEXT_LIBRARY','HOUR_LINKED_TEXTS','SPEECH_DATA','INTERNAL_SUBHEADINGS','SPEECH_END_VISUAL_BREAKS']

def hf(p):
 h=hashlib.sha256();
 with open(p,'rb') as f:
  for c in iter(lambda:f.read(1<<20),b''):h.update(c)
 return h.hexdigest()
def hb(b):return hashlib.sha256(b).hexdigest()
def die(m):raise SystemExit('FAIL '+m)
def jconst(s,name):
 m=re.search(r'const\s+'+re.escape(name)+r'\s*=\s*',s)
 if not m: raise ValueError('missing '+name)
 start=m.end(); dec=json.JSONDecoder(); obj,end=dec.raw_decode(s[start:]);return obj

def protect_fingerprints(s):
 out={}
 for n in PROTECTED:
  o=jconst(s,n); raw=json.dumps(o,ensure_ascii=False,separators=(',',':'),sort_keys=True).encode(); out[n]={'sha256':hb(raw),'count':len(o) if hasattr(o,'__len__') else None}
 return out

def replace1(s,old,new,label):
 c=s.count(old)
 if c!=1: die(f'{label}: expected 1 exact match, found {c}')
 return s.replace(old,new,1)

def preflight(stage):
 if not BASE.exists() or hf(BASE)!=BASE_SHA:die('baseline ZIP identity mismatch')
 for p in [GOV,RUNTIME_GOV,THIS,FOUR,REOPEN,IREOPEN]:
  if not p.exists():die('missing required script '+str(p))
 shutil.rmtree(stage,ignore_errors=True);stage.mkdir(parents=True)
 with zipfile.ZipFile(BASE) as z:z.extractall(stage)
 a=stage/'index.html';b=stage/'luisa_24_heures.html'
 if hf(a)!=BASE_RUNTIME_SHA or a.read_bytes()!=b.read_bytes():die('baseline runtime twin/hash mismatch')
 s=a.read_text('utf-8')
 gates={
 'app_version':"const APP_VERSION = 'v101.85';" in s,
 'schema8':'const STORAGE_SCHEMA_VERSION=8;' in s,
 'snapshot5':'const PERSONAL_SNAPSHOT_VERSION = 5;' in s,
 'source_edition':jconst(s,'CORPUS').get('source_edition')=='GE / Lumen Luminis / septembre 2021',
 'library_sanitizer':'function sanitizeLibraryMarksStore' in s,
 'library_snapshot':'libraryMarks: state.libraryMarks' in s,
 'library_storage':"['lp24_library_marks', JSON.stringify(snapshot.libraryMarks)]" in s,
 'library_espace':'Lectures marquées' in s and 'removeLibraryMarkFromEspace' in s,
 'library_export':'libraryMarks: sanitizeLibraryMarksStore(state.libraryMarks)' in s,
 'library_import':"if (hasOwn('libraryMarks'))" in s,
 'library_journal':"lines.push('## Lectures marquées'" in s,
 'library_undo':'function undoLatestLibraryMarkRemoval' in s,
 'five_colors':all(x in s for x in ["'yellow'","'blue'","'green'","'purple'","'pink'"])
 }
 if not all(gates.values()):die('preflight support/source gate failed '+repr([k for k,v in gates.items() if not v]))
 return s,gates,protect_fingerprints(s)

def patch_runtime(s):
 # TH1-01 visual CSS: full H2 container no longer highlighted; inline mark reuses body hl classes.
 old='''.library-title-mark-wrap{display:flex;flex-direction:column;align-items:flex-start;gap:0.55rem;margin-bottom:0.3rem;}
.library-title-mark-wrap .reader-title{display:inline;box-decoration-break:clone;-webkit-box-decoration-break:clone;border-radius:0.32rem;padding:0.04em 0.18em;transition:background 0.15s;}
.library-title-mark-yellow{background:#fef9c3;} .library-title-mark-blue{background:#dbeafe;} .library-title-mark-green{background:#dcfce7;} .library-title-mark-purple{background:#ede9fe;} .library-title-mark-pink{background:#fce7f3;}
[data-theme="dark"] .library-title-mark-yellow{background:#713f12;color:#fef9c3;} [data-theme="dark"] .library-title-mark-blue{background:#1e3a5f;color:#dbeafe;} [data-theme="dark"] .library-title-mark-green{background:#14532d;color:#dcfce7;} [data-theme="dark"] .library-title-mark-purple{background:#3b0764;color:#ede9fe;} [data-theme="dark"] .library-title-mark-pink{background:#500724;color:#fce7f3;}
.library-title-mark-btn{font-family:var(--font-ui);font-size:0.78rem;font-weight:700;color:var(--accent);background:var(--accent-pale);border:1.5px solid var(--accent-light);border-radius:999px;min-height:44px;padding:0.48rem 0.85rem;cursor:pointer;touch-action:manipulation;}
.library-title-mark-btn[aria-pressed="true"]{background:var(--accent);color:#fff;border-color:var(--accent);}'''
 new='''.library-title-mark-wrap{display:flex;flex-direction:column;align-items:flex-start;gap:0.55rem;margin-bottom:0.3rem;}
.library-title-mark-wrap .reader-title{display:block;margin-bottom:0;}
mark.library-title-inline-mark{display:inline;padding:0 0.08em;border-radius:0.16rem;box-decoration-break:clone;-webkit-box-decoration-break:clone;cursor:pointer;touch-action:manipulation;transition:background 0.15s,outline-color 0.15s;}
mark.library-title-inline-mark:focus-visible{outline:3px solid var(--accent-light);outline-offset:3px;}
.library-title-mark-btn{font-family:var(--font-ui);font-size:0.78rem;font-weight:700;color:var(--accent);background:var(--accent-pale);border:1.5px solid var(--accent-light);border-radius:999px;min-height:44px;padding:0.48rem 0.85rem;cursor:pointer;touch-action:manipulation;}
.library-title-mark-btn[aria-pressed="true"]{background:var(--accent);color:#fff;border-color:var(--accent);}
#libraryMarkerPicker .cp-swatch[aria-pressed="true"]{outline:3px solid var(--ink);outline-offset:3px;box-shadow:0 0 0 2px var(--bg);}'''
 s=replace1(s,old,new,'TH1-01 CSS')
 # Picker controls get selection semantics and consistent removal wording.
 old='''    <button type="button" class="cp-swatch cp-yellow" onclick="applyLibraryMarkerColor('yellow')" aria-label="Jaune" title="Jaune"></button>
    <button type="button" class="cp-swatch cp-blue" onclick="applyLibraryMarkerColor('blue')" aria-label="Bleu" title="Bleu"></button>
    <button type="button" class="cp-swatch cp-green" onclick="applyLibraryMarkerColor('green')" aria-label="Vert" title="Vert"></button>
    <button type="button" class="cp-swatch cp-purple" onclick="applyLibraryMarkerColor('purple')" aria-label="Violet" title="Violet"></button>
    <button type="button" class="cp-swatch cp-pink" onclick="applyLibraryMarkerColor('pink')" aria-label="Rose" title="Rose"></button>'''
 new='''    <button type="button" class="cp-swatch cp-yellow" data-library-marker-color="yellow" aria-pressed="false" onclick="applyLibraryMarkerColor('yellow')" aria-label="Jaune" title="Jaune"></button>
    <button type="button" class="cp-swatch cp-blue" data-library-marker-color="blue" aria-pressed="false" onclick="applyLibraryMarkerColor('blue')" aria-label="Bleu" title="Bleu"></button>
    <button type="button" class="cp-swatch cp-green" data-library-marker-color="green" aria-pressed="false" onclick="applyLibraryMarkerColor('green')" aria-label="Vert" title="Vert"></button>
    <button type="button" class="cp-swatch cp-purple" data-library-marker-color="purple" aria-pressed="false" onclick="applyLibraryMarkerColor('purple')" aria-label="Violet" title="Violet"></button>
    <button type="button" class="cp-swatch cp-pink" data-library-marker-color="pink" aria-pressed="false" onclick="applyLibraryMarkerColor('pink')" aria-label="Rose" title="Rose"></button>'''
 s=replace1(s,old,new,'TH1-02 picker swatches')
 s=replace1(s,'<button type="button" class="cp-remove" id="libraryMarkerRemoveBtn" onclick="removeLibraryMarkerFromPicker()" style="display:none">✕ Retirer le surlignage du titre</button>','<button type="button" class="cp-remove" id="libraryMarkerRemoveBtn" onclick="removeLibraryMarkerFromPicker()" style="display:none">✕ Supprimer le surlignage</button>','TH1-02 remove wording')
 # Replace title marker helper block through before openLibraryText.
 a=s.index('let _pendingLibraryMarkerId = null;'); b=s.index('\nfunction openLibraryText(',a)
 newblock=r'''let _pendingLibraryMarkerId = null;
let _libraryMarkUndoToken = null;
function getLibraryMark(itemId) { return (state.libraryMarks || {})[itemId] || null; }
function getLibraryMarkClass(itemId) { const m=getLibraryMark(itemId); return m ? ('hl-' + m.color) : ''; }
function renderLibraryReaderTitleInner(item) {
  const title = escHtml(item.title);
  const badge = item.status==='placeholder' ? '<span class="placeholder-badge">À intégrer</span>' : '';
  const mark = getLibraryMark(item.id);
  if (!mark) return title + badge;
  return `<mark id="libraryReaderTitleMark" class="library-title-inline-mark hl ${getLibraryMarkClass(item.id)}" role="button" tabindex="0" aria-label="Modifier ou supprimer le surlignage de cette lecture" onclick="openLibraryMarkerPicker('${escHtml(item.id)}',this)" onkeydown="handleLibraryTitleMarkKeydown(event,'${escHtml(item.id)}')">${title}</mark>${badge}`;
}
function handleLibraryTitleMarkKeydown(event,itemId) {
  if (!event || (event.key !== 'Enter' && event.key !== ' ')) return;
  event.preventDefault();
  openLibraryMarkerPicker(itemId,event.currentTarget);
}
function refreshLibraryMarkerTitleUi(itemId) {
  if (state.view !== 'libraryText' || state.currentSection !== itemId) return;
  const item=getLibraryItem(itemId); if(!item) return;
  const title = document.getElementById('libraryReaderTitle');
  const btn = document.getElementById('libraryTitleMarkBtn');
  const mark = getLibraryMark(itemId);
  if (title) title.innerHTML = renderLibraryReaderTitleInner(item);
  if (btn) {
    btn.setAttribute('aria-pressed', mark ? 'true' : 'false');
    btn.textContent = mark ? 'Modifier / retirer le surlignage' : 'Surligner le titre';
    btn.setAttribute('aria-label', mark ? 'Modifier ou supprimer le surlignage du titre' : 'Surligner le titre');
  }
}
function updateLibraryMarkerPickerSelection(itemId) {
  const mark=getLibraryMark(itemId);
  document.querySelectorAll('#libraryMarkerPicker [data-library-marker-color]').forEach(function(btn){
    btn.setAttribute('aria-pressed', mark && btn.dataset.libraryMarkerColor===mark.color ? 'true' : 'false');
  });
  const label=document.getElementById('libraryMarkerPickerLabel');
  if(label) label.textContent = mark ? 'Modifier le surlignage du titre' : 'Surligner le titre en';
}
function openLibraryMarkerPicker(itemId, triggerEl) {
  if (!isValidLibraryMarkId(itemId)) { showToast('Lecture introuvable'); return; }
  _pendingLibraryMarkerId = itemId;
  const picker = document.getElementById('libraryMarkerPicker');
  const remove = document.getElementById('libraryMarkerRemoveBtn');
  if (!picker || !remove) return;
  const mark=getLibraryMark(itemId);
  remove.style.display = mark ? 'block' : 'none';
  updateLibraryMarkerPickerSelection(itemId);
  picker.classList.add('open','cp-bottom');
  const stableReturn=document.getElementById('libraryTitleMarkBtn') || triggerEl || document.activeElement;
  installFocusTrap(picker, closeLibraryMarkerPicker, { returnFocusTo: stableReturn });
}
function closeLibraryMarkerPicker() {
  const picker=document.getElementById('libraryMarkerPicker');
  if (picker) { cleanupFocusTrap(picker,true); picker.classList.remove('open','cp-bottom'); }
  _pendingLibraryMarkerId=null;
}
function applyLibraryMarkerColor(color) {
  const itemId=_pendingLibraryMarkerId;
  if (!itemId || !isValidLibraryMarkId(itemId) || !['yellow','blue','green','purple','pink'].includes(color)) { closeLibraryMarkerPicker(); return; }
  const before=buildPersonalSnapshotFromState();
  const old=getLibraryMark(itemId); const now=new Date().toISOString();
  if (!state.libraryMarks || typeof state.libraryMarks!=='object') state.libraryMarks={};
  state.libraryMarks[itemId]={color,created_at:(old&&old.created_at)||now,updated_at:now};
  const committed=commitDurableChange(before, old ? 'Modification du surlignage du titre' : 'Ajout du surlignage du titre');
  closeLibraryMarkerPicker();
  if (committed.ok) { refreshLibraryMarkerTitleUi(itemId); updateRightContextPanel(); showToast(old ? 'Couleur du titre modifiée' : 'Titre surligné ◐'); }
}
function removeLibraryMark(itemId, showUndo=true) {
  if (!isValidLibraryMarkId(itemId) || !getLibraryMark(itemId)) return false;
  const beforeSnapshot=buildPersonalSnapshotFromState();
  const beforeStore=sanitizeLibraryMarksStore(state.libraryMarks);
  delete state.libraryMarks[itemId];
  const committed=commitDurableChange(beforeSnapshot,'Suppression du surlignage du titre');
  if (!committed.ok) return false;
  const afterStore=sanitizeLibraryMarksStore(state.libraryMarks);
  _libraryMarkUndoToken={before_store:beforeStore,after_store:afterStore,item_id:itemId};
  refreshLibraryMarkerTitleUi(itemId);
  if (state.view==='espace') showEspaceView(false); else updateRightContextPanel();
  if (showUndo) showToastWithAction('Surlignage du titre supprimé.', 'Annuler', undoLatestLibraryMarkRemoval, 8000);
  return true;
}
function removeLibraryMarkerFromPicker() { const id=_pendingLibraryMarkerId; closeLibraryMarkerPicker(); if (id) removeLibraryMark(id,true); }
function removeLibraryMarkFromEspace(itemId,event) { if(event){event.preventDefault();event.stopPropagation();} removeLibraryMark(itemId,true); }
function undoLatestLibraryMarkRemoval() {
  const token=_libraryMarkUndoToken; if(!token){showToast('Aucune suppression de titre à annuler.');return false;}
  if (JSON.stringify(sanitizeLibraryMarksStore(state.libraryMarks))!==JSON.stringify(token.after_store)) { _libraryMarkUndoToken=null; showToast('Annulation impossible : les lectures marquées ont changé.'); return false; }
  const before=buildPersonalSnapshotFromState(); state.libraryMarks=sanitizeLibraryMarksStore(token.before_store);
  const committed=commitDurableChange(before,'Annulation de la suppression du titre');
  if (!committed.ok) return false;
  const id=token.item_id; _libraryMarkUndoToken=null; refreshLibraryMarkerTitleUi(id);
  if(state.view==='espace')showEspaceView(false);else updateRightContextPanel();
  showToast('Suppression du titre annulée.'); return true;
}
'''
 s=s[:a]+newblock+s[b:]
 # Reader title render.
 old='''<div class="library-title-mark-wrap"><h2 id="libraryReaderTitle" class="reader-title ${getLibraryMarkClass(item.id)}">${escHtml(item.title)}${item.status==='placeholder'?'<span class="placeholder-badge">À intégrer</span>':''}</h2><button type="button" id="libraryTitleMarkBtn" class="library-title-mark-btn" aria-pressed="${getLibraryMark(item.id)?'true':'false'}" onclick="openLibraryMarkerPicker('${escHtml(item.id)}',this)">${getLibraryMark(item.id)?'Modifier le surlignage du titre':'Surligner le titre'}</button></div>'''
 new='''<div class="library-title-mark-wrap"><h2 id="libraryReaderTitle" class="reader-title">${renderLibraryReaderTitleInner(item)}</h2><button type="button" id="libraryTitleMarkBtn" class="library-title-mark-btn" aria-pressed="${getLibraryMark(item.id)?'true':'false'}" aria-label="${getLibraryMark(item.id)?'Modifier ou supprimer le surlignage du titre':'Surligner le titre'}" onclick="openLibraryMarkerPicker('${escHtml(item.id)}',this)">${getLibraryMark(item.id)?'Modifier / retirer le surlignage':'Surligner le titre'}</button></div>'''
 s=replace1(s,old,new,'TH1-02 reader title render')
 # Help quick-nav styles.
 css_anchor='.help-row-text { font-size: var(--ui-size, 16px); color: var(--ink2); line-height: 1.5; }'
 css_new=css_anchor+'''\n.help-quick-nav{margin:0 0 1rem;padding:0.85rem;border:1px solid var(--bg3);border-radius:var(--radius);background:var(--bg2);}\n.help-quick-title{font-family:var(--font-display);font-weight:800;color:var(--ink);margin-bottom:0.55rem;}\n.help-quick-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:0.45rem;}\n.help-quick-btn{min-height:44px;text-align:left;border:1px solid var(--bg3);border-radius:10px;background:var(--bg);color:var(--ink2);font:600 0.82rem var(--font-ui);padding:0.55rem 0.65rem;cursor:pointer;}\n.help-quick-btn:focus-visible,.help-section-hd[tabindex="-1"]:focus{outline:3px solid var(--accent-light);outline-offset:2px;}'''
 s=replace1(s,css_anchor,css_new,'TH1-03 help quick styles')
 # Replace complete Help function with factual reconciled version.
 hs=s.index('function showHelp()'); he=s.index('function showProvenance()',hs)
 newhelp=r'''function helpJumpTo(sectionId) {
  const target=document.getElementById(sectionId); if(!target) return false;
  const heading=target.querySelector('.help-section-hd');
  try { target.scrollIntoView({behavior:'smooth',block:'start'}); } catch(_e) { target.scrollIntoView(); }
  if(heading){ heading.setAttribute('tabindex','-1'); setTimeout(()=>{ try{heading.focus({preventScroll:true});}catch(_e){try{heading.focus();}catch(_e2){}} },220); }
  return true;
}
function showHelp() {
  const existing = document.getElementById('helpModalOverlay');
  if (existing) { closeHelpModal(); return; }
  const helpReturnFocus = (document.activeElement && document.activeElement !== document.body) ? document.activeElement : document.getElementById('helpBtn');
  closeSidebar();
  const fp = CORPUS.fingerprint_sha256 || '';
  const sourceEdition = CORPUS.source_edition || 'Source non renseignée';
  const overlay = document.createElement('div');
  overlay.id = 'helpModalOverlay';
  overlay.className = 'help-modal-overlay';
  overlay.setAttribute('role','dialog');
  overlay.setAttribute('aria-modal','true');
  overlay.setAttribute('aria-label','Aide et À propos');
  overlay.addEventListener('click', function(e){ if (e.target === overlay) closeHelpModal(); });
  overlay.innerHTML = `
    <div class="help-modal" tabindex="-1">
      <div class="help-modal-topbar">
        <div><div class="help-modal-kicker">Guide d’utilisation</div><h2 class="help-modal-title">Aide et À propos</h2></div>
        <button type="button" class="help-modal-close" onclick="closeHelpModal()" aria-label="Fermer l’aide">× Fermer</button>
      </div>
      <div class="help-modal-scroll">
      <nav class="help-quick-nav" aria-label="Accès rapide à l’aide"><div class="help-quick-title">Que voulez-vous faire ?</div><div class="help-quick-grid">
        <button class="help-quick-btn" onclick="helpJumpTo('help-reading')">Commencer / reprendre une Heure</button>
        <button class="help-quick-btn" onclick="helpJumpTo('help-actions')">Surligner / prendre une note</button>
        <button class="help-quick-btn" onclick="helpJumpTo('help-title-mark')">Marquer une lecture Approfondir</button>
        <button class="help-quick-btn" onclick="helpJumpTo('help-espace')">Retrouver mes éléments dans Mon Espace</button>
        <button class="help-quick-btn" onclick="helpJumpTo('help-backup')">Sauvegarder / restaurer mes données</button>
        <button class="help-quick-btn" onclick="helpJumpTo('help-samsung')">Utiliser Samsung / Android</button>
        <button class="help-quick-btn" onclick="helpJumpTo('help-search')">Rechercher un texte</button>
        <button class="help-quick-btn" onclick="helpJumpTo('help-update')">Mettre l’app à jour</button>
        <button class="help-quick-btn" onclick="helpJumpTo('help-support')">Signaler un problème</button>
      </div></nav>

      <div class="help-section" id="help-navigation"><div class="help-section-hd">Navigation principale</div><div class="help-section-body">
        <div class="help-row"><span class="help-icon">🏠</span><span class="help-row-text"><strong>Accueil</strong> — Reprendre votre dernière Heure, voir les 24 Heures, accéder aux prières, à Approfondir et à Mon Espace.</span></div>
        <div class="help-row"><span class="help-icon">⏱</span><span class="help-row-text"><strong>Heures</strong> — Parcourir les 24 Heures par titre et horaire puis ouvrir celle que vous souhaitez prier.</span></div>
        <div class="help-row"><span class="help-icon">🔎</span><span class="help-row-text"><strong>Recherche</strong> — Chercher dans les Heures, Réflexions, Prières, Compléments et Paroles directes. La loupe du haut ouvre le même écran.</span></div>
        <div class="help-row"><span class="help-icon">▤</span><span class="help-row-text"><strong>Mon Espace</strong> — Retrouver reprise de lecture, progression, surlignages, passages à vérifier, notes, <strong>Lectures marquées</strong> et sauvegardes.</span></div>
        <div class="help-row"><span class="help-icon">📖</span><span class="help-row-text"><strong>Approfondir</strong> — Ouvrir les textes du Livre du Ciel et les textes liés aux Heures.</span></div>
        <div class="help-row"><span class="help-icon">🙏</span><span class="help-row-text"><strong>Prières &amp; compléments</strong> — Dans Réglages → Parcours, ouvre les prières du parcours et les textes complémentaires dans une destination séparée.</span></div>
        <div class="help-row"><span class="help-icon">←</span><span class="help-row-text"><strong>Retour</strong> — Revenir à l’écran précédent en restaurant le contexte de lecture enregistré lorsque cette reprise est disponible.</span></div>
      </div></div>

      <div class="help-section" id="help-reading"><div class="help-section-hd">Lire et prier une Heure</div><div class="help-section-body">
        <div class="help-row"><span class="help-icon">✝</span><span class="help-row-text"><strong>Méditation</strong> — Texte principal de l’Heure. <strong>Réflexions et pratiques</strong> ouvre les réflexions associées. <strong>Textes liés</strong> ouvre les textes d’approfondissement liés à cette Heure.</span></div>
        <div class="help-row"><span class="help-icon">▰</span><span class="help-row-text"><strong>Ligne de progression</strong> — Indique approximativement la proportion de l’Heure parcourue.</span></div>
        <div class="help-row"><span class="help-icon">≡</span><span class="help-row-text"><strong>Plan</strong> — Lorsqu’il est disponible, liste les scènes internes et permet d’y aller directement.</span></div>
        <div class="help-row"><span class="help-icon">🕯</span><span class="help-row-text"><strong>Prières de début et de fin</strong> — Les boutons de l’Heure ouvrent les prières correspondantes sans perdre volontairement votre place.</span></div>
        <div class="help-row"><span class="help-icon">✓</span><span class="help-row-text"><strong>Méditée</strong> — Enregistre ou annule l’Heure comme méditée et met à jour votre progression.</span></div>
      </div></div>

      <div class="help-section" id="help-actions"><div class="help-section-hd">Surligner, noter et copier</div><div class="help-section-body">
        <div class="help-note"><strong>Trois modèles distincts :</strong> sur iPhone/iPad et les appareils compatibles, sélectionnez précisément les mots ; sur Samsung/Android lorsque <strong>Paragraphe</strong> est proposé, le surlignage porte sur le paragraphe entier ; dans Approfondir, <strong>Surligner le titre</strong> marque la lecture entière tout en colorant visuellement le texte du titre.</div>
        <div class="help-row"><span class="help-icon">◐</span><span class="help-row-text"><strong>Surligner un passage</strong> — Ouvre la palette Jaune · Bleu · Vert · Violet · Rose. Les passages surlignés sont sauvegardés et apparaissent dans Mon Espace.</span></div>
        <div class="help-row"><span class="help-icon">✎</span><span class="help-row-text"><strong>Note</strong> — Une note est rattachée au paragraphe, même si quelques mots seulement étaient sélectionnés. Plusieurs notes peuvent être enregistrées sur le même paragraphe, chacune jusqu’à 2 000 caractères.</span></div>
        <div class="help-row"><span class="help-icon">⎘</span><span class="help-row-text"><strong>Copier</strong> — Copie le texte sélectionné, ou le paragraphe ciblé, avec sa référence lisible.</span></div>
        <div class="help-row"><span class="help-icon">🎨</span><span class="help-row-text"><strong>Modifier ou supprimer un passage surligné</strong> — Touchez/cliquez le surlignage existant, choisissez une autre couleur ou <strong>✕ Supprimer le surlignage</strong>. Après suppression, <strong>Annuler</strong> reste disponible temporairement.</span></div>
      </div></div>

      <div class="help-section" id="help-title-mark"><div class="help-section-hd">Marquer une lecture dans Approfondir</div><div class="help-section-body">
        <div class="help-row"><span class="help-icon">▰</span><span class="help-row-text"><strong>Surligner le titre</strong> — Choisissez l’une des cinq couleurs. Le surlignage suit les lignes du texte du titre comme un surlignage de passage, mais le repère enregistré concerne la <strong>lecture entière</strong> et reste indépendant des passages surlignés dans son contenu.</span></div>
        <div class="help-row"><span class="help-icon">🎨</span><span class="help-row-text"><strong>Changer la couleur ou supprimer</strong> — Touchez directement le titre déjà surligné, ou utilisez <strong>Modifier / retirer le surlignage</strong>. La palette indique la couleur actuelle et propose <strong>✕ Supprimer le surlignage</strong>.</span></div>
        <div class="help-row"><span class="help-icon">↶</span><span class="help-row-text"><strong>Annuler</strong> — Après une suppression réussie, Annuler restaure temporairement le repère et sa couleur précédente.</span></div>
        <div class="help-row"><span class="help-icon">▤</span><span class="help-row-text"><strong>Lectures marquées</strong> — Le repère apparaît dans <strong>Mon Espace → Lectures marquées</strong>. Ouvrir cet élément rouvre la lecture complète au début.</span></div>
      </div></div>

      <div class="help-section" id="help-notes"><div class="help-section-hd">Notes</div><div class="help-section-body">
        <div class="help-step"><span class="help-step-n">1</span><span class="help-step-text">Ouvrez <strong>Note</strong> depuis le passage concerné.</span></div>
        <div class="help-step"><span class="help-step-n">2</span><span class="help-step-text">Écrivez jusqu’à <strong>2 000 caractères</strong> puis appuyez sur <strong>Enregistrer</strong>.</span></div>
        <div class="help-step"><span class="help-step-n">3</span><span class="help-step-text">Retrouvez la note dans la fiche du paragraphe et dans <strong>Mon Espace → Notes</strong>.</span></div>
        <div class="help-step"><span class="help-step-n">4</span><span class="help-step-text">Pour supprimer une note, utilisez <strong>✕</strong>. Après suppression, <strong>Annuler</strong> reste disponible temporairement.</span></div>
      </div></div>

      <div class="help-section" id="help-samsung"><div class="help-section-hd">Samsung / Android</div><div class="help-section-body">
        <div class="help-row"><span class="help-icon">◐</span><span class="help-row-text"><strong>Paragraphe</strong> — Sur les appareils Android/Samsung où ce mode est pris en charge, activez <strong>Paragraphe</strong> puis touchez le paragraphe à traiter.</span></div>
        <div class="help-note">Dans ce mode, le surlignage coloré porte sur le paragraphe entier afin d’éviter les menus Recherche/Traduction déclenchés par la sélection native. Sur iPhone/iPad, la sélection exacte des mots reste la méthode prévue.</div>
      </div></div>

      <div class="help-section" id="help-reperes"><div class="help-section-hd">Repères, paroles directes, taille et thème</div><div class="help-section-body">
        <div class="help-row"><span class="help-icon">#</span><span class="help-row-text"><strong>Repères</strong> — Affiche ou masque les indications techniques : numéros de paragraphe, références source et badges d’attribution Jésus / Père / Marie.</span></div>
        <div class="help-row"><span class="help-icon">✝</span><span class="help-row-text"><strong>Paroles directes</strong> — Les paroles identifiées de Jésus, du Père et de Marie sont distinguées dans le texte et peuvent être recherchées via le filtre Paroles directes. Si un texte ou une attribution vous semble incorrect, utilisez <strong>Signaler un problème de texte</strong>.</span></div>
        <div class="help-row"><span class="help-icon">A</span><span class="help-row-text"><strong>Taille du texte</strong> — Petit 16 px · Normal 19 px · Grand 22 px · Très grand 26 px.</span></div>
        <div class="help-row"><span class="help-icon">◒</span><span class="help-row-text"><strong>Affichage</strong> — Automatique suit le thème de l’appareil ; Clair et Sombre imposent le thème choisi.</span></div>
      </div></div>

      <div class="help-section" id="help-search"><div class="help-section-hd">Recherche</div><div class="help-section-body">
        <div class="help-row"><span class="help-icon">🔍</span><span class="help-row-text">Tapez un mot ou une expression puis utilisez <strong>Tout · Heures · Réflexions · Prières · Compléments · Paroles directes</strong>. Les résultats ouvrent le contenu correspondant et, lorsque l’ancre existe, le passage concerné.</span></div>
        <div class="help-row"><span class="help-icon">✝</span><span class="help-row-text"><strong>Paroles directes</strong> peut aussi afficher les paroles identifiées sans texte saisi et filtrer <strong>Tous · Jésus · Père · Marie</strong>.</span></div>
      </div></div>

      <div class="help-section" id="help-espace"><div class="help-section-hd">Mon Espace</div><div class="help-section-body">
        <div class="help-row"><span class="help-icon">▶</span><span class="help-row-text"><strong>Position de lecture</strong> — Lorsqu’une position est enregistrée, <strong>Reprendre</strong> rouvre l’Heure à cette position, <strong>Ouvrir au début</strong> ouvre l’Heure au début et <strong>Effacer cette position</strong> supprime cette reprise enregistrée.</span></div>
        <div class="help-row"><span class="help-icon">📊</span><span class="help-row-text"><strong>Progression</strong> — Voir les Heures méditées et gérer le cycle.</span></div>
        <div class="help-row"><span class="help-icon">🖍</span><span class="help-row-text"><strong>Surlignages / Passages à vérifier / Notes / Lectures marquées</strong> — Ouvrez un élément pour revenir au passage ou à la lecture concernée.</span></div>
      </div></div>

      <div class="help-section" id="help-backup"><div class="help-section-hd">Sauvegarder et restaurer</div><div class="help-section-body">
        <div class="help-row"><span class="help-icon">⬇</span><span class="help-row-text"><strong>Exporter la sauvegarde JSON</strong> — Format destiné à restaurer vos données dans l’app. Il contient, lorsqu’ils sont présents, progression, positions de lecture, réglages, surlignages de passages, notes et <strong>Lectures marquées</strong>.</span></div>
        <div class="help-row"><span class="help-icon">⬆</span><span class="help-row-text"><strong>Importer</strong> — Remplace vos données actuelles par celles d’une sauvegarde 24 Heures compatible, après confirmation.</span></div>
        <div class="help-row"><span class="help-icon">↗</span><span class="help-row-text"><strong>Journal lisible</strong> — Le fichier Markdown contient progression, surlignages, notes et <strong>Lectures marquées</strong>. Il est destiné à la lecture et <strong>ne peut pas être importé</strong> comme sauvegarde.</span></div>
        <div class="help-note"><strong>Important :</strong> vos données personnelles sont enregistrées localement lorsque le stockage de l’appareil/navigateur est disponible. Créez une sauvegarde JSON avant de supprimer ou réinstaller l’app, d’effacer les données du navigateur/site ou de changer d’appareil.</div>
      </div></div>

      <div class="help-section" id="help-practice"><div class="help-section-hd">Comment pratiquer et progression</div><div class="help-section-body">
        <div class="help-row"><span class="help-icon">✝</span><span class="help-row-text"><strong>Parcours conseillé</strong> — Prier une Heure par jour, dans l’ordre, puis continuer l’Heure suivante. Vous pouvez aussi choisir une Heure selon le moment de la journée ou parcourir librement les Heures.</span></div>
        <div class="help-row"><span class="help-icon">📖</span><span class="help-row-text"><strong>Comment pratiquer</strong> ouvre le texte détaillé des différentes manières de pratiquer les Heures.</span></div>
        <div class="help-row"><span class="help-icon">↺</span><span class="help-row-text"><strong>Nouveau cycle</strong> — Après un cycle accompli, utilisez Recommencer. Une réinitialisation en cours demande confirmation.</span></div>
      </div></div>

      <div class="help-section" id="help-update"><div class="help-section-hd">Mise à jour de l’app</div><div class="help-section-body">
        <div class="help-row"><span class="help-icon">↻</span><span class="help-row-text">Lorsqu’une nouvelle version est détectée, une bannière peut proposer <strong>Actualiser</strong>. Appuyez dessus pour demander le chargement de la nouvelle version.</span></div>
        <div class="help-row"><span class="help-icon">✎</span><span class="help-row-text">Une note non enregistrée ouverte bloque l’actualisation afin d’éviter de perdre le brouillon : enregistrez ou fermez d’abord la note.</span></div>
        <div class="help-row"><span class="help-icon">⌕</span><span class="help-row-text"><strong>Rechercher une mise à jour</strong> lance une vérification manuelle. Hors ligne ou si le serveur ne répond pas, cette vérification peut être momentanément impossible.</span></div>
        <div class="help-row"><span class="help-icon">↺</span><span class="help-row-text">Si la bannière de mise à jour reste affichée après <strong>Actualiser</strong>, fermez complètement l’app puis rouvrez-la avant de signaler le problème.</span></div>
        <button class="integrity-btn" onclick="manualUpdateCheck()">↻ Rechercher une mise à jour</button>
      </div></div>

      <div class="help-section" id="help-support"><div class="help-section-hd">Assistance, liens et confidentialité</div><div class="help-section-body">
        <div class="help-row"><span class="help-icon">!</span><span class="help-row-text"><strong>Signaler un problème de texte</strong> copie un rapport avec version, empreinte du corpus, route, Heure/onglet quand applicable, ID stable et référence source disponible. Ajoutez vous-même la description du problème.</span></div>
        <div class="help-row"><span class="help-icon">⌘</span><span class="help-row-text"><strong>Copier les diagnostics</strong> copie des informations techniques utiles au dépannage.</span></div>
        <div class="help-note"><strong>Vie privée :</strong> Partager, Copier le lien, Signaler un problème de texte et Diagnostics n’ajoutent pas automatiquement le contenu de vos notes ni celui de vos surlignages personnels.</div>
        <button class="integrity-btn" onclick="copyTextIssueReport()">! Signaler un problème de texte</button>
        <button class="integrity-btn" onclick="copyDiagnostics()">⌘ Copier les diagnostics</button>
      </div></div>

      <div class="help-section" id="help-about"><div class="help-section-hd">À propos</div><div class="help-section-body">
        <div class="help-row"><span class="help-icon">✦</span><span class="help-row-text"><strong>Version :</strong> ${escHtml(APP_VERSION)}</span></div>
        <div class="help-row"><span class="help-icon">📚</span><span class="help-row-text"><strong>Source principale du corpus :</strong> ${escHtml(sourceEdition)}</span></div>
        <div class="help-row"><span class="help-icon">#</span><span class="help-row-text"><strong>Empreinte corpus :</strong> <code>${escHtml(fp.slice(0,16))}</code></span></div>
        <div class="help-note">Vos notes, surlignages, Lectures marquées, progression et positions de lecture sont des données personnelles conservées localement lorsque le stockage de l’appareil/navigateur est disponible. Utilisez la sauvegarde JSON pour les restaurer.</div>
      </div></div>

      </div>
    </div>`;
  document.body.appendChild(overlay);
  document.body.style.overflow = 'hidden';
  const modal = overlay.querySelector('.help-modal');
  if (modal) installFocusTrap(modal, closeHelpModal, { returnFocusTo: helpReturnFocus });
}
'''
 s=s[:hs]+newhelp+s[he:]
 # Version identity.
 s=replace1(s,"const APP_VERSION = 'v101.85';","const APP_VERSION = 'v101.86';",'version app')
 s=replace1(s,"const BUILD_DATE = '2026-08-18'; // v101.85 / user-feedback corrective: UF-17, UF-15, library title marks","const BUILD_DATE = '2026-08-19'; // v101.86 / title-highlight UX + Aide/À propos reconciliation",'build date')
 s=s.replace('/* v101.85 — Approfondir title / whole-reading marker. Independent of character-offset highlights. */','/* v101.86 — Approfondir whole-reading marker presented with body-style inline title highlighting. */',1)
 s=s.replace('<!-- v101.85 — dedicated whole-reading/title marker picker. Kept separate from text selection and Samsung paragraph mode. -->','<!-- v101.86 — whole-reading/title marker picker; same visual colour language as body highlights, separate persistence model. -->',1)
 return s


def patch_active_qa(stage):
 mdp=stage/'REAL_DEVICE_QA_CHECKLIST.md'; csvp=stage/'REAL_DEVICE_QA_RESULTS_TEMPLATE.csv'
 md=mdp.read_text('utf-8')
 exact={
 '# 24H interaction closure / v101.85 — physical device, installed-PWA and live-origin checklist':'# 24H interaction closure / v101.86 TH1 — physical device, installed-PWA and live-origin checklist',
 'Use the exact v101.85 candidate bytes. Record PASS/FAIL/NOT_TESTED for every numbered scenario.':'Use the exact v101.86 TH1 candidate bytes. Record PASS/FAIL/NOT_TESTED for every numbered scenario.',
 'Existing installed build → v101.85 update preserves notes, coloured highlights, reading position and progress; obsolete legacy ◈ marks may be discarded.':'Existing installed build → v101.86 update preserves notes, coloured highlights, Lectures marquées, reading position and progress; obsolete legacy ◈ marks may be discarded.',
 '33. Visible version v101.85.':'33. Visible version v101.86.',
 '35. Cache generation is luisa-24h-v101-84.':'35. Cache generation is luisa-24h-v101-86.',
 '36. Existing install updates to v101.85 without loss of supported personal data; retired legacy ◈ marks are intentionally not preserved.':'36. Existing install updates to v101.86 without loss of supported personal data, including Lectures marquées; retired legacy ◈ marks are intentionally not preserved.',
 '41. A canonical snapshot with `snapshot_version` greater than 4 remains byte-for-byte unchanged after boot, even when legacy mirrors and the R41 marker are absent.':'41. A canonical snapshot with `snapshot_version` greater than 5 remains byte-for-byte unchanged after boot, even when legacy mirrors and the R41 marker are absent.',
 '67. Help attribution-status honesty: open Aide → Recherche and À propos du corpus; confirm it does NOT say the direct-speech review is still pending, and states that the editorial review of the current attribution layer is already closed.':'67. Help attribution-status honesty: open Aide and confirm it does not claim that direct-speech editorial review is pending or already closed; it describes identified words of Jésus, du Père et de Marie factually and retains the text-problem reporting path.',
 '74. Export a backup containing a highlight, import it into the same v101.85 build, and confirm the highlight still carries valid `text_hash`, `para_hash` and `paragraph_fingerprint` integrity metadata and renders at the same passage.':'74. Export a backup containing a highlight, import it into the same v101.86 build, and confirm the highlight still carries valid `text_hash`, `para_hash` and `paragraph_fingerprint` integrity metadata and renders at the same passage.',
 '## v101.85 user-feedback additions':'## v101.86 user-feedback and TH1 additions',
 '80. Export/import a v101.85 backup and confirm title marks survive; import an older schema-7/snapshot-4 backup and confirm existing data survives with no title marks invented.':'80. Export/import a v101.86 backup and confirm title marks survive; import an older schema-7/snapshot-4 backup and confirm existing data survives with no title marks invented.'
 }
 for old,new in exact.items():
  if md.count(old)!=1: die('active QA markdown expected exact row missing: '+old[:80])
  md=md.replace(old,new,1)
 append = (
 "\n81. Approfondir title visual: on a narrow phone viewport and with a long wrapped title, marking the reading colours only the title text fragments (inline highlighter effect), not the full heading rectangle.\n"
 "82. Direct title interaction: tap/click the highlighted title itself; the colour picker opens and the current colour is visibly selected.\n"
 "83. Recolour/remove/Undo: change the title colour, remove it directly from the title picker, then use Annuler and confirm the exact previous colour returns in the reader and Mon Espace.\n"
 "84. Keyboard/accessibility: on desktop, Enter and Space on a highlighted Approfondir title open the picker; Escape closes it and focus remains usable.\n"
 "85. Aide TH1 truth: confirm the 9-action “Que voulez-vous faire ?” navigation works, the source is GE / Lumen Luminis / septembre 2021, Lectures marquées/JSON/journal/local-data/update guidance is present, and no unsupported “review pending/closed” certification claim appears.\n"
 )
 if '81. Approfondir title visual:' in md: die('active QA markdown TH1 rows already present unexpectedly')
 md=md.rstrip()+append
 mdp.write_text(md,'utf-8')
 txt=csvp.read_text('utf-8')
 reps={
 'iPhone,G-13,Existing installed build → v101.85 update preserves supported personal data; obsolete legacy ◈ marks may be discarded.,NOT_TESTED,,':'iPhone,G-13,Existing installed build → v101.86 update preserves supported personal data including Lectures marquées; obsolete legacy ◈ marks may be discarded.,NOT_TESTED,,',
 'Live/Installed PWA,G-33,Visible version v101.85.,NOT_TESTED,,':'Live/Installed PWA,G-33,Visible version v101.86.,NOT_TESTED,,',
 'Live/Installed PWA,G-35,Cache generation is luisa-24h-v101-84.,NOT_TESTED,,':'Live/Installed PWA,G-35,Cache generation is luisa-24h-v101-86.,NOT_TESTED,,',
 'Live/Installed PWA,G-36,Existing install updates to v101.85 without loss of supported personal data; retired legacy ◈ marks are not preserved.,NOT_TESTED,,':'Live/Installed PWA,G-36,Existing install updates to v101.86 without loss of supported personal data including Lectures marquées; retired legacy ◈ marks are not preserved.,NOT_TESTED,,',
 'Data safety,G-41,"A canonical snapshot with `snapshot_version` greater than 4 remains byte-for-byte unchanged after boot, even when legacy mirrors and the R41 marker are absent.",NOT_TESTED,,':'Data safety,G-41,"A canonical snapshot with `snapshot_version` greater than 5 remains byte-for-byte unchanged after boot, even when legacy mirrors and the R41 marker are absent.",NOT_TESTED,,',
 'Help,G-67,Help attribution-status honesty: no stale pending-review wording; Aide states the current direct-speech attribution review is already closed.,NOT_TESTED,,':'Help,G-67,Help attribution-status honesty: Aide makes no unsupported pending/closed editorial-certification claim; identified direct words are described factually and reporting remains available.,NOT_TESTED,,',
 'User feedback,G-80,v101.85 backup round-trip preserves title marks and schema-7/snapshot-4 migration preserves prior data.,NOT_TESTED,,':'User feedback,G-80,v101.86 backup round-trip preserves title marks and schema-7/snapshot-4 migration preserves prior data.,NOT_TESTED,,'
 }
 for old,new in reps.items():
  if txt.count(old)!=1: die('active QA CSV expected row missing: '+old[:90])
  txt=txt.replace(old,new,1)
 extra=(
 'TH1 title UX,G-81,"Approfondir long wrapped title uses inline text-following highlight, not a full heading rectangle.",NOT_TESTED,,\n'
 'TH1 title UX,G-82,Tap/click highlighted title opens picker and current colour is visibly selected.,NOT_TESTED,,\n'
 'TH1 title UX,G-83,Direct recolour/remove/Annuler restores the exact previous title colour in reader and Mon Espace.,NOT_TESTED,,\n'
 'TH1 title UX,G-84,Desktop Enter/Space on highlighted title opens picker; Escape closes it with usable focus.,NOT_TESTED,,\n'
 'Help,G-85,"Aide 9-action quick navigation, source edition, Lectures marquées/backup/journal/local-data/update guidance are correct and no unsupported pending/closed review claim appears.",NOT_TESTED,,\n'
 )
 if 'G-81' in txt: die('active QA CSV TH1 rows already present unexpectedly')
 txt=txt.rstrip()+"\n"+extra
 csvp.write_text(txt,'utf-8')
 import csv as _csv, io as _io
 rows=list(_csv.DictReader(_io.StringIO(txt)))
 ids=[r['scenario_id'] for r in rows]
 mdids=re.findall(r'(?m)^(\d+)\.',md)
 expected=[f'G-{int(n):02d}' for n in mdids]
 if len(ids)!=len(set(ids)) or ids!=expected: die('active QA scenario parity/uniqueness failure')
 badstrings=['Visible version v101.85','luisa-24h-v101-84','updates to v101.85','same v101.85 build','Export/import a v101.85 backup','greater than 4','review is already closed','states that the editorial review of the current attribution layer is already closed']
 for b in badstrings:
  if b in md or b in txt: die('stale active QA assertion remains: '+b)
 required=['Visible version v101.86','luisa-24h-v101-86','greater than 5','G-85','GE / Lumen Luminis / septembre 2021']
 joined=md+'\n'+txt
 if not all(x in joined for x in required): die('active QA required current assertion missing')
 return {'scenarios':len(ids),'first':ids[0],'last':ids[-1],'md_sha256':hf(mdp),'csv_sha256':hf(csvp)}

def prepare(outroot):
 stage=outroot/'staging';s,gates,prot=preflight(stage)
 qa=patch_active_qa(stage)
 base_s=s
 # purge superseded generated evidence, keep historical README lineage and static assets.
 for rel in ['audit/independent_four_pass_audit.md','reports/full_regression_matrix.csv','reports/runtime_behaviour_matrix.csv','reports/help_claim_ledger.csv','reports/pass3_claim_ledger.csv','reports/pass4_contradiction_stale_scan.txt','reports/report_claims_vs_evidence_audit.md','reports/stale_reference_scan.txt','metadata/hash_manifest.json','metadata/package_manifest.json','metadata/final_decision_lock.json','metadata/build_provenance.json','metadata/auditor_provenance.json']:
  p=stage/rel
  if p.exists():p.unlink()
 shutil.rmtree(stage/'scripts',ignore_errors=True);(stage/'scripts').mkdir(parents=True,exist_ok=True)
 for p in [GOV,RUNTIME_GOV,THIS,FOUR,REOPEN,IREOPEN]:shutil.copy2(p,stage/'scripts'/p.name)
 (stage/'audit').mkdir(exist_ok=True);(stage/'reports').mkdir(exist_ok=True);(stage/'metadata').mkdir(exist_ok=True)
 # patch runtime once, twin copy.
 s=patch_runtime(s)
 (stage/'index.html').write_text(s,'utf-8');(stage/'luisa_24_heures.html').write_text(s,'utf-8')
 # protected gate immediately after patch.
 postprot=protect_fingerprints(s)
 if prot!=postprot:die('protected data drift after runtime patch')
 if 'const STORAGE_SCHEMA_VERSION=8;' not in s or 'const PERSONAL_SNAPSHOT_VERSION = 5;' not in s:die('schema/snapshot drift')
 # version/package facing files.
 sw=stage/'sw.js';ws=sw.read_text('utf-8');ws=ws.replace('/* v101.85 */','/* v101.86 */',1).replace("const CACHE_NAME = 'luisa-24h-v101-85';","const CACHE_NAME = 'luisa-24h-v101-86';",1);sw.write_text(ws,'utf-8')
 v=json.loads((stage/'version.json').read_text('utf-8'));v['app_version']='v101.86';v['build_date']=BUILD_DATE;v['evidence_stage']='24H-TITLE-HELP-TH1-R2-AUDIT-RECONCILED';v['status']='PREPUBLIC_TITLE_HELP_R2_AUDIT_RECONCILED_EXTERNAL_GATES_PENDING';v['real_device_status']='Static/browser/package validation only until final audits pass; exact v101.86 iPhone/iPad/Samsung, installed-PWA/offline/live-origin, assistive-technology and rollback certification remain NOT_TESTED.';(stage/'version.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
 m=json.loads((stage/'manifest.json').read_text('utf-8'));m['version']='v101.86';(stage/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n','utf-8')
 readme=(stage/'README.md').read_text('utf-8');readme=readme.replace('Version: `v101.85`','Version: `v101.86`',1);note='''\n## v101.86 — Stage TH1 title-highlight UX + Aide/À propos reconciliation (19 August 2026)\n\n- Approfondir title markers keep the stable `libraryMarks` whole-reading model but now render with the same inline `mark.hl-*` visual treatment as body highlights.\n- Marked titles are directly keyboard/touch editable; current colour is exposed in the picker; recolour/remove/Undo remain durable.\n- Aide/À propos is reconciled to current runtime truth, adds task-oriented jumps, Lectures marquées/backup/journal/source-edition/platform/update guidance, and removes the unsupported “editorial review closed” statement.\n- Storage schema remains 8; personal snapshot remains 5; all protected devotional/corpus/speech structures are unchanged.\n- Physical-device/PWA/AT/live/rollback gates remain external NOT_TESTED.\n\n## v101.85 — superseded baseline lineage\n''';
 r2note='''
## v101.86 — TH1-R2 audit reconciliation (19 August 2026)

- Runtime HTML remains byte-identical to TH1-R1.
- Active physical-device/live QA checklist and results template are reconciled to v101.86/schema 8/snapshot 5/current cache/title-highlight Help truth.
- Pass 4 now treats stale current-facing claims inside active QA artifacts as blocking rather than historical provenance.
- Five explicit TH1 title/help physical QA scenarios are added.

'''
 marker='Version: `v101.86`\n';readme=readme.replace(marker,marker+r2note+note,1);(stage/'README.md').write_text(readme,'utf-8')
 # direct static gates per fix.
 static={
  'TH1-01_inline_mark_css':'mark.library-title-inline-mark' in s and '.library-title-mark-yellow' not in s,
  'TH1-01_reader_h2_uncolored':'class="reader-title">${renderLibraryReaderTitleInner(item)}' in s,
  'TH1-02_direct_title_control':'role="button" tabindex="0"' in s and 'handleLibraryTitleMarkKeydown' in s,
  'TH1-02_current_color_semantics':'data-library-marker-color' in s and "aria-pressed', mark && btn.dataset.libraryMarkerColor===mark.color" in s,
  'TH1-02_remove_wording':'✕ Supprimer le surlignage</button>' in s,
  'TH1-03_quick_nav':"Que voulez-vous faire ?" in s and 'function helpJumpTo' in s,
  'TH1-04_source_dynamic':"const sourceEdition = CORPUS.source_edition" in s,
  'TH1-04_no_closed_claim':'revue éditoriale de la couche d’attribution des paroles directes du corpus actuel est déjà clôturée' not in s,
  'TH1-04_librarymarks_help':'JSON' in s and 'Lectures marquées' in s,
  'version_v10186':"const APP_VERSION = 'v101.86';" in s,
 }
 if not all(static.values()):die('static per-fix gate '+repr([k for k,v in static.items() if not v]))
 # Build reports that do not overclaim browser/independent gates.
 with (stage/'reports/no_regression_fix_ledger.csv').open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=['item','status','changed_files','evidence','redo_count']);w.writeheader();
  w.writerows([
   {'item':'TH1-01','status':'PASS_STATIC','changed_files':'index.html; luisa_24_heures.html','evidence':'inline mark.hl-* renderer; H2 no colour class; protected fingerprints unchanged','redo_count':'0'},
   {'item':'TH1-02','status':'PASS_STATIC','changed_files':'index.html; luisa_24_heures.html','evidence':'direct click/keyboard handler, picker aria-pressed current colour, recolour/remove/Undo paths preserved','redo_count':'0'},
   {'item':'TH1-03','status':'PASS_STATIC','changed_files':'index.html; luisa_24_heures.html','evidence':'task-oriented Help jump controls and target IDs added','redo_count':'0'},
   {'item':'TH1-04','status':'PASS_STATIC','changed_files':'index.html; luisa_24_heures.html','evidence':'Help factual reconciliation incl dynamic source edition, Lectures marquées backup/journal, platform/update/data safety; unsupported closed-review claim removed','redo_count':'0'},
  ])
 (stage/'reports/root_deploy_consistency_report.md').write_text(f'# Runtime twin consistency\n\n`index.html` and `luisa_24_heures.html` are byte-identical after TH1 patch. SHA-256: `{hf(stage/"index.html")}`. This package layout has no separate deploy folder.\n','utf-8')
 (stage/'reports/nested_zip_consistency_report.md').write_text('# Nested ZIP consistency\n\nNo nested ZIP is present in the staging tree; nested package comparison is not applicable.\n','utf-8')
 prov={'target_version':APP_VERSION,'build_date':BUILD_DATE,'baseline_zip':BASE.name,'baseline_sha256':BASE_SHA,'baseline_runtime_sha256':BASE_RUNTIME_SHA,'governing_script_sha256':hf(GOV),'runtime_stage_script_sha256':hf(RUNTIME_GOV),'build_script_sha256':hf(THIS),'protected_before':prot,'protected_after':postprot,'storage_schema':8,'personal_snapshot':5,'preflight_gates':gates,'static_fix_gates':static,'active_qa_reconciliation':qa,'change_scope':['title marker presentation/interaction','Help/A propos','version/cache metadata'],'explicitly_not_changed':PROTECTED+['storage schema','personal snapshot']}
 (stage/'metadata/build_provenance.json').write_text(json.dumps(prov,ensure_ascii=False,indent=2)+'\n','utf-8')
 ap={'governing_script':GOV.name,'governing_script_sha256':hf(GOV),'runtime_stage_script':RUNTIME_GOV.name,'runtime_stage_script_sha256':hf(RUNTIME_GOV),'build_script':THIS.name,'build_script_sha256':hf(THIS),'independent_four_pass_auditor':FOUR.name,'independent_four_pass_auditor_sha256':hf(FOUR),'final_reopen_auditor':REOPEN.name,'final_reopen_auditor_sha256':hf(REOPEN),'independent_reopen_auditor':IREOPEN.name,'independent_reopen_auditor_sha256':hf(IREOPEN)}
 (stage/'metadata/auditor_provenance.json').write_text(json.dumps(ap,ensure_ascii=False,indent=2)+'\n','utf-8')
 receipt={'status':'PREPARED','runtime_sha256':hf(stage/'index.html'),'protected':postprot,'members':sum(1 for p in stage.rglob('*') if p.is_file())}
 (outroot/'prepare_receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(receipt,indent=2))

def deterministic_zip(root,zpath):
 files=sorted([p for p in root.rglob('*') if p.is_file()],key=lambda p:p.relative_to(root).as_posix())
 with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for p in files:
   rel=p.relative_to(root).as_posix();info=zipfile.ZipInfo(rel,date_time=(2026,8,19,12,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=(0o100644<<16);z.writestr(info,p.read_bytes())

def finalize(outroot,zpath):
 stage=outroot/'staging'
 req=['audit/independent_four_pass_audit.md','reports/runtime_behaviour_matrix.csv','reports/full_regression_matrix.csv','reports/help_claim_ledger.csv','reports/pass3_claim_ledger.csv','reports/pass4_contradiction_stale_scan.txt','reports/report_claims_vs_evidence_audit.md','reports/stale_reference_scan.txt']
 miss=[x for x in req if not (stage/x).exists()]
 if miss:die('independent evidence missing '+repr(miss))
 four=(stage/'audit/independent_four_pass_audit.md').read_text('utf-8')
 if 'FOUR_PASS_PREPACKAGE_GATE = PASS' not in four:die('independent four-pass not PASS')
 # runtime protected and twins again.
 if (stage/'index.html').read_bytes()!=(stage/'luisa_24_heures.html').read_bytes():die('runtime twins diverged')
 s=(stage/'index.html').read_text('utf-8');bp=json.loads((stage/'metadata/build_provenance.json').read_text('utf-8'))
 if protect_fingerprints(s)!=bp['protected_before']:die('protected data drift before packaging')
 # prepackage decision metadata is honest; postpackage final lock will be outside immutable ZIP.
 lock={'app_version':APP_VERSION,'stage':'TH1-R2','prepackage_four_pass_gate':'PASS','final_package_reopen_gate':'REQUIRED_POSTPACKAGE','independent_reopen_gate':'REQUIRED_POSTPACKAGE','final_status':'PENDING_POSTPACKAGE_AUDITS','public_release_ready':False,'external_gates_not_tested':['PHYSICAL-IPHONE','PHYSICAL-IPAD','PHYSICAL-SAMSUNG','PWA-MIGRATION-OFFLINE','H6-IOS-OVERSCROLL','VOICEOVER','TALKBACK','NVDA','CONSTRAINED-PERFORMANCE','LIVE-V10186-BYTE-BINDING','VERIFIED-ROLLBACK']}
 (stage/'metadata/final_decision_lock.json').write_text(json.dumps(lock,ensure_ascii=False,indent=2)+'\n','utf-8')
 # manifests last; hash_manifest excludes both manifests, package_manifest excludes itself.
 allfiles=lambda:sorted([p for p in stage.rglob('*') if p.is_file()],key=lambda p:p.relative_to(stage).as_posix())
 scope=[p for p in allfiles() if p.relative_to(stage).as_posix() not in ['metadata/hash_manifest.json','metadata/package_manifest.json']]
 hm={'algorithm':'sha256','files':[{'path':p.relative_to(stage).as_posix(),'sha256':hf(p),'bytes':p.stat().st_size} for p in scope]};(stage/'metadata/hash_manifest.json').write_text(json.dumps(hm,ensure_ascii=False,indent=2)+'\n','utf-8')
 scope=[p for p in allfiles() if p.relative_to(stage).as_posix()!='metadata/package_manifest.json']
 pm={'app_version':APP_VERSION,'stage':'TH1-R2','files':[{'path':p.relative_to(stage).as_posix(),'sha256':hf(p),'bytes':p.stat().st_size} for p in scope]};(stage/'metadata/package_manifest.json').write_text(json.dumps(pm,ensure_ascii=False,indent=2)+'\n','utf-8')
 deterministic_zip(stage,zpath)
 print(json.dumps({'status':'PACKAGED','zip':str(zpath),'sha256':hf(zpath),'bytes':zpath.stat().st_size,'members':len(zipfile.ZipFile(zpath).namelist()),'runtime_sha256':hf(stage/'index.html')},indent=2))

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['prepare','finalize']);ap.add_argument('--outroot',required=True);ap.add_argument('--zip');a=ap.parse_args();out=Path(a.outroot);out.mkdir(parents=True,exist_ok=True)
 if a.mode=='prepare':prepare(out)
 else:
  if not a.zip:die('--zip required')
  finalize(out,Path(a.zip))
