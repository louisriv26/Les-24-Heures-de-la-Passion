# 24 Heures de la Passion — v101.86 TH1-R2
## Four-pass audit reconciliation — active QA/evidence correction, runtime frozen

**Baseline runtime source:** `L24H_v10185_GITHUB_DEPLOY_USER_FEEDBACK_CORRECTED_HARDENED_R4_AUDIT_RECONCILED.zip`  
**Baseline source SHA-256:** `09ef964e62dfe3005637c20b5a5fde0094bd9767a85ef6513582e81cb84d0ea5`  
**R1 package under audit:** `L24H_v10186_GITHUB_DEPLOY_TITLE_HELP_HARDENED_R1.zip`  
**R1 SHA-256:** `c0947b99eebadb84b28a9897e83b4c30b2c6b3b9e59b6a7b777574ae691a90cb`  
**Runtime SHA-256 to preserve:** `dd9476f9bb56a2bd344e29a881f9c21666a2844f08175b27a693168449b3d49c`  
**Storage schema:** 8 — MUST NOT CHANGE  
**Personal snapshot:** 5 — MUST NOT CHANGE

## 0. Governing failure and stop rule

The four-pass re-audit found that R1 contains active QA artifacts that are stale and contradictory:

- `REAL_DEVICE_QA_CHECKLIST.md` is headed/instructed for v101.85;
- active live/PWA rows expect v101.85 and cache `luisa-24h-v101-84`;
- future-snapshot safety still says `snapshot_version > 4` although current snapshot is 5;
- Help QA row 67 requires the direct-speech editorial review to be described as "already closed", contradicting the v101.86 Help correction that deliberately removed that unsupported claim;
- `REAL_DEVICE_QA_RESULTS_TEMPLATE.csv` repeats the same stale current-facing claims;
- the stale-reference scanner incorrectly classified these active QA references as historical provenance.

Therefore R1 is `FAIL_REPORT_INTEGRITY` for the current four-pass request.

This stage is **evidence/QA-only**. If any runtime HTML, corpus, speech, storage schema, personal snapshot, or user-facing app behaviour changes, STOP and FAIL.

## 1. Exact allowed corrections

1. Update active QA checklist/template identity from v101.85 to v101.86.
2. Update expected current cache generation to `luisa-24h-v101-86`.
3. Update current future-snapshot threshold from `> 4` to `> 5`.
4. Replace Help attribution QA wording with the v101.86 factual rule: no pending/closed editorial-certification claim; Help describes identified direct words neutrally and retains the reporting path.
5. Update title-marker backup test identity from v101.85 to v101.86.
6. Add explicit physical/device QA rows for v101.86 TH1 title-marker UX:
   - inline highlight follows title text rather than whole heading box;
   - direct tap/click opens picker and exposes current colour;
   - recolour/remove/exact Undo;
   - long wrapped title at large font remains text-following;
   - Help quick navigation and source-edition/current factual wording.
7. Harden Pass 4 so any old/current mismatch inside `REAL_DEVICE_QA_CHECKLIST.md` or `REAL_DEVICE_QA_RESULTS_TEMPLATE.csv` is blocking unless the row is explicitly historical (e.g. v101.79/v101.53 migration fixture).
8. Expand Pass 1/Pass 2/final reopen evidence to verify QA checklist/template parity and current claims.
9. Preserve the v101.86 runtime byte-for-byte.

## 2. Protected runtime/data

MUST remain byte/hash identical to R1:

- `index.html`
- `luisa_24_heures.html`
- `CORPUS`
- `TEXT_LIBRARY`
- `HOUR_LINKED_TEXTS`
- `SPEECH_DATA`
- `INTERNAL_SUBHEADINGS`
- `SPEECH_END_VISUAL_BREAKS`
- schema 8
- snapshot 5
- `sw.js` runtime/cache identity already current at v101.86
- `manifest.json` app version
- title-highlight implementation
- Help/À propos runtime implementation

## 3. Mandatory per-fix cycle

For each evidence/QA correction:

`IMPLEMENT → DIFF REVIEW → LINE-BY-LINE CHECK → TARGETED ASSERTION → MINI-REGRESSION → INDEPENDENT RECHECK → PASS OR REDO`

Do not proceed past a failed gate.

## 4. Four passes

### Pass 1 — files vs build script

- reproduce v101.86 runtime from frozen R4 baseline;
- prove runtime is exactly `dd9476f9...b3d49c`;
- prove QA files are generated/current and their scenario IDs are unique/parity-aligned;
- verify script/auditor provenance and hashes;
- verify all protected fingerprints.

### Pass 2 — runtime/package behaviour

- rerun the existing 37 Chromium scenarios and Help claim audit;
- verify QA scenarios G-33/G-35/G-36/G-41/G-67/G-80 and new TH1 QA rows against runtime/package truth;
- syntax, speech/render, title lifecycle, Help truth, H15/H17 and backup/migration regressions remain PASS.

### Pass 3 — active reports line by line

Parse every line of every active package report. In the post-package meta-audit, also parse:

- `audit/independent_four_pass_audit.md`;
- primary reopened-ZIP report;
- independent reopened-ZIP report;
- final execution/deep-recheck report;
- final decision lock.

Any unsupported claim = `FAIL_REPORT_INTEGRITY`.

### Pass 4 — contradictions/stale claims/numbers/evidence

Recursive scan of root, scripts, reports, metadata, runtime, QA checklist and QA template. Active QA files must not contain stale current-facing v101.85/v101-84/cache/snapshot-4/closed-review assertions.

Historical migration/baseline references are permitted only when their context explicitly identifies them as historical.

## 5. Deterministic packaging

Build twice independently from the frozen R4 baseline. ZIP hashes and bytes must match exactly. If not, stop, diagnose, correct, discard prior reopen evidence, rebuild twice.

## 6. Mandatory reopened-ZIP gates

After final ZIP is frozen:

1. reopen/extract from disk in a fresh directory;
2. validate manifests/hashes/member parity/path safety;
3. validate runtime twin/hash/protected fingerprints;
4. validate QA checklist/template current truth and scenario parity;
5. rerun fresh browser scenarios;
6. verify every package report claim;
7. run a separately implemented independent reopened-ZIP auditor in another fresh directory;
8. only then create final decision lock.

## 7. Final decision rule

- `PASS` only if all critical gates including external physical/PWA/AT/live/rollback gates are actually proven.
- `LIMITED_PASS` if package/static/browser/reopened gates pass and external gates remain explicitly NOT_TESTED.
- `FAIL_REPORT_INTEGRITY` if any report/QA artifact overstates or contradicts current evidence.
- `FAIL_EVIDENCE_MISSING` if a required proof is absent.
- `FAIL` for any other critical gate failure.

No Word review packs are to be generated.
