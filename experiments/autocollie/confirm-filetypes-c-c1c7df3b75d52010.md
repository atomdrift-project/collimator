# Confirm FAIL — c1c7df3b75d52010 on `filetypes/c`

Cycle `20260613T192505-confirm-c1c7df3b75d52010` — 2026-06-13T19:25:05Z

averaged ensemble PR_AUC regressed: 0.9862 -> 0.9769 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c1c7df3b75d52010` | `76a771940e3ea6f2` | `76a771940e3ea6f2` | `76a771940e3ea6f2` |
| PR AUC | 0.9862 | 0.9751 | 0.9771 | 0.9759 |
| ROC AUC | 0.9939 | 0.9887 | 0.9893 | 0.9888 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
