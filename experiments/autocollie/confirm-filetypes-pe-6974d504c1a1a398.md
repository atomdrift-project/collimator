# Confirm PASS — 6974d504c1a1a398 on `filetypes/pe`

Cycle `20260608T104658-confirm-6974d504c1a1a398` — 2026-06-08T10:46:58Z

PR_AUC held across 3 seeds (orig 0.9989)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `6974d504c1a1a398` | `aabe6accc0ee6cf3` | `aabe6accc0ee6cf3` | `aabe6accc0ee6cf3` |
| PR AUC | 0.9989 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9990 | 0.9998 | 0.9998 | 0.9998 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=6974d504c1a1a398
```
