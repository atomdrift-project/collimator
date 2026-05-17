# Confirm PASS — 302ea54c449b659f on `filetypes/javascript`

Cycle `20260515T231056-confirm-302ea54c449b659f` — 2026-05-15T23:10:56Z

PR_AUC held across 3 seeds (orig 0.9997)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `302ea54c449b659f` | `7592aa9bfaacf07a` | `7592aa9bfaacf07a` | `7592aa9bfaacf07a` |
| PR AUC | 0.9997 | 0.9998 | 0.9998 | 0.9998 |
| ROC AUC | 0.9995 | 0.9997 | 0.9997 | 0.9997 |
| Recall@3FPM | — | 0.8623 | 0.8287 | 0.8747 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=302ea54c449b659f
```
