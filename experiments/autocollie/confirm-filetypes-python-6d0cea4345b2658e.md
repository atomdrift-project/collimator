# Confirm FAIL — 6d0cea4345b2658e on `filetypes/python`

Cycle `20260704T153855-confirm-6d0cea4345b2658e` — 2026-07-04T15:38:55Z

averaged ensemble PR_AUC regressed: 0.9112 -> 0.8423 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `6d0cea4345b2658e` | `feff635d23825558` | `feff635d23825558` | `feff635d23825558` |
| PR AUC | 0.9112 | 0.8359 | 0.8418 | 0.8407 |
| ROC AUC | 0.9555 | 0.9350 | 0.9484 | 0.9468 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
