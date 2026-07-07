# Confirm FAIL — 9165276b845f9226 on `filegroups/source`

Cycle `20260705T182819-confirm-9165276b845f9226` — 2026-07-05T18:28:19Z

averaged ensemble PR_AUC regressed: 0.8644 -> 0.5262 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `9165276b845f9226` | `1539b23c1c278395` | `1539b23c1c278395` | `1539b23c1c278395` |
| PR AUC | 0.8644 | 0.5122 | 0.5155 | 0.5105 |
| ROC AUC | 0.8468 | 0.8696 | 0.8696 | 0.8594 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
