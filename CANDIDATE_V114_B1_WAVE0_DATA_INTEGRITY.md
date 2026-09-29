# 24H v114 B1 — Wave 0 data-integrity candidate

Predecessor: exact live main commit `9d55c3a3238b6dac2fbbd1b9d4a9347d284e0c69` (v111.0/R36).

This supersedes the failed/unqualified v113 Wave-0 candidate. The v113 branch remains immutable.

Authorized mutation: `BKP-24H-01` only.

- Normal JSON backups and direct imports share the same 32 MiB ceiling.
- Larger exports are still downloadable, but are named `archive-secours`, are explicitly described as not directly restorable in this version, and do not update the last-restorable-backup timestamp.
- The stale predecessor claim that 32 MiB necessarily exceeds all realistic self-exports is removed.
- Corpus, provenance, Search, personal-state schema/concurrency architecture and Update-v2 behavior remain protected.
- Production deployment is NOT authorized by candidate construction.
