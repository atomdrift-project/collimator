# Confirm FAIL — 90ee656a6e193b6b on `filetypes/powershell`

Cycle `20260628T130252-confirm-90ee656a6e193b6b` — 2026-06-28T13:02:52Z

averaged ensemble PR_AUC regressed: 0.9934 -> 0.9877 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `90ee656a6e193b6b` | `ef1ded27a5a58018` | `ef1ded27a5a58018` | `ef1ded27a5a58018` |
| PR AUC | 0.9934 | 0.9872 | 0.9874 | 0.9876 |
| ROC AUC | 0.9837 | 0.9776 | 0.9784 | 0.9786 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
