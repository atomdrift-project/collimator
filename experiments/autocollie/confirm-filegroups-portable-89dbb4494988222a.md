# Confirm FAIL — 89dbb4494988222a on `filegroups/portable`

Cycle `20260606T145407-confirm-89dbb4494988222a` — 2026-06-06T14:54:07Z

averaged ensemble PR_AUC regressed: 0.9507 -> 0.9158 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `89dbb4494988222a` | `ace3845cd2e41329` | `ace3845cd2e41329` | `ace3845cd2e41329` |
| PR AUC | 0.9507 | 0.9174 | 0.9147 | 0.9144 |
| ROC AUC | 0.9953 | 0.9689 | 0.9600 | 0.9624 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
