# Confirm FAIL — e4ef9e9af34ffbac on `filetypes/jpeg`

Cycle `20260527T010528-confirm-e4ef9e9af34ffbac` — 2026-05-27T01:05:28Z

averaged ensemble PR_AUC regressed: 0.9798 -> 0.9707 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e4ef9e9af34ffbac` | `5c7a7dad41d27ae5` | `5c7a7dad41d27ae5` | `5c7a7dad41d27ae5` |
| PR AUC | 0.9798 | 0.9767 | 0.9671 | 0.9712 |
| ROC AUC | 0.9839 | 0.9806 | 0.9749 | 0.9771 |
| Recall@3FPM | — | 0.8000 | 0.6400 | 0.7200 |
| verdict | — | PASS | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (1/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
