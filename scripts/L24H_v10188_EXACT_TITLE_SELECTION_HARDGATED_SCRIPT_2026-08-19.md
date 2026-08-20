# L24H v101.88 — Exact Approfondir title-text selection + reading-marker separation — hard-gated execution script

## Governing baseline

- Frozen baseline package: `L24H_v10187_GITHUB_DEPLOY_TITLE_REAL_DEVICE_ISOLATION_R1.zip`
- Required baseline SHA-256: `710416524b57501f5154fd9b333c19ac622b3352c2d36a6d7af8f07172538d28`
- Baseline app: `v101.87`
- Storage schema: `8` — protected unless a gate proves a change is unavoidable.
- Personal snapshot: `5` — protected unless a gate proves a change is unavoidable.
- No Word review packs.

## User requirement being implemented

On iPhone/iPad, selecting **part of an Approfondir title** must enter the same normal annotation pipeline as body text and offer the normal app actions **Surligner / Note / Copier / Fermer**. Only the selected title words must be highlighted. Existing whole-reading `libraryMarks` must remain a separate feature and must no longer masquerade as a text highlight.

The existing whole-reading control is renamed **Marquer cette lecture** and continues to drive `Mon Espace → Lectures marquées`, backup/import and whole-reading reopening. Existing `libraryMarks` data must be preserved without destructive migration.

## Mandatory stop conditions before modification

STOP before changing app bytes if any of the following occurs:

1. Baseline ZIP hash does not match exactly.
2. `index.html` and `luisa_24_heures.html` are not byte-identical.
3. `STORAGE_SCHEMA_VERSION != 8` or `PERSONAL_SNAPSHOT_VERSION != 5`.
4. Existing generic `state.textHighlights` records cannot safely represent a title target with stable ID + offsets + text hash.
5. Existing `validPersonalId()` cannot accept a deterministic `.TITLE` ID without weakening validation.
6. Existing `getTargetInfo()`, `renderParaText()`, highlight persistence, stale detection, Mon Espace, export/import, Undo or note/copy pathways cannot support the new target without a product/editorial decision.
7. Existing `libraryMarks` cannot be visually separated from title text while preserving stored user data.
8. Any corpus/devotional/source wording change would be required.
9. Any speech-data or source-backed editorial judgement would be required.
10. Any conflicting file/version authority is discovered.

## Protected data and behaviour

The following must remain semantically and byte-wise unchanged unless a gate explicitly proves a necessary runtime-only reference change:

- `CORPUS`
- `TEXT_LIBRARY` content and titles
- `HOUR_LINKED_TEXTS`
- `SPEECH_DATA`
- `INTERNAL_SUBHEADINGS`
- `SPEECH_END_VISUAL_BREAKS`
- all paragraph IDs/order
- all source text and source provenance
- H15 and H17 corrections
- body highlight behaviour
- existing notes
- Samsung whole-paragraph highlighting behaviour
- existing `libraryMarks` personal data
- storage schema 8 / snapshot 5

## Intended runtime architecture

### A. Stable title annotation target

Add one canonical helper:

```text
makeLibraryTitleId(itemId) = itemId + '.TITLE'
```

Example:

```text
PASSION24.TEXT.HOW_TO_PRACTICE.TITLE
```

`getTargetInfo()` must resolve this as:

```text
type = library_title
text = exact item.title
label = Titre — <item.title>
libraryId = item.id
```

Placeholder/hidden/non-user-visible entries must not become active annotation targets.

### B. Title DOM

The actual title text must be content, not highlight UI.

The visible Approfondir title must render through the normal highlight renderer using its stable target ID. It must expose a dedicated `.library-title-selectable` surface and must not carry `data-highlight-ui`, button semantics or `libraryMarks` click handlers.

### C. Native iOS selection

The iPhone/iPad selection whitelist must explicitly include `.library-title-selectable` and descendants.

All selection resolvers that enumerate supported text surfaces must use one canonical selector constant so single-range and ordered-range logic cannot drift.

### D. Whole-reading marker separation

`libraryMarks` remains a separate reading-level feature.

Visible wording changes:

```text
Surligner le titre           → Marquer cette lecture
Modifier / retirer ...       → Modifier / retirer le repère
Lectures marquées            → unchanged
```

The reading marker may retain its stored colour, but its UI must not rewrite or wrap title text. `refreshLibraryMarker...()` must update only the separate marker control/indicator.

### E. Existing normal annotation pipeline

Selecting title text on iPhone/iPad must use the existing action bar and existing stores:

- Surligner → `state.textHighlights[titleId]`
- Note → `state.notes[titleId]`
- Copier → normal context copy path
- recolour → existing `onMarkClick()` / colour picker
- remove → existing highlight removal
- Undo → existing annotation undo
- stale detection → existing `stableTextHash()` against exact title text
- Mon Espace → exact title highlights/notes appear with title label
- reopen → `openLibraryText(libraryId)` then target title ID
- JSON backup/import → existing generic textHighlight/note format
- journal → existing generic highlight/note export

No title-specific offset store may be introduced.

### F. Samsung/Android

Do not enable native word-selection on Samsung/Android. Existing Samsung paragraph mode remains unchanged for body paragraphs. The new title target must not silently make title word-selection a Samsung feature in this stage.

## Per-fix mandatory cycle

For every changed block:

```text
IMPLEMENT
→ exact diff
→ line-by-line review
→ build-script compliance
→ targeted runtime test
→ mini-regression
→ independent recheck
→ PASS or REDO/REVERT
```

Do not continue to the next item after a failed gate.

## Required targeted tests before packaging

### Target registry

1. All visible non-group Approfondir items get exactly one deterministic `.TITLE` ID.
2. IDs are unique and pass `validPersonalId()`.
3. `getTargetInfo(titleId).text === item.title`.
4. hidden/groups/placeholders are not incorrectly exposed.

### DOM/rendering

5. All visible Approfondir titles render one `.library-title-selectable` surface.
6. Title surface target ID resolves to the correct reading.
7. Title surface contains no whole-reading `data-highlight-ui` wrapper.
8. Existing `libraryMarks` do not rewrite title innerHTML.

### Native selection contract

9. Synthetic DOM Range wholly inside title resolves to title target.
10. `setPendingSelectionFromRange()` succeeds.
11. exact start/end offsets equal selected title substring.
12. context action bar offers Surligner / Note / Copier / Fermer.
13. title range across a visual line wrap still resolves correctly.
14. no cross-title/body selection is claimed as supported in this stage.

### Highlight lifecycle

15. create yellow partial title highlight.
16. only selected words are marked.
17. reload persists.
18. tap highlight → colour picker.
19. recolour blue.
20. delete.
21. Undo restores exact previous colour and offsets.
22. multiple non-overlapping title highlights can coexist.
23. title highlight + body highlight can coexist.
24. existing whole-reading mark + partial title highlight can coexist independently.

### Notes/copy

25. title selection Note opens against title target.
26. saved title note persists and appears in Mon Espace.
27. title selection Copy uses selected title words and correct label.

### Integrity/export

28. title highlight has valid `text_hash`, `para_hash`, `paragraph_fingerprint`.
29. title edit/stale simulation is detected rather than silently misanchored.
30. JSON export/import round-trip preserves title highlights/notes and libraryMarks.
31. schema-7/snapshot-4 and current schema-8/snapshot-5 compatibility remains valid.
32. foreign/prototype-polluted backup rejection remains valid.
33. readable journal includes title highlights/notes and reading marks distinctly.

### Regression

34. ordinary body exact-text highlighting still works.
35. ordinary notes/copy still work.
36. Samsung paragraph-mode body highlighting remains unchanged.
37. H15/H17 remain correct.
38. speech target/offset validation remains 0 errors.
39. search/navigation/Mon Espace still work.
40. all visible Approfondir texts open with no runtime exception.

## Help / wording reconciliation

Help must accurately distinguish:

- **Surligner du texte dans un titre**: exact selected words, same annotation actions as body on compatible devices.
- **Marquer cette lecture**: whole-reading marker stored in `libraryMarks` and shown under Lectures marquées.
- Samsung/Android paragraph mode remains separate.

No Help claim may describe a whole-reading mark as a title text highlight.

## Version/update

If modification gates pass:

- `APP_VERSION = v101.88`
- `version.json = v101.88`
- SW cache generation = `luisa-24h-v101-88`
- README/active QA current-facing strings updated to v101.88.

## Independent four-pass before packaging

Pass 1 — verify files vs this script and exact diff scope.

Pass 2 — execute runtime/package behaviour tests, including the title Range resolver and full highlight lifecycle.

Pass 3 — parse every active report line and bind claims to current evidence.

Pass 4 — scan recursively for contradictions, stale PASS/FAIL, stale v101.87 current-facing instructions, old cache names, stale title-marker wording and obsolete counts.

Any failure blocks packaging.

## Deterministic packaging gate

Build twice independently from the frozen baseline. ZIP A and ZIP B must be byte-for-byte identical. If not, FAIL and locate/remove nondeterministic evidence fields before proceeding.

## Mandatory final package reopen gate

After writing the final immutable ZIP:

1. reopen from disk into a fresh folder;
2. recompute all hashes/manifests;
3. validate root/twin runtime identity;
4. validate version/cache metadata;
5. validate all protected data hashes;
6. rerun syntax, title-target, title-highlight, body-highlight, notes/copy, migration, speech, Help and stale-reference gates against extracted final bytes;
7. rerun fresh browser scenarios against the extracted final bytes;
8. compare every active report claim to actual extracted evidence.

If this gate is not PASS, final status is FAIL.

## Separate independent reopened-ZIP audit

A separately implemented auditor must reopen the same immutable ZIP in another fresh folder and independently reproduce the critical package/runtime/title/highlight/Help checks.

If this gate is not PASS, final status is FAIL.

## Final decision rule

`PASS` is allowed only if all critical machine/package/reopened-ZIP gates pass and there is no remaining critical real-device requirement.

Because the original defect is physical iPhone native selection, unless the exact v101.88 package is physically tested on the reporting iPhone during this execution, the maximum final status is:

```text
LIMITED_PASS
```

and the physical-iPhone exact-title-selection gate remains `NOT_TESTED` for v101.88.

The final response must match the final decision lock exactly.
