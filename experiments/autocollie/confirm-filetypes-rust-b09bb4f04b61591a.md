# Confirm FAIL — b09bb4f04b61591a on `filetypes/rust`

Cycle `20260602T013731-confirm-b09bb4f04b61591a` — 2026-06-02T01:37:31Z

averaged ensemble PR_AUC regressed: 0.9280 -> 0.8934 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b09bb4f04b61591a` | `e669137406de6d8a` | `e669137406de6d8a` | `e669137406de6d8a` |
| PR AUC | 0.9280 | 0.8932 | 0.8890 | 0.8921 |
| ROC AUC | 0.9902 | 0.9881 | 0.9872 | 0.9895 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
