# Confirm FAIL — 9445b9b1b5c81388 on `filetypes/c`

Cycle `20260628T125134-confirm-9445b9b1b5c81388` — 2026-06-28T12:51:34Z

averaged ensemble PR_AUC regressed: 0.9848 -> 0.9766 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `9445b9b1b5c81388` | `d428888d00b63360` | `d428888d00b63360` | `d428888d00b63360` |
| PR AUC | 0.9848 | 0.9758 | 0.9744 | 0.9756 |
| ROC AUC | 0.9928 | 0.9915 | 0.9911 | 0.9914 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
