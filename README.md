# Luisa — 24 Heures de la Passion

Version: `v101.2`

Notes: security hotfix — closed a stored-XSS in the note-delete render path (an imported backup file could carry a hostile note `id` that executed script when the note modal was opened); fixed by escaping the id at the sink and charset-restricting the note-id sanitizer. Found in a full multi-lens audit before any user report. No corpus, speech-attribution, or reading-behaviour change. Clean app identity ("24 Heures" / "Les 24 Heures de la Passion", plain `v101.x` scheme) carried over from v101.1. Internal history is tracked in `luisa-24h-state_1.md`.

Status: `LIMITED_PASS_STATIC` — static/package checks (JS/CSS syntax, replica parity, corpus/speech structure) pass. Real-device validation is NOT_TESTED; the Android install path (a Play Protect "compatibility too low" warning on a browser-minted WebAPK) is under investigation — see `REAL_DEVICE_QA_CHECKLIST.md`.