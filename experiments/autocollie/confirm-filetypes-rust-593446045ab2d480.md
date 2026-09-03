# Confirm FAIL — 593446045ab2d480 on `filetypes/rust`

Cycle `20260825T214630-confirm-593446045ab2d480` — 2026-08-25T21:46:30Z

averaged ensemble PR_AUC regressed: 0.2585 -> 0.1826 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `593446045ab2d480` | `b7932f337fbbe810` | `b7932f337fbbe810` | `b7932f337fbbe810` |
| PR AUC | 0.2585 | 0.1423 | 0.1565 | 0.1683 |
| ROC AUC | 0.7836 | 0.8351 | 0.8328 | 0.8440 |
| Recall@L50 | — | 0.0165 | 0.0041 | 0.0247 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
