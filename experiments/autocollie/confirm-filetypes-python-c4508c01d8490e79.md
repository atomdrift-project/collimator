# Confirm FAIL — c4508c01d8490e79 on `filetypes/python`

Cycle `20260705T163028-confirm-c4508c01d8490e79` — 2026-07-05T16:30:28Z

averaged ensemble PR_AUC regressed: 0.9138 -> 0.8431 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c4508c01d8490e79` | `f9d880e4cf3b2a2f` | `f9d880e4cf3b2a2f` | `f9d880e4cf3b2a2f` |
| PR AUC | 0.9138 | 0.8432 | 0.8407 | 0.8434 |
| ROC AUC | 0.9464 | 0.9501 | 0.9458 | 0.9518 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
