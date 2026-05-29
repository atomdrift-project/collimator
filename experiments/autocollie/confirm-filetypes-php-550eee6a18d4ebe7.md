# Confirm FAIL — 550eee6a18d4ebe7 on `filetypes/php`

Cycle `20260526T215155-confirm-550eee6a18d4ebe7` — 2026-05-26T21:51:55Z

averaged ensemble PR_AUC regressed: 1.0000 -> 0.9924 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `550eee6a18d4ebe7` | `7c8e16626d64f6e6` | `7c8e16626d64f6e6` | `7c8e16626d64f6e6` |
| PR AUC | 1.0000 | 0.9928 | 0.9929 | 0.9913 |
| ROC AUC | 1.0000 | 0.9971 | 0.9968 | 0.9962 |
| Recall@3FPM | — | 0.1438 | 0.2009 | 0.1164 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
