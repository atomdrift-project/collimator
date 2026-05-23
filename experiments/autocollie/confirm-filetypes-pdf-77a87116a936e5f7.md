# Confirm FAIL — 77a87116a936e5f7 on `filetypes/pdf`

Cycle `20260523T174931-confirm-77a87116a936e5f7` — 2026-05-23T17:49:31Z

averaged ensemble PR_AUC regressed: 1.0000 -> 0.9942 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `77a87116a936e5f7` | `a22c3d3c9c4cb245` | `a22c3d3c9c4cb245` | `a22c3d3c9c4cb245` |
| PR AUC | 1.0000 | 0.9942 | 0.9942 | 0.9942 |
| ROC AUC | 0.9994 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
