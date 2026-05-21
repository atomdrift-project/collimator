# Confirm FAIL — 22e2c91d61e7aa77 on `filetypes/text`

Cycle `20260521T031200-confirm-22e2c91d61e7aa77` — 2026-05-21T03:12:00Z

averaged ensemble PR_AUC regressed: 0.9684 -> 0.9602 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `22e2c91d61e7aa77` | `5fe73c8898deeacf` | `5fe73c8898deeacf` | `5fe73c8898deeacf` |
| PR AUC | 0.9684 | 0.9534 | 0.9571 | 0.9605 |
| ROC AUC | 0.9843 | 0.9808 | 0.9764 | 0.9790 |
| Recall@3FPM | — | 0.5455 | 0.7727 | 0.8182 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
