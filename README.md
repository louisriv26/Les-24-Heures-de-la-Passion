# Luisa — 24 Heures de la Passion

Version: `v101.87`
Stage: `T87-R1`
Build date: `2026-08-19`

## v101.87 — real-device title-marker interaction repair

Real-device feedback proved that the v101.86 Approfondir title marker was not reliable on the user's physical device despite Chromium tests. v101.87 preserves the stable `libraryMarks` whole-reading model and the inline body-style title highlight, and repairs the mobile event-isolation omission: `libraryMarkerPicker` and the title-marker controls are now protected by the same selection/touch isolation used by ordinary highlight UI.

The service-worker cache generation is bumped to `luisa-24h-v101-87` so the repaired runtime is not served from the v101.86 cache generation.

No devotional/corpus/speech structure changed. Storage remains schema 8 / snapshot 5.

Physical-device confirmation of the exact v101.87 build remains mandatory before the title feature is considered closed.

Runtime SHA-256: `c8b599bf10d31099e33ba54cb64801d17d4ae8df1ed7c7ba7e6009eda275ff99`
