# Confirm FAIL — 7eef92f6a8464359 on `filetypes/ruby`

Cycle `20260526T191512-confirm-7eef92f6a8464359` — 2026-05-26T19:15:12Z

averaged ensemble PR_AUC regressed: 1.0000 -> 0.9627 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `7eef92f6a8464359` | `3fce07ede30eae64` | `3fce07ede30eae64` | `3fce07ede30eae64` |
| PR AUC | 1.0000 | 0.9192 | 0.9627 | 0.9093 |
| ROC AUC | 1.0000 | 0.9972 | 0.9986 | 0.9954 |
| Recall@3FPM | — | 0.4444 | 0.6667 | 0.5556 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
