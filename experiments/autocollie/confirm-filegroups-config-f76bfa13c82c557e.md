# Confirm PASS — f76bfa13c82c557e on `filegroups/config`

Cycle `20260525T070827-confirm-f76bfa13c82c557e` — 2026-05-25T07:08:27Z

PR_AUC held across 3 seeds (orig 0.9997)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f76bfa13c82c557e` | `93af56d8afff0045` | `93af56d8afff0045` | `93af56d8afff0045` |
| PR AUC | 0.9997 | 0.9997 | 0.9997 | 0.9997 |
| ROC AUC | 0.9995 | 0.9995 | 0.9994 | 0.9995 |
| Recall@3FPM | — | 0.9013 | 0.8922 | 0.9522 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=f76bfa13c82c557e
```
