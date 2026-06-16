# Confirm FAIL — 7a762ac3ce925a0f on `filetypes/plist`

Cycle `20260616T051654-confirm-7a762ac3ce925a0f` — 2026-06-16T05:16:54Z

averaged ensemble PR_AUC regressed: 0.2233 -> 0.1384 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `7a762ac3ce925a0f` | `5f71b08d598d2aed` | `5f71b08d598d2aed` | `5f71b08d598d2aed` |
| PR AUC | 0.2233 | 0.0601 | 0.1705 | 0.0972 |
| ROC AUC | 0.7398 | 0.5273 | 0.7814 | 0.4117 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
