# Confirm FAIL — 25cc40c83dbdae07 on `filetypes/gem`

Cycle `20260704T172639-confirm-25cc40c83dbdae07` — 2026-07-04T17:26:39Z

averaged ensemble PR_AUC regressed: 0.9992 -> 0.9885 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `25cc40c83dbdae07` | `f2f283c9822740f7` | `f2f283c9822740f7` | `f2f283c9822740f7` |
| PR AUC | 0.9992 | 0.9884 | 0.9886 | 0.9882 |
| ROC AUC | 0.9996 | 0.9880 | 0.9899 | 0.9880 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
