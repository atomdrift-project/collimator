# Confirm PASS — 1b27ee11bdefd660 on `filegroups/native`

Cycle `20260528T090158-confirm-1b27ee11bdefd660` — 2026-05-28T09:01:58Z

PR_AUC held across 3 seeds (orig 0.9996)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `1b27ee11bdefd660` | `0374c9c8c9e9b19a` | `0374c9c8c9e9b19a` | `0374c9c8c9e9b19a` |
| PR AUC | 0.9996 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9996 | 0.9999 | 0.9999 | 0.9999 |
| Recall@3FPM | — | 0.8510 | 0.8178 | 0.8379 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=1b27ee11bdefd660
```
