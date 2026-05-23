# Confirm FAIL — e8c27bda4d46d6db on `filetypes/pdf`

Cycle `20260523T213857-confirm-e8c27bda4d46d6db` — 2026-05-23T21:38:57Z

averaged ensemble PR_AUC regressed: 1.0000 -> 0.9942 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e8c27bda4d46d6db` | `b0448b309fefdb78` | `b0448b309fefdb78` | `b0448b309fefdb78` |
| PR AUC | 1.0000 | 0.9942 | 0.9942 | 0.9942 |
| ROC AUC | 0.9992 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
