# Confirm FAIL — ccb6d89bec70bb42 on `filetypes/c`

Cycle `20260808T103730-confirm-ccb6d89bec70bb42` — 2026-08-08T10:37:30Z

averaged ensemble PR_AUC regressed: 0.7530 -> 0.4271 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `ccb6d89bec70bb42` | `25eaab96c355af9e` | `25eaab96c355af9e` | `25eaab96c355af9e` |
| PR AUC | 0.7530 | 0.4226 | 0.4184 | 0.4125 |
| ROC AUC | 0.8806 | 0.8786 | 0.8839 | 0.8436 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
