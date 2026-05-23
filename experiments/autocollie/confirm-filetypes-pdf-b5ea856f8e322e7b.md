# Confirm FAIL — b5ea856f8e322e7b on `filetypes/pdf`

Cycle `20260523T194949-confirm-b5ea856f8e322e7b` — 2026-05-23T19:49:49Z

averaged ensemble PR_AUC regressed: 1.0000 -> 0.9942 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b5ea856f8e322e7b` | `260617df0fa14de6` | `260617df0fa14de6` | `260617df0fa14de6` |
| PR AUC | 1.0000 | 0.9942 | 0.9942 | 0.9942 |
| ROC AUC | 0.9992 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
