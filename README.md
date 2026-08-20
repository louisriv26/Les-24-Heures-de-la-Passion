# 24 Heures de la Passion — v101.88

Version: `v101.88`  
Evidence stage: `T88-R1`

## v101.88 — exact Approfondir title-text selection

Real iPhone feedback proved that v101.87 still did not implement the required feature: selecting part of an Approfondir title did not enter the normal annotation pipeline. v101.88 makes each visible Approfondir title a stable `PASSION24.TEXT.<ID>.TITLE` text target and routes native title selection through the same Surligner / Note / Copier pipeline as body text.

The existing `libraryMarks` whole-reading store is preserved but is now presented separately as **Marquer cette lecture**. It no longer rewrites or colours the title text.

Storage remains schema 8 / snapshot 5. Corpus, source text, speech data and paragraph IDs are unchanged.

Service-worker cache generation: `luisa-24h-v101-88`.

The exact physical-iPhone title-selection gate remains NOT_TESTED until this exact package is tested on the reporting iPhone.
