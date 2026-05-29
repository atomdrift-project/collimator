# Confirm FAIL — 7224b277b744c023 on `filetypes/jpeg`

Cycle `20260527T010541-confirm-7224b277b744c023` — 2026-05-27T01:05:41Z

averaged ensemble PR_AUC regressed: 0.9740 -> 0.9660 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `7224b277b744c023` | `c3a8d45e467836b4` | `c3a8d45e467836b4` | `c3a8d45e467836b4` |
| PR AUC | 0.9740 | 0.9705 | 0.9664 | 0.9665 |
| ROC AUC | 0.9789 | 0.9749 | 0.9737 | 0.9726 |
| Recall@3FPM | — | 0.8000 | 0.6800 | 0.7200 |
| verdict | — | PASS | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (1/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
