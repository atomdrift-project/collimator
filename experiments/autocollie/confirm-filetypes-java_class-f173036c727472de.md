# Confirm FAIL — f173036c727472de on `filetypes/java_class`

Cycle `20260628T115833-confirm-f173036c727472de` — 2026-06-28T11:58:33Z

averaged ensemble PR_AUC regressed: 0.9883 -> 0.9791 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f173036c727472de` | `3d91188c3b42f2f1` | `3d91188c3b42f2f1` | `3d91188c3b42f2f1` |
| PR AUC | 0.9883 | 0.9773 | 0.9759 | 0.9786 |
| ROC AUC | 0.9979 | 0.9965 | 0.9963 | 0.9968 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
