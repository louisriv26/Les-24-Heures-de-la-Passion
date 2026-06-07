# Deployment handoff — prototype-76

Package: `luisa_24_heures_app_v76_stage5h_android_samsung_scroll_repair_locked.zip`

Stage: Stage 5H — Android/Samsung main content scroll repair

Deploy the contents of this folder or the nested `luisa_24h_github_deploy.zip` to GitHub Pages.

Primary change:

- Android/Samsung-only main-content scroll repair. Aide already had independent modal scrolling; this patch gives the main app pages an explicit Android content scroll root.

Real-device validation remains required for:

- Samsung/Android Chrome or Samsung Internet: Accueil, Heure complète, Textes, Mon Espace, and Aide must all scroll correctly;
- iPhone Safari and installed iPhone PWA regression;
- iPad Safari portrait and landscape regression;
- highlighting/text selection;
- update banner;
- offline/PWA behaviour.
