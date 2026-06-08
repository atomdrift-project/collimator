# Confirm FAIL — 4d37190c17fa2760 on `filetypes/plist`

Cycle `20260608T110815-confirm-4d37190c17fa2760` — 2026-06-08T11:08:15Z

averaged ensemble PR_AUC regressed: 0.2830 -> 0.2414 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `4d37190c17fa2760` | `8fb357525b86e1b2` | `8fb357525b86e1b2` | `8fb357525b86e1b2` |
| PR AUC | 0.2830 | 0.2209 | 0.2445 | 0.1914 |
| ROC AUC | 0.8184 | 0.7923 | 0.8051 | 0.7568 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
