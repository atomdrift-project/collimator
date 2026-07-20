# Confirm PASS — c32b84c607a73447 on `filetypes/python-bytecode`

Cycle `20260711T000814-confirm-c32b84c607a73447` — 2026-07-11T00:08:14Z

PR_AUC held across 3 seeds (orig 0.9947)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c32b84c607a73447` | `48e87694ffbd64bf` | `48e87694ffbd64bf` | `48e87694ffbd64bf` |
| PR AUC | 0.9947 | 0.9938 | 0.9937 | 0.9942 |
| ROC AUC | 0.9974 | 0.9976 | 0.9975 | 0.9969 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=c32b84c607a73447
```
