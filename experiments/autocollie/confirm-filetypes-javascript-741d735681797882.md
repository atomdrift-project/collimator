# Confirm PASS — 741d735681797882 on `filetypes/javascript`

Cycle `20260601T210141-confirm-741d735681797882` — 2026-06-01T21:01:41Z

PR_AUC held across 3 seeds (orig 0.9994)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `741d735681797882` | `e47d587c9df281b4` | `e47d587c9df281b4` | `e47d587c9df281b4` |
| PR AUC | 0.9994 | 0.9992 | 0.9992 | 0.9992 |
| ROC AUC | 0.9990 | 0.9989 | 0.9990 | 0.9990 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=741d735681797882
```
