# Confirm FAIL — fcfe7073e6d1832c on `filetypes/ruby`

Cycle `20260526T191525-confirm-fcfe7073e6d1832c` — 2026-05-26T19:15:25Z

averaged ensemble PR_AUC regressed: 1.0000 -> 0.8894 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `fcfe7073e6d1832c` | `60655c54ac030ebf` | `60655c54ac030ebf` | `60655c54ac030ebf` |
| PR AUC | 1.0000 | 0.8412 | 0.8246 | 0.8949 |
| ROC AUC | 1.0000 | 0.9963 | 0.9954 | 0.9954 |
| Recall@3FPM | — | 0.1111 | 0.1111 | 0.4444 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
