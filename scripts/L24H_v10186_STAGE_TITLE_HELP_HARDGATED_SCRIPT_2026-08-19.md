# 24 Heures de la Passion — v101.86 — Stage TH1
## Approfondir title-highlight UX repair + Aide/À propos reconciliation — hard-gated execution script

**Date:** 2026-08-19  
**Baseline authority:** `L24H_v10185_GITHUB_DEPLOY_USER_FEEDBACK_CORRECTED_HARDENED_R4_AUDIT_RECONCILED.zip`  
**Baseline ZIP SHA-256:** `09ef964e62dfe3005637c20b5a5fde0094bd9767a85ef6513582e81cb84d0ea5`  
**Baseline runtime HTML SHA-256:** `c43ff8934c12b24668c9c0cf55ebb12a9eb6ecd8ed265e68e4d78aaf0fd86050`  
**Target app version:** `v101.86`  
**Storage schema:** `8` — MUST NOT CHANGE  
**Personal snapshot:** `5` — MUST NOT CHANGE

---

# 0. Governing decision and stop rule

This stage is permitted only because the scope is fully determined by the current runtime and the user's accepted product intent:

1. `libraryMarks` remains the canonical **whole-reading marker** keyed by stable visible `TEXT_LIBRARY` item ID.
2. No character-offset title highlight is introduced.
3. The visible title marker must look like ordinary body highlighting: highlight follows the title text, including wrapped lines, rather than colouring the whole `<h2>` box.
4. A marked title itself must open the existing five-colour picker for recolour/removal; the explicit control remains available as a discoverable/accessibility fallback.
5. Aide/À propos must describe the final runtime truth, including Lectures marquées, backup/journal coverage, platform differences, reading-position actions, Prières & compléments, update recovery, source edition, local-data warning and neutral direct-speech wording.
6. No Word review pack is generated.

**STOP BEFORE MODIFICATION** if any of the following is found:

- baseline ZIP/hash/runtime identity mismatch;
- conflicting copies of the active runtime;
- missing current `libraryMarks` persistence/sanitizer/export/import/Undo support;
- missing source-edition evidence in the authoritative runtime;
- any need to choose new devotional wording, alter source text, speaker attribution, paragraph structure, or corpus meaning;
- any requirement to change storage schema/snapshot to achieve the scope;
- any ambiguity about whether a Help statement is supported by current runtime behaviour.

No modification may occur until all pre-modification gates pass.

---

# 1. Baseline freeze and inventory

Before changing any byte:

1. Verify baseline ZIP SHA-256 exactly.
2. Extract into a fresh staging directory.
3. Verify `index.html` and `luisa_24_heures.html` are byte-identical and match the baseline runtime hash.
4. Record file/member inventory and hashes.
5. Verify:
   - `APP_VERSION = 'v101.85'`;
   - `STORAGE_SCHEMA_VERSION = 8`;
   - `PERSONAL_SNAPSHOT_VERSION = 5`;
   - `CORPUS.source_edition = 'GE / Lumen Luminis / septembre 2021'`;
   - five permitted title-marker colours;
   - `libraryMarks` sanitizer, snapshot, durable local storage, Mon Espace, JSON export/import, Markdown journal and Undo paths exist.
6. Parse and fingerprint these protected runtime data constants:
   - `CORPUS`;
   - `TEXT_LIBRARY`;
   - `HOUR_LINKED_TEXTS`;
   - `SPEECH_DATA`;
   - `INTERNAL_SUBHEADINGS`;
   - `SPEECH_END_VISUAL_BREAKS`.

If any gate fails: **FAIL and STOP**.

---

# 2. Exact allowed scope

## TH1-01 — Approfondir title visual highlight

Change presentation only:

- preserve `libraryMarks` storage shape and semantics;
- preserve stable library item IDs;
- render a marked title using `mark.hl-{yellow|blue|green|purple|pink}` so the background follows the title glyph lines;
- do not place the colour class on the full `<h2>` container;
- no full-width title-card/background treatment;
- retain correct dark-mode highlight classes;
- keep placeholder badges outside the `<mark>`.

## TH1-02 — Direct edit/recolour/remove interaction

For a marked title:

- title mark has `role="button"`, `tabindex="0"` and explicit accessible label;
- click/tap opens the existing dedicated library-marker picker;
- Enter and Space open the picker;
- picker identifies the currently selected colour via `aria-pressed="true"` and a visible selected state;
- picker wording when marked: `Modifier le surlignage du titre`;
- removal wording: `✕ Supprimer le surlignage`;
- recolour is immediate and durable;
- remove is immediate and durable;
- Undo restores the exact prior colour/store;
- explicit fallback button remains and reads:
  - unmarked: `Surligner le titre`;
  - marked: `Modifier / retirer le surlignage`.

No title-marker persistence semantics may change.

## TH1-03 — Aide task navigation

At the top of Aide add a compact `Que voulez-vous faire ?` navigation area with buttons/links that jump within the Help modal to these existing factual domains:

- Commencer / reprendre une Heure;
- Surligner / noter;
- Marquer une lecture Approfondir;
- Mon Espace / retrouver mes éléments;
- Sauvegarder / restaurer;
- Samsung / Android;
- Rechercher;
- Mettre l’app à jour;
- Signaler un problème.

The jump must remain inside the Help modal and preserve keyboard/focus usability.

## TH1-04 — Aide/À propos factual reconciliation

Update Help so every statement is supported by current runtime evidence. It must explicitly cover:

1. **Approfondir title marker lifecycle**
   - five colours;
   - text-line visual highlight;
   - tap marked title to edit;
   - recolour;
   - remove;
   - Undo;
   - `Mon Espace → Lectures marquées`;
   - reopen complete reading at start;
   - independent of body passage highlights.

2. **Three highlighting models**
   - iPhone/iPad/compatible selection: exact selected-text highlight;
   - supported Samsung/Android paragraph mode: whole paragraph;
   - Approfondir title: whole-reading marker presented as a title-text highlight.

3. **Mon Espace**
   - Reprendre;
   - Ouvrir au début;
   - Effacer cette position;
   - Surlignages;
   - Passages à vérifier;
   - Notes;
   - Lectures marquées.

4. **Backup**
   - JSON backup includes progression, reading positions, settings, body highlights, notes and Lectures marquées when present;
   - JSON is the restoration format;
   - readable Markdown journal includes progression, highlights, notes and Lectures marquées but is not importable.

5. **Local-data safety**
   - data is stored locally when storage is available;
   - recommend JSON backup before deleting/reinstalling the app, clearing browser/site data or changing device.

6. **Prières & compléments**
   - explicitly describe the separate destination in Réglages/Parcours.

7. **Updates**
   - explain Actualiser when offered;
   - manual update check;
   - offline/server-unavailable limitation;
   - if an update banner persists after Actualiser, fully close and reopen the app before escalating.

8. **Direct words / Repères**
   - remove any unsupported statement that editorial review is “closed”;
   - factual wording only: identified direct words of Jésus/Père/Marie are distinguished/searchable;
   - Repères controls technical paragraph/source/speaker badges;
   - provide text-problem reporting route for suspected attribution/text issue.

9. **À propos**
   - dynamic app version;
   - dynamic `CORPUS.source_edition`;
   - corpus fingerprint;
   - concise local-data statement;
   - no internal audit/schema jargon shown to normal users.

No theological/editorial claim may be added.

---

# 3. Protected areas — zero-change requirement

The following are byte/semantic protected unless the stage stops for explicit user adjudication:

- all text and metadata inside `CORPUS`;
- all text and metadata inside `TEXT_LIBRARY`;
- `HOUR_LINKED_TEXTS`;
- `SPEECH_DATA` and all offsets;
- `INTERNAL_SUBHEADINGS`;
- `SPEECH_END_VISUAL_BREAKS`;
- paragraph IDs/order/stable refs;
- H15 correction;
- H17 visual-break correction;
- body text-highlighting storage/offset model;
- Samsung paragraph-highlight model;
- search corpus/index semantics;
- notes;
- progress logic;
- service-worker update mechanism except version/cache identity required by v101.86;
- personal storage schema 8 and snapshot 5.

Protected data hashes/counts must be compared before/after and in reopened ZIP.

---

# 4. Version/package changes allowed

Because user-visible runtime and Help change, update consistently to `v101.86`:

- `APP_VERSION`;
- `BUILD_DATE = '2026-08-19'`;
- `version.json`;
- `manifest.json` version;
- service-worker current version comment and `CACHE_NAME = 'luisa-24h-v101-86'`;
- README current-release section;
- current package/report metadata.

Historical version strings may remain only when explicitly classified as historical/compatibility/provenance evidence.

Do **not** bump storage schema or personal snapshot.

---

# 5. Mandatory per-fix cycle

For each TH1 item separately:

`PLAN → IMPLEMENT → DIFF → LINE-BY-LINE REVIEW → BUILD-SCRIPT COMPLIANCE → TARGETED TEST → MINI-REGRESSION → INDEPENDENT RECHECK → PASS OR REDO`

Do not proceed to the next item until the current item passes.

If any item fails:

1. stop;
2. diagnose exact failure;
3. correct or revert;
4. rerun the item gate from scratch;
5. record `redo_count`;
6. proceed only after PASS.

---

# 6. Targeted title-marker runtime tests

Execute real browser/runtime scenarios, not token-presence assertions:

1. unmarked title renders normal text and explicit `Surligner le titre` control;
2. each of five colours renders as an inline `<mark class="hl hl-COLOR">` inside the title;
3. full `<h2>` does not receive a colour/background class;
4. multi-line/narrow viewport title highlight follows text fragments, not full title-box width;
5. largest font setting remains usable;
6. light mode;
7. dark mode;
8. clicking/tapping marked title opens picker;
9. Enter opens picker;
10. Space opens picker;
11. current colour has selected state/`aria-pressed=true`;
12. recolour updates exact mark class and persisted store;
13. remove deletes marker;
14. Undo restores exact previous colour;
15. reload persists;
16. Mon Espace → Lectures marquées shows the reading;
17. opening from Mon Espace returns to the reading start;
18. remove from Mon Espace works and Undo works;
19. JSON export contains library mark;
20. current JSON import restores it;
21. schema-7/snapshot-4 compatible migration still restores it;
22. readable Markdown journal includes Lectures marquées;
23. invalid library ID rejected;
24. invalid colour rejected;
25. prototype-pollution payload rejected;
26. picker Escape/focus return works;
27. ordinary body highlight creation/recolour/remove unchanged;
28. Samsung paragraph-mode gate unchanged.

Physical iPhone/iPad/Samsung behaviour remains external NOT_TESTED unless actual device evidence exists.

---

# 7. Help truth audit

Create a Help claim ledger. For every user-facing factual statement in the active Help modal, record:

- section;
- exact/normalized claim;
- runtime evidence function/data/UI;
- evidence type;
- status `VERIFIED` or `FAIL`.

No factual Help claim may remain unsupported.

Specific mandatory assertions:

- `Lectures marquées` appears in Mon Espace Help;
- JSON backup explicitly lists Lectures marquées;
- Markdown journal explicitly lists Lectures marquées;
- source edition is rendered from `CORPUS.source_edition`;
- no “revue éditoriale … clôturée” claim remains;
- update persistent-banner recovery guidance exists;
- Prières & compléments destination exists and is documented;
- reading-position open-at-start/delete actions are documented only if runtime controls exist;
- all task-navigation targets resolve inside the Help modal.

---

# 8. Full regression/package gates

After all items pass:

- JavaScript syntax;
- service-worker syntax;
- root/twin HTML byte identity;
- 24 Hours count;
- prayer/section/library counts;
- all protected data hash/count parity;
- H15 exact wording;
- H17 contiguous `et` and break position 155;
- all speech targets/offsets/overlaps;
- all visual-break bounds/mid-word scan;
- search smoke tests;
- navigation/back-stack smoke tests;
- notes/highlights/progress smoke tests;
- backup/import smoke tests;
- sanitizers/prototype-pollution tests;
- Help modal focus trap/Escape;
- task-navigation anchor tests;
- accessibility semantics for title mark and picker;
- update/version/cache consistency;
- package manifest/hash manifest validation;
- required evidence files.

Regression matrix must show **0 FAIL**. Untested external gates must remain explicit `NOT_TESTED`.

---

# 9. Four-pass independent audit

A separately implemented auditor—not the build script—must run:

### Pass 1 — files vs governing/build script
Verify exact scope, protected hashes, versioning, changed files, script universe and provenance.

### Pass 2 — runtime/package behaviour
Rerun adversarial browser scenarios and package/runtime validation.

### Pass 3 — active reports line by line
Parse every line of every active report and compare each claim to current evidence. Any unsupported PASS/claim = `FAIL_REPORT_INTEGRITY`.

### Pass 4 — contradictions/stale claims/numbers/evidence
Recursive scan across root files, scripts, reports, metadata, app HTML and all package contents. Historical/compatibility references must be explicitly justified; any unjustified current stale claim = FAIL.

Do not package a PASS universe unless all four passes pass.

---

# 10. Deterministic packaging gate

Build the candidate twice independently from the same frozen baseline and same scripts.

- ZIP A SHA-256 must equal ZIP B SHA-256.
- Byte-for-byte equality required.
- No wall-clock/runtime-generated nondeterministic values may enter evidence files.

If hashes differ: FAIL, diagnose, correct, rebuild twice, and discard any prior reopen audit binding.

---

# 11. Mandatory final-package reopen gate

After writing the final ZIP:

1. reopen it from disk in a fresh directory;
2. test ZIP integrity/path safety/duplicate members;
3. recompute all hashes;
4. verify manifests against actual ZIP files;
5. verify runtime twins and version/cache metadata;
6. rebuild actual render target map;
7. validate all speech targets/offsets;
8. validate protected-data hashes/counts;
9. rerun title-marker browser scenarios;
10. rerun Help truth/anchor checks;
11. rerun stale-reference scan;
12. re-audit all report claims;
13. verify final decision lock does not overstate external tests.

If this gate is anything other than PASS, final status is FAIL and execution stops.

---

# 12. Separate independent reopened-ZIP audit

A separately implemented second auditor must reopen the same final ZIP from disk in another fresh directory and independently verify at least:

- ZIP SHA/member identity;
- required evidence universe;
- manifests/hashes;
- runtime twins/version/cache;
- protected data;
- title marker inline rendering/recolour/remove/Undo/persistence/Mon Espace/export-import;
- Help source edition/claims/task navigation;
- H15/H17/speech/visual-break regression;
- stale/current claim integrity;
- decision lock.

If this independent audit is not PASS, final status is FAIL.

---

# 13. Final decision lock

Use:

- `PASS` only if every critical static/runtime/package gate, deterministic rebuild, final reopened ZIP and independent reopened audit pass **and no critical external gate remains untested**;
- `LIMITED_PASS` if all package/static/browser/reopened gates pass but physical-device/PWA/AT/live/rollback evidence remains NOT_TESTED;
- `FAIL`, `FAIL_REPORT_INTEGRITY`, or `FAIL_EVIDENCE_MISSING` exactly when applicable.

Because the 11 external R4 gates are expected to remain untested in this execution, the maximum legitimate final status is expected to be `LIMITED_PASS`, unless new actual external evidence is supplied.

The assistant final response must match the final decision lock exactly.

---

# 14. Required final evidence artifacts

At minimum package/include:

- this governing script;
- executed build script;
- separately implemented four-pass auditor;
- primary reopen auditor;
- independent reopen auditor;
- `reports/no_regression_fix_ledger.csv`;
- `reports/full_regression_matrix.csv`;
- `reports/runtime_behaviour_matrix.csv`;
- `reports/help_claim_ledger.csv`;
- `reports/stale_reference_scan.txt`;
- `reports/root_deploy_consistency_report.md`;
- `reports/nested_zip_consistency_report.md`;
- `reports/report_claims_vs_evidence_audit.md`;
- `audit/independent_four_pass_audit.md`;
- `metadata/build_provenance.json`;
- `metadata/auditor_provenance.json`;
- `metadata/hash_manifest.json`;
- `metadata/package_manifest.json`;
- `metadata/final_decision_lock.json`.

No Word review pack may be generated.
