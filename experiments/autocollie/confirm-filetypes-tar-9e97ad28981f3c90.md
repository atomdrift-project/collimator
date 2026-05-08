# Confirm FAIL — 9e97ad28981f3c90 on `filetypes/tar`

Cycle `20260508T202739-confirm-9e97ad28981f3c90` — 2026-05-08T20:27:39Z

averaged ensemble F1 regressed: 1.0000 -> 0.9406 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `9e97ad28981f3c90` | `b35161e08868fce5` | `b35161e08868fce5` | `b35161e08868fce5` |
| F1 | 1.0000 | 0.9953 | 0.9458 | 0.9662 |
| ROC AUC | 1.0000 | 0.9992 | 1.0000 | 1.0000 |
| AP | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| recall@3 FP/M | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| verdict | — | PASS | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (1/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
