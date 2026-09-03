# Confirm PASS — 70383d155a63bb3e on `filetypes/xlsx`

Cycle `20260825T202207-confirm-70383d155a63bb3e` — 2026-08-25T20:22:07Z

PR_AUC held across 3 seeds (orig 0.9874)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `70383d155a63bb3e` | `29236a1348dee332` | `29236a1348dee332` | `29236a1348dee332` |
| PR AUC | 0.9874 | 0.9904 | 0.9713 | 0.9867 |
| ROC AUC | 0.7689 | 0.8165 | 0.5557 | 0.7563 |
| Recall@L50 | — | 0.3083 | 0.2991 | 0.2996 |
| verdict | — | PASS | FAIL | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=70383d155a63bb3e
```
