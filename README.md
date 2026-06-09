# Luisa — 24 Heures de la Passion

Current package: `luisa_24_heures_app_v94_stage6h4_evidence_integrity_cleanup_locked.zip`  
App version: `prototype-94`  
Stage: Stage 6H.4 — evidence integrity and stale-reference cleanup  
Status: `LIMITED_PASS_STATIC`

## Samsung highlighting flow

On Samsung/Android, use paragraph highlighting only:

1. Tap **Paragraphe**.
2. Tap one paragraph.
3. The instruction hint should disappear.
4. The colour picker should show **Surligner ce paragraphe en**.
5. Choose a colour directly.
6. The whole paragraph should be highlighted.
7. Reload and confirm persistence.
8. Confirm the highlight appears in **Mon Espace**.
9. Confirm no Samsung/Google Translate/Search/Copy overlay appears.

The **Annuler** button only cancels paragraph mode. It is not part of the normal highlight flow.

## iPhone/iPad regression check

Select exact text, tap **Surligner**, choose a colour, and confirm only the selected text is highlighted and persists.

## Release status

This package has static/reopened-ZIP evidence. It is not public-release PASS until real Samsung, iPhone, iPad, installed PWA, and live update tests pass.
