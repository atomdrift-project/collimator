# Confirm FAIL — f66d05dfe8e86388 on `filetypes/pdf`

Cycle `20260615T062829-confirm-f66d05dfe8e86388` — 2026-06-15T06:28:29Z

averaged ensemble PR_AUC regressed: 1.0000 -> 0.9915 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f66d05dfe8e86388` | `38fcbea211002f16` | `38fcbea211002f16` | `38fcbea211002f16` |
| PR AUC | 1.0000 | 0.9894 | 0.9915 | 0.9894 |
| ROC AUC | 0.9989 | 0.5000 | 0.5979 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
