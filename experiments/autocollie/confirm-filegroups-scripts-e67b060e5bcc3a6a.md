# Confirm PASS — e67b060e5bcc3a6a on `filegroups/scripts`

Cycle `20260601T151655-confirm-e67b060e5bcc3a6a` — 2026-06-01T15:16:55Z

PR_AUC held across 3 seeds (orig 0.9979)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e67b060e5bcc3a6a` | `1e434adc3e08c6a1` | `1e434adc3e08c6a1` | `1e434adc3e08c6a1` |
| PR AUC | 0.9979 | 0.9988 | 0.9987 | 0.9988 |
| ROC AUC | 0.9977 | 0.9986 | 0.9985 | 0.9986 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e67b060e5bcc3a6a
```
