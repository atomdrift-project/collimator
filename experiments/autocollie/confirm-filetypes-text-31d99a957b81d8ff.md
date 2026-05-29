# Confirm FAIL — 31d99a957b81d8ff on `filetypes/text`

Cycle `20260525T212046-confirm-31d99a957b81d8ff` — 2026-05-25T21:20:46Z

averaged ensemble PR_AUC regressed: 0.9558 -> 0.9361 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `31d99a957b81d8ff` | `6c4bdf0f9d944f45` | `6c4bdf0f9d944f45` | `6c4bdf0f9d944f45` |
| PR AUC | 0.9558 | 0.9276 | 0.9368 | 0.9431 |
| ROC AUC | 0.9738 | 0.9451 | 0.9505 | 0.9606 |
| Recall@3FPM | — | 0.6667 | 0.8095 | 0.7619 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
