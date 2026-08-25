# v101.121 four-pass deep audit

**PASS_PREFREEZE**

## Pass 1 — files vs build script
- Baseline ZIP hash: PASS — `66b5fbff29865faa9a2cf55aad28c090de86fefe1ea8911feaf124f3eff97d5d`.
- Authorized HTML reverse-diff: PASS.
- Protected declarations: 14/14 byte-identical.
- `showHelp()` function: byte-identical to v101.120.
- Current packaged build/audit tooling inventory: PASS.

## Pass 2 — runtime/package behaviour
- Help browser: 70/70 PASS.
- Broad Chromium: 52/52 PASS.
- Quoted-span fixed point: A=0, B=0; 398 relevant spans.
- Exhaustive presentation: 1990/1990 PASS.
- Service-worker logic: 15/15 PASS.

## Pass 3 — every active report line vs current evidence
- The successor uses direct per-line evidence bindings, not generic presence text.
- `reports/active_report_line_audit.csv` is generated after this report is frozen and must cover every nonblank line in the active inventory.
- The final reopened-ZIP audits independently revalidate that exact coverage and every evidence field.

## Pass 4 — contradictions, stale PASS/FAIL claims, stale numbers and obsolete evidence
- Unexplained current-facing stale version/reference claims: 0.
- Obsolete current-tool semantic assumptions: 0.
- The v101.120 failing independent-prefreeze checker is historical-only and not current tooling.
- First-party report claims: 9/9 directly supported.
- Separately implemented prefreeze audit: 18/18 PASS.

Final immutable ZIP reopen audits are deliberately external and are not claimed inside this package. Physical-device/live-origin gates remain NOT_TESTED.
