# Confirm FAIL — 1a99e19fdadd1f4c on `filetypes/rust`

Cycle `20260608T161649-confirm-1a99e19fdadd1f4c` — 2026-06-08T16:16:49Z

averaged ensemble PR_AUC regressed: 0.1091 -> 0.0886 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `1a99e19fdadd1f4c` | `f90825686aa49bf3` | `f90825686aa49bf3` | `f90825686aa49bf3` |
| PR AUC | 0.1091 | 0.0970 | 0.0883 | 0.0869 |
| ROC AUC | 0.7178 | 0.5253 | 0.4730 | 0.4990 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
