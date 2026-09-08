# Real-device QA checklist — v101.138 R2

Use only the exact v101.138 R2 candidate identified by the external SHA-bound receipt.

## Identity
- app_version = v101.138
- build_revision = R2
- cache_name = luisa-24h-v101-138-r2
- APP_EVIDENCE_STAGE = RELEASE_ACCESSIBILITY_CLEANUP_R2
- corpus fingerprint begins `87733d22b5e899e2` and is unchanged

## A. Aide / Assistance focus
- Open Aide et À propos.
- Activate quick navigation **Signaler un problème** using keyboard and representative screen-reader navigation.
- It must scroll to Assistance and active focus must land on heading `#help-support-title` (`.help-feature-title`).
- Activate at least one pre-existing quick-nav target (for example Rechercher un texte); focus must still land on its `.help-section-hd`.
- Assistance controls remain styled, usable, and correctly named.
- Both support payloads identify `Version : v101.138 R2`.

## B. Layout
Check light and dark modes on phone/tablet/desktop widths: no horizontal overflow; Assistance stacks on phone and uses two columns when space permits; Vie privée and À propos des textes remain separate.

## C. Existing-PWA update
Under the governing handover assumption that v101.138 R1 was not deployed, test the observed live v101.137 R2 installation → v101.138 R2 without uninstalling. Preserve at least one note, highlight, meditated Hour, last place, theme and font size. Close/reopen three times.

## D. Corpus regression
- canonical CORPUS and TEXT_LIBRARY match certified R1 bytes; fingerprint unchanged.
- stable IDs/order unchanged.
- 24 PRESERVE_MOVE records remain evidence-only/not visible.
- no H23/H24 governance or source-critical changes.

## E. Physical/offline/accessibility
Run iPhone, iPad portrait/landscape and Samsung/Android; verify normal navigation, persistence, true offline cold reopen, representative VoiceOver/TalkBack, Help focus behavior and close/focus return.

Final public deployment remains unauthorized until all mandatory external gates pass.
