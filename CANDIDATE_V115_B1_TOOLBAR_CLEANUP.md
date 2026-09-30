# 24H v115 B1 — bounded selection-toolbar cleanup successor

Date: 30 September 2026

Predecessor: exact frozen Wave-0 candidate `v114/B1`.
Predecessor deploy ZIP SHA-256: `8aa02262e2cd77620dd2f09738eef1298fb752e939e81e900e7680917fe30d27`.
Finding: `24H-SEL-NAV-01`.

## Authorized mutation

One bounded UX repair only:

- `showHome()` dismisses the contextual selection/action toolbar with target, pending-state and DOM-selection cleanup before rendering Home;
- any pending delayed search-destination selection-clear timer is cancelled when navigating Home.

Root cause: search/selection flows can create `#contextActionBar` as a body-level UI element. The prior `showHome()` route changed the application view but did not close that toolbar. A later DOM-selection collapse did not remove an already-open toolbar, allowing stale contextual actions to remain visible on Home.

## Mechanical successor bindings

The public candidate identity advances to `v115/B1`, release sequence `115000001`, release ID `24h-v115-b1-20260930-toolbar-cleanup`. CSP inline-script hash, service-worker cache identity and canonical-shell SHA-256 are rebound mechanically to the exact successor bytes.

## Protected surfaces

No authorized semantic mutation to:

- devotional corpus / `CORPUS`;
- `TEXT_LIBRARY`;
- `SPEECH_DATA`;
- provenance public projection;
- Search semantics;
- personal-state schema or IndexedDB/Web-Locks concurrency architecture;
- backup/import logic, including the v114 32 MiB repair;
- Update-v2 protocol.

## Authority

Production deployment: **NOT AUTHORIZED**.
App-Test qualification staging: separate action.
Any further material byte change requires a new candidate identity.
