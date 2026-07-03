# Confirm FAIL — f75ef39e9b31eca7 on `filegroups/scripts`

Cycle `20260703T063411-confirm-f75ef39e9b31eca7` — 2026-07-03T06:34:11Z

averaged ensemble PR_AUC regressed: 0.9497 -> 0.7698 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f75ef39e9b31eca7` | `c6f1b974dc9edeac` | `c6f1b974dc9edeac` | `c6f1b974dc9edeac` |
| PR AUC | 0.9497 | 0.7676 | 0.7611 | 0.8298 |
| ROC AUC | 0.9498 | 0.9339 | 0.9303 | 0.9569 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
