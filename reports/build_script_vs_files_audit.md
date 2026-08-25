# Build script vs files audit — v101.121

**PASS**

- Baseline ZIP SHA-256: `66b5fbff29865faa9a2cf55aad28c090de86fefe1ea8911feaf124f3eff97d5d` — verified.
- Baseline HTML SHA-256: `1ef9375c896fa20aa0d4ea5d80022f98655ab8613a1156bc0fda56fa42d85eed` — verified.
- Authorized reverse-diff to v101.120 HTML: PASS.
- Protected declarations: 14/14 byte-identical.
- `showHelp()` function: byte-identical to v101.120.
- Obsolete v101.120 independent-prefreeze checker: removed from current tooling and retained only under `scripts/historical/`.
- Current builder and both final-reopen auditor implementations are packaged before freeze.
