# Confirm FAIL — 9296d9845bd4d7f5 on `filetypes/crx`

Cycle `20261029T030601-confirm-9296d9845bd4d7f5` — 2026-10-29T03:06:01Z

averaged ensemble PR_AUC regressed: 0.8691 -> 0.8621 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `9296d9845bd4d7f5` | `dea5d4fb619611de` | `dea5d4fb619611de` | `dea5d4fb619611de` |
| PR AUC | 0.8691 | 0.8565 | 0.8649 | 0.8494 |
| ROC AUC | 0.9798 | 0.9787 | 0.9772 | 0.9761 |
| Recall@L50 | — | 0.3248 | 0.3248 | 0.3439 |
| verdict | — | FAIL | PASS | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (1/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
