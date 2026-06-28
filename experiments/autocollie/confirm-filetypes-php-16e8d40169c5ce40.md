# Confirm FAIL — 16e8d40169c5ce40 on `filetypes/php`

Cycle `20260628T135054-confirm-16e8d40169c5ce40` — 2026-06-28T13:50:54Z

averaged ensemble PR_AUC regressed: 0.9949 -> 0.9862 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `16e8d40169c5ce40` | `bd0f79ed8e46d2d8` | `bd0f79ed8e46d2d8` | `bd0f79ed8e46d2d8` |
| PR AUC | 0.9949 | 0.9846 | 0.9853 | 0.9862 |
| ROC AUC | 0.9977 | 0.9958 | 0.9960 | 0.9960 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
