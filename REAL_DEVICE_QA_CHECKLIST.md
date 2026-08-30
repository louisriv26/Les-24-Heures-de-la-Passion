# Real-device QA checklist — v101.122

Package under test must match the final locked ZIP SHA-256 and report `v101.122` in Aide.

## Hour-24 priority
- Hour 23 retains Réflexion et pratique / Approfondir / Revenir au début / Prier la 24e Heure.
- Hour 24 retains Réflexion et pratique / Approfondir / Revenir au début.
- Incomplete Hour-24 cycle state shows X/24 and no restart.
- 23/24 → Méditée updates immediately to 24/24 complete.
- Undo Méditée immediately returns to incomplete.
- 24/24 restart confirmation preserves notes/highlights/preferences and opens Hour 1 directly.
- No disabled Suivante on Hour 24.
- No redundant in-content Revenir à l’Accueil where persistent Accueil is present.

## Platforms
- iPhone: exact-selection highlighting, Hour-24 terminal layout, bottom navigation.
- iPad portrait/landscape: same plus orientation/scroll containment.
- Samsung/Android: whole-paragraph highlighting, Hour-24 terminal layout, bottom navigation.
- Installed PWA update, close/reopen and true offline cold reopen.
- VoiceOver/TalkBack representative checks.

Record results in `REAL_DEVICE_QA_RESULTS_TEMPLATE.csv`. Browser emulation is not physical-device evidence.
