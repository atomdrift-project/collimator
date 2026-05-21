# Confirm FAIL — 8c2da1468c354787 on `filetypes/pdf`

Cycle `20260521T071058-confirm-8c2da1468c354787` — 2026-05-21T07:10:58Z

averaged ensemble PR_AUC regressed: 1.0000 -> 0.9942 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `8c2da1468c354787` | `b12a326b64e5c657` | `b12a326b64e5c657` | `b12a326b64e5c657` |
| PR AUC | 1.0000 | 0.9942 | 0.9942 | 0.9942 |
| ROC AUC | 0.9991 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
