# Luisa — 24 Heures de la Passion

Version: `v101.49`

Promotes v101.26 through v101.49 to production in one step (prior production was v101.25).

## Corpus — complete, unchanged in content since v101.44

R3A (reverence capitalisation, grammar/punctuation, 9 substantive editorial items individually
approved) and R3B (all 24 Hours, reconciled against both complete Italian witnesses and the English
witness) are both complete. Full-text convergence and two independent blind adversarial revalidation
passes ran at v101.40–v101.44. All six protected declarations (`CORPUS`, `TEXT_LIBRARY`,
`HOUR_LINKED_TEXTS`, `SPEECH_DATA`, `INTERNAL_SUBHEADINGS`, `SPEECH_END_VISUAL_BREAKS`) verified
byte-identical to the v101.44 contract at every subsequent app-only release, including this one.

## What changed for users since v101.25

- **Service-worker update flow fixed (FINDING-01).** Pressing "Actualiser" could complete while the
  app stayed on the old version — permanently, not just for one reload. This is the cause of the
  reported iOS symptom ("it actualises but stays on the old version"). Fixed by forcing each cached
  asset to refresh from the network during install, so a new cache generation can never be seeded
  from a stale one.
- **Notes are now reachable on phone and tablet, from both routes.** There are two separate mobile
  action bars — one raised by long-pressing a paragraph, one raised by selecting text — and both now
  offer **Note**. Neither route worked before; this was not a regression, notes had simply never been
  reachable on a touch device.
- **Stale highlights are recovered instead of silently disappearing.** A highlight anchors to a
  paragraph's id, character offsets and a text fingerprint; any of the accumulated editorial
  corrections could invalidate all three, leaving a highlight that stopped rendering with no
  explanation and no way to remove it. Stale highlights are now re-anchored automatically wherever
  the location is unambiguous, and any that cannot be recovered are listed in **Mon Espace** with a
  plain explanation and a working **✕ Retirer** button.
- **Speech punctuation restored (P2-COLON).** The colon introducing direct speech, and the spaces
  either side of it, are no longer dropped from rendered text — 99 paragraphs across 22 Hours plus
  the Approfondir section.
- **Progress persistence fixed.** The last-opened Hour, study-mode toggle, and a completed progress
  reset are now backed by a single canonical value, fixing cases where the resume card forgot the
  Hour, study mode reverted, or a reset resurrected the old resume point.
- **Readability:** meditated-hour borders are now consistently thicker on both the home grid and the
  Heures list; a dark-mode label that read 2.18:1 contrast now reads 6.32:1; the theme option reads
  "Automatique" instead of "Système"; a misplaced blurb was removed from the Gethsémani Compléments
  section.

## Real-device status

**Confirmed by Louis on iPhone and iPad**, 1 August 2026: the update flow (Actualiser landing on the
new version) and the new selection-bar Note button. Internal history, full version-by-version
detail, and the open items still being tracked (a hardcoded corpus unit count pending an independent
recount; one unreproduced Android WebAPK install report) are in `luisa-24h-state_1.md`.
