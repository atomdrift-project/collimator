# Confirm FAIL — 3ce56f9c51515db7 on `filetypes/ole`

Cycle `20260526T215134-confirm-3ce56f9c51515db7` — 2026-05-26T21:51:34Z

averaged ensemble PR_AUC regressed: 1.0000 -> 0.9833 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3ce56f9c51515db7` | `a4cefaac89c55c26` | `a4cefaac89c55c26` | `a4cefaac89c55c26` |
| PR AUC | 1.0000 | 0.9833 | 0.9833 | 0.9833 |
| ROC AUC | 1.0000 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
