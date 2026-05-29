# Confirm FAIL — 702c6e2b84541626 on `filetypes/kotlin`

Cycle `20260526T225625-confirm-702c6e2b84541626` — 2026-05-26T22:56:25Z

averaged ensemble PR_AUC regressed: 0.9999 -> 0.9903 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `702c6e2b84541626` | `8b71626b42d26721` | `8b71626b42d26721` | `8b71626b42d26721` |
| PR AUC | 0.9999 | 0.9903 | 0.9903 | 0.9903 |
| ROC AUC | 0.9956 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
