# Confirm FAIL — 58852d9209ce56a6 on `filetypes/groovy`

Cycle `20261106T011521-confirm-58852d9209ce56a6` — 2026-11-06T01:15:21Z

averaged ensemble PR_AUC regressed: 0.8857 -> 0.8672 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `58852d9209ce56a6` | `ee7384b48fb5cde4` | `ee7384b48fb5cde4` | `ee7384b48fb5cde4` |
| PR AUC | 0.8857 | 0.8705 | 0.8654 | 0.8786 |
| ROC AUC | 0.9971 | 0.9965 | 0.9954 | 0.9958 |
| Recall@L50 | — | 0.7500 | 0.7500 | 0.7500 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
