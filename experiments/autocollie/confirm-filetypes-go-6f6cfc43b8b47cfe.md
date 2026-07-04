# Confirm FAIL — 6f6cfc43b8b47cfe on `filetypes/go`

Cycle `20260704T114307-confirm-6f6cfc43b8b47cfe` — 2026-07-04T11:43:07Z

averaged ensemble PR_AUC regressed: 0.9575 -> 0.9075 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `6f6cfc43b8b47cfe` | `afd329e8ea539149` | `afd329e8ea539149` | `afd329e8ea539149` |
| PR AUC | 0.9575 | 0.9046 | 0.9042 | 0.9047 |
| ROC AUC | 0.9847 | 0.9660 | 0.9665 | 0.9654 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
