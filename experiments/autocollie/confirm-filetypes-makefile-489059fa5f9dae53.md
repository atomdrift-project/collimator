# Confirm PASS — 489059fa5f9dae53 on `filetypes/makefile`

Cycle `20260527T061115-confirm-489059fa5f9dae53` — 2026-05-27T06:11:15Z

PR_AUC held across 3 seeds (orig 0.0769)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `489059fa5f9dae53` | `321898339fe9e58d` | `321898339fe9e58d` | `321898339fe9e58d` |
| PR AUC | 0.0769 | 0.0769 | 0.0769 | 0.0769 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=489059fa5f9dae53
```
