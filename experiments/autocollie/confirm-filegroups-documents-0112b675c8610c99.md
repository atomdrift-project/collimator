# Confirm PASS — 0112b675c8610c99 on `filegroups/documents`

Cycle `20260523T192616-confirm-0112b675c8610c99` — 2026-05-23T19:26:16Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `0112b675c8610c99` | `e916fda5f040c9d0` | `e916fda5f040c9d0` | `e916fda5f040c9d0` |
| PR AUC | 1.0000 | 0.9986 | 0.9987 | 0.9986 |
| ROC AUC | 0.9985 | 0.8989 | 0.9019 | 0.8989 |
| Recall@3FPM | — | 0.5075 | 0.6532 | 0.5075 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=0112b675c8610c99
```
