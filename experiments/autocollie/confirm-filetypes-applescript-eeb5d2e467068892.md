# Confirm FAIL — eeb5d2e467068892 on `filetypes/applescript`

Cycle `20261106T015830-confirm-eeb5d2e467068892` — 2026-11-06T01:58:30Z

averaged ensemble PR_AUC regressed: 0.8717 -> 0.8259 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `eeb5d2e467068892` | `cadb3822476b9fa7` | `cadb3822476b9fa7` | `cadb3822476b9fa7` |
| PR AUC | 0.8717 | 0.8341 | 0.8654 | 0.8162 |
| ROC AUC | 0.9556 | 0.9355 | 0.9388 | 0.9312 |
| Recall@L50 | — | 0.3846 | 0.4615 | 0.3077 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
