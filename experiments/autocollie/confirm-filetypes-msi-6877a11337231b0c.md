# Confirm FAIL — 6877a11337231b0c on `filetypes/msi`

Cycle `20260606T180749-confirm-6877a11337231b0c` — 2026-06-06T18:07:49Z

averaged ensemble PR_AUC regressed: 1.0000 -> 0.9850 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `6877a11337231b0c` | `2684bdbc6439829e` | `2684bdbc6439829e` | `2684bdbc6439829e` |
| PR AUC | 1.0000 | 0.9850 | 0.9850 | 0.9850 |
| ROC AUC | 1.0000 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
