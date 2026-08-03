# Confirm FAIL — 57a7e87baa9f221c on `filetypes/go`

Cycle `20260723T072109-confirm-57a7e87baa9f221c` — 2026-07-23T07:21:09Z

averaged ensemble PR_AUC regressed: 0.9562 -> 0.9485 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `57a7e87baa9f221c` | `842385a15d849709` | `842385a15d849709` | `842385a15d849709` |
| PR AUC | 0.9562 | 0.9440 | 0.9497 | 0.9464 |
| ROC AUC | 0.9787 | 0.9768 | 0.9767 | 0.9773 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
