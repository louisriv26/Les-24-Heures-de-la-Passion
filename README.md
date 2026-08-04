# Luisa — 24 Heures de la Passion

Version: `v101.51`

Prior production was v101.49 (1 August 2026). This release carries three fixes found by Louis on his
own iPhone and iPad after that promotion.

## Corpus — complete, unchanged in content since v101.44

R3A (reverence capitalisation, grammar/punctuation, 9 substantive editorial items individually
approved) and R3B (all 24 Hours, reconciled against both complete Italian witnesses and the English
witness) are both complete. Full-text convergence and two independent blind adversarial revalidation
passes ran at v101.40–v101.44. All six protected declarations (`CORPUS`, `TEXT_LIBRARY`,
`HOUR_LINKED_TEXTS`, `SPEECH_DATA`, `INTERNAL_SUBHEADINGS`, `SPEECH_END_VISUAL_BREAKS`) verify
byte-identical to the v101.44 hash contract at every release since, including this one.

## What changed since v101.49

- **The app no longer stays zoomed and scrollable sideways after you write a note.** iOS Safari zooms
  the page in whenever a text field with a font smaller than 16px is focused, and it never zooms back
  out — so the note panel appeared slightly wider than the screen and the whole app remained pannable
  long after the panel was closed. The note box (14.4px) and the Approfondir section search (15.2px)
  are now 16px. Pinch-zoom is deliberately still available; suppressing it would have hidden the
  symptom at the cost of accessibility.
- **Mon Espace now shows all your highlights.** They were sorted by passage label and only the first
  eight were drawn, so any highlight whose label begins with a letter — every **Prière** and every
  **Complément** — fell past the end of the list and could never be seen, however many you had. The
  list is now ordered **newest first**, and the eight-entry limit became a preview with a
  **"Voir mes N surlignages"** button that opens the full list. Notes had the identical silent limit
  and now have the identical button. Highlights that need attention are still listed first.

## Carried forward from v101.26–v101.49

- Notes reachable on phone and tablet from **both** routes — long-pressing a paragraph and selecting
  text. Neither worked before this line of fixes.
- Recovery for highlights broken by editorial corrections: re-anchored automatically where the
  passage can be located unambiguously, and otherwise listed in Mon Espace with a plain explanation
  and a working **✕ Retirer** button.
- The service-worker update fix, so pressing **Actualiser** genuinely lands on the new version.
- Speech punctuation restored across 99 paragraphs (22 Hours plus Approfondir); progress, study mode
  and reset persistence fixes; meditated-hour border weight; a dark-mode contrast fix; "Automatique"
  in place of "Système"; Gethsémani Compléments cleanup.

## Real-device status

**Confirmed by Louis on iPhone**, 3 August 2026: the note-panel zoom behaviour and Mon Espace
highlight visibility. Earlier confirmations covered the update flow and the selection-bar Note button
on iPhone and iPad.

Internal history, the full version-by-version record, the corpus decision record and the open items
still tracked (a hardcoded corpus unit count pending an independent recount; one unreproduced Android
WebAPK install report) are in `luisa-24h-state_1.md` in the project working directory.
