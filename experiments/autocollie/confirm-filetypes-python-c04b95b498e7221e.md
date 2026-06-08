# Confirm PASS — c04b95b498e7221e on `filetypes/python`

Cycle `20260608T182718-confirm-c04b95b498e7221e` — 2026-06-08T18:27:18Z

PR_AUC held across 3 seeds (orig 0.9989)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c04b95b498e7221e` | `ea8d3dbab56212cb` | `ea8d3dbab56212cb` | `ea8d3dbab56212cb` |
| PR AUC | 0.9989 | 0.9938 | 0.9940 | 0.9939 |
| ROC AUC | 0.9989 | 0.9948 | 0.9949 | 0.9949 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=c04b95b498e7221e
```
