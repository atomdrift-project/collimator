# Confirm FAIL — 8b54303f1c4f4c1d on `filetypes/plist`

Cycle `20260712T110619-confirm-8b54303f1c4f4c1d` — 2026-07-12T11:06:19Z

averaged ensemble PR_AUC regressed: 1.0000 -> 0.9000 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `8b54303f1c4f4c1d` | `e1deca96da5c67a2` | `e1deca96da5c67a2` | `e1deca96da5c67a2` |
| PR AUC | 1.0000 | 0.8889 | 0.8860 | 0.8788 |
| ROC AUC | 1.0000 | 0.9914 | 0.9840 | 0.9802 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
