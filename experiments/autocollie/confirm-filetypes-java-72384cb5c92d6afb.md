# Confirm FAIL — 72384cb5c92d6afb on `filetypes/java`

Cycle `20260803T205728-confirm-72384cb5c92d6afb` — 2026-08-03T20:57:28Z

averaged ensemble PR_AUC regressed: 0.8118 -> 0.7396 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `72384cb5c92d6afb` | `e4c546b801dc0861` | `e4c546b801dc0861` | `e4c546b801dc0861` |
| PR AUC | 0.8118 | 0.7185 | 0.7419 | 0.7109 |
| ROC AUC | 0.9808 | 0.9815 | 0.9804 | 0.9801 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
