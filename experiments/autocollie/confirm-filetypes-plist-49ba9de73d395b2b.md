# Confirm FAIL — 49ba9de73d395b2b on `filetypes/plist`

Cycle `20260805T015950-confirm-49ba9de73d395b2b` — 2026-08-05T01:59:50Z

averaged ensemble PR_AUC regressed: 0.1486 -> 0.1259 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `49ba9de73d395b2b` | `3a87ea2594c44e2e` | `3a87ea2594c44e2e` | `3a87ea2594c44e2e` |
| PR AUC | 0.1486 | 0.1160 | 0.0911 | 0.1311 |
| ROC AUC | 0.7637 | 0.7793 | 0.6867 | 0.7839 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
