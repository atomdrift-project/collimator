# Confirm FAIL — ed10e9bff5a1cf12 on `filetypes/ole`

Cycle `20260525T202350-confirm-ed10e9bff5a1cf12` — 2026-05-25T20:23:50Z

averaged ensemble PR_AUC regressed: 1.0000 -> 0.9833 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `ed10e9bff5a1cf12` | `e33351408cf62a98` | `e33351408cf62a98` | `e33351408cf62a98` |
| PR AUC | 1.0000 | 0.9833 | 0.9833 | 0.9833 |
| ROC AUC | 1.0000 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
