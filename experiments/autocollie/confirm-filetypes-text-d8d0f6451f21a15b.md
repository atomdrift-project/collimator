# Confirm FAIL — d8d0f6451f21a15b on `filetypes/text`

Cycle `20260703T011936-confirm-d8d0f6451f21a15b` — 2026-07-03T01:19:36Z

averaged ensemble PR_AUC regressed: 0.8689 -> 0.8606 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d8d0f6451f21a15b` | `5f3e2ea1e10c35b0` | `5f3e2ea1e10c35b0` | `5f3e2ea1e10c35b0` |
| PR AUC | 0.8689 | 0.8613 | 0.8377 | 0.8486 |
| ROC AUC | 0.9154 | 0.9410 | 0.9168 | 0.9283 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
