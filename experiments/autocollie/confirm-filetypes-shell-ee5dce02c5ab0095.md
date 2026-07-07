# Confirm FAIL — ee5dce02c5ab0095 on `filetypes/shell`

Cycle `20260705T163254-confirm-ee5dce02c5ab0095` — 2026-07-05T16:32:54Z

averaged ensemble PR_AUC regressed: 0.9608 -> 0.9547 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `ee5dce02c5ab0095` | `f2cd58c9f2480038` | `f2cd58c9f2480038` | `f2cd58c9f2480038` |
| PR AUC | 0.9608 | 0.9533 | 0.9545 | 0.9543 |
| ROC AUC | 0.9791 | 0.9783 | 0.9799 | 0.9791 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
