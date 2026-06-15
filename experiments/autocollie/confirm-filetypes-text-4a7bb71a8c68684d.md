# Confirm FAIL — 4a7bb71a8c68684d on `filetypes/text`

Cycle `20260615T055154-confirm-4a7bb71a8c68684d` — 2026-06-15T05:51:54Z

averaged ensemble PR_AUC regressed: 0.9473 -> 0.9390 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `4a7bb71a8c68684d` | `429be18d4d9583d7` | `429be18d4d9583d7` | `429be18d4d9583d7` |
| PR AUC | 0.9473 | 0.9320 | 0.9431 | 0.9381 |
| ROC AUC | 0.9752 | 0.9638 | 0.9695 | 0.9700 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | PASS | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (1/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
