# Confirm FAIL — 5844f6904e367851 on `filetypes/php`

Cycle `20260825T223701-confirm-5844f6904e367851` — 2026-08-25T22:37:01Z

averaged ensemble PR_AUC regressed: 0.8938 -> 0.8248 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `5844f6904e367851` | `6b24e2ea8c7aaabe` | `6b24e2ea8c7aaabe` | `6b24e2ea8c7aaabe` |
| PR AUC | 0.8938 | 0.8269 | 0.8204 | 0.8162 |
| ROC AUC | 0.9601 | 0.9571 | 0.9557 | 0.9564 |
| Recall@L50 | — | 0.6423 | 0.6703 | 0.6788 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
