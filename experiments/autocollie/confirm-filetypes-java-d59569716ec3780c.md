# Confirm FAIL — d59569716ec3780c on `filetypes/java`

Cycle `20260804T230439-confirm-d59569716ec3780c` — 2026-08-04T23:04:39Z

averaged ensemble PR_AUC regressed: 0.8282 -> 0.7371 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d59569716ec3780c` | `13b9c156a24de0ed` | `13b9c156a24de0ed` | `13b9c156a24de0ed` |
| PR AUC | 0.8282 | 0.7244 | 0.7161 | 0.7136 |
| ROC AUC | 0.9815 | 0.9767 | 0.9788 | 0.9783 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
