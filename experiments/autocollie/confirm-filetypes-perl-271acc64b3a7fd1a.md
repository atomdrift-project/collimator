# Confirm FAIL — 271acc64b3a7fd1a on `filetypes/perl`

Cycle `20260521T080327-confirm-271acc64b3a7fd1a` — 2026-05-21T08:03:27Z

averaged ensemble PR_AUC regressed: 1.0000 -> 0.9940 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `271acc64b3a7fd1a` | `eda9b5316106b469` | `eda9b5316106b469` | `eda9b5316106b469` |
| PR AUC | 1.0000 | 0.9978 | 0.9959 | 0.9940 |
| ROC AUC | 1.0000 | 0.9998 | 0.9996 | 0.9994 |
| Recall@3FPM | — | 0.9524 | 0.9524 | 0.9524 |
| verdict | — | PASS | PASS | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (2/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
