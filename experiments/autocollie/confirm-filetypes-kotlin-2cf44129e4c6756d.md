# Confirm FAIL — 2cf44129e4c6756d on `filetypes/kotlin`

Cycle `20260526T225624-confirm-2cf44129e4c6756d` — 2026-05-26T22:56:24Z

averaged ensemble PR_AUC regressed: 1.0000 -> 0.9903 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `2cf44129e4c6756d` | `11f44a8dabcb7c6d` | `11f44a8dabcb7c6d` | `11f44a8dabcb7c6d` |
| PR AUC | 1.0000 | 0.9903 | 0.9903 | 0.9903 |
| ROC AUC | 0.9984 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
