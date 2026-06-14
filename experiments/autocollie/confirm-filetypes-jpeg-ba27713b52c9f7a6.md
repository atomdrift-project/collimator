# Confirm FAIL — ba27713b52c9f7a6 on `filetypes/jpeg`

Cycle `20260613T233927-confirm-ba27713b52c9f7a6` — 2026-06-13T23:39:27Z

averaged ensemble PR_AUC regressed: 0.2746 -> 0.2584 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `ba27713b52c9f7a6` | `24cffd22a5ada381` | `24cffd22a5ada381` | `24cffd22a5ada381` |
| PR AUC | 0.2746 | 0.2560 | 0.2595 | 0.2376 |
| ROC AUC | 0.6732 | 0.6461 | 0.6537 | 0.5287 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
