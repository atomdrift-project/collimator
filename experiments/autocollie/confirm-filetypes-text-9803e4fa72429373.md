# Confirm FAIL — 9803e4fa72429373 on `filetypes/text`

Cycle `20260522T172240-confirm-9803e4fa72429373` — 2026-05-22T17:22:40Z

averaged ensemble PR_AUC regressed: 0.9691 -> 0.9582 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `9803e4fa72429373` | `a064e62a5a82c381` | `a064e62a5a82c381` | `a064e62a5a82c381` |
| PR AUC | 0.9691 | 0.9564 | 0.9638 | 0.9626 |
| ROC AUC | 0.9851 | 0.9808 | 0.9816 | 0.9816 |
| Recall@3FPM | — | 0.6818 | 0.7727 | 0.7727 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
