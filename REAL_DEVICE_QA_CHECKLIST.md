# REAL DEVICE QA — v101.89

All scenarios are **NOT_TESTED** until executed on the stated real device/build.

- G-01 — iPhone: open an Approfondir text, select part of the title, and confirm the app bar `Surligner / Note / Copier / Fermer` appears.
- G-02 — iPhone: select title text beginning at the first visible character and confirm the app bar appears.
- G-03 — iPhone: select title text ending at the last visible character and confirm the app bar appears.
- G-04 — iPhone: select words spanning a wrapped title line and confirm exact selected-text highlighting.
- G-05 — iPhone: create yellow title highlight, recolour blue, remove, then Annuler; exact range/colour must restore.
- G-06 — iPhone: mark the reading separately with `Marquer cette lecture`; existing partial title highlight must remain unchanged.
- G-07 — iPhone: body-text selection/highlighting still shows the normal app bar and works unchanged.
- G-08 — iPad: repeat G-01/G-04/G-05.
- G-09 — Samsung/Android: paragraph highlighting remains unchanged; native title word selection is not enabled.
- G-10 — installed PWA: confirm app displays v101.89 and cache generation is `luisa-24h-v101-89`.
