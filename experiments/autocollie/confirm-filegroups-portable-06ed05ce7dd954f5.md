# Confirm FAIL — 06ed05ce7dd954f5 on `filegroups/portable`

Cycle `20260705T162738-confirm-06ed05ce7dd954f5` — 2026-07-05T16:27:38Z

averaged ensemble PR_AUC regressed: 0.8541 -> 0.2130 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `06ed05ce7dd954f5` | `99be126c900d30be` | `99be126c900d30be` | `99be126c900d30be` |
| PR AUC | 0.8541 | 0.1109 | 0.0021 | 0.1748 |
| ROC AUC | 0.9358 | 0.5102 | 0.1305 | 0.5742 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
