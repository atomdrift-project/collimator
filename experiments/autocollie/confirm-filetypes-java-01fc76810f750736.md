# Confirm FAIL — 01fc76810f750736 on `filetypes/java`

Cycle `20260628T132032-confirm-01fc76810f750736` — 2026-06-28T13:20:32Z

averaged ensemble PR_AUC regressed: 0.9704 -> 0.9263 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `01fc76810f750736` | `944d0c7c087e236e` | `944d0c7c087e236e` | `944d0c7c087e236e` |
| PR AUC | 0.9704 | 0.9171 | 0.9192 | 0.9312 |
| ROC AUC | 0.9872 | 0.9683 | 0.9788 | 0.9818 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
