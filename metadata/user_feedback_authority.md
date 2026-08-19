# Real-device authority — 19 August 2026

User reports that Approfondir title highlighting still does not work on the physical device. This overrides prior Chromium-only PASS evidence for that feature. Code inspection identifies omission of `libraryMarkerPicker` from the shared mobile highlight event-isolation layer. v101.87 repairs that omission. Physical-device confirmation remains required.
