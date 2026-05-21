# Confirm FAIL — 526eca61405aea3c on `filetypes/text`

Cycle `20260521T065410-confirm-526eca61405aea3c` — 2026-05-21T06:54:10Z

averaged ensemble PR_AUC regressed: 0.9666 -> 0.9593 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `526eca61405aea3c` | `d7248e373dd56416` | `d7248e373dd56416` | `d7248e373dd56416` |
| PR AUC | 0.9666 | 0.9405 | 0.9671 | 0.9531 |
| ROC AUC | 0.9834 | 0.9720 | 0.9834 | 0.9738 |
| Recall@3FPM | — | 0.5909 | 0.8182 | 0.7727 |
| verdict | — | FAIL | PASS | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (1/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
