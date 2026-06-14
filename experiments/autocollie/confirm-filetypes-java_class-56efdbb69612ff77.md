# Confirm FAIL — 56efdbb69612ff77 on `filetypes/java_class`

Cycle `20260614T201027-confirm-56efdbb69612ff77` — 2026-06-14T20:10:27Z

averaged ensemble PR_AUC regressed: 0.9221 -> 0.8460 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `56efdbb69612ff77` | `cd259e858929fe0d` | `cd259e858929fe0d` | `cd259e858929fe0d` |
| PR AUC | 0.9221 | 0.8389 | 0.8464 | 0.8427 |
| ROC AUC | 0.9708 | 0.8825 | 0.9381 | 0.9249 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
