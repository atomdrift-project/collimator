# Confirm FAIL — 3a55afa6f384e3ba on `filetypes/python`

Cycle `20260805T003350-confirm-3a55afa6f384e3ba` — 2026-08-05T00:33:50Z

averaged ensemble PR_AUC regressed: 0.9495 -> 0.8933 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3a55afa6f384e3ba` | `c1f21b8b2b3d1cad` | `c1f21b8b2b3d1cad` | `c1f21b8b2b3d1cad` |
| PR AUC | 0.9495 | 0.8891 | 0.8897 | 0.8876 |
| ROC AUC | 0.9722 | 0.9752 | 0.9730 | 0.9721 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
