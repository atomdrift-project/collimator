# Confirm PASS — a13f4ea43589ee4c on `filetypes/elf`

Cycle `20260607T030032-confirm-a13f4ea43589ee4c` — 2026-06-07T03:00:32Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a13f4ea43589ee4c` | `c738f38e16634281` | `c738f38e16634281` | `c738f38e16634281` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=a13f4ea43589ee4c
```
