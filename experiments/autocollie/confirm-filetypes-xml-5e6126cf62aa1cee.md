# Confirm FAIL — 5e6126cf62aa1cee on `filetypes/xml`

Cycle `20260821T131032-confirm-5e6126cf62aa1cee` — 2026-08-21T13:10:32Z

averaged ensemble PR_AUC regressed: 0.2599 -> 0.1757 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `5e6126cf62aa1cee` | `c51ac9ca724a5437` | `c51ac9ca724a5437` | `c51ac9ca724a5437` |
| PR AUC | 0.2599 | 0.1939 | 0.1713 | 0.1692 |
| ROC AUC | 0.6650 | 0.6853 | 0.7094 | 0.6869 |
| Recall@L50 | — | 0.1171 | 0.1171 | 0.1104 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
