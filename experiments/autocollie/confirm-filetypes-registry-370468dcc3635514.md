# Confirm FAIL — 370468dcc3635514 on `filetypes/registry`

Cycle `20261102T220227-confirm-370468dcc3635514` — 2026-11-02T22:02:27Z

averaged ensemble PR_AUC regressed: 0.9573 -> 0.9503 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `370468dcc3635514` | `b56f9413f8cc8856` | `b56f9413f8cc8856` | `b56f9413f8cc8856` |
| PR AUC | 0.9573 | 0.9562 | 0.9494 | 0.9479 |
| ROC AUC | 0.9996 | 0.9996 | 0.9996 | 0.9995 |
| Recall@L50 | — | 0.8214 | 0.8393 | 0.8393 |
| verdict | — | PASS | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (1/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
