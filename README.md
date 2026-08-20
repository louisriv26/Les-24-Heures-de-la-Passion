# 24 Heures de la Passion — v101.89 · R2 audit reconciled

Version: `v101.89`  
Cache: `luisa-24h-v101-89`  
Storage schema: `8` · personal snapshot: `5`

## v101.89 — WebKit/iPhone title Range-boundary repair

Physical iPhone feedback proved v101.88 still failed to show the app actions after selecting part of an Approfondir title. The deeper root cause is Range-boundary normalisation: v101.88 accepted title Ranges whose endpoints were inside `.library-title-selectable`, but rejected equivalent WebKit-style Ranges with a boundary on the surrounding `<h2>`. v101.89 adds a narrowly scoped boundary-aware resolver and keeps exact title highlights in the ordinary `textHighlights` engine.

`Marquer cette lecture` remains a separate whole-reading marker (`libraryMarks`).

Physical iPhone validation of this exact v101.89 build remains required before the title-selection gate can pass.

## R2 evidence reconciliation

The v101.89 runtime is byte-for-byte unchanged from R1. R2 corrects the active Web App Manifest version from stale `v101.88` to `v101.89` and hardens the auditors so `manifest.json` is part of the active stale-reference gate. Physical iPhone exact-title selection remains NOT_TESTED on v101.89.
