# Confirm FAIL — 1b8083fa32ece294 on `filegroups/source`

Cycle `20260703T025751-confirm-1b8083fa32ece294` — 2026-07-03T02:57:51Z

averaged ensemble PR_AUC regressed: 0.8717 -> 0.5378 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `1b8083fa32ece294` | `ad8049cc8e521376` | `ad8049cc8e521376` | `ad8049cc8e521376` |
| PR AUC | 0.8717 | 0.5370 | 0.5205 | 0.5188 |
| ROC AUC | 0.8515 | 0.8782 | 0.8733 | 0.8850 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
