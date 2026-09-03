# Confirm FAIL — 7d4e2766b50addfa on `filetypes/shell`

Cycle `20260821T125102-confirm-7d4e2766b50addfa` — 2026-08-21T12:51:02Z

averaged ensemble PR_AUC regressed: 0.9715 -> 0.9639 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `7d4e2766b50addfa` | `1d929b42c0afdc85` | `1d929b42c0afdc85` | `1d929b42c0afdc85` |
| PR AUC | 0.9715 | 0.9612 | 0.9624 | 0.9646 |
| ROC AUC | 0.9853 | 0.9848 | 0.9860 | 0.9867 |
| Recall@L50 | — | 0.8368 | 0.8336 | 0.8377 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
