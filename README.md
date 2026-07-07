# Luisa — 24 Heures de la Passion

Version: `v101.3`

Notes: restored the persistent bottom navigation (Accueil / Heures / Approfondir / Espace) on tablet and desktop — it had been hidden on every screen wider than a phone, leaving those users with no section switcher. The bar now appears at all widths (centered and width-capped on wide screens; phones unchanged). Audit finding CSS4. Carries the v101.2 security hotfix (note-id stored-XSS closed). No corpus, speech-attribution, or reading-behaviour change. Internal history is tracked in `luisa-24h-state_1.md`.

Status: `LIMITED_PASS_STATIC` — static/package checks (JS/CSS syntax, replica parity, corpus/speech structure) pass. Real-device validation is NOT_TESTED; the Android install path (a Play Protect "compatibility too low" warning on a browser-minted WebAPK) is under investigation — see `REAL_DEVICE_QA_CHECKLIST.md`.