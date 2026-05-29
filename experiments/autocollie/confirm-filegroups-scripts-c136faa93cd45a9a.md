# Confirm PASS — c136faa93cd45a9a on `filegroups/scripts`

Cycle `20260528T034129-confirm-c136faa93cd45a9a` — 2026-05-28T03:41:29Z

PR_AUC held across 3 seeds (orig 0.9975)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c136faa93cd45a9a` | `ca39521ad01b4fb6` | `ca39521ad01b4fb6` | `ca39521ad01b4fb6` |
| PR AUC | 0.9975 | 0.9989 | 0.9989 | 0.9989 |
| ROC AUC | 0.9973 | 0.9988 | 0.9987 | 0.9988 |
| Recall@3FPM | — | 0.7042 | 0.6694 | 0.6709 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=c136faa93cd45a9a
```
