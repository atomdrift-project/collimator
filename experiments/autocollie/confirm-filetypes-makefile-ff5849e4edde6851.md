# Confirm PASS — ff5849e4edde6851 on `filetypes/makefile`

Cycle `20260607T204723-confirm-ff5849e4edde6851` — 2026-06-07T20:47:23Z

PR_AUC held across 3 seeds (orig 0.5111)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `ff5849e4edde6851` | `c3f1403daeb15cfa` | `c3f1403daeb15cfa` | `c3f1403daeb15cfa` |
| PR AUC | 0.5111 | 0.5528 | 0.5528 | 0.5111 |
| ROC AUC | 0.9219 | 0.9297 | 0.9297 | 0.9219 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=ff5849e4edde6851
```
