# Confirm FAIL — 8cdedfd52f49dc78 on `filetypes/makefile`

Cycle `20260606T180825-confirm-8cdedfd52f49dc78` — 2026-06-06T18:08:25Z

averaged ensemble PR_AUC regressed: 0.9501 -> 0.8303 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `8cdedfd52f49dc78` | `77cc23666f6b3f55` | `77cc23666f6b3f55` | `77cc23666f6b3f55` |
| PR AUC | 0.9501 | 0.8305 | 0.8140 | 0.8304 |
| ROC AUC | 0.9996 | 0.9778 | 0.9700 | 0.9754 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
