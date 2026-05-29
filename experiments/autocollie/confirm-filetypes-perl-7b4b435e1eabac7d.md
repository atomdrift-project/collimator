# Confirm FAIL — 7b4b435e1eabac7d on `filetypes/perl`

Cycle `20260526T194005-confirm-7b4b435e1eabac7d` — 2026-05-26T19:40:05Z

averaged ensemble PR_AUC regressed: 1.0000 -> 0.9908 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `7b4b435e1eabac7d` | `36c40c4802a543ef` | `36c40c4802a543ef` | `36c40c4802a543ef` |
| PR AUC | 1.0000 | 0.9908 | 0.9908 | 0.9881 |
| ROC AUC | 1.0000 | 0.9989 | 0.9989 | 0.9985 |
| Recall@3FPM | — | 0.9524 | 0.9524 | 0.9524 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
