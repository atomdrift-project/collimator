# Confirm FAIL — 2cb18cafd329d4e1 on `filegroups/media`

Cycle `20260705T162925-confirm-2cb18cafd329d4e1` — 2026-07-05T16:29:25Z

averaged ensemble PR_AUC regressed: 0.2574 -> 0.1349 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `2cb18cafd329d4e1` | `97749f4f9212a700` | `97749f4f9212a700` | `97749f4f9212a700` |
| PR AUC | 0.2574 | 0.1151 | 0.1376 | 0.1305 |
| ROC AUC | 0.5637 | 0.5917 | 0.7133 | 0.7012 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
