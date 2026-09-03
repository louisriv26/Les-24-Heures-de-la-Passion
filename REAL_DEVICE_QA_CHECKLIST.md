# Real-device QA checklist — v101.132

Package under test must match the final locked v101.132 ZIP SHA-256 published in the external decision lock and report `v101.132` in Aide.

## Required external gates
- iPhone: core navigation, exact-selection highlighting, Hour-24 terminal layout, bottom navigation, updated M1C001–M1C004 presentation.
- iPad portrait/landscape: same plus orientation and scroll containment.
- Samsung/Android: whole-paragraph highlighting, Hour-24 terminal layout, bottom navigation, updated M1C001–M1C004 presentation.
- Installed PWA update from v101.131, close/reopen, and true offline cold reopen.
- VoiceOver/TalkBack representative navigation and speech-label checks.
- Live origin must be byte-bound to the final locked ZIP before any deployment claim.

Record results in `REAL_DEVICE_QA_RESULTS_TEMPLATE.csv`. Browser emulation is not physical-device evidence.
