# Real-device QA checklist — v101.121

Package under test must match the final locked ZIP SHA-256 and report `v101.121` in Aide.

## Help modal
- Open Aide from Accueil, Reader and Réglages; close it and confirm the previous screen/place is preserved.
- Confirm “Comment pratiquer les 24 Heures” is the first quick action.
- Confirm all nine quick actions jump to visible sections.
- Confirm “Passages à vérifier” clearly refers to personal highlight placement, not doubtful Luisa text.
- Confirm the direct-speech explanation distinguishes Jésus/Père/Marie attribution badges from visual dialogue continuity.
- Confirm Aide documents Réglages → Référence du passage → Partager / Copier le lien.
- Confirm Aide scrolls to the final About information on iPhone, iPad portrait/landscape and Samsung.

## Regression
- Samsung: whole-paragraph highlighting, persistence and Mon Espace.
- iPhone/iPad: exact selected-text highlighting and title highlighting.
- Reader scroll/orientation, search, notes, Mon Espace, update/Actualiser.
- Quoted-span presentation controls, including P053/P068 and nested P090.
- Installed-PWA update, true offline cold reopen, VoiceOver/TalkBack and exact live GitHub Pages byte binding.
