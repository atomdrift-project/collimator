# Confirm FAIL — 1b2f9045267af70e on `filetypes/java`

Cycle `20260527T053537-confirm-1b2f9045267af70e` — 2026-05-27T05:35:37Z

averaged ensemble PR_AUC regressed: 0.5435 -> 0.5067 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `1b2f9045267af70e` | `630aeb17283e935a` | `630aeb17283e935a` | `630aeb17283e935a` |
| PR AUC | 0.5435 | 0.3178 | 0.5385 | 0.5400 |
| ROC AUC | 0.7708 | 0.7188 | 0.7396 | 0.7500 |
| Recall@3FPM | — | 0.0000 | 0.3333 | 0.3333 |
| verdict | — | FAIL | FAIL | PASS |

## Disposition

This spec did not survive multi-seed reseeding (1/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
