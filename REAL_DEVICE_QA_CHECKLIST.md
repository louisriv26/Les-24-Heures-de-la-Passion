# Real-device QA — Les 24 Heures de la Passion · R47

App version: `prototype-101r59-stage7d-r47-meditation-ux`  
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

### 3. Prier / Étudier mode
- [ ] Default mode is Prier (prayer — clean reading, no para numbers or action buttons)
- [ ] Tapping the mode pill (✝/✏) switches to Étudier (study — para numbers visible, action buttons visible)
- [ ] Mode persists after closing and reopening the app

### 4. Favourites — scroll-to-para (R46 regression test)
- [ ] In any hour, add a paragraph to favourites (✦ button in Étudier mode)
- [ ] Navigate away (home screen)
- [ ] Open Mon Espace → Favoris, tap the saved favourite
- [ ] App opens the correct hour and **scrolls to the saved paragraph** (not top of page)
- [ ] Repeat with a paragraph from Promesses et bienfaits (text library)

### 5. B10 regression test — Promesses et bienfaits (critical)
- [ ] Open Approfondir tab in any hour, or search for "Promesses"
- [ ] Open "Promesses et bienfaits" entry P074 ("LDC 11 - 14 août 1915…")
- [ ] Confirm text is the August 1915 continuation — NOT the November 1914 entry
- [ ] Confirm P077 ("LDC 11 - 4 novembre 1914 (1ère fois)") shows correct date

### 6. Search
- [ ] Search for a French word (e.g. "cœur") — results appear
- [ ] Tap a result — app opens the correct hour and scrolls to the paragraph
- [ ] Clear search returns to normal state

### 7. Highlights
- [ ] iPhone/iPad: select text in a paragraph → highlight colour picker appears → choose a colour → text is highlighted
- [ ] Samsung/Android: tap paragraph action button → full paragraph highlighted in chosen colour
- [ ] Highlights persist after closing and reopening the app

### 8. Help modal and toast (R45b regression test)
- [ ] Open ⚙ Réglages → ? (help) modal opens
- [ ] Tap "Rechercher une mise à jour" button
- [ ] Toast "Vous avez déjà la dernière version" (or update prompt) appears **above** the modal, not hidden behind it

### 9. Dark mode
- [ ] Toggle dark mode in Réglages — all screens render correctly
- [ ] No invisible text (white on white or black on black)

### 10. R47 — Unified Méditée button (NEW)
- [ ] Open any hour
- [ ] Confirm there is **no** "Méditée aujourd'hui / Appuyez après votre méditation" bar at the top of the reader
- [ ] Confirm there is **no** "Marquer lue" button — only a single "Méditée" button in the bottom nav
- [ ] Tap "Méditée" — button label changes to "✓ Méditée" and toast "✓ Xe Heure méditée" appears
- [ ] Return to home screen — daily card at top shows the hour as today's méditée hour
- [ ] Progress bar on home screen increments
- [ ] Re-open the same hour — button shows "✓ Méditée"
- [ ] Tap again to un-mark — button reverts to "Méditée", progress decrements

### 11. R47 — Tappable done daily card (NEW)
- [ ] Mark any hour as méditée (see scenario 10)
- [ ] Return to home screen
- [ ] Daily card shows "Méditée aujourd'hui" with the hour title and an arrow (→)
- [ ] Tap the daily card — app navigates to the **next** hour (not stays on done)
- [ ] If hour 24 has been méditée, daily card shows "Cycle accompli" with "↺ Recommencer le cycle"

### 12. R47 — Cycle restart shortcut (NEW)
- [ ] Mark at least one hour as méditée so the progress strip is visible
- [ ] Progress strip shows "Progression du cycle", the bar, a count (X/24), and a ↺ button
- [ ] Tap ↺ — a confirmation prompt resets the cycle (progress returns to 0/24)
- [ ] (If hour 24 was méditée) Confirm "Recommencer le cycle" link in the cycle-complete daily card also triggers the reset

### 13. PWA install (served URL only)
- [ ] "Add to Home Screen" prompt appears or is available via browser menu
- [ ] Installed PWA launches in standalone mode (no browser chrome)
- [ ] App icon and name display correctly on home screen

### 14. Offline (served URL only — test after first successful online load)
- [ ] Enable airplane mode
- [ ] Close and reopen the installed PWA
- [ ] App loads and is fully usable offline

### 15. Update banner (served URL only)
- [ ] If testing with a previously cached version, update banner should appear
- [ ] Tapping the banner reloads to the new version

### 16. 24-day cycle progress
- [ ] Reading an hour marks it as read (progress counter increments)
- [ ] Progress persists after close/reopen
- [ ] "Reprendre la lecture" button on home screen navigates to the next unread hour

### 17. Data persistence
- [ ] Favourites, highlights, read progress all survive app close and reopen
- [ ] Mon Espace shows correct favourites and highlights

---

## Pass criteria for L2

All scenarios in sections 1–12 must PASS on at least iPad Safari and iPhone Safari.  
Sections 13–15 require the live URL.  
Any P0 failure (app crash, data loss, broken navigation) blocks L2 certification.

---

## Result recording

Fill in `REAL_DEVICE_QA_RESULTS_TEMPLATE.csv` — one row per scenario per device.  
Result values: PASS / FAIL / PARTIAL / SKIP  
Include: device model, OS version, browser version, tester name, date.
