# Confirm PASS — e9adf33781332a00 on `filegroups/portable`

Cycle `20260522T164101-confirm-e9adf33781332a00` — 2026-05-22T16:41:01Z

PR_AUC held across 3 seeds (orig 0.9961)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e9adf33781332a00` | `60603d5829b59f05` | `60603d5829b59f05` | `60603d5829b59f05` |
| PR AUC | 0.9961 | 0.9960 | 0.9949 | 0.9970 |
| ROC AUC | 0.9990 | 0.9990 | 0.9988 | 0.9993 |
| Recall@3FPM | — | 0.7733 | 0.7733 | 0.8467 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e9adf33781332a00
```
