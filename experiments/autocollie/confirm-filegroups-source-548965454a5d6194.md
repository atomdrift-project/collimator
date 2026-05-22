# Confirm PASS — 548965454a5d6194 on `filegroups/source`

Cycle `20260521T191111-confirm-548965454a5d6194` — 2026-05-21T19:11:11Z

PR_AUC held across 3 seeds (orig 0.9988)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `548965454a5d6194` | `d7a214a6430e0c44` | `d7a214a6430e0c44` | `d7a214a6430e0c44` |
| PR AUC | 0.9988 | 0.9988 | 0.9988 | 0.9987 |
| ROC AUC | 0.9981 | 0.9981 | 0.9980 | 0.9980 |
| Recall@3FPM | — | 0.9210 | 0.9310 | 0.8975 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=548965454a5d6194
```
