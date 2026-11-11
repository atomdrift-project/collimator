# Confirm FAIL — 69b2a241d77d0e8b on `filetypes/deb`

Cycle `20261106T195336-confirm-69b2a241d77d0e8b` — 2026-11-06T19:53:36Z

averaged ensemble PR_AUC regressed: 0.3133 -> 0.2313 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `69b2a241d77d0e8b` | `40012f4f483add3c` | `40012f4f483add3c` | `40012f4f483add3c` |
| PR AUC | 0.3133 | 0.2122 | 0.0730 | 0.2114 |
| ROC AUC | 0.8047 | 0.7926 | 0.5810 | 0.7469 |
| Recall@L50 | — | 0.1429 | — | 0.1429 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
