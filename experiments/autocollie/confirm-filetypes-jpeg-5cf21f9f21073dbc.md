# Confirm FAIL — 5cf21f9f21073dbc on `filetypes/jpeg`

Cycle `20260614T044714-confirm-5cf21f9f21073dbc` — 2026-06-14T04:47:14Z

averaged ensemble PR_AUC regressed: 0.2733 -> 0.1842 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `5cf21f9f21073dbc` | `9392dc43679eee03` | `9392dc43679eee03` | `9392dc43679eee03` |
| PR AUC | 0.2733 | 0.1842 | 0.1116 | 0.1116 |
| ROC AUC | 0.6671 | 0.5952 | 0.5941 | 0.5941 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
