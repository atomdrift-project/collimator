# Confirm PASS — a6cdcc86ecf36110 on `filetypes/json`

Cycle `20260702T235620-confirm-a6cdcc86ecf36110` — 2026-07-02T23:56:20Z

PR_AUC held across 3 seeds (orig 0.9691)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a6cdcc86ecf36110` | `2340d26c6b31dd3e` | `2340d26c6b31dd3e` | `2340d26c6b31dd3e` |
| PR AUC | 0.9691 | 0.9777 | 0.9744 | 0.9669 |
| ROC AUC | 0.9668 | 0.9831 | 0.9781 | 0.9743 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=a6cdcc86ecf36110
```
