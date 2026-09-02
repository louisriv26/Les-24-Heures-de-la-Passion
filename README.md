# Les 24 Heures de la Passion — v101.128

UX-only successor of immutable v101.127.

## Méditée recovery access

- Keeps the normal bottom `Méditée` action.
- Activates a discreet recovery/status control under the Hour header for users who forgot to mark the Hour at the end.
- Uses one state authority (`state.readHours`) and one mutation path (`markMeditee`).
- Adds no corpus/devotional-text, speaker, continuity-authority, storage-schema or snapshot-schema changes.

## Validation boundary

Package-local evidence is pre-final-reopen. Physical devices, installed-PWA update, true offline cold reopen, VoiceOver/TalkBack and live GitHub Pages exact-byte binding remain external gates.
