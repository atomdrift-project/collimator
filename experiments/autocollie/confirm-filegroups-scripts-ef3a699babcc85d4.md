# Confirm FAIL — ef3a699babcc85d4 on `filegroups/scripts`

Cycle `20260805T003925-confirm-ef3a699babcc85d4` — 2026-08-05T00:39:25Z

averaged ensemble PR_AUC regressed: 0.9876 -> 0.9652 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `ef3a699babcc85d4` | `57e4c88436bd8d16` | `57e4c88436bd8d16` | `57e4c88436bd8d16` |
| PR AUC | 0.9876 | 0.9641 | 0.9636 | 0.9680 |
| ROC AUC | 0.9855 | 0.9897 | 0.9902 | 0.9902 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
