# Confirm FAIL — bdac86367739a985 on `filetypes/png`

Cycle `20260527T004431-confirm-bdac86367739a985` — 2026-05-27T00:44:31Z

averaged ensemble PR_AUC regressed: 0.9870 -> 0.9806 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `bdac86367739a985` | `71b54825596a3388` | `71b54825596a3388` | `71b54825596a3388` |
| PR AUC | 0.9870 | 0.9698 | 0.9766 | 0.9793 |
| ROC AUC | 0.9756 | 0.9606 | 0.9606 | 0.9568 |
| Recall@3FPM | — | 0.9231 | 0.9231 | 0.9231 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
