# Confirm PASS — e67b060e5bcc3a6a on `filegroups/scripts`

Cycle `20260704T083116-confirm-e67b060e5bcc3a6a` — 2026-07-04T08:31:16Z

PR_AUC held across 3 seeds (orig 0.9979)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e67b060e5bcc3a6a` | `d082d95ae7ab28d4` | `d082d95ae7ab28d4` | `d082d95ae7ab28d4` |
| PR AUC | 0.9979 | 0.9937 | 0.9937 | 0.9938 |
| ROC AUC | 0.9977 | 0.9949 | 0.9949 | 0.9949 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e67b060e5bcc3a6a
```
