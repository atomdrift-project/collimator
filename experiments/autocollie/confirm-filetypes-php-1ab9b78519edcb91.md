# Confirm FAIL — 1ab9b78519edcb91 on `filetypes/php`

Cycle `20260827T095347-confirm-1ab9b78519edcb91` — 2026-08-27T09:53:47Z

averaged ensemble PR_AUC regressed: 0.8913 -> 0.8285 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `1ab9b78519edcb91` | `787bbd59cdf697d2` | `787bbd59cdf697d2` | `787bbd59cdf697d2` |
| PR AUC | 0.8913 | 0.8252 | 0.8245 | 0.8229 |
| ROC AUC | 0.9656 | 0.9547 | 0.9576 | 0.9502 |
| Recall@L50 | — | 0.6816 | 0.6501 | 0.6659 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
