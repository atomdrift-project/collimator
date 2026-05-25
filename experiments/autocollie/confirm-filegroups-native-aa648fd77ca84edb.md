# Confirm PASS — aa648fd77ca84edb on `filegroups/native`

Cycle `20260525T115420-confirm-aa648fd77ca84edb` — 2026-05-25T11:54:20Z

PR_AUC held across 3 seeds (orig 0.9995)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `aa648fd77ca84edb` | `afe4f9bc928efb53` | `afe4f9bc928efb53` | `afe4f9bc928efb53` |
| PR AUC | 0.9995 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9995 | 1.0000 | 1.0000 | 1.0000 |
| Recall@3FPM | — | 0.8928 | 0.9139 | 0.8390 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=aa648fd77ca84edb
```
