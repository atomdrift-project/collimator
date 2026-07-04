# Confirm PASS — 72d038b149724e88 on `filegroups/native`

Cycle `20260704T172725-confirm-72d038b149724e88` — 2026-07-04T17:27:25Z

PR_AUC held across 3 seeds (orig 0.9989)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `72d038b149724e88` | `bbc5621450ee3b48` | `bbc5621450ee3b48` | `bbc5621450ee3b48` |
| PR AUC | 0.9989 | 0.9995 | 0.9994 | 0.9994 |
| ROC AUC | 0.9989 | 0.9982 | 0.9981 | 0.9981 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=72d038b149724e88
```
