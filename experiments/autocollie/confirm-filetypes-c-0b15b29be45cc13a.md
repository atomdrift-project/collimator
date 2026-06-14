# Confirm FAIL — 0b15b29be45cc13a on `filetypes/c`

Cycle `20260613T220053-confirm-0b15b29be45cc13a` — 2026-06-13T22:00:53Z

averaged ensemble PR_AUC regressed: 0.9904 -> 0.9751 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `0b15b29be45cc13a` | `c92647089519d708` | `c92647089519d708` | `c92647089519d708` |
| PR AUC | 0.9904 | 0.9737 | 0.9748 | 0.9746 |
| ROC AUC | 0.9951 | 0.9884 | 0.9881 | 0.9882 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
