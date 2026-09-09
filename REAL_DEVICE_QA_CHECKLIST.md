# Real-device QA checklist — v101.141 R1

Use only the exact externally SHA-bound v101.141 R1 candidate. Internal browser evidence does not substitute for physical-device/PWA/accessibility gates.

## Search completeness
- Search each of the 24 exact Hour titles; confirm the owning Hour appears and opens correctly.
- Search each of the 5 exact Prayer titles; confirm the owning prayer appears and opens correctly.
- Search each Section title; confirm the owning complement appears and opens correctly.
- Under `Paroles directes`, verify representative linked-LDC/library speech for Jésus, Marie and Père appears and opens at the exact stable paragraph.
- With no query under `Paroles directes`, verify speaker filters Tous/Jésus/Père/Marie operate normally.
- Run a query with more than 60 matches; verify the exact total is displayed without `+` and the UI still states that only the first 60 are shown.
- Verify accent/ligature folding, search highlighting, category filters and search deep links remain correct.

## Protected regression
- Canonical Hours, Réflexions, Prières, Compléments and linked-LDC ordinary text search remain correct.
- All 36 v101.140 linked-LDC corrected records remain searchable under corrected wording.
- Existing notes/highlights/progression/last-place/theme/font survive installed-PWA update.

## External gates
- Physical iPhone validation.
- Physical iPad portrait and landscape validation.
- Physical Samsung/Android validation.
- Live-origin exact-byte binding.
- Installed-PWA update and three close/reopen cycles.
- True offline cold reopen.
- Representative VoiceOver and TalkBack navigation.

Final public deployment remains unauthorized until all external gates are evidenced.
