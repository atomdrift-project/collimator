# Confirm FAIL — 3f3c33365f5463c2 on `filetypes/java_class`

Cycle `20260827T100027-confirm-3f3c33365f5463c2` — 2026-08-27T10:00:27Z

averaged ensemble PR_AUC regressed: 0.8735 -> 0.7995 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3f3c33365f5463c2` | `8280fc876225217d` | `8280fc876225217d` | `8280fc876225217d` |
| PR AUC | 0.8735 | 0.7990 | 0.7963 | 0.7752 |
| ROC AUC | 0.9461 | 0.9052 | 0.8991 | 0.8871 |
| Recall@L50 | — | 0.7303 | 0.4757 | 0.3670 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
