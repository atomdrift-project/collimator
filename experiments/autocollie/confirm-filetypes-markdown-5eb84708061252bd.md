# Confirm FAIL — 5eb84708061252bd on `filetypes/markdown`

Cycle `20261110T195304-confirm-5eb84708061252bd` — 2026-11-10T19:53:04Z

confirmation measured L25 recall regressed: 0.81250 -> 0.75000

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `5eb84708061252bd` | `18d65a3206a41024` | `18d65a3206a41024` | `18d65a3206a41024` |
| PR AUC | 0.7705 | 0.7744 | 0.7750 | 0.7837 |
| ROC AUC | 0.9369 | 0.9379 | 0.9554 | 0.9474 |
| Recall@L50 | — | 0.3125 | 0.3750 | 0.3750 |
| verdict | — | PASS | PASS | PASS |

## Disposition

This spec did not survive multi-seed reseeding (3/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
