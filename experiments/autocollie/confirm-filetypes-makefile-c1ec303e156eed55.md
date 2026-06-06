# Confirm FAIL — c1ec303e156eed55 on `filetypes/makefile`

Cycle `20260606T180837-confirm-c1ec303e156eed55` — 2026-06-06T18:08:37Z

averaged ensemble PR_AUC regressed: 0.9167 -> 0.8309 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c1ec303e156eed55` | `b87efbb33cda7210` | `b87efbb33cda7210` | `b87efbb33cda7210` |
| PR AUC | 0.9167 | 0.8255 | 0.8108 | 0.8326 |
| ROC AUC | 0.9994 | 0.9801 | 0.9731 | 0.9772 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
