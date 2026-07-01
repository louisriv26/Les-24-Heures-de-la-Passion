# Real-device QA — Les 24 Heures de la Passion · R49j

App version: `prototype-101r59-stage8a-r49j-prayer-hour`
Release level: L1 Static Certified — this test campaign targets L2 Device Certified.
Live URL: https://louisriv26.github.io/Les-24-Heures-de-la-Passion/

---

## How to test

**Option A — Live site (recommended for PWA/SW tests):**
Open the URL above in Safari/Chrome on the device.

**Option B — Local file:**
Open `app/luisa_24_heures.html` directly in the browser.
Note: service worker, offline, and update tests require a served URL (Option A).

---

## Required platforms

| Platform | Browser | Priority |
|---|---|---|
| iPad | Safari | Critical |
| iPhone | Safari | Critical |
| Android (Samsung or other) | Chrome | Critical |
| Desktop | Chrome or Firefox | Supplementary |

---

## Test scenarios

### 1. Boot and first render
- [ ] App loads without console errors
- [ ] Home screen shows hours grid and progress counter
- [ ] Fonts render correctly (Cinzel headers, EB Garamond body — not system fallback)
- [ ] Dark/light mode respects system preference on first load

### 2. Reader — basic navigation
- [ ] Open an hour from the home screen
- [ ] Scroll through the full hour text
- [ ] Switch between Méditation / Réflexions / Approfondir tabs
- [ ] Navigate to next/previous hour via end-of-hour buttons
- [ ] Back button returns to home screen

### 3. Repères d'étude (# toggle)
- [ ] Default state: no paragraph numbers, no action buttons (prayer-clean reading)
- [ ] Tapping the `#` pill switches to repères d'étude — para numbers, action buttons, speaker badges visible
- [ ] Toast "Repères d'étude affichés" / "Repères d'étude masqués" appears on toggle
- [ ] State persists after closing and reopening the app

### 4. Notes (R49C)
- [ ] With repères d'étude ON, tap ✎ on any paragraph — note modal opens
- [ ] Type a note (test near 2000-char limit) and save
- [ ] Note dot appears on that paragraph
- [ ] Reopen the note, edit, and delete it — dot disappears
- [ ] Notes persist after closing and reopening the app
- [ ] **Known gap:** notes are NOT included in Mon Espace export/import (see Open defects) — do not expect a note to survive an export→import round trip

### 5. Plan sheet (R49E, Hours 15–24 only)
- [ ] Open Hour 15 or later — confirm `≡ Plan` button appears in reader header
- [ ] Open an hour before 15 — confirm the button does NOT appear (no internal subheadings)
- [ ] Tap `≡ Plan` — sheet lists scenes for that hour
- [ ] Tap a scene — reader jumps to that scene

### 6. Paroles directes — browse and speaker filter (R49F)
- [ ] Open search, select the "Paroles directes" filter with an empty query — results populate without typing
- [ ] Use the speaker sub-filter (Jésus / Père / Marie) — result set narrows correctly
- [ ] Enter a query while the speech filter is active — results narrow and highlight the match

### 7. B10 regression test — Promesses et bienfaits (critical)
- [ ] Open Approfondir tab in any hour, or search for "Promesses"
- [ ] Open "Promesses et bienfaits" entry P074 ("LDC 11 - 14 août 1915…")
- [ ] Confirm text is the August 1915 continuation — NOT the November 1914 entry
- [ ] Confirm P077 ("LDC 11 - 4 novembre 1914 (1ère fois)") shows correct date

### 8. Search — general
- [ ] Search for a French word (e.g. "cœur") — results appear
- [ ] Tap a Benefits result — app scrolls to the exact matched paragraph
- [ ] **Known gap:** prayer, library, and ordinary-section results open at the top of the target, not the exact matched paragraph (see Open defects) — do not fail this as a regression, it is a documented existing limitation
- [ ] Clear search returns to normal state

### 9. Prière avant chaque Heure — dynamic ordinal (R49J)
- [ ] Open Hour 1 → open "Prière avant chaque Heure" from the reader's opening buttons → paragraph 1 reads "la 1re Heure"
- [ ] Open Hour 10 (or any hour 2–24) the same way → reads "la Ne Heure" (e.g. "la 10e Heure")
- [ ] **Known gap:** opening the same prayer from the sidebar/home/search outside an active hour can still show the "(préciser)" placeholder (see Open defects) — do not fail this as a regression, it is a documented existing limitation

### 10. Highlights
- [ ] iPhone/iPad: select text in a paragraph → highlight colour picker appears → choose a colour → text is highlighted
- [ ] Samsung/Android: tap paragraph action button → full paragraph highlighted in chosen colour
- [ ] Highlights persist after closing and reopening the app

### 11. Méditée button and cycle progress
- [ ] Open any hour, tap "Méditée" — button shows "✓ Méditée", toast confirms
- [ ] Home screen daily card and progress bar update accordingly
- [ ] Tap again to un-mark — reverts, progress decrements
- [ ] ↺ cycle-restart button resets progress with confirmation prompt

### 12. Mon Espace / export-import
- [ ] Mon Espace shows Surlignages, Notes, Export/Import sections (no Favoris — removed R49I)
- [ ] Export produces a JSON file
- [ ] Import a previously exported file — confirms replacement, restores highlights/theme/settings
- [ ] **Known gap:** notes and last-read hour are not restored by import even though the confirmation says data will be replaced (see Open defects)

### 13. Dark mode
- [ ] Toggle dark mode in Réglages — all screens render correctly
- [ ] No invisible text (white on white or black on black)

### 14. PWA install (served URL only)
- [ ] "Add to Home Screen" prompt appears or is available via browser menu
- [ ] Installed PWA launches in standalone mode (no browser chrome)
- [ ] App icon and name display correctly on home screen — should read "24 Heures R49j" / full name "Stage 8A/R49j"

### 15. Offline (served URL only — test after first successful online load)
- [ ] Enable airplane mode
- [ ] Close and reopen the installed PWA
- [ ] App loads and is fully usable offline

### 16. Update banner (served URL only)
- [ ] If testing with a previously cached version, update banner should appear
- [ ] Tapping the banner reloads to the new version

### 17. Data persistence
- [ ] Highlights, notes, read progress, repères d'étude state all survive app close and reopen
- [ ] Mon Espace shows correct highlights and notes

---

## Pass criteria for L2

All scenarios in sections 1–13 must PASS on at least iPad Safari and iPhone Safari (excluding the documented "Known gap" items, which are tracked as open defects, not test failures).
Sections 14–16 require the live URL.
Any P0 failure (app crash, data loss, broken navigation) blocks L2 certification.

---

## Result recording

Fill in `REAL_DEVICE_QA_RESULTS_TEMPLATE.csv` — one row per scenario per device.
Result values: PASS / FAIL / PARTIAL / SKIP
Include: device model, OS version, browser version, tester name, date.
