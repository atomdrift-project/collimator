# Confirm PASS — a1b887082ade9b7c on `filetypes/pe`

Cycle `20260712T172303-confirm-a1b887082ade9b7c` — 2026-07-12T17:23:03Z

PR_AUC held across 3 seeds (orig 0.9989)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a1b887082ade9b7c` | `c620cc7dc2051b2c` | `c620cc7dc2051b2c` | `c620cc7dc2051b2c` |
| PR AUC | 0.9989 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9989 | 0.9997 | 0.9998 | 0.9998 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=a1b887082ade9b7c
```
