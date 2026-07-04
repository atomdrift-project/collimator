# Confirm FAIL — f2b2b446ac8a9e7a on `filegroups/media`

Cycle `20260704T135109-confirm-f2b2b446ac8a9e7a` — 2026-07-04T13:51:09Z

averaged ensemble PR_AUC regressed: 0.3511 -> 0.1242 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f2b2b446ac8a9e7a` | `5aebdc4c2334ff75` | `5aebdc4c2334ff75` | `5aebdc4c2334ff75` |
| PR AUC | 0.3511 | 0.1339 | 0.1204 | 0.1213 |
| ROC AUC | 0.7655 | 0.6491 | 0.4375 | 0.4482 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
