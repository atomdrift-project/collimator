# Confirm FAIL — db37b8727e001efb on `filetypes/xml`

Cycle `20261110T105454-confirm-db37b8727e001efb` — 2026-11-10T10:54:54Z

averaged ensemble PR_AUC regressed: 0.8878 -> 0.8822 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `db37b8727e001efb` | `64d588781b4f290a` | `64d588781b4f290a` | `64d588781b4f290a` |
| PR AUC | 0.8878 | 0.8722 | 0.8859 | 0.8897 |
| ROC AUC | 0.9759 | 0.9683 | 0.9743 | 0.9689 |
| Recall@L50 | — | 0.2704 | 0.3014 | 0.3070 |
| verdict | — | FAIL | PASS | PASS |

## Disposition

This spec did not survive multi-seed reseeding (2/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
