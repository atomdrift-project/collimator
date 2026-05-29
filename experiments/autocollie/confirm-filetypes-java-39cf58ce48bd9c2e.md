# Confirm FAIL — 39cf58ce48bd9c2e on `filetypes/java`

Cycle `20260525T212754-confirm-39cf58ce48bd9c2e` — 2026-05-25T21:27:54Z

averaged ensemble PR_AUC regressed: 0.6056 -> 0.3889 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `39cf58ce48bd9c2e` | `f79af9b247b134e0` | `f79af9b247b134e0` | `f79af9b247b134e0` |
| PR AUC | 0.6056 | 0.3556 | 0.3889 | 0.3889 |
| ROC AUC | 0.8125 | 0.8021 | 0.8125 | 0.8125 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
