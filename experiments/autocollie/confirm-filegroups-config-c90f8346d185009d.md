# Confirm PASS — c90f8346d185009d on `filegroups/config`

Cycle `20260524T185742-confirm-c90f8346d185009d` — 2026-05-24T18:57:42Z

PR_AUC held across 3 seeds (orig 0.9998)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c90f8346d185009d` | `71de9b1b466256f2` | `71de9b1b466256f2` | `71de9b1b466256f2` |
| PR AUC | 0.9998 | 0.9996 | 0.9997 | 0.9998 |
| ROC AUC | 0.9995 | 0.9992 | 0.9995 | 0.9996 |
| Recall@3FPM | — | 0.8391 | 0.8361 | 0.9539 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=c90f8346d185009d
```
