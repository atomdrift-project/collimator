# Confirm FAIL — 6fbe5966cbcdeb56 on `filetypes/java_class`

Cycle `20260628T121044-confirm-6fbe5966cbcdeb56` — 2026-06-28T12:10:44Z

averaged ensemble PR_AUC regressed: 0.8904 -> 0.8091 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `6fbe5966cbcdeb56` | `fe3e07ab72d6ad4d` | `fe3e07ab72d6ad4d` | `fe3e07ab72d6ad4d` |
| PR AUC | 0.8904 | 0.1595 | 0.8091 | 0.1595 |
| ROC AUC | 0.9556 | 0.8936 | 0.8688 | 0.8936 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
