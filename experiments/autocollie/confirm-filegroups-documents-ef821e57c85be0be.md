# Confirm PASS — ef821e57c85be0be on `filegroups/documents`

Cycle `20260704T140006-confirm-ef821e57c85be0be` — 2026-07-04T14:00:06Z

PR_AUC held across 3 seeds (orig 0.9374)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `ef821e57c85be0be` | `51a7cb4f54a15a96` | `51a7cb4f54a15a96` | `51a7cb4f54a15a96` |
| PR AUC | 0.9374 | 0.9770 | 0.9789 | 0.9793 |
| ROC AUC | 0.9037 | 0.8908 | 0.8987 | 0.9004 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=ef821e57c85be0be
```
