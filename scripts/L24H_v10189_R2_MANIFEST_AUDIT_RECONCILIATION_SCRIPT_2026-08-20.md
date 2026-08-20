# L24H v101.89 R2 — manifest/evidence reconciliation — hard-gated script

## Authority
Baseline is the exact v101.89 R1 ZIP with SHA-256 `350143c948097d70e6a54e649a61f2508a82f7f25b93eb0662d9aab5c81ce20b`.
Physical iPhone exact-title-selection remains `NOT_TESTED` for v101.89. No runtime or corpus claim may convert that gate to PASS.

## Scope lock
This stage may modify only release/evidence metadata, QA/audit scripts/reports, manifests, and README wording needed to reconcile the stale active manifest. It must not change `index.html`, `luisa_24_heures.html`, `sw.js`, corpus/speech data, storage schema, or personal snapshot.

## Gate 0 — stop-before-modification
1. Baseline ZIP hash must match exactly.
2. `index.html` and `luisa_24_heures.html` must be twins.
3. Runtime must declare `APP_VERSION = v101.89` and SW cache `luisa-24h-v101-89`.
4. `manifest.json.version` must reproduce the discovered stale value `v101.88`; otherwise stop because the diagnosed scope no longer matches the bytes.
5. Physical iPhone v101.89 gate must still be NOT_TESTED.

## Correction
- Set `manifest.json.version` to `v101.89` only.
- Regenerate README/reports/provenance so R2 is identified as an evidence/package reconciliation with runtime unchanged.
- Harden independent auditor to check manifest version and active stale-reference policy.
- Include `manifest.json` in the active Pass-3 ledger and Pass-4 current-facing scan.
- No current-facing file may use `v101.88` except explicit sentences describing the failed baseline/previous version.

## Mandatory verification
### Pass 1
- file/hash/manifests closure;
- runtime/SW byte identity to R1;
- manifest version v101.89;
- QA build v101.89.

### Pass 2
- rerun packaged title boundary runtime audit;
- JS and SW syntax;
- physical iPhone remains NOT_TESTED.

### Pass 3
- parse every line of active current QA/report/manifest/decision files and classify it against current evidence.

### Pass 4
- scan all text files for version/cache/status tokens;
- stale baseline references permitted only in explicit history/provenance/scripts;
- active manifest/QA/runtime/current decision files must be v101.89.

## Determinism
Build twice independently from the exact R1 ZIP. ZIP hashes must be byte-identical.

## Reopened ZIP gates
After the deterministic ZIP is frozen:
1. primary reopened-ZIP audit from a fresh extraction;
2. separately implemented independent reopened-ZIP audit;
3. terminal meta-audit binds all final claims to the exact ZIP hash.

## Decision lock
- Any failed machine/reopen/evidence gate => FAIL / FAIL_REPORT_INTEGRITY.
- If all machine/reopen gates pass but physical iPhone v101.89 remains untested => LIMITED_PASS, `public_release_ready=false`.
- Never claim the physical iPhone title issue fixed until the exact package passes on device.
