# Confirm FAIL — d2b59c4f02ac41b6 on `filetypes/php`

Cycle `20260526T215209-confirm-d2b59c4f02ac41b6` — 2026-05-26T21:52:09Z

averaged ensemble PR_AUC regressed: 1.0000 -> 0.9925 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d2b59c4f02ac41b6` | `e19dbcccb7ab14f8` | `e19dbcccb7ab14f8` | `e19dbcccb7ab14f8` |
| PR AUC | 1.0000 | 0.9936 | 0.9917 | 0.9913 |
| ROC AUC | 1.0000 | 0.9966 | 0.9965 | 0.9958 |
| Recall@3FPM | — | 0.2877 | 0.1187 | 0.1301 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
