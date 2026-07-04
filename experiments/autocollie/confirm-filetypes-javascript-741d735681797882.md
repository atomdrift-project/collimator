# Confirm PASS — 741d735681797882 on `filetypes/javascript`

Cycle `20260704T095825-confirm-741d735681797882` — 2026-07-04T09:58:25Z

PR_AUC held across 3 seeds (orig 0.9994)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `741d735681797882` | `25d914ff909ad3ac` | `25d914ff909ad3ac` | `25d914ff909ad3ac` |
| PR AUC | 0.9994 | 0.9988 | 0.9988 | 0.9988 |
| ROC AUC | 0.9990 | 0.9986 | 0.9986 | 0.9986 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=741d735681797882
```
