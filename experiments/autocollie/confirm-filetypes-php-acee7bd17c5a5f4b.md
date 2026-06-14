# Confirm FAIL — acee7bd17c5a5f4b on `filetypes/php`

Cycle `20260614T044750-confirm-acee7bd17c5a5f4b` — 2026-06-14T04:47:50Z

averaged ensemble PR_AUC regressed: 0.8293 -> 0.8182 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `acee7bd17c5a5f4b` | `b1f1b45e6a22547b` | `b1f1b45e6a22547b` | `b1f1b45e6a22547b` |
| PR AUC | 0.8293 | 0.8160 | 0.8183 | 0.8183 |
| ROC AUC | 0.9355 | 0.9272 | 0.9367 | 0.9364 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
