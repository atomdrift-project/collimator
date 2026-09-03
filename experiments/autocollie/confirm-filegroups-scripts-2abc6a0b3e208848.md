# Confirm FAIL — 2abc6a0b3e208848 on `filegroups/scripts`

Cycle `20260824T234703-confirm-2abc6a0b3e208848` — 2026-08-24T23:47:03Z

averaged ensemble PR_AUC regressed: 0.9878 -> 0.9455 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `2abc6a0b3e208848` | `c919c1c9caf5543a` | `c919c1c9caf5543a` | `c919c1c9caf5543a` |
| PR AUC | 0.9878 | 0.9534 | 0.9266 | 0.9487 |
| ROC AUC | 0.9856 | 0.9899 | 0.9867 | 0.9893 |
| Recall@L50 | — | 0.4121 | 0.4527 | 0.4404 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
