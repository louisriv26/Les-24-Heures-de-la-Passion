# Luisa — 24 Heures de la Passion

Version: `v101.1`

Notes: clean app identity — installed/PWA name is now "24 Heures" / "Les 24 Heures de la Passion" (no build/stage strings in the user-facing name), and the version scheme is a plain `v101.x`. No corpus, speech-attribution, or reading-behaviour change from the prior build. Internal history is tracked in `luisa-24h-state_1.md`.

Status: `LIMITED_PASS_STATIC` — static/package checks (JS/CSS syntax, replica parity, corpus/speech structure) pass. Real-device validation is NOT_TESTED; the Android install path (a Play Protect "compatibility too low" warning on a browser-minted WebAPK) is under investigation — see `REAL_DEVICE_QA_CHECKLIST.md`.