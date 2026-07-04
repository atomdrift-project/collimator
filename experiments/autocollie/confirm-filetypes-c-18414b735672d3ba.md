# Confirm FAIL — 18414b735672d3ba on `filetypes/c`

Cycle `20260704T083813-confirm-18414b735672d3ba` — 2026-07-04T08:38:13Z

averaged ensemble PR_AUC regressed: 0.9913 -> 0.9759 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `18414b735672d3ba` | `3ab8ac917ab5e597` | `3ab8ac917ab5e597` | `3ab8ac917ab5e597` |
| PR AUC | 0.9913 | 0.9750 | 0.9752 | 0.9750 |
| ROC AUC | 0.9956 | 0.9909 | 0.9914 | 0.9909 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
