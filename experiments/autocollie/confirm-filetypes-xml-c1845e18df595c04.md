# Confirm FAIL — c1845e18df595c04 on `filetypes/xml`

Cycle `20260704T143245-confirm-c1845e18df595c04` — 2026-07-04T14:32:45Z

averaged ensemble PR_AUC regressed: 0.2011 -> 0.0978 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c1845e18df595c04` | `2d58058560342eb3` | `2d58058560342eb3` | `2d58058560342eb3` |
| PR AUC | 0.2011 | 0.1018 | 0.1017 | 0.0959 |
| ROC AUC | 0.6164 | 0.5076 | 0.5086 | 0.4754 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
