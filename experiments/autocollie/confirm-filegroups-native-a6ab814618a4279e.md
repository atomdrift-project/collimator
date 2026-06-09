# Confirm PASS — a6ab814618a4279e on `filegroups/native`

Cycle `20260609T104349-confirm-a6ab814618a4279e` — 2026-06-09T10:43:49Z

PR_AUC held across 3 seeds (orig 0.9993)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a6ab814618a4279e` | `16e84f161b64801c` | `16e84f161b64801c` | `16e84f161b64801c` |
| PR AUC | 0.9993 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9993 | 0.9999 | 0.9999 | 0.9999 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=a6ab814618a4279e
```
