# Confirm FAIL — fac5f53f3ccd4bc5 on `filegroups/scripts`

Cycle `20260704T164353-confirm-fac5f53f3ccd4bc5` — 2026-07-04T16:43:53Z

averaged ensemble PR_AUC regressed: 0.9510 -> 0.8174 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `fac5f53f3ccd4bc5` | `f0effa8e9032208d` | `f0effa8e9032208d` | `f0effa8e9032208d` |
| PR AUC | 0.9510 | 0.8166 | 0.8175 | 0.8210 |
| ROC AUC | 0.9553 | 0.9558 | 0.9565 | 0.9582 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
