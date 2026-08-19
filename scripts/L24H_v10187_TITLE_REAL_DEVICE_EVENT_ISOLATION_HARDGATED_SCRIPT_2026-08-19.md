# L24H v101.87 — Approfondir title real-device event-isolation repair — HARD-GATED EXECUTION SCRIPT

## Decision context

Authoritative baseline is the exact v101.86 TH1-R2 ZIP:

- file: `L24H_v10186_GITHUB_DEPLOY_TITLE_HELP_HARDENED_R2_AUDIT_RECONCILED.zip`
- SHA-256: `760196b75ee89bb54eaf7780909028e84748ca3bc5b77b62342067fa40602494`
- runtime HTML SHA-256: `dd9476f9bb56a2bd344e29a881f9c21666a2844f08175b27a693168449b3d49c`
- storage schema: 8
- personal snapshot: 5

Real-device user feedback on 19 August 2026 supersedes prior Chromium-only PASS evidence for Approfondir title highlighting: the feature still does not work reliably on the user's device.

Direct code inspection identifies a concrete mobile event-isolation defect:

- ordinary highlight UI is protected by `stage6fIsHighlightUiTarget()` / `stage6fBindHighlightUiEventIsolation()` / `stage6fShouldSuppressSelectionCapture()`;
- the title marker picker is `#libraryMarkerPicker` / `[data-library-marker-ui="true"]` and was omitted from those protections;
- real touch/pointer events can therefore enter the global selection-capture machinery while the title picker is being used.

This stage repairs only that proven interaction-layer omission and bumps release/cache identity to v101.87 so the repaired runtime receives a fresh service-worker cache generation.

## Hard stop rules

STOP before modifying if any of the following is false or ambiguous:

1. baseline ZIP hash matches exactly;
2. root runtime twins are byte-identical;
3. v101.86 contains the current inline title-marker architecture (`libraryMarks`, `libraryMarkerPicker`, direct title mark edit, five colours, remove/Undo);
4. `stage6fIsHighlightUiTarget()` does not already protect `libraryMarkerPicker` / `[data-library-marker-ui="true"]`;
5. `stage6fShouldSuppressSelectionCapture()` does not already suppress while `libraryMarkerPicker` is open;
6. source/corpus/speech changes are unnecessary;
7. no editorial/product decision is required.

Do not continue past a failed gate.

## Protected data and behaviour

Must remain semantically/hash identical unless version identity inherently changes the containing HTML bytes:

- `CORPUS`
- `TEXT_LIBRARY`
- `HOUR_LINKED_TEXTS`
- `SPEECH_DATA`
- `INTERNAL_SUBHEADINGS`
- `SPEECH_END_VISUAL_BREAKS`
- storage schema 8
- personal snapshot 5
- paragraph IDs/order
- notes/highlights/favourites/progress semantics
- body highlighting
- Samsung whole-paragraph mode
- H15/H17 corrections
- title-marker persistence model (`libraryMarks`)
- Help content except version identity if displayed dynamically

## Exact approved runtime changes

### T87-01 — protect the title marker UI from global selection capture

Modify `stage6fIsHighlightUiTarget(target)` so these are treated as protected highlight UI:

- `#libraryMarkerPicker`
- `[data-library-marker-ui="true"]`
- `.library-title-inline-mark`
- `.library-title-mark-btn`

### T87-02 — bind event isolation to the title picker

`stage6fBindStaticHighlightUi()` must call `stage6fBindHighlightUiEventIsolation(document.getElementById('libraryMarkerPicker'))`.

`openLibraryMarkerPicker()` must defensively bind the same isolation before opening and mark the highlight UI protection interval.

### T87-03 — suppress global selection capture while title picker is open

`stage6fShouldSuppressSelectionCapture()` must return true while either the ordinary colour picker or the title marker picker is open.

Before opening the title picker, any residual native text selection may be cleared because the title marker is whole-reading metadata and does not depend on a native text selection.

### T87-04 — identify the title controls as highlight UI

Add `data-highlight-ui="true"` to:

- `#libraryMarkerPicker`
- the dynamic inline title `<mark>`
- the `Surligner le titre` / modify button

Retain `data-library-marker-ui="true"` for specific classification.

### T87-05 — version/cache generation bump

- `APP_VERSION`: v101.87
- service-worker comment/version: v101.87
- cache: `luisa-24h-v101-87`
- `version.json`: v101.87, build date 2026-08-19
- README/current QA identity: v101.87

Do not change manifest id/scope/start_url.

## Mandatory per-fix gate

For every fix:

`IMPLEMENT → EXACT DIFF → LINE-BY-LINE REVIEW → PROTECTED-DATA CHECK → JS/SW SYNTAX → TARGETED TEST → MINI-REGRESSION → INDEPENDENT RECHECK → PASS OR REDO`

No next fix until the current fix passes.

## Targeted runtime tests

At minimum, under Chromium with mobile/touch emulation plus synthetic native-selection pressure:

1. open an Approfondir reading;
2. open title marker picker from button;
3. verify picker is protected by `stage6fIsHighlightUiTarget`;
4. dispatch pointer/touch end events on picker/swatch;
5. dispatch `selectionchange` with a non-collapsed title selection while picker is open;
6. verify global selection capture/context action bar does not replace or close title picker;
7. choose all five colours;
8. direct tap/click highlighted title reopens picker;
9. recolour;
10. remove;
11. Undo restores exact colour;
12. persistence after reload;
13. Mon Espace entry and open-at-start;
14. ordinary body highlight still works;
15. Samsung paragraph mode regression check;
16. long/multiline title inline rendering;
17. dark/light mode;
18. keyboard Enter/Space;
19. Help title guidance remains truthful.

## Package/evidence gates

- deterministic ZIP build twice, byte-for-byte identical;
- manifests recomputed only after runtime/evidence freeze;
- active reports cannot overclaim physical iPhone/iPad/Samsung success;
- physical-device title gate remains NOT_TESTED until the user confirms the exact v101.87 live/device build;
- stale-reference scan must treat v101.86 as historical baseline only, never current-facing QA.

## Final immutable ZIP gate

After writing the final ZIP:

1. reopen from disk in a fresh folder;
2. recompute all hashes/manifests;
3. validate runtime twins/version/cache;
4. revalidate protected structures and speech offsets;
5. rerun targeted title event-isolation scenarios;
6. independently audit in a second fresh folder with separately implemented logic;
7. compare report claims against the final immutable package.

## Final decision lock

- PASS is forbidden unless primary reopened-ZIP audit and independent reopened-ZIP audit both PASS.
- Even if both pass, overall status must remain `LIMITED_PASS` while real physical-device/PWA/live/AT gates remain untested.
- If either reopened audit fails: final status = FAIL and do not present package as successful.
- Do not regenerate Word review packs.
