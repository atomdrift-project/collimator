# Confirm FAIL — 58982c397ebc88ff on `filetypes/go`

Cycle `20260808T223921-confirm-58982c397ebc88ff` — 2026-08-08T22:39:21Z

averaged ensemble PR_AUC regressed: 0.4782 -> 0.3409 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `58982c397ebc88ff` | `f153e682f5fcee82` | `f153e682f5fcee82` | `f153e682f5fcee82` |
| PR AUC | 0.4782 | 0.3421 | 0.3302 | 0.3382 |
| ROC AUC | 0.7431 | 0.7372 | 0.7351 | 0.7390 |
| Recall@L50 | — | 0.1568 | 0.1612 | 0.1711 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
