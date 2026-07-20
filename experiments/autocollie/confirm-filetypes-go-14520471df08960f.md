# Confirm PASS — 14520471df08960f on `filetypes/go`

Cycle `20260710T225032-confirm-14520471df08960f` — 2026-07-10T22:50:32Z

PR_AUC held across 3 seeds (orig 0.9479)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `14520471df08960f` | `0ab1b381c2e94476` | `0ab1b381c2e94476` | `0ab1b381c2e94476` |
| PR AUC | 0.9479 | 0.9480 | 0.9478 | 0.9505 |
| ROC AUC | 0.9727 | 0.9740 | 0.9730 | 0.9744 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=14520471df08960f
```
