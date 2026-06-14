# Confirm FAIL — 3bfe25ee03038bbb on `filetypes/php`

Cycle `20260613T234012-confirm-3bfe25ee03038bbb` — 2026-06-13T23:40:12Z

averaged ensemble PR_AUC regressed: 0.8324 -> 0.8064 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3bfe25ee03038bbb` | `757fd6e2825ce1db` | `757fd6e2825ce1db` | `757fd6e2825ce1db` |
| PR AUC | 0.8324 | 0.8075 | 0.8059 | 0.8050 |
| ROC AUC | 0.9368 | 0.9357 | 0.9215 | 0.9358 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
