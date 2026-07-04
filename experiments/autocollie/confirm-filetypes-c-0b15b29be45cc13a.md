# Confirm FAIL — 0b15b29be45cc13a on `filetypes/c`

Cycle `20260704T083832-confirm-0b15b29be45cc13a` — 2026-07-04T08:38:32Z

averaged ensemble PR_AUC regressed: 0.9904 -> 0.9762 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `0b15b29be45cc13a` | `460f60e7a018cbdb` | `460f60e7a018cbdb` | `460f60e7a018cbdb` |
| PR AUC | 0.9904 | 0.9749 | 0.9759 | 0.9740 |
| ROC AUC | 0.9951 | 0.9905 | 0.9918 | 0.9905 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
